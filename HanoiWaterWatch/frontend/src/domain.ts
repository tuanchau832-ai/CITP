export const formatValue = (v: number | null | undefined, d = 2, locale = 'en') => v == null || !Number.isFinite(v) ? '—' : new Intl.NumberFormat(locale, { minimumFractionDigits: d, maximumFractionDigits: d }).format(v);
export const formatTime = (v: string | null | undefined, locale = 'en') => v ? new Intl.DateTimeFormat(locale, { timeZone: 'Asia/Ho_Chi_Minh', dateStyle: 'medium', timeStyle: 'medium' }).format(new Date(v)) + ' ICT' : '—';
export function acceptVersion<T extends {
    version: number;
}>(old: T | undefined, next: T): T { return old && old.version > next.version ? old : next; }
export function withGaps<T extends {
    t: string;
    v: number | null;
}>(points: T[], interval: number): (T | {
    t: string;
    v: null;
})[] { return points.flatMap((p, i) => i && Date.parse(p.t) - Date.parse(points[i - 1].t) > interval * 1.5 ? [{ t: new Date(Date.parse(points[i - 1].t) + interval).toISOString(), v: null }, p] : [p]); }
export const displayCurrent = (value: number | null, status: string, disconnected: boolean): number | null => disconnected || ['sensor_fault', 'offline', 'unavailable'].includes(status) ? null : value;
export const formatShortTime = (v: string, locale = 'en') => new Intl.DateTimeFormat(locale, { timeZone: 'Asia/Ho_Chi_Minh', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date(v));
export function historyCsv(points: Array<{
    t: string;
    v: number | null;
}>, unit: string) { return ['measured_at,value,unit,is_simulated', ...points.map(p => `${p.t},${p.v ?? ''},${unit},true`)].join('\n'); }
export function rollingWindow(now:number,hours:number){const end=Math.floor(now/10000)*10000;return {from:new Date(end-hours*3600000).toISOString(),to:new Date(end).toISOString()}}
export function mergeHistoryTail(points:Array<{t:string;v:number|null}>,sensor:{measured_at:string|null;value:number|null;status:string},from:string){const at=sensor.measured_at;if(!at||Date.parse(at)<Date.parse(from)||(points.length&&Date.parse(at)<=Date.parse(points[points.length-1].t)))return points;return [...points,{t:at,v:displayCurrent(sensor.value,sensor.status,false)}]}
export function scopedReviewId(alertId:string,serverId:number|undefined,local:{alertId:string;id:number}|undefined){return serverId??(local?.alertId===alertId?local.id:undefined)}
type AlertEvent={type:string;at:string;actor?:string;data?:{note?:string}};
export function visibleAlertEvents(events:AlertEvent[]|undefined,authenticated:boolean):AlertEvent[]{return authenticated?events||[]:(events||[]).filter(e=>e.type!=='note').map(({type,at})=>({type,at}))}
export function activeReplayId(station:string,status:string|undefined,session:{id:string;source:string;station_code?:string;ended_at?:string|null}|null|undefined):string|undefined{return status==='replay'&&session?.source==='simulated_replay'&&!session.ended_at&&(!session.station_code||session.station_code===station)?session.id:undefined}
