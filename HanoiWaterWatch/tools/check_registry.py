"""Check channel mappings, complete circuit wiring and generated firmware freshness."""
import json
from pathlib import Path
from gen_registry import generate
ROOT=Path(__file__).resolve().parents[1]
def check():
    station=json.loads((ROOT/'shared/registry/HWW-KNG-001.json').read_text(encoding='utf-8'))
    assert [s['channel'] for s in station['sensors']]==['ph','do','turbidity','temp'],'firmware channel order must follow blueprint 05'
    types=json.loads((ROOT/'shared/registry/sensor_types.json').read_text(encoding='utf-8'))['types']
    diagram=json.loads((ROOT/'firmware/diagram.json').read_text(encoding='utf-8'))
    ids=[p['id'] for p in diagram['parts']];assert len(ids)==len(set(ids)), 'duplicate part IDs'
    edges={frozenset(c[:2]) for c in diagram['connections']}
    for c in diagram['connections']:
        for endpoint in c[:2]:assert endpoint.split(':')[0] in ids, endpoint
    for sensor in station['sensors']:
        assert sensor['channel'] in types
        part=sensor['wokwi']['part_id'];pin=sensor['wokwi']['pin']
        assert part in ids
        signal='DQ' if sensor['channel']=='temp' else 'SIG'
        assert frozenset([part+':'+signal,'esp:'+pin]) in edges
        for name,target in [('VCC','esp:3V3'),('GND','esp:GND.1')]:assert frozenset([part+':'+name,target]) in edges
    for i,pin in enumerate([16,17,18,19,23],1):
        assert frozenset([f'dip1:{i}a',f'esp:{pin}']) in edges
        assert frozenset([f'dip1:{i}b','esp:GND.1']) in edges
    assert (ROOT/'firmware/src/generated/registry.h').read_text(encoding='utf-8')==generate(),'run tools/gen_registry.py'
    print('Registry, generated constants, ADC1 pins, sensor power, fault and network wiring: passed')
if __name__=='__main__':check()
