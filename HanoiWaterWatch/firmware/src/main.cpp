#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_SSD1306.h>
#include <sys/time.h>
#include <time.h>
#include <esp_sntp.h>
#include "core.h"
#include "generated/registry.h"
#if __has_include("../include/config.h")
#include "../include/config.h"
#endif
#include "../include/config.example.h"

// Sampling and UI run independently of blocking HTTPS on core 0.
hww::Buffer buffer;
SemaphoreHandle_t guard;
OneWire wire(4); DallasTemperature temperature(&wire);
Adafruit_SSD1306 oled(128,64,&Wire,-1);
const unsigned faultPins[]={16,17,18,19};
volatile uint32_t lastAck=0,txAt=0; volatile int lastHttp=0;
volatile bool authError=false; volatile uint8_t serverStatus=0;
uint32_t seq=0, modeStart=0; unsigned mode=0; String boot;
volatile uint8_t timeSource=0;

String utc(int64_t milliseconds){
  time_t seconds=milliseconds/1000;struct tm t;gmtime_r(&seconds,&t);
  char out[32];strftime(out,sizeof(out),"%Y-%m-%dT%H:%M:%S",&t);
  char frac[8];snprintf(frac,sizeof(frac),".%03dZ",int(milliseconds%1000));return String(out)+frac;
}
int64_t epochNow(){struct timeval t;gettimeofday(&t,nullptr);return int64_t(t.tv_sec)*1000+t.tv_usec/1000;}
void syncServer(const String& stamp){
  if(timeSource==1 || stamp.length()<19)return;
  struct tm tm{};if(!strptime(stamp.c_str(),"%Y-%m-%dT%H:%M:%S",&tm))return;
  time_t seconds=mktime(&tm);struct timeval tv{seconds,0};settimeofday(&tv,nullptr);timeSource=2;
}
void serializeFrame(JsonObject out,const hww::Frame& f,uint32_t now){
  out["seq"]=f.seq;out["uptime_ms"]=f.uptime;out["buffered"]=uint32_t(now-f.uptime)>4000;
  out["mode"]=hww::modeName(f.mode);out["time_source"]=f.clock==1?"ntp":f.clock==2?"server":"uptime";
  if(f.clock)out["measured_at"]=utc(f.epoch);else out["measured_at"]=nullptr;
  JsonObject readings=out["readings"].to<JsonObject>();
  for(unsigned i=0;i<4;i++){
    const auto& r=f.readings[i];JsonObject j=readings[registry::channels[i].name].to<JsonObject>();
    if(r.fault)j["v"]=nullptr;else j["v"]=r.value;
    j["u"]=registry::channels[i].unit;j["q"]=r.fault?"fault":"ok";
    if(r.fault)j["fr"]=r.fault==1?"injected":r.fault==2?"disconnected":"out_of_range";
    if(r.raw<0 || r.fault)j["raw"]=nullptr;else j["raw"]=r.raw;
    j["gen"]=r.profile?"profile":"input";
  }
}
void uplink(void*){
  hww::Backoff backoff;unsigned limit=20,interval=2000;uint32_t due=0,lastConnect=0;bool metaDone=false;
  WiFiClientSecure tls;WiFiClient local;tls.setCACert(ROOT_CA_PEM);
  String base=INGEST_BASE_URL;
  // HTTP is allowed only on the optional private Wokwi loopback gateway.
  bool https=base.startsWith("https://");
  bool allowed=https || base=="http://host.wokwi.internal:8000";
  for(;;){
    uint32_t now=millis();
    if(digitalRead(23)==LOW){WiFi.disconnect();vTaskDelay(pdMS_TO_TICKS(100));continue;}
    if(WiFi.status()!=WL_CONNECTED){
      if(!lastConnect || now-lastConnect>=15000){WiFi.begin(WIFI_SSID,WIFI_PASSWORD,6);lastConnect=now;}
      vTaskDelay(pdMS_TO_TICKS(100));continue;
    }
    if(!allowed || (https && !strlen(ROOT_CA_PEM))){lastHttp=-2;vTaskDelay(pdMS_TO_TICKS(1000));continue;}
    if(int32_t(now-due)<0){vTaskDelay(pdMS_TO_TICKS(50));continue;}
    HTTPClient http;http.setTimeout(8000);http.setConnectTimeout(8000);http.setReuse(true);
    WiFiClient& client=https?static_cast<WiFiClient&>(tls):local;
    if(!metaDone){
      http.begin(client,base+"/api/v1/meta");int code=http.GET();
      if(code==200){JsonDocument doc;if(!deserializeJson(doc,http.getString())){syncServer(doc["server_time"].as<String>());metaDone=true;}}
      http.end();
    }
    xSemaphoreTake(guard,portMAX_DELAY);auto frames=buffer.select(limit);unsigned depth=buffer.size();unsigned dropped=buffer.dropped;xSemaphoreGive(guard);
    if(frames.empty()){vTaskDelay(pdMS_TO_TICKS(50));continue;}
    if(boot.isEmpty()){
      String seed=String(esp_random())+":"+utc(epochNow())+":"+String(millis());
      char id[9];snprintf(id,sizeof(id),"%08lx",(unsigned long)hww::crc32(seed.c_str()));boot=id;
    }
    now=millis();JsonDocument doc;doc["schema"]="hww.frames.v1";doc["station_code"]=registry::station;
    doc["device_code"]=registry::device;doc["boot_id"]=boot;doc["fw_version"]="0.4.0";
    doc["sent_uptime_ms"]=now;if(timeSource)doc["sent_at"]=utc(epochNow());else doc["sent_at"]=nullptr;
    JsonObject diag=doc["diag"].to<JsonObject>();diag["buffer_depth"]=depth;diag["dropped_frames"]=dropped;
    static unsigned rejected=0;diag["rejected_batches"]=rejected;diag["wifi_rssi"]=WiFi.RSSI();
    JsonArray list=doc["frames"].to<JsonArray>();for(const auto& f:frames)serializeFrame(list.add<JsonObject>(),f,now);
    String body;serializeJson(doc,body);http.begin(client,base+"/api/v1/ingest/frames");
    const char* headers[]={"Retry-After"};http.collectHeaders(headers,1);
    http.addHeader("Content-Type","application/json");http.addHeader("X-Device-Key",DEVICE_KEY);txAt=millis();
    int code=http.POST(body);lastHttp=code;unsigned wait=backoff.next(esp_random()%1001);
    if(code==200){
      JsonDocument response;if(!deserializeJson(response,http.getString())){
        xSemaphoreTake(guard,portMAX_DELAY);
        for(JsonObject result:response["results"].as<JsonArray>()){
          uint32_t acknowledged=result["seq"]; // Only acknowledge sequences actually submitted.
          for(const auto& f:frames)if(f.seq==acknowledged)buffer.ack(acknowledged);
        }xSemaphoreGive(guard);
        String status=response["station_status"].as<String>();serverStatus=status=="abnormal"?3:status=="degraded"?2:status=="normal"?1:0;
        syncServer(response["server_time"].as<String>());interval=std::max(2000u,response["next_min_interval_ms"].as<unsigned>());
        lastAck=millis();authError=false;backoff.reset();wait=interval;
      }
    }else if(code==401 || code==403){authError=true;wait=60000;}
    else if(code==409){xSemaphoreTake(guard,portMAX_DELAY);buffer.ack(frames[0].seq);xSemaphoreGive(guard);wait=10000;}
    else if(code==413){limit=std::max(1u,limit/2);}
    else if(code==422){xSemaphoreTake(guard,portMAX_DELAY);for(const auto& f:frames)buffer.ack(f.seq);xSemaphoreGive(guard);rejected++;}
    else if(code==429 || code==503){unsigned seconds=http.header("Retry-After").toInt();if(seconds)wait=seconds*1000;}
    http.end();due=millis()+std::max(interval,wait);
  }
}

