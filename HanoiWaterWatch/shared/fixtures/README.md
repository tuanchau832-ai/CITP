# Synthetic replay fixtures

`replays/*.jsonl` is the authoritative deterministic replay input. Each line is
`{"t_offset_ms": 0, "frames": [...]}`. Time offsets are relative to the replay
session; backend replay shifts frame timestamps to the new session start.
No fixture represents environmental measurements.

Regenerate all six with `python tools/sim_device.py --fixtures shared/fixtures/replays`.
Each fixture runs from 0 to 240 seconds at two-second intervals (demo-golden
runs to 260 seconds). Normal defaults
are pH 7.21, DO 6.40 mg/L, turbidity 18.4 NTU and temperature 27.25 degC.

- demo-golden: 70 s baseline, 180 NTU until 130 s, recovery, turbidity fault
  150–180 s, recovery, network gap 200–230 s and buffered reconnect.
- tlh-loop: 70 s baseline, 180 NTU until 130 s, then recovery.
- turbidity-spike: same deterministic spike for isolated rule tests.
- gradual-ph: pH falls 7.2 to 5.4 over 120 s, holds to 180 s, then recovers.
- sensor-fault: injected turbidity fault from 70 s until 110 s; null value/raw.
- network-gap: no deliveries from 70 s to 100 s; recovery carries the newest
  frame first plus 15 buffered old frames. No readings are lost.

To emit complete ingest envelopes instead, use
`python tools/sim_device.py --scenario turbidity-spike --out batches.jsonl`.
These output envelopes are wire-compatible with `/api/v1/ingest/frames`.
