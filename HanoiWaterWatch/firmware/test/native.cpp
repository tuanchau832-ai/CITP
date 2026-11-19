#include "core.h"
#include <cassert>
#include <cmath>
#include <iostream>
int main() {
  assert(hww::crc32("123456789")==0xcbf43926u);
  assert(std::abs(hww::transfer(2109,14,1,2)-7.21)<.001);
  assert(std::abs(hww::transfer(555,1000,2,1)-18.4)<.001);
  hww::Buffer b;
  for(unsigned i=0;i<605;i++){ hww::Frame f{}; f.seq=i; b.push(f); }
  assert(b.size()==600 && b.dropped==5);
  auto batch=b.select(20);
  assert(batch.size()==20 && batch[0].seq==604 && batch[1].seq==5 && batch[19].seq==23);
  b.ack(604); b.ack(7); b.ack(999);
  assert(b.size()==598 && b.select(1)[0].seq==603);
  hww::Backoff back;
  for(unsigned expected: {1000,2000,4000,8000,16000,30000,30000}) assert(back.next(500)==expected);
  back.reset(); assert(back.next(0)==800); assert(back.next(1000)==2400);
  hww::Frame f{};hww::profile(f,1,120000);assert(std::abs(f.readings[0].value-5.4)<.001 && f.readings[0].profile);
  std::cout << "transfer, overflow, live-first batches, selective acknowledgements, backoff: passed\n";
}
