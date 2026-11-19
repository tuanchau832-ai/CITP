#pragma once
#include <array>
#include <vector>
#include <cmath>
#include <cstdint>
#include <algorithm>
namespace hww {
inline uint32_t crc32(const char* value){uint32_t crc=0xffffffff;while(*value){crc^=uint8_t(*value++);for(unsigned i=0;i<8;i++)crc=(crc>>1)^(0xedb88320u&uint32_t(-int32_t(crc&1)));}return ~crc;}
inline double transfer(unsigned raw,double maximum,unsigned power,unsigned decimals) {
  double scale=std::pow(10.,decimals);
  return std::round(maximum*std::pow(std::min(raw,4095u)/4095.,power)*scale)/scale;
}
struct Reading { float value=0; int16_t raw=-1; uint8_t fault=0; bool profile=false; };
struct Frame { uint32_t seq=0, uptime=0; int64_t epoch=0; uint8_t clock=0, mode=0; std::array<Reading,4> readings; };
class Buffer {
  std::array<Frame,600> frames{}; size_t count=0, head=0;
public:
  uint32_t dropped=0;
  size_t size() const {return count;}
  void push(const Frame& frame) { if(count==600){head=(head+1)%600; count--; dropped++;} frames[(head+count++)%600]=frame; }
  std::vector<Frame> select(size_t limit) const {
    std::vector<Frame> out; if(!count || !limit)return out;
    out.push_back(frames[(head+count-1)%600]);
    for(size_t i=0;i+1<count && out.size()<limit;i++)out.push_back(frames[(head+i)%600]);
    return out;
  }
  void ack(uint32_t seq) {for(size_t i=0;i<count;i++)if(frames[(head+i)%600].seq==seq){for(size_t j=i;j+1<count;j++)frames[(head+j)%600]=frames[(head+j+1)%600];count--;break;}}
};
class Backoff { unsigned step=0; public:
  unsigned next(unsigned random1000) {unsigned base=std::min(30000u,1000u<<std::min(step++,5u));return base*(800+std::min(random1000,1000u)*.4)/1000;}
  void reset(){step=0;}
};
inline const char* modeName(unsigned mode){return mode==1?"gradual_ph":mode==2?"spike_turb":mode==3?"do_drop":"manual";}
inline void profile(Frame& f,unsigned mode,uint32_t elapsed) {
  f.mode=mode;
  if(mode==1){f.readings[0].value=std::round((7.2f-1.8f*std::min(elapsed/120000.f,1.f))*100)/100;f.readings[0].profile=true;f.readings[0].raw=-1;}
  if(mode==2){f.readings[2].value=180;f.readings[2].profile=true;f.readings[2].raw=-1;}
  if(mode==3){f.readings[1].value=1.8;f.readings[1].profile=true;f.readings[1].raw=-1;}
}
}
