# Firmware and simulation delivery

ESP32 source implements ADC1 sampling at 4 Hz, averaging eight samples into a
two-second frame, asynchronous 10-bit DS18B20 conversions, injected channel
faults, debounced MODE profiles, and a 600-frame ring buffer. A separate core-0
uplink task sends the newest frame plus up to 19 oldest frames, keeps frames
until individual acknowledgements, and applies response-specific retry/drop
behavior. Server station status drives lamps, beacon, OLED and transition
buzzer; the device contains no water-quality alert thresholds.

The clock starts NTP and falls back to the meta response's server_time. A cold
RTC uses the firmware build timestamp solely to bootstrap TLS certificate date
verification; it never labels sample timestamps as authoritative. NTP's sync
callback or authenticated server_time establishes the actual frame clock. Frames
created before a clock is available use null measured_at with uptime metadata.
Boot identity uses CRC32 of ESP32 randomness, clock and uptime once at first
send. All profiles and slider transfer curves are explicitly synthetic.

## Configure and run

1. Copy `include/config.example.h` to ignored `include/config.h`.
2. Set HTTPS host, station-scoped demo key and the host's actual root CA PEM.
   No key or certificate is supplied. Empty CA refuses transmission. Certificate
   verification remains enabled. Only `http://host.wokwi.internal:8000` is allowed
   as an HTTP exception for the documented private-gateway topology.
3. Install PlatformIO and run `pio run -d firmware -e esp32` from the root.
4. Open `firmware/diagram.json` in Wokwi, or generate the web folder:
   `python tools/bundle_wokwi_web.py --config firmware/include/config.h`.
   Upload its files to a Wokwi ESP32 project; config.h stays git-ignored.
5. Set the sliders as desired. Their initial Wokwi 10-bit control positions
   approximate the blueprint's 12-bit ADC defaults. DS18B20 starts at 27.25 C
   (10-bit resolution). MODE cycles manual / gradual pH / turbidity spike / DO
   drop; profiles return to manual after 180 / 60 / 60 seconds respectively.
   DIP 1–4 inject pH/DO/turbidity/temp faults. DIP 5 disconnects Wi-Fi.

Software device (standard-library Python, local backend):

```powershell
python tools/sim_device.py --base-url http://localhost:8000 --key $env:HWW_DEVICE_KEY --scenario spike_turb
python tools/sim_device.py --scenario network-gap --out network-batches.jsonl
python tools/sim_device.py --fixtures shared/fixtures/replays
python tools/check_registry.py
```

The software device uses Python's verified TLS defaults for HTTPS. Local HTTP
is useful with the local development API. It handles individual acknowledgement,
bounded queues, newest-first recovery, auth/busy/schema/size/rate errors and
backoff. A bounded `--frames` run exits with any unsent backlog still in memory;
it does not provide persistent delivery after process exit.

## Verification performed on 18 November 2026

- Wrote native tests first; initial build failed because implementation was absent.
- Compiled with g++ C++17 and ran native assertions for transfer rounding,
  overflow eviction, newest+oldest selection, selective/out-of-order/missing
  acknowledgements, CRC32 boot hash, profile endpoint and jitter/cap/reset.
- Python unittest contract/profile/fault tests passed.
- Generated all six replay fixtures and Wokwi web bundle.
- Registry checker passed circuit part identity, mapped pins, sensor power,
  fault switch/network wiring and generated constants freshness.
- Python tooling and Blender preparation scripts passed syntax compilation.
- Installed PlatformIO 6.2 into the workspace and compiled the ESP32 target with
  Espressif32 6.9.0 / Arduino 2.0.17 and all pinned libraries. Build and link
  succeeded, producing `firmware.elf` and `firmware.bin`. Static RAM: 81,872 of
  327,680 bytes (25.0%). Flash: 1,027,753 of 1,310,720 bytes (78.4%).
- Fixed an SDK `config.h` name collision found by the real compile; optional
  local settings now have guarded defaults. Only upstream OneWire `#undef`
  warnings remained; there were no application compile errors in the final build.
- Validated every committed replay frame and CLI fault batches against the
  backend's Pydantic Frame and Batch models.
- Pin names checked against official Wokwi references:
  https://docs.wokwi.com/parts/wokwi-dip-switch-8,
  https://docs.wokwi.com/parts/wokwi-potentiometer,
  https://docs.wokwi.com/parts/wokwi-ds18b20,
  https://docs.wokwi.com/parts/board-ssd1306.

## Checks awaiting external prerequisites

Wokwi CLI and Blender are unavailable on this host. The ESP32 target compiled
successfully but has **not been run in Wokwi**. Confirm the circuit
in the editor, then perform the blueprint S2
TLS/keep-alive/NTP/randomness/sampling timing checks on the deployed endpoint.
No cloud endpoint, demo key, public Wokwi project URL or root certificate was
provided. No successful live HTTPS device transport is claimed.

The user will upload the station model. `blender/scripts/prepare_station.py`
and `tools/check_glb.py` prepare and validate that asset after upload. No model
is fabricated or supplied; full Blender execution, export orientation and
hotspot geometry checks remain pending.
