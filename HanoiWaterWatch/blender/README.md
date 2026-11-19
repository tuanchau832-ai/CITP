# Station model handoff

The user will upload the station model. No source model, generated stand-in or
GLB is included. The application uses its accessible schematic until that file
is provided. Tinkercad design URL: awaiting the user's upload.

Export the source as OBJ + MTL, in millimetres. Give each clickable component a
unique material/colour. Put both files in `blender/source/`. Use the registry's
model components and sensor model_node fields for the exact required node names.
Fill `scripts/material_map.json` with `{ "imported_material_name": "sensor_ph" }`
entries for every material. The empty map deliberately fails until real materials
can be inspected. Static parts also need explicit mappings.

Run from the repository root with Blender 4.x:

```powershell
blender -b -P blender/scripts/prepare_station.py -- --input blender/source/station.obj --map blender/scripts/material_map.json --registry shared/registry/HWW-KNG-001.json --out blender/out/station-v1.raw.glb
```

The script scales millimetres to metres, separates materials, merges meshes
assigned to each node, validates names, assigns hww_id extras, cleans geometry,
sets independent PBR materials, writes a GLB and .blend, and reports triangle
counts and glTF-space centres. Review report hotspot coordinates against the
registry after upload. The default OBJ axis interpretation must be visually
checked on the supplied export. Verify <100,000 triangles and <=2 MB after
optimisation; preserve nodes/materials when optimising. Do not rename nodes in
the frontend to accommodate an unvalidated export.

Blender is not installed on the current machine; execution and visual export
verification await the source and Blender runtime.
