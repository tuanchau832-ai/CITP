import { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet';
import { useNavigate } from 'react-router-dom';
import type { Station, Snapshot } from './types';
import { statusColor } from './common';
import 'leaflet/dist/leaflet.css';
export default function StationMap({ stations, states }: {
    stations: Station[];
    states: (Snapshot | undefined)[];
}) { const nav = useNavigate(); const [failed, setFailed] = useState(false); return <div className="map-wrap"><MapContainer center={[21.005, 105.826]} zoom={12} scrollWheelZoom={false} aria-hidden="true"><TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" eventHandlers={{ tileerror: () => setFailed(true) }}/>{stations.map((s, i) => <CircleMarker key={s.code} center={[s.location.lat, s.location.lng]} radius={11} pathOptions={{ color: '#fff', weight: 3, fillColor: statusColor(states[i]?.station_status || 'unavailable'), fillOpacity: 1 }} eventHandlers={{ click: () => nav(`/stations/${s.code}/model`) }}><Tooltip>{s.code} · {states[i]?.station_status || 'unavailable'}</Tooltip></CircleMarker>)}</MapContainer>{failed && <span className="map-notice">Map tiles unavailable · use the station list</span>}<span className="map-caption">Illustrative locations · Hanoi, Vietnam</span></div>; }
