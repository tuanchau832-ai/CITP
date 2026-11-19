import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Activity, Download, Box, Clock3 } from 'lucide-react';
import { useStationState, useStation, useHistory, useResource } from './api';
import { SensorCard, QueryState, StatusBadge, Source, useText, Empty } from './common';
import { formatTime, formatValue, withGaps, formatShortTime, historyCsv,rollingWindow,mergeHistoryTail } from './domain';
import {useClock} from './clock';
import type { Sensor } from './types';
export default function DashboardPage() { const { code = 'HWW-KNG-001' } = useParams(), { t } = useTranslation(), text = useText(); const q = useStationState(code), station = useStation(code); const [range, setRange] = useState('1'); const now=useClock();const {from,to}=rollingWindow(now,Number(range)); const timeline = useResource<{
    availability: {
        pct: number;
        received_frames: number;
        expected_frames: number;
    };
    items: Array<{
        at: string;
        type: string;
        sensor_uid: string | null;
        data: Record<string, unknown>;
    }>;
}>('timeline', `/stations/${code}/timeline?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}&limit=30`); return <><div className="page-title"><div><div className="eyebrow">{t('dashboard')} / {code}</div><h1>{text(station.data?.name)}</h1><p>{t('oneSnapshot')}</p></div><Link className="button" to={`/stations/${code}/model`}><Box size={16}/>{t('model')}</Link></div><QueryState loading={q.isLoading} error={q.error}/><div className="station-meta"><StatusBadge status={q.data?.station_status}/><Source state={q.data}/><span>{t('snapshot')} v{q.data?.version ?? '—'}</span><span>{t('lastFrame')}: {formatTime(q.data?.last_frame_at)}</span></div><div className="sensor-grid">{q.data?.sensors.map(s => <SensorCard key={s.uid} sensor={s} disconnected={q.isError}/>)}</div><div className="section-heading"><div><h2>{t('history')}</h2><p>{t('gapsVisible')}</p></div><label className="inline-label">{t('range')}<select value={range} onChange={e => setRange(e.target.value)}><option value="0.25">{t('minutes15')}</option><option value="1">{t('hour1')}</option><option value="6">{t('hours6')}</option><option value="24">{t('hours24')}</option><option value="168">{t('days7')}</option></select></label></div><div className="chart-grid">{q.data?.sensors.map(s => <HistoryChart key={s.uid} sensor={s} code={code} from={from} to={to}/>)}</div><section className="panel"><div className="panel-head"><h2><Clock3 size={18}/>{t('timeline')}</h2><span className="badge">{t('availability')}: {timeline.data ? formatValue(timeline.data.availability.pct, 1) + '%' : '—'}</span></div><QueryState loading={timeline.isLoading} error={timeline.error}/>{timeline.data?.items.length ? <div className="timeline">{timeline.data.items.map((e, i) => <div className="timeline-item" key={i}><span className="timeline-dot"/><div><strong>{e.type.replaceAll('_', ' ')}</strong><small>{e.sensor_uid || code} · {formatTime(e.at)}</small>{Boolean(e.data.alert_id) && <Link to={'/alerts/' + e.data.alert_id}>Alert #{String(e.data.alert_id)}</Link>}</div></div>)}</div> : <Empty>{t('noEvents')}</Empty>}</section></>; }
export function HistoryChart({ sensor, code, from, to }: {
    sensor: Sensor;
    code: string;
    from: string;
    to: string;
}) { const { t } = useTranslation(); const q = useHistory(code, sensor.channel, from, to); const [table, setTable] = useState(false); const interval = q.data?.bucket === 'raw' ? 2000 : q.data?.bucket === '10s' ? 10000 : q.data?.bucket === '1m' ? 60000 : q.data?.bucket === '5m' ? 300000 : 3600000; const data = withGaps(mergeHistoryTail(q.data?.points || [],sensor,from), interval); function csv() { const url = URL.createObjectURL(new Blob([historyCsv(q.data?.points || [], sensor.unit)], { type: 'text/csv;charset=utf-8' })); const a = document.createElement('a'); a.href = url; a.download = `${code}-${sensor.channel}-simulated.csv`; a.click(); URL.revokeObjectURL(url); } return <section className="panel chart-panel"><div className="panel-head"><div><h2>{sensor.channel === 'do' ? t('oxygenLabel') : sensor.channel === 'temp' ? t('tempLabel') : sensor.channel === 'ph' ? 'pH' : t('turbidityLabel')}</h2><p>{sensor.unit === 'degC' ? '°C' : sensor.unit} · {t('source')} · {q.data?.bucket || 'auto'}</p></div><div className="button-group"><button onClick={() => setTable(!table)}>{t(table ? 'chart' : 'table')}</button><button disabled={!data.length} onClick={csv} aria-label={t('csv')}><Download size={14}/></button></div></div><QueryState loading={q.isLoading} error={q.error}/>{!q.isLoading && !q.isError && !data.length ? <Empty>{t('noHistory')}</Empty> : table ? <div className="table-wrap"><table><thead><tr><th>{t('time')}</th><th>{t('value')}</th><th>{t('faults')}</th></tr></thead><tbody>{q.data?.points.map(p => <tr key={p.t}><td>{formatTime(p.t)}</td><td>{formatValue(p.v, sensor.decimals)} {sensor.unit}</td><td>{p.faults}</td></tr>)}</tbody></table></div> : <div className="chart"><ResponsiveContainer width="100%" height={220}><LineChart data={data} margin={{ left: 0, right: 20, top: 20, bottom: 5 }}><CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" vertical={false}/><XAxis dataKey="t" tickFormatter={v => formatShortTime(v)} tick={{ fontSize: 10 }} minTickGap={45}/><YAxis tick={{ fontSize: 10 }} width={42}/><Tooltip labelFormatter={v => formatTime(String(v))}/><Line type="linear" dataKey="v" name={sensor.channel} stroke="#0284c7" strokeWidth={2} dot={false} connectNulls={false} isAnimationActive={false}/></LineChart></ResponsiveContainer></div>}</section>; }
