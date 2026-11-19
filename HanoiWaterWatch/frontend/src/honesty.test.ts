import { it, expect } from 'vitest';
import { displayCurrent, formatTime } from './domain';
import en from './locales/en.json';
import vi from './locales/vi.json';
it('hides current values for sensor faults, offline and unavailable snapshots', () => { expect(displayCurrent(8, 'sensor_fault', false)).toBeNull(); expect(displayCurrent(8, 'offline', false)).toBeNull(); expect(displayCurrent(8, 'unavailable', false)).toBeNull(); expect(displayCurrent(8, 'normal', true)).toBeNull(); expect(displayCurrent(0, 'normal', false)).toBe(0); });
it('always renders timestamps in ICT', () => { expect(formatTime('2026-01-01T00:00:00Z')).toContain('7:00:00'); expect(formatTime('2026-01-01T00:00:00Z')).toContain('ICT'); });
it('provides both languages for every translation key', () => expect(Object.keys(en).sort()).toEqual(Object.keys(vi).sort()));
