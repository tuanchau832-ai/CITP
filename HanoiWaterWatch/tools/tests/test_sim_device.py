import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sim_device as sim
class SimulatorTests(unittest.TestCase):
    def test_registry_units_and_channel_order(self):
        import json
        root=Path(__file__).resolve().parents[2]
        types=json.loads((root/'shared/registry/sensor_types.json').read_text(encoding='utf-8'))['types']
        self.assertEqual(sim.UNITS,{channel:types[channel]['unit'] for channel in sim.UNITS})
    def test_contract_and_fault(self):
        f=sim.frame(40, 'sensor-fault')
        self.assertEqual(f['readings']['turbidity']['q'],'fault')
        self.assertIsNone(f['readings']['turbidity']['v'])
        self.assertEqual(f['readings']['turbidity']['fr'],'injected')
        p=sim.envelope([f], 'HWW-KNG-001', 'wokwi-esp32-01', '123456ab')
        self.assertEqual(p['schema'],'hww.frames.v1')
        self.assertNotIn('source',p)
    def test_spike_and_recovery(self):
        self.assertEqual(sim.frame(0,'turbidity-spike')['readings']['turbidity']['v'],18.4)
        self.assertEqual(sim.frame(40,'turbidity-spike')['readings']['turbidity']['v'],180)
        self.assertEqual(sim.frame(80,'turbidity-spike')['readings']['turbidity']['v'],18.4)
    def test_profile_and_uptime(self):
        f=sim.frame(60,'gradual-ph',clock='uptime')
        self.assertEqual(f['readings']['ph']['v'],5.4)
        self.assertIsNone(f['measured_at'])
        self.assertEqual(f['readings']['ph']['gen'],'profile')
    def test_golden_all_phases(self):
        self.assertEqual(sim.frame(80,'demo-golden')['readings']['turbidity']['q'],'fault')
        self.assertEqual(sim.frame(95,'demo-golden')['readings']['turbidity']['q'],'ok')
        import tempfile,json
        with tempfile.TemporaryDirectory() as tmp:
            sim.fixtures(Path(tmp))
            records=[json.loads(line) for line in (Path(tmp)/'demo-golden.jsonl').read_text().splitlines()]
        self.assertFalse(any(200000<=r['t_offset_ms']<230000 for r in records))
        recovery=next(r for r in records if r['t_offset_ms']==230000)
        self.assertEqual(len(recovery['frames']),16)
        self.assertTrue(recovery['frames'][1]['buffered'])
if __name__=='__main__': unittest.main()
