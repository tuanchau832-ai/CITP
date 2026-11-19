"""Cross-subsystem checks on artifacts produced by independent implementations."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.schemas import Batch


class ContractTests(unittest.TestCase):
    def test_replay_frames_validate_against_real_ingest_model(self):
        recordings = list((ROOT / 'shared/fixtures/replays').glob('*.jsonl'))
        self.assertGreaterEqual(len(recordings), 6)
        types = json.loads((ROOT / 'shared/registry/sensor_types.json').read_text(encoding='utf-8-sig'))['types']
        for path in recordings:
            last_offset = -1
            for line in path.read_text(encoding='utf-8-sig').splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                self.assertGreaterEqual(record['t_offset_ms'], last_offset)
                last_offset = record['t_offset_ms']
                frames = record['frames']
                batch = Batch.model_validate({
                    'schema': 'hww.frames.v1', 'station_code': 'HWW-KNG-001',
                    'device_code': 'wokwi-esp32-01', 'boot_id': '1234abcd',
                    'fw_version': 'contract-test', 'sent_at': None,
                    'sent_uptime_ms': max(frame['uptime_ms'] for frame in frames),
                    'diag': {}, 'frames': frames,
                })
                for frame in batch.frames:
                    for channel, reading in frame.readings.items():
                        self.assertIn(channel, types)
                        self.assertEqual(reading.u, types[channel]['unit'])

    def test_station_identity_and_planned_station(self):
        records = [json.loads(p.read_text(encoding='utf-8-sig')) for p in (ROOT / 'shared/registry').glob('HWW-*.json')]
        self.assertEqual(len(records), 3)
        self.assertEqual(len({r['station']['code'] for r in records}), 3)
        for registry in records:
            code = registry['station']['code']
            self.assertEqual({s['channel'] for s in registry['sensors']}, {'ph', 'do', 'turbidity', 'temp'})
            for sensor in registry['sensors']:
                self.assertEqual(sensor['uid'], code + ':' + sensor['channel'])
            self.assertEqual(registry['station']['location']['precision'], 'illustrative')
            if registry['station']['data_mode'] == 'planned':
                self.assertFalse(registry.get('device'))


if __name__ == '__main__':
    unittest.main()
