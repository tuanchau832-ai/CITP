"""Create the complete, deterministic Wokwi circuit from blueprint 04."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parts=[];connections=[]
def part(kind,id,x,y,**attrs):parts.append(dict(type=kind,id=id,left=x,top=y,attrs=attrs))
def wire(a,b,color='green'):connections.append([a,b,color,[]])
def power(id):wire(id+':VCC','esp:3V3','red');wire(id+':GND','esp:GND.1','black')
part('board-esp32-devkit-c-v4','esp',0,0)
for id,pin,y,value in [('pot_ph',34,-180,527),('pot_do',35,-100,327),('pot_turb',32,-20,139)]:
    part('wokwi-slide-potentiometer',id,-280,y,value=str(value),travelLength='30');power(id);wire(id+':SIG','esp:'+str(pin),'orange')
part('wokwi-ds18b20','temp1',-200,130,temperature='27.25');power('temp1');wire('temp1:DQ','esp:4')
part('wokwi-resistor','r_ow',-120,100,value='4700');wire('r_ow:1','temp1:DQ');wire('r_ow:2','esp:3V3','red')
part('wokwi-dip-switch-8','dip1',160,260)
for n,pin in enumerate([16,17,18,19,23],1):wire(f'dip1:{n}a',f'esp:{pin}');wire(f'dip1:{n}b','esp:GND.1','black')
part('wokwi-pushbutton','btn_mode',-60,260,color='blue',label='MODE');wire('btn_mode:1.l','esp:33');wire('btn_mode:2.l','esp:GND.1','black')
part('board-ssd1306','oled1',200,-180,i2cAddress='0x3c');power('oled1');wire('oled1:SDA','esp:21');wire('oled1:SCL','esp:22')
for n,(id,pin,color) in enumerate([('led_g',25,'green'),('led_y',26,'yellow'),('led_r',27,'red'),('led_beacon',14,'red'),('led_tx',2,'blue')]):
    x=220+n*65;part('wokwi-led',id,x,-20,color=color);part('wokwi-resistor','r_'+id,x,60,value='220')
    wire('esp:'+str(pin),'r_'+id+':1');wire('r_'+id+':2',id+':A');wire(id+':C','esp:GND.1','black')
part('wokwi-buzzer','bz1',350,150,volume='0.1');wire('bz1:2','esp:13');wire('bz1:1','esp:GND.1','black')
if __name__=='__main__':(ROOT/'firmware/diagram.json').write_text(json.dumps(dict(version=1,author='Hanoi WaterWatch',editor='wokwi',parts=parts,connections=connections),indent=2)+'\n',encoding='utf-8')
