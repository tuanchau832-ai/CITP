"""Run inside Blender 4.x: import the user's OBJ, bind named nodes and export GLB.

Material map is {"exact imported material name": "registry_node"}. Unknown
materials and missing nodes fail rather than silently substituting geometry.
"""
import argparse
import json
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True);p.add_argument('--map',type=Path,required=True)
    p.add_argument('--registry',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--scale',type=float,default=.001)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    if not a.input.is_file():raise ValueError('Upload the station OBJ and associated MTL first: '+str(a.input))
    mapping=json.loads(a.map.read_text(encoding='utf-8'));registry=json.loads(a.registry.read_text(encoding='utf-8'))
    required={c['node']:c for c in registry['model']['components']}
    for sensor in registry['sensors']:required[sensor['model_node']]={'kind':'sensor','hww_id':sensor['uid']}
    if not mapping:raise ValueError('Fill material_map.json from the uploaded OBJ material names before running.')
    if set(mapping.values())-set(required):raise ValueError('Unknown registry nodes: '+str(set(mapping.values())-set(required)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=str(a.input.resolve()),global_scale=a.scale)
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    if not meshes:raise ValueError('Input contains no meshes')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join()
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
    groups={}
    for obj in list(bpy.context.scene.objects):
        if obj.type!='MESH':continue
        mats={obj.material_slots[polygon.material_index].material.name for polygon in obj.data.polygons
              if polygon.material_index<len(obj.material_slots) and obj.material_slots[polygon.material_index].material}
        if len(mats)!=1:raise ValueError(f'Expected one material per separated mesh: {obj.name}: {mats}')
        material=next(iter(mats))
        if material not in mapping:raise ValueError('Unmapped material: '+material)
        groups.setdefault(mapping[material],[]).append(obj)
    missing=set(required)-set(groups)
    if missing:raise ValueError('Missing required nodes: '+', '.join(sorted(missing)))
    report=[];total=0
    for node,objects in sorted(groups.items()):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1:bpy.ops.object.join()
        obj=bpy.context.object;obj.name=node;obj.data.name=node+'_mesh';obj['hww_id']=required[node].get('hww_id',node)
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        bmesh.ops.remove_doubles(mesh,verts=list(mesh.verts),dist=.0001)
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces))
        mesh.to_mesh(obj.data);mesh.free();obj.data.update()
        material=bpy.data.materials.new('mat_'+node);material.use_nodes=True
        shader=material.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.584,.617,.673,1);shader.inputs['Roughness'].default_value=.5
        if required[node].get('kind')=='indicator':
            shader.inputs['Emission Color'].default_value=(.584,.617,.673,1);shader.inputs['Emission Strength'].default_value=.25
        obj.data.materials.clear();obj.data.materials.append(material)
        obj.data.calc_loop_triangles();triangles=len(obj.data.loop_triangles);total+=triangles
        corners=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
        center=[sum(v[i] for v in corners)/8 for i in range(3)]
        # Convert Blender Z-up coordinates to glTF Y-up for registry hotspots.
        report.append({'node':node,'hww_id':obj['hww_id'],'triangles':triangles,'hotspot':[center[0],center[2],-center[1]]})
    if total>=100000:raise ValueError(f'Triangle budget exceeded: {total}')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out.with_suffix('.blend').resolve()))
    bpy.ops.export_scene.gltf(filepath=str(a.out.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_apply=True,export_cameras=False,export_lights=False)
    report_path=a.out.with_suffix('.report.json');report_path.write_text(json.dumps({'triangles':total,'nodes':report},indent=2)+'\n',encoding='utf-8')
    print('Prepared uploaded model:',a.out,'Report:',report_path)
if __name__=='__main__':main()
