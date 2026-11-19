"""Validate an uploaded GLB without a graphics stack (structure/identity/budgets)."""
import argparse
import json
from pathlib import Path
import struct
ROOT=Path(__file__).resolve().parents[1]
def check(path,registry_path):
    raw=path.read_bytes()
    if len(raw)>2*1024*1024:raise ValueError('GLB exceeds 2 MiB budget')
    if len(raw)<20:raise ValueError('Not a GLB')
    magic,version,total=struct.unpack_from('<III',raw)
    if magic!=0x46546c67 or version!=2 or total!=len(raw):raise ValueError('Invalid GLB v2 header')
    length,kind=struct.unpack_from('<II',raw,12)
    if kind!=0x4e4f534a:raise ValueError('Missing JSON chunk')
    doc=json.loads(raw[20:20+length]);nodes=doc.get('nodes',[])
    names={n.get('name'):n for n in nodes}
    registry=json.loads(registry_path.read_text(encoding='utf-8'))
    expected={c['node']:c['node'] for c in registry['model']['components']}
    expected.update({s['model_node']:s['uid'] for s in registry['sensors']})
    for node,uid in expected.items():
        if node not in names:raise ValueError('Missing node: '+node)
        if sum(n.get('name')==node for n in nodes)!=1:raise ValueError('Duplicate required node: '+node)
        if names[node].get('extras',{}).get('hww_id')!=uid:raise ValueError('Wrong hww_id: '+node)
    triangles=0
    for mesh in doc.get('meshes',[]):
        for primitive in mesh.get('primitives',[]):
            if primitive.get('mode',4)!=4:raise ValueError('Only TRIANGLES geometry is supported')
            accessor=primitive.get('indices',primitive.get('attributes',{}).get('POSITION'))
            if accessor is None:raise ValueError('Primitive lacks geometry accessor')
            triangles+=doc['accessors'][accessor]['count']//3
    if triangles>=100000:raise ValueError('Triangle budget exceeded')
    print(f'GLB structure, {len(expected)} required identities, {triangles} triangles, {len(raw)} bytes: passed')
    print('Visual orientation and hotspot-centre distances still require Blender/frontend verification.')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('path',type=Path);p.add_argument('--registry',type=Path,default=ROOT/'shared/registry/HWW-KNG-001.json');a=p.parse_args();check(a.path,a.registry)
if __name__=='__main__':main()
