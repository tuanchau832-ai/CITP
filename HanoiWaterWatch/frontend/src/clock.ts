import { useSyncExternalStore } from 'react';
let now = Date.now();
let offset = 0;
const listeners = new Set<() => void>();
let timer: ReturnType<typeof setInterval> | undefined;
export function syncServerClock(date: string | null) { if (date) {
    const n = Date.parse(date);
    if (Number.isFinite(n))
        offset = n - Date.now();
} }
function subscribe(cb: () => void) { listeners.add(cb); if (!timer)
    timer = setInterval(() => { now = Date.now() + offset; listeners.forEach(f => f()); }, 1000); return () => { listeners.delete(cb); if (!listeners.size && timer) {
    clearInterval(timer);
    timer = undefined;
} }; }
export function useClock() { return useSyncExternalStore(subscribe, () => now, () => now); }
