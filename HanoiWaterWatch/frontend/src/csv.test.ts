import { it, expect } from 'vitest';
import { historyCsv } from './domain';
it('exports separate CSV records and leaves missing values empty', () => { expect(historyCsv([{ t: '2026-01-01T00:00:00Z', v: null }, { t: '2026-01-01T00:00:02Z', v: 0 }], 'NTU')).toBe('measured_at,value,unit,is_simulated\n2026-01-01T00:00:00Z,,NTU,true\n2026-01-01T00:00:02Z,0,NTU,true'); });
