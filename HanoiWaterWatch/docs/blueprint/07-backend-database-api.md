# 07: Backend services, database and API contracts

← [06 UI/UX](06-ui-ux.md) · Next: [08 Roadmap](08-roadmap.md)

This document covers deliverables 5 (backend services and API contracts) and 6 (database ERD). Stack: FastAPI, Pydantic v2, SQLAlchemy 2 (async, `asyncpg`), Alembic, PostgreSQL 16, `sse-starlette`, PyJWT, `argon2-cffi`. One uvicorn worker (ADR-0004).

## 7.1 Services

| Service (`backend/app/services/`) | Responsibility | Called by | Writes |
|-----------------------------------|----------------|-----------|--------|
| `device_auth.py` | Look up a device by key prefix, compare SHA-256 in constant time, check `enabled` | Ingest route | — |
| `ingest_service.py` | The 11-step pipeline in §7.2 | Ingest route, `ReplayService` | frames, measurements (through the others) |
| `session_service.py` | Find or open the simulation session for `(device, boot_id)`; takeover; end idle sessions | `IngestService`, `FreshnessMonitor`, `ReplayService` | simulation_sessions, stations.active_device_id |
| `rule_engine.py` + `rules/*.py` | Evaluate rules for one measurement; pure decisions plus a baseline query | `IngestService`, `FreshnessMonitor` | — (returns transitions) |
| `alert_service.py` | Open and clear alerts from rule transitions; lifecycle actions; reviews | `IngestService`, API routes | alerts, alert_events, incident_reviews |
| `state_service.py` | Update `sensor_state`, recompute station status, bump `station_state.version`, write `station_events` | `IngestService`, `FreshnessMonitor`, admin reset | sensor_state, station_state, station_events |
| `freshness_monitor.py` | Background task, every 1 s: offline detection (`STN_OFFLINE`), session end after 60 s idle | Startup | via `StateService`, `AlertService`, `SessionService` |
| `replay_service.py` | Load `.jsonl` recordings; run them through `IngestService` in real time with a replay device; TLH loop | Startup, replay routes | via `IngestService` |
| `registry_loader.py` | Load and validate `shared/registry/*.json`; upsert stations, sensor types, sensors and devices; keep an in-memory copy for validation | Startup, `cli.py seed` | stations, sensor_types, sensors, devices |
| `event_bus.py` | In-process async pub/sub; events are published **after commit** | Services, SSE route | — |
| `auth_service.py` | Password check (argon2id), JWT issue/verify, role checks | Auth routes, `deps.py` | users.last_login_at |
| `maintenance.py` | Daily retention purge; demo reset (only when `DEMO_MODE`) | Startup, admin route | all data tables |

Routes (`api/v1/*.py`) only parse, authorise, call a service and serialise. All SQL lives in services.

## 7.2 Ingest pipeline

`POST /api/v1/ingest/frames` runs these steps. Steps 5 to 10 are **one database transaction**.

