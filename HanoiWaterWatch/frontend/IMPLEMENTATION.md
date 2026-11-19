# Frontend implementation

React 19 + strict TypeScript/Vite SPA with an exact dependency lockfile. The API is the only source of measurements and status decisions. All routes carry the fixed simulated-data notice; station locations are explicitly illustrative.

## Implemented

- Responsive slate/sky application shell with navigation, public/staff session state, API connectivity, EN/VI language switch and persistent language choice.
- Overview: three API registry stations, lazy Leaflet/OSM map, accessible station directory, server status summary and recent anomalies. A tile failure leaves station navigation available.
- Dashboard: four sensor cards, timestamped readings, range selection, lazy Recharts history with explicit null gaps, accessible history tables, CSV export, frame availability and event timeline.
- Model: lazy React Three Fiber, GLB-magic validation, named sensor nodes, server-computed sensor materials and beacon/LED states, cloned-material cleanup, keyboard camera controls, reset, URL sensor selection, HTML sensor buttons and an SVG 2D schematic. Missing asset, rendering error or context loss leaves the schematic and sensor list available.
- Alert workspace: URL-persisted filters, public evidence/basis/history, staff acknowledgement and notes, reviewer start/submit workflow restricted to the four allowed demo outcomes. Server authorisation remains authoritative.
- Simulation: pipeline, circuit/pin explanation, scenario instructions, configured Wokwi link, actual device/session diagnostics, accepted-payload inspector and authenticated replay start/takeover/speed/stop.
- Login/logout use same-origin HttpOnly-cookie sessions. Every POST sends JSON and `X-Requested-With: hww`.

## Consistency and honesty

`useStationState` uses precisely `['stationState', code]` with a monotonic-version guard. Every station view shares that cache. Failed station requests time out after eight seconds and do not retry; current numbers are suppressed on error and stale model visuals are greyed. Fault/offline/unavailable values are suppressed independently of the numeric payload. Previous valid values remain separately labelled. HTTP Date corrects the shared one-second clock. Formatting always uses ICT. No client thresholds or generated sample readings exist.

## Verification

- `npm test`: 4 files, 12 tests passing. Coverage includes null readings, snapshot versions, rolling history, late points, staff note privacy, replay state, ICT, locale parity and CSV exports.
- `npm run build`: strict TypeScript followed by the production Vite bundle (see final agent report for latest result).
- Production dependencies: `npm audit --omit=dev --json --offline` reports zero advisories from the current cached audit metadata.
- Full audit: five high advisories in development-only Vite/Vitest dependency chains caused by picomatch 4.0.7. `npm view picomatch version` returned 4.0.7, so no published patched release was available. Critical advisories in the original tooling were removed by updating Vite to 7.3.8, Vitest to 4.1.12 and Router to 7.18.5.
- Expected bundle warning: the lazily loaded Three/R3F model chunk is approximately 952 kB minified (259 kB gzip). It is not downloaded on the overview route or while the model asset is absent.

## Remaining verification and supplied assets

The user-provided model has not been supplied. Place it at `public/models/station-v1.glb`; named sensor meshes must match the shared registry. The schematic is explicitly illustrative and is not presented as the user's 3D model. Real GLB picking, beacon geometry, WebGL/context-loss handling and mobile frame-rate checks need the actual asset.

The 19 November worktree added Playwright browser coverage and an axe check on the fallback route. See `docs/reports/verification.md` for the results. English and Vietnamese key sets match. Vietnamese copy still needs a native speaker review, and some schematic identifiers and captions are in English.

Use `npm ci`, `npm run dev` (127.0.0.1 with `/api` proxied to port 8000), `npm test`, and `npm run build`. Production serves `dist` through the backend.
