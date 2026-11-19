# ESP32 / Wokwi

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for setup, wiring controls, verification
evidence and outstanding live hardware checks. All sensor values are simulated.

```powershell
python tools/gen_registry.py
python tools/check_registry.py
pio run -d firmware -e esp32
pio run -d firmware -e native
python tools/bundle_wokwi_web.py --config firmware/include/config.h
```

Copy `include/config.example.h` to ignored `include/config.h`, then supply the
demo endpoint, demo device key and actual TLS root CA. Never disable certificate
verification. `diagram.json` includes every power/signal/indicator connection.

Software simulations, without Wokwi:

```powershell
python tools/sim_device.py --scenario demo-golden --frames 131 --out batches.jsonl
python tools/sim_device.py --scenario demo-golden --frames 131 --recording --out recording.jsonl
python tools/sim_device.py --fault turbidity:70:110 --outage 150:180 --out batches.jsonl
```

`--out` defaults to exact hww.frames.v1 envelopes; `--recording` selects replay
records `{t_offset_ms,frames:[...]}`. Replay inputs committed to
`shared/fixtures/replays/` use the latter format.
