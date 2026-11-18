# 01: MVP specification and technology decisions

← [Blueprint index](README.md) · Next: [02 Architecture](02-architecture.md)

## 1.1 Goal

Show, live and end to end, how one Hanoi WaterWatch monitoring station would work:

> A presenter moves a simulated turbidity input in Wokwi. Within about 5 seconds the ESP32 has sent the reading to the backend, the backend has validated, stored and evaluated it, and the dashboard, the 3D station model and the device's own status LEDs all show the **same** value and status. If a configured rule fires, a **preliminary** alert appears for an authorised reviewer.

The demonstration is honest about its data. Every value is simulated, every screen says so, and no simulated value is ever presented as evidence about water quality in Hanoi.

## 1.2 MVP functions

| ID | Function | Phase | Proven by |
|----|----------|-------|-----------|
| F01 | Station registry: 3 stations on the map. `HWW-KNG-001` is driven live by Wokwi, `HWW-TLH-001` by a looping replay, and `HWW-NHU-001` is "planned", so it is always `unavailable`. Each has 4 sensors (pH, DO, turbidity, temperature). | 1, 4 | AC-09, T-C-01 |
| F02 | Wokwi ESP32 circuit: 3 slide potentiometers (pH, DO, turbidity), 1 DS18B20 (temperature), DIP switches for fault and network-drop injection, a MODE button for scripted scenarios, an OLED, 3 status LEDs, a beacon LED and a buzzer. | 3 | T-W-01..06 |
| F03 | HTTPS ingest of JSON frame batches with device key, schema validation, idempotency, and store-and-forward on the device. | 3, 4 | AC-05, AC-07, AC-12 |
| F04 | PostgreSQL storage with provenance on every measurement (`simulated_wokwi`, `simulated_replay`, `simulated_script`). | 4 | T-B-03 |
| F05 | Rule engine with 6 rules: validity → `sensor_fault`; pH and temperature reference bands; turbidity-spike and DO-drop change heuristics; station offline. | 4 | T-B-06..11 |
| F06 | Alerts with lifecycle (open → acknowledged → under review → closed), "preliminary" labelling, in-app notification (toast and bell) for signed-in staff. | 4, 5 | AC-03, T-E-05 |
| F07 | One versioned station-state snapshot (`GET /stations/{code}/state`) that every view renders. | 4 | AC-06 |
| F08 | Page 1, Monitoring Overview: Leaflet map, station status, recent anomalies, simulated-data indicators. | 5 | T-E-01 |
| F09 | Page 2, Station Digital Model: R3F model from Tinkercad, click/hover/select sensors, live statuses, freshness, 2D fallback. | 2, 5 | AC-10, T-F-05, T-F-07, T-F-08 |
| F10 | Page 3, Monitoring Dashboard: 4 parameter cards, history charts, timestamps, normal/abnormal event timeline, availability. | 5 | T-E-02 |
| F11 | Page 4, Alerts and Incident Review: list, severity, timestamps, evidence class, acknowledge, review and classify, history. | 4, 5 | AC-13, T-E-05 |
| F12 | Page 5, Simulation Demonstration: circuit explanation, link to the Wokwi project, run instructions, live connection status, payload inspector, replay controls. | 5 | T-E-04 |
| F13 | Deterministic replay of recorded sessions through the same ingest pipeline, with "takeover" of a station. | 4 | AC-08 |
| F14 | Roles: anonymous viewer (public pages), operator, reviewer, admin. | 4 | T-S-03 |
| F15 | Simulated-data labelling on every data-bearing screen and in every API response (`is_simulated`). | 5 | AC-09 |
| F16 | Deployment: one container (API and SPA) plus managed PostgreSQL behind HTTPS; `docker compose` locally. | 1, 7 | T-D-01 |
| F17 | Device status LEDs mirror the *server-computed* station status from the ingest response. | 3, 6 | AC-03 |

**MVP+ (planned, first to be cut if late):** SSE live nudge (Phase 6), Vietnamese translation (strings are externalised from day 1).

**Stretch (only after M4):** exploded view and labels toggle (B-61); Wokwi custom chip "water probe" with labelled range sliders; Wokwi CI scenario tests (needs a Pro plan); stuck-sensor rule; web push notifications.

## 1.3 Minimum viable demonstration (MVD), milestone M3

The MVD is the smallest thing worth presenting. It must work before any MVP+ or stretch work starts.