void setup(){
  Serial.begin(115200);guard=xSemaphoreCreateMutex();
  for(auto pin:faultPins)pinMode(pin,INPUT_PULLUP);
  pinMode(23,INPUT_PULLUP);pinMode(33,INPUT_PULLUP);
  for(int pin:{25,26,27,14,2,13})pinMode(pin,OUTPUT);
  analogReadResolution(12);temperature.begin();temperature.setResolution(10);temperature.setWaitForConversion(false);temperature.requestTemperatures();
  Wire.begin(21,22);oled.begin(SSD1306_SWITCHCAPVCC,0x3c);oled.setTextSize(1);oled.setTextColor(SSD1306_WHITE);
  setenv("TZ","UTC0",1);tzset();
  // A cold ESP32 has no RTC date. Bootstrap TLS certificate date checks from
  // this build's date, but never label readings with that approximate clock.
  // Until NTP or authenticated meta succeeds, they remain uptime-only.
  if(time(nullptr)<1700000000){struct tm built{};strptime(__DATE__ " " __TIME__,"%b %d %Y %H:%M:%S",&built);struct timeval initial{mktime(&built),0};settimeofday(&initial,nullptr);}
  sntp_set_time_sync_notification_cb([](struct timeval*){timeSource=1;});
  WiFi.mode(WIFI_STA);configTime(0,0,"pool.ntp.org","time.google.com");
  xTaskCreatePinnedToCore(uplink,"uplink",16384,nullptr,1,nullptr,0);
}
void loop(){
  static uint32_t sampled=0,buttonChanged=0,uiAt=0,beepAt=0;static bool buttonRaw=true,buttonStable=true;
  static unsigned samples=0,lastStatus=0;static uint32_t sums[3]={};static hww::Frame latest;
  static float tempSum=0;static unsigned tempSamples=0,tempFault=0;
  uint32_t now=millis();bool button=digitalRead(33);
  if(button!=buttonRaw){buttonRaw=button;buttonChanged=now;}
  if(button!=buttonStable && now-buttonChanged>=50){buttonStable=button;if(!button){mode=(mode+1)%4;modeStart=now;}}
  if(mode && now-modeStart>=(mode==1?180000u:60000u))mode=0;
  if(now-sampled>=250){
    sampled=now;for(unsigned i=0;i<3;i++)sums[i]+=analogRead(registry::channels[i].pin);
    float measured=temperature.getTempCByIndex(0);
    if(measured==DEVICE_DISCONNECTED_C)tempFault=2;
    else if(measured<-55 || measured>125)tempFault=3;
    else{tempSum+=measured;tempSamples++;}
    temperature.requestTemperatures();
    samples++;
    if(samples==8){
      hww::Frame f;f.seq=seq++;f.uptime=now;f.clock=timeSource;f.epoch=f.clock?epochNow():0;
      for(unsigned i=0;i<3;i++){auto c=registry::channels[i];f.readings[i].raw=(sums[i]+4)/8;f.readings[i].value=hww::transfer(f.readings[i].raw,c.maximum,c.power,c.decimals);sums[i]=0;}
      f.readings[3].value=tempSamples?round(tempSum/tempSamples*100)/100:0;
      f.readings[3].fault=tempFault;tempSum=0;tempSamples=0;tempFault=0;
      hww::profile(f,mode,now-modeStart);
      for(unsigned i=0;i<4;i++)if(digitalRead(faultPins[i])==LOW)f.readings[i].fault=1;
      xSemaphoreTake(guard,portMAX_DELAY);buffer.push(f);xSemaphoreGive(guard);latest=f;samples=0;
    }
  }
  unsigned status=serverStatus;
  if(status==3 && lastStatus!=3)beepAt=now;lastStatus=status;
  unsigned elapsed=now-beepAt;if(beepAt && (elapsed<120 || (elapsed>=240 && elapsed<360)))tone(13,1200);else noTone(13);
  bool stale=!lastAck || now-lastAck>15000;
  digitalWrite(25,!authError && !stale && status==1);
  digitalWrite(26,!authError && (stale?(now/500)%2:status==2));
  digitalWrite(27,authError?(now/250)%2:!stale && status==3);
  digitalWrite(14,!authError && !stale && status==3);digitalWrite(2,txAt && now-txAt<50);
  if(now-uiAt>=250){
    uiAt=now;oled.clearDisplay();oled.setCursor(0,0);oled.printf("%s M%u\n",registry::station,mode);
    for(unsigned i=0;i<4;i++){oled.print(registry::channels[i].name);oled.print(' ');if(latest.readings[i].fault)oled.print("FAULT");else oled.print(latest.readings[i].value,registry::channels[i].decimals);oled.print(i%2?'\n':' ');}
    xSemaphoreTake(guard,portMAX_DELAY);unsigned depth=buffer.size();xSemaphoreGive(guard);
    oled.printf("%s q:%u #%lu\n",authError?"AUTH ERR":stale?"LINK LOST":"LINK OK",depth,(unsigned long)latest.seq);
    oled.printf("SRV %s %d\n",status==3?"ABNORMAL":status==2?"degraded":status==1?"normal":"unknown",lastHttp);
    oled.println("SIMULATED DATA");oled.display();
  }
  delay(1);
}
