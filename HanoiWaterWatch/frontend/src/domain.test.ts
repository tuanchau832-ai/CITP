import { describe, it, expect } from 'vitest';
import { formatValue, acceptVersion, withGaps } from './domain';
describe('honest monitoring presentation', () => {
    it('does not turn missing or fault values into numbers', () => { expect(formatValue(null, 2)).toBe('—'); expect(formatValue(0, 2)).toBe('0.00'); });
    it('rejects an older snapshot', () => { expect(acceptVersion({ version: 5 }, { version: 4 })).toEqual({ version: 5 }); expect(acceptVersion({ version: 5 }, { version: 6 })).toEqual({ version: 6 }); });
    it('breaks history across missing samples', () => { expect(withGaps([{ t: '2026-01-01T00:00:00Z', v: 3 }, { t: '2026-01-01T00:00:10Z', v: 4 }], 2000)).toHaveLength(3); expect(withGaps([{ t: '2026-01-01T00:00:00Z', v: 3 }, { t: '2026-01-01T00:00:10Z', v: 4 }], 2000)[1].v).toBeNull(); });
});