| # | Step | Failure → response |
|---|------|--------------------|
| 1 | **Limits:** body ≤ 64 KB (checked on `Content-Length` and while reading); token bucket per key prefix and per IP (`INGEST_RATE_PER_S` 2, `INGEST_BURST` 10) | 413 `payload_too_large`; 429 `rate_limited` + `Retry-After` |
| 2 | **Kill switch:** `INGEST_ENABLED` | 503 `ingest_disabled` |
| 3 | **Authenticate:** `X-Device-Key` → `key_prefix` (first 8 chars) → device row → `hmac.compare_digest(sha256(key), key_hash)`; device `enabled` | 401 `invalid_device_key`; 403 `device_disabled` |
| 4 | **Validate:** Pydantic model generated to match `frame-batch.v1.schema.json` (`extra="forbid"`); `station_code` and `device_code` equal the key's binding; channels exist for the station; units equal the registry unit | 422 `schema_invalid` / `unknown_channel` / `unit_mismatch`; 403 `station_mismatch` |
| 5 | **Begin** transaction; `SELECT … FROM station_state WHERE station_id = $1 FOR UPDATE` (serialises all writers of this station, including the freshness monitor and replays) | 503 `db_unavailable` |
| 6 | **Takeover check:** if `stations.active_device_id` is another device whose session is still open → reject; if it is empty or that session has ended → claim the station for this device | 409 `station_busy` |
| 7 | **Session:** find the open session for `(device_id, boot_id)`; if none, end the station's other open session (`end_reason = superseded`) and open a new one with `source` derived from `devices.kind` (rule R4); write `session_started` event | — |
| 8 | **Frames:** sort by `seq`; derive `measured_at` for `time_source = uptime`; mark frames older than 24 h `rejected: too_old` and frames more than 5 min in the future `rejected: future_timestamp`; `INSERT … ON CONFLICT (device_id, boot_id, seq) DO NOTHING RETURNING id` → new vs `duplicate`; seq gap within a boot → `frames_missing` event | per-frame result |
| 9 | **Measurements** for new frames: one row per reading with `source`, `quality` (`ok`; `fault` from the device; `invalid` when outside the type's valid range), `fault_reason`, `raw`, `gen` | — |
| 10 | **Rules and state**, for each new frame in `measured_at` order: `RuleEngine` (§7.4) → transitions → `AlertService` opens or clears alerts (`detected_late = true` if the frame is older than the sensor's current state); `StateService` advances `sensor_state` **only if `measured_at` is newer**, recomputes the station status, writes `status_changed` events; then `station_state.version += 1` once if at least one frame was accepted; **commit** | 503 `db_unavailable` (whole batch rolled back; the device keeps the frames) |
| 11 | **After commit:** publish `state_changed {station_code, version}` and `alert_opened` / `alert_updated`; record `last_batch` and counters in the session; return the ack | — |

**Ack** (200) as in [04 §4.8](04-wokwi-integration.md#48-payload-contract-hwwframesv1): per-seq `results`, totals, `station_status`, `state_version`, `server_time`, `next_min_interval_ms`.

**Rejected unauthenticated requests are not written to the database.** The service keeps an in-memory count of recent 401s per claimed `station_code` (single worker), which the Simulation page shows as "Rejected: invalid_device_key (3 in the last minute)" (scenario SC7).

**Performance:** a 20-frame backlog batch is about 20 inserts into `frames`, 80 into `measurements` and 40 baseline queries; this takes well under 200 ms on a small managed Postgres. The live case (1 frame) takes about 10 ms.

## 7.3 Time

| Topic | Rule |
|-------|------|
| Storage | Every timestamp is `timestamptz`; the server session time zone is UTC |
| API | ISO 8601 with milliseconds and `Z` (`2026-11-17T08:30:20.000Z`) |
| Display | The client converts to ICT (`Asia/Ho_Chi_Minh`, UTC+7, no daylight saving) |
| `measured_at` | From the device (`ntp` or `server` offset); derived for `uptime` frames as `received_at − (sent_uptime_ms − uptime_ms)` |
| `received_at` | Server clock when the batch was read; used for freshness, offline detection and session timeouts (never device time) |
| Ordering | History and rules use `measured_at`; the live state advances only on newer `measured_at` |
| Bounds | Frames > 24 h old or > 5 min in the future are rejected per frame |
| Buckets | `date_bin(interval, measured_at, '2000-01-01 00:00:00+00')`; because ICT is a whole-hour offset, buckets up to 1 h line up with ICT clock times |
| Client clock | The UI estimates its offset from the HTTP `Date` header, so "1 s ago" is correct even if the viewer's clock is wrong |

## 7.4 Rule engine

### 7.4.1 Rules (seeded by `alembic/versions/0002_seed_rules.py`, editable by admins through E28)

| Code | Applies to | Category | Severity | Trigger (per evaluated reading) | Persistence | Clear | Basis (`basis_text`, `is_regulatory`, `basis_status`) |
|------|-----------|----------|----------|---------------------------------|-------------|-------|------------------------------------------------------|
| `VALID_RANGE` | every sensor | equipment | warning | `quality ∈ {fault, invalid}` (device fault flag, or outside the type's physical range: pH 0–14, DO 0–20 mg/L, turbidity 0–1000 NTU, temperature −5–60 °C) | 1 | 2 consecutive `ok` readings | "Instrument plausibility check", no, `not_applicable` |
| `REF_PH_BAND` | `ph` | water_quality | critical | value < 6.0 or > 9.0 | 3 | 3 readings within 6.0–9.0 | "Reference band from QCVN 40:2025/BTNMT (industrial wastewater), pH 6–9. Verification of the official text pending.", yes, `unverified` |
| `REF_TEMP_MAX` | `temp` | water_quality | warning | value > 40 °C | 3 | 3 readings ≤ 40 °C | "Reference maximum from QCVN 40:2025/BTNMT, 40 °C. Verification of the official text pending.", yes, `unverified` |
| `CHG_TURB_SPIKE` | `turbidity` | water_quality | warning | value ≥ max(3 × baseline, baseline + 50) | 2 | 5 readings below the threshold | "Demo heuristic: ≥ 3× the 5-minute median and ≥ +50 NTU. No regulatory meaning.", no, `not_applicable` |
| `CHG_DO_DROP` | `do` | water_quality | warning | value ≤ 0.5 × baseline **and** baseline − value ≥ 2.0 mg/L | 3 | 5 readings ≥ 0.8 × baseline | "Demo heuristic: DO at or below half its 5-minute median and down ≥ 2 mg/L. No regulatory meaning.", no, `not_applicable` |
| `STN_OFFLINE` | station | equipment | info | no accepted frame for `OFFLINE_AFTER_S` (15 s) by `received_at`, while the station has a device | — (freshness monitor) | next accepted frame | "Connectivity check", no, `not_applicable` |

QCVN 40 is an effluent standard, not a river-water standard. The basis text says so, and the UI shows "reference band, verification of official text pending" until an admin sets `basis_status = verified` with a `basis_reference` (E28). Until then the bands are not called legal limits anywhere.

### 7.4.2 Baseline (change rules)

* `baseline(t) = median(value)` of the same sensor's `ok` readings with `measured_at ∈ [t − 300 s, t − 10 s]` (`percentile_cont(0.5) WITHIN GROUP (ORDER BY value)`).
* Valid only with **≥ 30 samples** and **≥ 60 s since the session started**; otherwise the rule state is `warming_up` and the rule does not fire.
* **Frozen while the rule is active:** the baseline at the moment of opening is stored in the rule state and in the alert (`baseline_value`), so a long spike can't raise its own baseline and clear itself.
* The 10 s gap stops the first rising frames of an event from pulling the baseline up.

### 7.4.3 Evaluation

```text
for each new measurement m (in measured_at order):
    rs = sensor_state.rule_state[rule]                     # persisted JSONB, same transaction
    if rule is a water-quality rule and m.quality != ok:
        rs.pending = 0                                     # faults never count towards a trigger
        continue                                           # and never count towards clearing
    hit = rule.condition(m.value, baseline, params)
    if not rs.active:
        rs.pending = rs.pending + 1 if hit else 0
        if rs.pending >= rule.persistence:  → OPEN  (alert with observed, baseline, threshold, params snapshot)
    else:
        rs.clear_count = rs.clear_count + 1 if rule.clear(m.value, rs.frozen_baseline, params) else 0
        if rs.clear_count >= rule.clear_persistence:  → CLEAR (alert.cleared_at = m.measured_at)
```

* Rule state (`pending`, `active`, `clear_count`, `frozen_baseline`, `alert_id`) is stored in `sensor_state.rule_state`, so a restart or a back-filled batch continues where it stopped.
* Sensor status precedence is in [05 §5.5](05-synchronisation.md#55-status-model).
* Each rule is a small class in `rules/` with `condition`, `clear` and a JSON Schema for its `params`, and has its own unit tests with the scenario numbers (T-B-06..11).
* One alert per episode: a partial unique index allows only one *uncleared* alert per rule and sensor (or station). If the condition clears and later returns, a new alert opens.

### 7.4.4 Worked numbers

| Scenario | Inputs | Result |
|----------|--------|--------|
| SC3a turbidity slide | baseline 18.4; readings 65.8, 142.5, 142.5 | threshold max(55.2, 68.4) = 68.4; 65.8 below; 2 hits (seq 419, 420) → opens at seq 420, ≈ 4 s after the first changed frame |
| SC2 gradual pH | 7.2 → 5.4 over 120 s (−0.015/s) | below 6.0 at 80 s; 3 hits → open at ≈ 86 s |
| SC3c DO drop | baseline 6.4; reading 1.8 | 1.8 ≤ 3.2 and 4.6 ≥ 2.0; 3 hits → open at ≈ 6 s |
| SC4 fault | turbidity `q = fault` | `VALID_RANGE` opens at once; sensor `sensor_fault`; `CHG_TURB_SPIKE` ignores the reading |
| DS18B20 set to 100 °C | outside −5–60 | `VALID_RANGE` (equipment), not `REF_TEMP_MAX`: implausible water temperature is a sensor problem |

## 7.5 ERD (deliverable 6)

```mermaid
erDiagram
  STATIONS ||--o{ SENSORS : has
  SENSOR_TYPES ||--o{ SENSORS : "typed by"
  STATIONS ||--o{ DEVICES : "bound to"
  STATIONS ||--|| STATION_STATE : "current state"
  SENSORS ||--|| SENSOR_STATE : "current state"
  STATIONS ||--o{ SIMULATION_SESSIONS : runs
  DEVICES ||--o{ SIMULATION_SESSIONS : produces
  REPLAYS ||--o{ SIMULATION_SESSIONS : "replayed as"
  SIMULATION_SESSIONS ||--o{ FRAMES : contains
  FRAMES ||--o{ MEASUREMENTS : contains
  SENSORS ||--o{ MEASUREMENTS : measures
  ALERT_RULES ||--o{ ALERTS : raises
  STATIONS ||--o{ ALERTS : "raised for"
  SENSORS |o--o{ ALERTS : "raised for"
  SIMULATION_SESSIONS ||--o{ ALERTS : "during"
  ALERTS ||--o{ ALERT_EVENTS : "audit trail"
  USERS |o--o{ ALERT_EVENTS : "acted"
  INCIDENT_REVIEWS ||--|{ INCIDENT_REVIEW_ALERTS : groups
  ALERTS ||--o| INCIDENT_REVIEW_ALERTS : "reviewed in"
  USERS ||--o{ INCIDENT_REVIEWS : "reviewed by"
  STATIONS ||--o{ STATION_EVENTS : timeline

  STATIONS { bigint id PK
    text code UK
    jsonb name
    text data_mode
    bigint active_device_id FK }
  SENSORS { bigint id PK
    text uid UK
    bigint station_id FK
    text channel FK
    text model_node }
  DEVICES { bigint id PK
    text code UK
    text kind
    text key_prefix UK
    bytea key_hash
    bool enabled }
  SIMULATION_SESSIONS { uuid id PK
    text source
    text boot_id
    timestamptz started_at
    timestamptz ended_at }
  FRAMES { bigint id PK
    bigint device_id FK
    text boot_id
    int seq
    timestamptz measured_at
    timestamptz received_at }
  MEASUREMENTS { bigint id PK
    bigint sensor_id FK
    timestamptz measured_at
    float8 value
    text quality
    text source }
  ALERTS { bigint id PK
    text rule_code FK
    text evidence_class
    text review_status
    timestamptz opened_at
    timestamptz cleared_at }
  INCIDENT_REVIEWS { bigint id PK
    text status
    text outcome
    text lab_reference }
```

## 7.6 Tables

All primary keys are `bigint GENERATED ALWAYS AS IDENTITY` unless stated. Enumerations are `text` with `CHECK` constraints (easier to migrate than PostgreSQL enums). Migration: `alembic/versions/0001_initial.py`.

| Table | Columns (type, constraint) | Indexes and checks |
|-------|---------------------------|--------------------|
| `users` | `username text UNIQUE`, `display_name text`, `role text CHECK IN (operator, reviewer, admin)`, `password_hash text` (argon2id), `is_active bool DEFAULT true`, `created_at`, `last_login_at` | — |
| `sensor_types` | `code text PK` (`ph`…), `unit text`, `unit_display text`, `decimals smallint`, `valid_min float8`, `valid_max float8`, `label jsonb` | — |
| `stations` | `code text UNIQUE`, `name jsonb`, `river text`, `lat`, `lng numeric(8,5)`, `location_precision text`, `data_mode text CHECK IN (live_wokwi, replay_loop, planned)`, `timezone text`, `active_device_id bigint NULL FK devices`, `registry_version int` | — |
| `sensors` | `uid text UNIQUE`, `station_id FK`, `channel text FK sensor_types`, `model_node text`, `hotspot jsonb`, `wokwi jsonb`, `transfer jsonb` | `UNIQUE (station_id, channel)` |
| `devices` | `code text UNIQUE`, `kind text CHECK IN (wokwi_esp32, sim_script, replay)`, `station_id FK`, `key_prefix text UNIQUE NULL`, `key_hash bytea NULL`, `enabled bool`, `fw_version text`, `last_boot_id text`, `last_seen_at`, `rotated_at` | replay devices have no key |
| `replays` | `name text UNIQUE` (`demo-golden`…), `file_path text`, `description jsonb`, `frame_count int`, `duration_s int`, `sha256 text`, `created_at` | loaded from `shared/fixtures/replays/` at startup |
| `simulation_sessions` | `id uuid PK`, `station_id FK`, `device_id FK`, `replay_id FK NULL`, `source text CHECK IN (simulated_wokwi, simulated_script, simulated_replay, field_observation)`, `boot_id text NULL`, `fw_version text`, `started_at`, `last_frame_at`, `ended_at NULL`, `end_reason text NULL CHECK IN (idle_timeout, superseded, takeover, replay_finished, replay_stopped, demo_reset)`, `frames_accepted`, `frames_duplicate`, `frames_rejected int`, `last_seq int`, `last_diag jsonb`, `last_batch jsonb`, `last_error_code text`, `last_error_at` | partial `UNIQUE (station_id) WHERE ended_at IS NULL` (one open session per station) |
| `frames` | `session_id uuid FK`, `device_id FK`, `boot_id text`, `seq int`, `measured_at`, `time_source text`, `uptime_ms bigint`, `buffered bool`, `mode text`, `received_at` | `UNIQUE (device_id, boot_id, seq)` (idempotency); `(session_id, seq)` |
| `measurements` | `frame_id FK`, `sensor_id FK`, `measured_at`, `received_at`, `value float8 NULL`, `raw int NULL`, `quality text CHECK IN (ok, fault, invalid)`, `fault_reason text NULL`, `gen text`, `source text`, `is_simulated bool GENERATED ALWAYS AS (source <> 'field_observation') STORED` | `(sensor_id, measured_at DESC) INCLUDE (value, quality)`; `UNIQUE (frame_id, sensor_id)`; `CHECK ((quality = 'fault') = (value IS NULL))` |
| `sensor_state` | `sensor_id PK FK`, `value float8 NULL`, `measured_at`, `received_at`, `quality`, `gen`, `status text CHECK IN (normal, abnormal, sensor_fault, offline, unavailable)`, `status_since`, `last_valid_value`, `last_valid_at`, `valid_streak int`, `rule_state jsonb DEFAULT '{}'` | one row per sensor, created at seed |
| `station_state` | `station_id PK FK`, `version bigint DEFAULT 0`, `station_status text CHECK IN (normal, abnormal, degraded, offline, unavailable)`, `status_since`, `last_frame_at` (received), `last_measured_at`, `current_session_id uuid NULL` | the row lock in §7.2 step 5 |
| `station_events` | `station_id FK`, `sensor_id NULL FK`, `at timestamptz`, `type text CHECK IN (status_changed, station_offline, station_online, session_started, session_ended, frames_missing, takeover_started, takeover_ended, alert_opened, alert_cleared, alert_closed)`, `data jsonb` | `(station_id, at DESC)`; feeds the timeline (E07) |
| `alert_rules` | `code text PK`, `name jsonb`, `applies_to text` (channel or `station`), `category text CHECK IN (water_quality, equipment)`, `severity text CHECK IN (info, warning, critical)`, `params jsonb`, `persistence int`, `clear_persistence int`, `basis_text jsonb`, `is_regulatory bool`, `basis_status text CHECK IN (not_applicable, unverified, verified)`, `basis_reference text NULL`, `enabled bool`, `updated_at`, `updated_by FK users NULL` | `CHECK (basis_status <> 'verified' OR basis_reference IS NOT NULL)` |
| `alerts` | `rule_code FK`, `station_id FK`, `sensor_id FK NULL`, `session_id uuid FK NULL`, `category`, `severity`, `source text`, `evidence_class text CHECK IN (simulated_anomaly, environmental_observation, verified_incident)`, `is_preliminary bool DEFAULT true`, `review_status text CHECK IN (open, acknowledged, under_review, closed)`, `opened_at` (measured time), `detected_at` (server time), `detected_late bool`, `cleared_at NULL`, `closed_at NULL`, `observed_value`, `baseline_value NULL`, `threshold_value NULL`, `params_snapshot jsonb`, `basis_snapshot jsonb`, `outcome text NULL` | see checks below; `(review_status, opened_at DESC)`; `(station_id, opened_at DESC)`; partial `UNIQUE (rule_code, station_id, coalesce(sensor_id, 0)) WHERE cleared_at IS NULL` |
| `alert_events` | `alert_id FK`, `type text CHECK IN (opened, cleared, acknowledged, note, review_started, review_submitted, closed)`, `actor_user_id FK NULL` (NULL = system), `at`, `data jsonb` (note text, outcome) | `(alert_id, at)`; append-only (no UPDATE/DELETE grants for the app role except demo reset) |
| `incident_reviews` | `created_by FK users`, `status text CHECK IN (in_progress, submitted)`, `outcome text NULL CHECK IN (confirmed_simulated_anomaly, sensor_or_equipment_fault, false_positive, test_or_calibration, verified_incident, not_confirmed)`, `note text`, `lab_reference text NULL`, `started_at`, `submitted_at NULL` | `CHECK (outcome <> 'verified_incident' OR lab_reference IS NOT NULL)` |
| `incident_review_alerts` | `review_id FK`, `alert_id FK` | `PRIMARY KEY (review_id, alert_id)`; `UNIQUE (alert_id)` (an alert is reviewed once) |

**Data-honesty checks on `alerts`** (enforced by the database, tested in T-B-15):

```sql
CHECK (
  (source LIKE 'simulated\_%' AND evidence_class = 'simulated_anomaly')
  OR (source = 'field_observation' AND evidence_class IN ('environmental_observation', 'verified_incident'))
),
CHECK (evidence_class <> 'verified_incident' OR (review_status = 'closed' AND outcome = 'verified_incident'))
```

`AlertService` also refuses outcomes that cannot apply (`verified_incident`, `not_confirmed` on simulated alerts) with 422 `outcome_not_allowed`, so users get a clear error before the database would.

**Volume and retention:** one live station at 0.5 frames/s gives 4 measurement rows per 2 s (≈ 173 k/day). With the TLH replay loop running continuously, about 350 k rows/day. `maintenance.py` deletes frames, measurements and station events older than `RETENTION_DAYS` (default 7) once a day; alerts, reviews and sessions are kept. Expected database size stays under 500 MB.

## 7.7 Alert lifecycle

```mermaid
stateDiagram-v2
  [*] --> open: rule opens (system)
  open --> acknowledged: acknowledge (operator+)
  open --> under_review: included in a review (reviewer+)
  acknowledged --> under_review: included in a review (reviewer+)
  under_review --> closed: review submitted with outcome (reviewer+)
  closed --> [*]
  note right of open
    cleared_at is set independently when the
    rule's clear condition holds; it does not
    change review_status
  end note
```

| Action | Endpoint | Role | Allowed from | Writes |
|--------|----------|------|-------------|--------|
| Open | (rule engine) | system | — | alert, `opened` event, `alert_opened` station event |
| Clear | (rule engine) | system | any state | `cleared_at`, `cleared` event |
| Acknowledge | E17 | operator, reviewer, admin | `open` | `acknowledged` event |
| Add note | E18 | operator, reviewer, admin | any | `note` event |
| Start review | E23 | reviewer, admin | `open`, `acknowledged` | review row, `review_started` events, status `under_review` |
| Submit review | E26 | reviewer, admin (the review's creator or an admin) | review `in_progress` | outcome on review and alerts, `is_preliminary = false`, `closed_at`, `review_submitted` + `closed` events |

Invalid transitions return 409 `invalid_transition`. An alert that is closed while its condition is still active keeps blocking a duplicate alert (partial unique index) until the condition clears.

## 7.8 Conventions: auth, errors, pagination

**Roles** (each includes the ones before it): anonymous → operator → reviewer → admin.

| Capability | Anonymous | Operator | Reviewer | Admin |
|-----------|-----------|----------|----------|-------|
| Read stations, state, history, timeline, alerts, rules, sessions, link | ✓ | ✓ | ✓ | ✓ |
| See notes and user names on alerts | | ✓ | ✓ | ✓ |
| Acknowledge, add notes, export session frames, run replays | | ✓ | ✓ | ✓ |
| Create and submit incident reviews | | | ✓ | ✓ |
| Edit rules, rotate device keys, demo reset | | | | ✓ |

**User sessions:**
* `POST /auth/login` checks the argon2id hash (argon2-cffi defaults) and sets cookie `hww_session` = JWT (HS256, claims `sub`, `role`, `exp`, `jti`), `HttpOnly; Secure; SameSite=Strict; Path=/api`, 8 h lifetime. No token is stored in `localStorage`.
* CSRF defence: `SameSite=Strict`, plus every state-changing request must carry `Content-Type: application/json` and `X-Requested-With: hww` (a cross-site form can't set these without a CORS preflight, which the API never approves).
* Login is rate-limited to 5 attempts per minute per IP and username; the error never says which part was wrong.
* Demo users are created by `python -m app.cli seed` from `DEMO_*_USERNAME` / `DEMO_*_PASSWORD` environment variables. Passwords are never in the repo or docs.

**Device auth:** `X-Device-Key` on E14 only ([04 §4.9](04-wokwi-integration.md#49-authentication-and-security-on-a-public-simulator)). Keys are created and rotated with `python -m app.cli devices rotate-key wokwi-esp32-01` or E29; the key is printed once.

**Errors:** RFC 9457 `application/problem+json`:

```json
{ "type": "https://hww.example/problems/invalid_transition", "title": "Invalid alert transition",
  "status": 409, "code": "invalid_transition", "detail": "Alert 731 is closed.", "instance": "/api/v1/alerts/731/acknowledge" }
```

Common codes: `not_found` 404, `unauthenticated` 401, `forbidden` 403, `validation_error` 422, `invalid_transition` 409, `rate_limited` 429, `db_unavailable` 503, plus the ingest codes in [04 §4.8](04-wokwi-integration.md#48-payload-contract-hwwframesv1).

**Pagination:** list endpoints take `limit` (default 50, max 100) and an opaque `cursor`; responses return `items`, `next_cursor` (null at the end) and `total`.

**Other conventions:**
* Base path `/api/v1`; JSON `snake_case`; IDs exposed are codes, UIDs, alert and review numbers and session UUIDs.
* Every data response includes `"is_simulated": true` at the top level (F15).
* Server-provided text is `{ "en": "…", "vi": "…" }`.
* OpenAPI is generated by FastAPI at `/api/v1/openapi.json`; `frontend/src/api/schema.d.ts` is generated from it with `openapi-typescript` (`make gen`), and CI fails if it is stale.
* Security headers on all responses: `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, and on HTML: `Content-Security-Policy: default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://tile.openstreetmap.org; connect-src 'self'; frame-ancestors 'none'` (`wasm-unsafe-eval` is needed by the meshopt decoder; inline styles by Leaflet and drei `Html`).
* No CORS in normal use: the SPA and API share an origin, and in development Vite proxies `/api` to `:8000`. `CORS_ORIGINS` stays empty.

## 7.9 Endpoint catalogue

| ID | Method and path | Auth | Purpose |
|----|-----------------|------|---------|
| E01 | `GET /health` | none | Liveness and DB check for the host |
| E02 | `GET /meta` | none | Versions, server time, timings, Wokwi link |
| E03 | `GET /stations` | none | Station list with metadata |
| E04 | `GET /stations/{code}` | none | One station with sensors and model components |
| E05 | `GET /stations/{code}/state` | none | **The snapshot every view renders** |
| E06 | `GET /stations/{code}/measurements` | none | History for one channel, bucketed |
| E07 | `GET /stations/{code}/timeline` | none | Events and availability |
| E31 | `GET /stations/{code}/link` | none | Device link status for the Simulation page |
| E08 | `GET /alerts` | none (notes hidden) | Filtered alert list |
| E09 | `GET /alerts/{id}` | none (notes hidden) | Alert with evidence, history, review |
| E10 | `GET /rules` | none | Rules with their basis, for display |
| E11 | `GET /sessions` | none | Simulation sessions |
| E12 | `GET /sessions/{id}` | none | One session with counters |
| E13 | `GET /stream` | none | SSE nudges (Phase 6) |
| E14 | `POST /ingest/frames` | device key | Frame ingest ([04 §4.8](04-wokwi-integration.md#48-payload-contract-hwwframesv1)) |
| E15 | `POST /auth/login` | none | Sign in |
| E16 | `GET /auth/me` | user | Current user |
| E32 | `POST /auth/logout` | user | Sign out |
| E17 | `POST /alerts/{id}/acknowledge` | operator | Acknowledge |
| E18 | `POST /alerts/{id}/notes` | operator | Add a note |
| E19 | `GET /sessions/{id}/frames.jsonl` | operator | Export a session as a replay file |
| E20 | `GET /replays` | operator | List recordings |
| E21 | `POST /replays/{name}/runs` | operator | Start a replay run |
| E22 | `POST /replay-runs/{session_id}/stop` | operator | Stop a replay run |
| E23 | `POST /incident-reviews` | reviewer | Start a review of one or more alerts |
| E24 | `GET /incident-reviews/{id}` | operator | Read a review |
| E25 | `PATCH /incident-reviews/{id}` | reviewer | Change alerts or draft note |
| E26 | `POST /incident-reviews/{id}/submit` | reviewer | Submit outcome and close the alerts |
| E27 | `GET /incident-reviews` | operator | List reviews |
| E28 | `PUT /admin/rules/{code}` | admin | Edit a rule |
| E29 | `POST /admin/devices/{code}/rotate-key` | admin | New device key (shown once) |
| E30 | `POST /admin/demo-reset` | admin | Remove demo data |

E31 and E32 were added after the original numbering; IDs are kept stable because tests and issues refer to them.

### E01 `GET /health`

`200 {"status": "ok", "db": "ok", "app_version": "1.0.0", "uptime_s": 5231, "ingest_enabled": true}` · `503` with `"db": "unavailable"` when the database check fails. Used by the host's health check and T-D-01.

### E02 `GET /meta`

```json
{ "api_version": "v1", "app_version": "1.0.0", "server_time": "2026-11-17T08:28:01.902Z",
  "registry_version": 1, "frame_interval_ms": 2000, "offline_after_s": 15,
  "model": { "glb_path": "/models/station-v1.glb", "version": 1 },
  "wokwi_project_url": "https://wokwi.com/projects/<project-id>",
  "features": { "sse": true }, "languages": ["en", "vi"], "is_simulated": true }
```

The firmware reads `server_time` at boot ([04 §4.5.3](04-wokwi-integration.md#453-start-up-identity-and-clock)). The frontend compares `registry_version` with its bundled registry and shows "A new version is available. Reload." if they differ.

### E03 `GET /stations` and E04 `GET /stations/{code}`

E03 returns `items` of the E04 shape without `sensors` and `model`. E04:

```json
{ "code": "HWW-KNG-001", "name": { "en": "Kim Ngưu River, demo station 1", "vi": "Sông Kim Ngưu, trạm mô phỏng 1" },
  "river": "Kim Ngưu", "location": { "lat": 20.995, "lng": 105.861, "precision": "illustrative" },
  "data_mode": "live_wokwi", "registry_version": 1,
  "sensors": [ { "uid": "HWW-KNG-001:turbidity", "channel": "turbidity", "unit": "NTU", "unit_display": "NTU", "decimals": 1,
                 "label": { "en": "Turbidity", "vi": "Độ đục" }, "model_node": "sensor_turbidity",
                 "wokwi": { "part_id": "pot_turb", "pin": "32", "substitute": true } } ],
  "model": { "glb_path": "/models/station-v1.glb", "components": [ { "node": "beacon", "kind": "indicator", "label": { "en": "Alert beacon", "vi": "Đèn cảnh báo" } } ] },
  "is_simulated": true }
```

Errors: 404 `not_found`.

### E05 `GET /stations/{code}/state`

* **Purpose:** the single snapshot behind cards, 3D model, map, 2D schematic and detail panels.
* **Headers:** `ETag: W/"HWW-KNG-001:18345"`, `Cache-Control: no-cache`; `If-None-Match` → `304`.
* **Consistency:** read in one `REPEATABLE READ` transaction (G2).

```json
{
  "station_code": "HWW-KNG-001", "version": 18345, "generated_at": "2026-11-17T08:30:21.302Z",
  "data_source": "simulated_wokwi", "is_simulated": true,
  "station_status": "abnormal", "station_status_since": "2026-11-17T08:30:20.000Z",
  "last_frame_at": "2026-11-17T08:30:20.452Z", "freshness_s": 0.85, "offline_after_s": 15,
  "session": { "id": "0b6d5c2e-8f3a-4c1d-9a77-2f4e6b1c9d10", "source": "simulated_wokwi", "device_code": "wokwi-esp32-01", "started_at": "2026-11-17T08:28:02.871Z" },
  "sensors": [
    { "channel": "turbidity", "uid": "HWW-KNG-001:turbidity", "unit": "NTU", "decimals": 1, "model_node": "sensor_turbidity",
      "value": 142.5, "measured_at": "2026-11-17T08:30:20.000Z", "quality": "ok", "gen": "input",
      "status": "abnormal", "status_since": "2026-11-17T08:30:20.000Z", "last_valid": null, "fault_reason": null,
      "active_alert_id": 731 },
    { "channel": "do", "uid": "HWW-KNG-001:do", "unit": "mg/L", "decimals": 2, "model_node": "sensor_do",
      "value": null, "measured_at": "2026-11-17T08:30:20.000Z", "quality": "fault", "gen": "input",
      "status": "sensor_fault", "status_since": "2026-11-17T08:29:50.000Z",
      "last_valid": { "value": 6.40, "measured_at": "2026-11-17T08:29:48.000Z" }, "fault_reason": "injected",
      "active_alert_id": 729 }
  ],
  "open_alerts": [
    { "id": 731, "rule_code": "CHG_TURB_SPIKE", "sensor_uid": "HWW-KNG-001:turbidity", "category": "water_quality", "severity": "warning",
      "review_status": "open", "opened_at": "2026-11-17T08:30:20.000Z", "cleared_at": null },
    { "id": 729, "rule_code": "VALID_RANGE", "sensor_uid": "HWW-KNG-001:do", "category": "equipment", "severity": "warning",
      "review_status": "acknowledged", "opened_at": "2026-11-17T08:29:50.000Z", "cleared_at": null }
  ],
  "open_alert_count": 2
}
```

(The DO fault is added here only to show the fault shape; the 05 walkthrough has DO normal.)

Rules: `value` is null whenever `status ∈ {sensor_fault, offline, unavailable}`; `last_valid` is filled only then. `freshness_s` is computed at `generated_at`; the UI recomputes age from `last_frame_at` because a `304` reuses the old body. `open_alerts` lists alerts with `review_status ≠ closed`, so "active" (`cleared_at` null) and "cleared, awaiting review" can both be shown. Errors: 404.

### E06 `GET /stations/{code}/measurements`

Query: `channel` (required), `from`, `to` (ISO, max range 7 days), `bucket` = `auto` (default) | `raw` | `10s` | `1m` | `5m` | `1h`. `auto` picks raw ≤ 15 min, 10 s ≤ 1 h, 1 min ≤ 6 h, 5 min ≤ 24 h, 1 h above. Max 5,000 points (422 `range_too_large`).

```json
{ "station_code": "HWW-KNG-001", "channel": "turbidity", "unit": "NTU", "decimals": 1, "bucket": "raw",
  "from": "2026-11-17T08:15:00.000Z", "to": "2026-11-17T08:30:21.000Z",
  "points": [
    { "t": "2026-11-17T08:30:16.000Z", "v": 65.8,  "min": 65.8,  "max": 65.8,  "n": 1, "faults": 0 },
    { "t": "2026-11-17T08:30:18.000Z", "v": 142.5, "min": 142.5, "max": 142.5, "n": 1, "faults": 0 }
  ],
  "is_simulated": true }
```

Bucketed rows use `date_bin`; `v` is the mean of `ok` readings (null if none), `faults` counts fault and invalid readings. Missing buckets are omitted, so the chart can break lines at gaps.

### E07 `GET /stations/{code}/timeline`

Query: `from`, `to`, `types` (comma list), `limit`.

```json
{ "availability": { "from": "2026-11-17T07:30:21Z", "to": "2026-11-17T08:30:21Z", "expected_frames": 1800, "received_frames": 1761, "pct": 97.8 },
  "items": [
    { "at": "2026-11-17T08:30:20.000Z", "type": "alert_opened", "sensor_uid": "HWW-KNG-001:turbidity", "data": { "alert_id": 731, "rule_code": "CHG_TURB_SPIKE" } },
    { "at": "2026-11-17T08:30:20.000Z", "type": "status_changed", "sensor_uid": "HWW-KNG-001:turbidity", "data": { "from": "normal", "to": "abnormal" } },
    { "at": "2026-11-17T08:28:02.871Z", "type": "session_started", "sensor_uid": null, "data": { "source": "simulated_wokwi", "boot_id": "6f1c2a9e" } } ],
  "next_cursor": null, "is_simulated": true }
```

### E31 `GET /stations/{code}/link`

```json
{ "station_code": "HWW-KNG-001", "link_status": "receiving",
  "session": { "id": "0b6d5c2e-…", "source": "simulated_wokwi", "device_code": "wokwi-esp32-01", "boot_id": "6f1c2a9e", "fw_version": "0.4.0",
               "started_at": "2026-11-17T08:28:02.871Z", "frames_accepted": 421, "frames_duplicate": 3, "frames_rejected": 0 },
  "last_frame_received_at": "2026-11-17T08:30:20.452Z",
  "diag": { "buffer_depth": 0, "dropped_frames": 0, "rejected_batches": 0, "wifi_rssi": -42 },
  "last_error": null, "recent_auth_failures": 0,
  "last_batch": { "schema": "hww.frames.v1", "station_code": "HWW-KNG-001", "frames": [ { "seq": 420, "…": "…" } ] },
  "is_simulated": true }
```

`link_status`: `waiting` (no session) | `receiving` (< 6 s) | `delayed` (6–15 s) | `offline` | `replay` (a replay holds the station) | `rejected` (last request failed). The stored `last_batch` never contained the key, which travels only in a header.

### E08 `GET /alerts` and E09 `GET /alerts/{id}`

E08 query: `station`, `channel`, `review_status` (multi), `severity`, `category`, `evidence_class`, `rule`, `active` (bool: `cleared_at IS NULL`), `from`, `to`, `limit`, `cursor`.

```json
{ "items": [ { "id": 731, "rule_code": "CHG_TURB_SPIKE", "rule_name": { "en": "Turbidity spike", "vi": "Độ đục tăng đột biến" },
               "station_code": "HWW-KNG-001", "sensor_uid": "HWW-KNG-001:turbidity", "category": "water_quality", "severity": "warning",
               "evidence_class": "simulated_anomaly", "is_preliminary": true, "review_status": "open",
               "opened_at": "2026-11-17T08:30:20.000Z", "detected_at": "2026-11-17T08:30:20.471Z", "detected_late": false,
               "cleared_at": null, "observed_value": 142.5, "unit": "NTU" } ],
  "next_cursor": null, "total": 1, "is_simulated": true }
```

E09 adds `baseline_value`, `threshold_value`, `params_snapshot`, `basis_snapshot` (`basis_text`, `is_regulatory`, `basis_status`), `session`, `events[]` (`type`, `at`, `actor` and `data.note` only for staff), `review` (id, status, outcome) and `related_alert_ids` (other alerts of the same session within ±5 min). Errors: 404.

### E10 `GET /rules`

`items[]` with `code`, `name`, `applies_to`, `category`, `severity`, `params`, `persistence`, `clear_persistence`, `basis_text`, `is_regulatory`, `basis_status`, `basis_reference`, `enabled`. For display only.

### E11 `GET /sessions` and E12 `GET /sessions/{id}`

E11 query: `station`, `source`, `limit`, `cursor`. Items: `id`, `station_code`, `device_code`, `source`, `boot_id`, `replay_name`, `started_at`, `last_frame_at`, `ended_at`, `end_reason`, counters. E12 adds `last_diag` and `alert_ids`.

### E13 `GET /stream` (Phase 6)

Query `stations=HWW-KNG-001,HWW-TLH-001`. `text/event-stream`, `X-Accel-Buffering: no`, heartbeat comment every 15 s.

```text
event: state_changed
data: {"station_code":"HWW-KNG-001","version":18345}

event: alert_opened
data: {"alert_id":731,"station_code":"HWW-KNG-001","rule_code":"CHG_TURB_SPIKE","severity":"warning"}
```

Never carries values ([05 §5.8](05-synchronisation.md#58-update-strategy-polling-sse-or-websockets)).

### E14 `POST /ingest/frames`

Full contract in [04 §4.8](04-wokwi-integration.md#48-payload-contract-hwwframesv1); pipeline in §7.2.

### E15 `POST /auth/login`, E16 `GET /auth/me`, E32 `POST /auth/logout`

```http
POST /api/v1/auth/login
Content-Type: application/json
X-Requested-With: hww

{"username": "<from env>", "password": "<from env>"}
```

`200 {"user": {"username": "demo.reviewer", "display_name": "Demo Reviewer", "role": "reviewer"}}` + `Set-Cookie: hww_session=…; HttpOnly; Secure; SameSite=Strict; Path=/api; Max-Age=28800`. Errors: 401 `invalid_credentials`, 429. E16 returns the same `user` object or 401. E32 clears the cookie, `204`.

### E17 `POST /alerts/{id}/acknowledge` and E18 `POST /alerts/{id}/notes`

E17 body `{"note": "Seen, watching the station"}` (optional) → `200` with the E09 alert. Errors: 401, 403, 404, 409 `invalid_transition`.
E18 body `{"text": "Presenter moved the turbidity slider."}` (1–2,000 chars) → `201 {"event": {"type": "note", "at": "…", "actor": "demo.operator", "data": {"note": "…"}}}`.

### E19 `GET /sessions/{id}/frames.jsonl`

`application/x-ndjson`; one batch envelope per line with `t_offset_ms` from session start, in seq order. `tools/record_session.py` uses it to create `shared/fixtures/replays/*.jsonl`.

```text
{"t_offset_ms":0,"frames":[{"seq":0,"mode":"manual","readings":{"ph":{"v":7.21,"u":"pH","q":"ok","raw":2109,"gen":"input"},"…":"…"}}]}
{"t_offset_ms":2000,"frames":[{"seq":1,"…":"…"}]}
```

### E20–E22 Replays

* E20 `GET /replays` → `items[]`: `name`, `description`, `frame_count`, `duration_s`, `sha256`.
* E21 `POST /replays/demo-golden/runs`, body `{"station_code": "HWW-KNG-001", "speed": 1, "takeover": true, "loop": false}` → `202 {"session_id": "…", "station_code": "HWW-KNG-001", "replay": "demo-golden", "started_at": "…", "expected_end_at": "…"}`.
  * `speed` ∈ {1, 2, 5}. Frames are re-timed to `now + t_offset_ms / speed`, so rules see the same sequence; with `speed > 1`, time windows are scaled by the same factor (T-B-14 checks the same alerts open at speed 1 and 5).
  * `takeover: true` sets `stations.active_device_id` to the replay device, so live Wokwi frames get 409 `station_busy` until the run ends (`takeover_started` / `takeover_ended` events). Without takeover, the request fails with 409 if a live session is open.
* E22 `POST /replay-runs/{session_id}/stop` → `200` with the session (`end_reason = replay_stopped`).

### E23–E27 Incident reviews

E23 `POST /incident-reviews`

```json
{ "alert_ids": [731, 732], "note": "Turbidity spike and DO drop in the same demo run." }
```

→ `201 {"id": 57, "status": "in_progress", "alert_ids": [731, 732], "created_by": "demo.reviewer", "started_at": "…"}`; the alerts move to `under_review`. Errors: 409 `invalid_transition` (an alert is closed or already in a review), 422.

E26 `POST /incident-reviews/57/submit`

```json
{ "outcome": "confirmed_simulated_anomaly", "note": "Triggered by presenter in demo.", "lab_reference": null }
```

→ `200` with the review (`status: submitted`) and its alerts (`review_status: closed`, `is_preliminary: false`, `outcome`). Errors: 422 `outcome_not_allowed` (e.g. `verified_incident` for simulated alerts, or without `lab_reference`), 403 if the user is not the creator or an admin.

E24 returns the review; E25 accepts `{"add_alert_ids": [], "remove_alert_ids": [], "note": "…"}` while `in_progress`; E27 lists reviews (`status`, `limit`, `cursor`).

### E28–E30 Admin

* E28 `PUT /admin/rules/REF_PH_BAND`, body `{"enabled": true, "severity": "critical", "params": {"min": 6.0, "max": 9.0}, "persistence": 3, "clear_persistence": 3, "basis_status": "verified", "basis_reference": "QCVN 40:2025/BTNMT, Table 1"}` → `200` rule. `params` is validated against the rule's schema (422). New params apply to future evaluations; existing alerts keep their `params_snapshot`.
* E29 `POST /admin/devices/wokwi-esp32-01/rotate-key` → `200 {"device_code": "wokwi-esp32-01", "key": "hwwk_…", "key_prefix": "hwwk_7Qx", "rotated_at": "…"}` with `Cache-Control: no-store`. The old key stops working at once.
* E30 `POST /admin/demo-reset`, body `{"confirm": "RESET"}` → `202 {"deleted": {"sessions": 12, "frames": 40211, "measurements": 160844, "alerts": 9}}`. Removes sessions, frames, measurements, events, alerts and reviews; resets states; keeps users, rules, registry and replays; bumps every station's version.

## 7.10 Background tasks

| Task | Interval | Does |
|------|----------|------|
| Freshness monitor | 1 s | For each station with a device: if `now − last_frame_at > OFFLINE_AFTER_S` and not already offline → set sensors and station `offline`, open `STN_OFFLINE`, `station_offline` event, version + 1, publish. End sessions idle for `SESSION_END_AFTER_S` (60 s), release `active_device_id`. |
| TLH replay loop | continuous | If `REPLAY_TLH_ENABLED`, runs `tlh-loop.jsonl` on `HWW-TLH-001` with `loop: true` |
| Retention | daily 03:00 ICT | §7.6 |

All run as `asyncio` tasks started in the FastAPI lifespan. They depend on there being one worker process (ADR-0004); the upgrade path is PostgreSQL advisory locks plus `LISTEN/NOTIFY`.

## 7.11 Configuration (`.env.example`)

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://hww:hww@localhost:5432/hww` | secret in deployed environments |
| `JWT_SECRET` | — (required) | ≥ 32 random bytes; different per environment |
| `SESSION_TTL_MIN` | 480 | |
| `INGEST_ENABLED` | `true` | kill switch |
| `OFFLINE_AFTER_S` / `SESSION_END_AFTER_S` | 15 / 60 | |
| `FRAME_INTERVAL_MS` | 2000 | returned as `next_min_interval_ms` |
| `INGEST_RATE_PER_S` / `INGEST_BURST` | 2 / 10 | per device key and per IP |
| `INGEST_MAX_FRAMES` / `INGEST_MAX_BYTES` | 50 / 65536 | |
| `PUBLIC_BASE_URL` | — | used in problem `type` URLs and logs |
| `CORS_ORIGINS` | empty | SPA and API share an origin; set only for a split dev set-up |
| `DEMO_MODE` | `true` | enables E30 demo reset and the replay loop |
| `WOKWI_PROJECT_URL` | — | public project link shown on the Simulation page |
| `REPLAY_TLH_ENABLED` | `true` | |
| `RETENTION_DAYS` | 7 | |
| `DEMO_OPERATOR_USERNAME`, `DEMO_OPERATOR_PASSWORD`, `DEMO_REVIEWER_…`, `DEMO_ADMIN_…` | — | used only by `cli.py seed`; set in the host's secret store |
| `SSE_ENABLED` | `false` until Phase 6 | |
| `LOG_LEVEL` | `INFO` | JSON logs with `request_id`, `station_code`, `device_code`, never keys or passwords |

## 7.12 Seeding and migrations

1. `alembic upgrade head` (run by the deploy job before the new version starts).
2. `python -m app.cli seed`: loads the registry (stations, sensor types, sensors, devices, empty `sensor_state` and `station_state` rows), loads replays, upserts rules from `0002_seed_rules.py` defaults (without overwriting admin edits), creates demo users from env vars.
3. `python -m app.cli devices rotate-key wokwi-esp32-01`: prints the device key once; it goes into the Wokwi project's `config.h` (demo) or the developer's git-ignored `config.h`.

Migrations are forward-only during the project; every migration has an integration test that runs `upgrade head` on an empty database (T-B-01).
