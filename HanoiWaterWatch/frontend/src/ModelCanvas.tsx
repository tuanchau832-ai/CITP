import { Suspense, useEffect, useMemo, useRef } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { Bounds, OrbitControls, useGLTF } from '@react-three/drei';
import { Mesh, MeshStandardMaterial } from 'three';
import type { OrbitControls as OrbitControlsType } from 'three-stdlib';
import type { Sensor, Status } from './types';
import { statusColor } from './common';
function Asset({ sensors, status, onSelect }: {
    sensors: Sensor[];
    status: Status;
    onSelect: (s: string) => void;
}) { const gltf = useGLTF('/models/station-v1.glb'); const scene = useMemo(() => { const clone = gltf.scene.clone(true); clone.traverse(o => { if (o instanceof Mesh) {
    o.material = Array.isArray(o.material) ? o.material.map(m => m.clone()) : o.material.clone();
} }); return clone; }, [gltf.scene]); useEffect(() => () => { scene.traverse(o => { if (o instanceof Mesh)
    (Array.isArray(o.material) ? o.material : [o.material]).forEach(m => m.dispose()); }); }, [scene]); useEffect(() => { scene.traverse(o => { if (o instanceof Mesh) {
    const s = sensors.find(s => s.model_node === o.name);
    const mats = (Array.isArray(o.material) ? o.material : [o.material]) as MeshStandardMaterial[];
    if (s) {
        mats.forEach(m => { m.color.set(statusColor(s.status)); m.transparent = true; m.opacity = ['offline', 'unavailable'].includes(s.status) ? .6 : 1; });
        o.userData.channel = s.channel;
    }
    const on = o.name === 'beacon' ? status === 'abnormal' : o.name === 'led_red' ? status === 'abnormal' : o.name === 'led_yellow' ? status === 'degraded' : o.name === 'led_green' ? status === 'normal' : null;
    if (on !== null)
        mats.forEach(m => { m.emissive?.set(on ? o.name === 'led_green' ? '#16a34a' : o.name === 'led_yellow' ? '#d97706' : '#dc2626' : '#000000'); m.emissiveIntensity = on ? 1 : 0; });
} }); }, [scene, sensors, status]); return <primitive object={scene} onClick={(e: {
    stopPropagation: () => void;
    object: Mesh;
}) => { e.stopPropagation(); if (e.object.userData.channel)
    onSelect(e.object.userData.channel); }}/>; }
function Controls() { const ref = useRef<OrbitControlsType>(null); const { camera, gl } = useThree(); useEffect(() => { const element = gl.domElement; element.tabIndex = 0; element.setAttribute('aria-label', 'Station model: arrow keys rotate, plus and minus zoom, R resets'); function key(e: KeyboardEvent) { const c = ref.current; if (!c)
    return; if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', '+', '-', 'r', 'R'].includes(e.key)) {
    e.preventDefault();
    if (e.key === 'r' || e.key === 'R')
        c.reset();
    else if (e.key === '+' || e.key === '-')
        camera.position.multiplyScalar(e.key === '+' ? .9 : 1.1);
    else {
        const p = camera.position;
        const a = e.key === 'ArrowLeft' ? .1 : e.key === 'ArrowRight' ? -.1 : 0;
        const x = p.x;
        p.x = x * Math.cos(a) - p.z * Math.sin(a);
        p.z = x * Math.sin(a) + p.z * Math.cos(a);
        if (e.key === 'ArrowUp')
            p.y += .15;
        if (e.key === 'ArrowDown')
            p.y -= .15;
    }
    c.update();
} } element.addEventListener('keydown', key); return () => element.removeEventListener('keydown', key); }, [camera, gl]); return <OrbitControls ref={ref} makeDefault/>; }
export default function ModelCanvas({ sensors, status, onSelect }: {
    sensors: Sensor[];
    status: Status;
    onSelect: (s: string) => void;
}) { return <Canvas camera={{ position: [3, 2, 4], fov: 45 }} onCreated={({ gl }) => { gl.domElement.addEventListener('webglcontextlost', () => { gl.domElement.dispatchEvent(new CustomEvent('hww-context-lost', { bubbles: true })); }); }} aria-label="Station digital model"><ambientLight intensity={1.5}/><directionalLight position={[4, 6, 2]} intensity={2}/><directionalLight position={[-4, 3, -2]} intensity={1}/><Suspense fallback={null}><Bounds fit clip observe margin={1.3}><Asset sensors={sensors} status={status} onSelect={onSelect}/></Bounds></Suspense><Controls /></Canvas>; }