1. Wokwi ESP32 → HTTPS → **deployed** FastAPI → PostgreSQL, with all 4 parameters every 2 s.
2. Dashboard cards and the 3D model page show the same snapshot (value, status, `version`).
3. Turbidity spike → `CHG_TURB_SPIKE` alert → turbidity sensor red in 3D, beacon on, device red LED on.
4. DIP fault switch → sensor shows `sensor_fault`, the value is shown as "—", and no pollution alert is raised.
5. Network-drop switch → station `offline` within 15 s; on recovery the buffered frames back-fill without duplicates.
6. Replay of `demo-golden.jsonl` reproduces steps 3 to 5 without Wokwi.
7. The simulated-data banner is visible on every route.

Pages needed for the MVD: Overview (map with 1 station is acceptable), Model, Dashboard, a read-only Alerts list, and the Simulation page's connection panel.

## 1.4 Excluded from the MVP (and why)

| Excluded | Reason |
|----------|--------|
| Real sensors, real Hanoi data, field devices | Out of scope; `field_observation` provenance is reserved in the schema but nothing can produce it. |
| SMS, Zalo, e-mail, push notifications | External accounts, cost and consent; in-app notifications prove the flow. |
| Public resident accounts, subscriptions | Residents use the public read-only views. |
| ML or AI anomaly detection | Unjustifiable without real data; transparent rules are explainable. |
| Embedding Wokwi in the app | No supported embed API (see [04 §4.1.3](04-wokwi-integration.md#413-can-wokwi-be-embedded-in-the-app)). |
| MQTT broker, Kafka, TimescaleDB, Redis, Kubernetes | Volumes are tiny (≈ 1 frame per 2 s); every extra service is a demo-day failure point. |
| Editing the 3D model in the browser | The model is a fixed asset; only its visual state changes. |
| Lab (LIMS) integration | "Verified incident" stores a lab reference typed by a reviewer. |
| Offline PWA, native mobile app | Responsive web is enough. |
| Multi-tenant, organisation management | Single demo tenant. |

## 1.5 Data honesty rules

| Term in the UI | Meaning | Who can create it |
|----------------|---------|-------------------|
| **Simulated anomaly** | An alert raised by a rule on simulated data (`source` starts with `simulated_`). Always shows a "SIMULATED" badge. | Rule engine |
| **Environmental observation** | An alert raised on `field_observation` data before review. **Reserved:** no field data exists in this project, so the UI shows this class in the legend only. | Rule engine (future) |
| **Verified incident** | An environmental observation confirmed by a reviewer with a lab reference. The DB forbids it for simulated data (see [07 §7.6](07-backend-database-api.md#76-tables)). | Reviewer, field data only |
| **Demo review outcome** | What a reviewer can record for a simulated anomaly: `confirmed_simulated_anomaly`, `sensor_or_equipment_fault`, `false_positive`, `test_or_calibration`. | Reviewer |

Fixed copy (shown in `SimulatedDataBanner` and the footer, en and vi):

> **Simulated data.** All readings on this site come from a Wokwi electronics simulation or a recorded replay. They are not measurements of water in Hanoi. Station locations are illustrative.

Thresholds are presented with their basis (see [07 §7.4](07-backend-database-api.md#74-rule-engine)). Turbidity and DO rules are labelled **"demo heuristic, no regulatory meaning"**. pH and temperature bands are labelled **"reference band, verification of official text pending"** until a team member checks the official QCVN text and sets `basis_status = verified`.

## 1.6 Technology decisions

| Layer | Decision | Rejected alternatives | Justification |
|-------|----------|----------------------|---------------|
| Frontend framework | **React 19 + TypeScript 5 (strict) + Vite**, React Router, Tailwind CSS 4 | Next.js; Vue | Pure SPA served by FastAPI: one deployable, no SSR server. The R3F and react-leaflet ecosystems are React-first. |
| Server state | **TanStack Query 5** (one query per station state, polling) | Redux, RTK Query, SWR | Built-in polling, deduping, `select`, background refetch; one cache key feeds every view (rule R3). |
| UI state | **Zustand** (selected sensor, toggles only) | React Context only | Tiny; lets R3F (outside React DOM tree semantics) and DOM panels share selection without prop drilling. Never stores measurements. |
| 3D | **three.js via @react-three/fiber 9 + @react-three/drei 10** | Babylon.js, imperative three.js, Unity WebGL, Sketchfab embed | Declarative scene bound to React state; `useGLTF` (meshopt support), `OrbitControls`, `Bounds`, `Html`. R3F 9 pairs with React 19. |
| Map | **Leaflet 1.9 + react-leaflet 5**, OpenStreetMap raster tiles with attribution | Google Maps, Mapbox, MapLibre GL | No API key or billing; a handful of markers needs no vector tiles. Respect the OSM tile usage policy (low traffic, attribution). |
| Charts | **Recharts 3** | ECharts, raw D3, Chart.js | Declarative React charts; `ReferenceArea` for bands, `ReferenceDot` for alerts. Enough for ≤ 2,000 points per chart (server downsamples). |
| Backend | **Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (async, asyncpg), Alembic, Uvicorn** | Django, Node/Express | Typed validation at the ingest boundary, auto-generated OpenAPI (→ TypeScript types), async background tasks for freshness and replay. |
| Database | **PostgreSQL 16** | TimescaleDB, InfluxDB, SQLite, MongoDB | ≈ 170k measurement rows per station per day at 2 s intervals is trivial for Postgres with a btree index; `date_bin()` handles chart buckets; transactions keep state consistent. |
| Browser updates | **REST polling every 2 s** (MVP) → **SSE "nudge"** (Phase 6) | WebSockets, GraphQL subscriptions | Only server→client signalling is needed. SSE is plain HTTP and needs no extra infrastructure. The nudge only triggers a refetch of the same REST snapshot, so there's still one data path. |
| Device transport | **HTTPS POST JSON batches** to the deployed API | MQTT broker; serial bridge | See [04 §4.7](04-wokwi-integration.md#47-transport-evaluation-and-decision). Works from the free Wokwi plan, no broker to host or secure, gives a synchronous ack used for retries and LED status. |
| Firmware | **Arduino C++ on the arduino-esp32 core**; same sources build in wokwi.com and in PlatformIO for VS Code | MicroPython | Mature libraries (OneWire, DallasTemperature, ArduinoJson, Adafruit SSD1306), HTTPS with `WiFiClientSecure`, host-side unit tests with PlatformIO `native`. MicroPython would work but adds a second toolchain for no gain. |
| 3D asset pipeline | **Tinkercad .OBJ (+.MTL) → Blender 4.x LTS (scripted with `bpy`) → .glb → gltf-transform (meshopt)** | STL; direct OBJ loading; Draco | OBJ keeps per-shape colours as materials, which enables "separate by material"; GLB is the web-native binary glTF; meshopt decoding is built into drei `useGLTF`. |
| Auth (users) | **JWT bearer (PyJWT), argon2 password hashes**, 4 roles | Auth0, Keycloak, sessions with CSRF | Demo-sized, no external dependency; public pages need no login. |
| Auth (devices) | **Per-device random key in `X-Device-Key`**, SHA-256 hash stored, scoped to one station and simulated provenance | mTLS, HMAC signing | The key is visible in a public Wokwi project anyway (see [04 §4.9](04-wokwi-integration.md#49-authentication-and-security-on-a-public-simulator)); scope and rate limits are what protect the system. |
| Testing | pytest + httpx + testcontainers (Postgres); Vitest + Testing Library; Playwright + axe-core; PlatformIO `native` (Unity) for firmware logic | Cypress | One E2E runner, real Postgres in tests, firmware logic testable without a simulator. |
| Quality tools | Ruff, mypy, ESLint, Prettier, `openapi-typescript`, GitHub Actions | — | Generated API types prevent drift between backend and frontend. |
| Deployment | **One Docker image** (multi-stage: Node build → Python runtime; FastAPI serves `/api` and the SPA) + **managed PostgreSQL**, on any container host with automatic HTTPS | Separate frontend host + API host; Kubernetes | One URL, no CORS, one thing to restart. Host chosen in issue B-08 against the criteria in [10 §10.6](10-testing-demo-deploy.md#106-deployment-plan). |
| i18n | **react-i18next**, `en` default, `vi` available | — | The design brief asks for Vietnamese-friendly UI; strings are externalised from the start. |

### Version policy

Pin exact versions in Phase 1 (lockfiles committed: `package-lock.json`, `uv.lock` or `requirements.lock`, `platformio.ini` `platform =` version). Upgrade only between milestones. Known compatibility constraint: **@react-three/fiber 9, @react-three/drei 10 and react-leaflet 5 all require React 19.** Spike S3 confirms the combination on a phone.

## 1.7 Complexity explicitly rejected

* **No message broker.** The ESP32 talks HTTPS to the API, and the API's in-process event bus feeds SSE. If the API is ever scaled to more than one instance, replace the bus with PostgreSQL `LISTEN/NOTIFY` (documented in ADR-0004). No new service is needed.
* **No separate time-series database.** Postgres and one index are enough.
* **No client-side threshold logic.** The frontend only maps a server status to colours and icons.
* **No per-component polling.** One query per station feeds the map marker, cards, charts' "latest" point and the 3D model.
* **No Wokwi iframe, no scraping, no browser automation of Wokwi.**
