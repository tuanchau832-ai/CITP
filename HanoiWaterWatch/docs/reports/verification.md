# Implementation verification

Updated 19 November 2026. Local checks ran in the `HanoiWaterWatch` worktree on `feature/hanoi-waterwatch-platform`.

## Verified locally

- All supplied Markdown, DOCX and PDF documents were read before implementation; see `document-review.md`.
- The API runs on `http://127.0.0.1:8000` with a durable local SQLite database, random private staff credentials and a looping Tô Lịch replay.
- The production SPA is served by FastAPI, including direct requests to `/simulation`, `/alerts` and station model routes. The smoke script verifies API health, three stations, provenance and null masking.
- A complete golden replay at 5× was exercised over real HTTP, including normal, abnormal, sensor fault, offline and recovery. Staff acknowledgement, review, closure, logout and anonymous note redaction passed after correcting the logout response status.
- All 22 backend behavior and migration tests passed after the review fixes.
- Frontend TypeScript and Vite production builds passed. Domain tests cover missing/fault/stale values, ICT, version guarding, history gaps, locales and CSV semantics; further independent-review regressions are recorded below.
- ESP32 firmware compiled and linked with PlatformIO on 19 November. It uses 25.0% of RAM and 78.4% of the available flash budget. Native C++ assertions, five simulator unit tests, two cross-contract tests and the registry wiring checker passed.
- Docker Compose configuration parses. The container's frontend stage includes the shared registry imported by the application.

## Independent review

A fresh reviewer inspected the implementation. Findings included session side effects from duplicate/rejected batches, station snapshot versioning after review changes, frozen history bounds, replay controls after completion, private cached alert notes, replay concurrency and historical episode handling. Fixes and final regression results are recorded in the completion entry below; the pre-fix review is retained locally in `.local/final-review.md`.

## Not verified here

- The user-provided 3D model has not been uploaded. The accessible schematic is functional; actual model geometry, node mapping, performance and Blender conversion remain pending.
- Docker Desktop's engine was unavailable. A real PostgreSQL instance and container execution were not exercised locally. PostgreSQL DDL compilation passes; CI is configured to migrate PostgreSQL 16 and build the image.
- No public HTTPS host or Wokwi project URL has been configured. The live gateway, TLS certificate chain, OLED/device/UI agreement and ten-minute latency measurements remain pending.
- Tests used headless Chrome and SQLite locally. The 2D fallback passed a targeted axe scan and keyboard selection test. Full manual browser review, actual WebGL geometry, mobile frame rate and NVDA remain unchecked.
- The 19 November locked npm installation reported zero advisories from the available registry metadata. Development serving binds to loopback.

## Implementation choices

The API uses synchronous SQLAlchemy with a process lock, PostgreSQL row locks and one worker. Catalogue records use natural keys and JSONB registry metadata; timestamps use PostgreSQL timezone-aware columns. History aggregation occurs in Python for parity with local SQLite. SSE is explicitly disabled; polling remains the supported update path. See `backend/IMPLEMENTATION.md`, `frontend/IMPLEMENTATION.md` and `firmware/IMPLEMENTATION.md` for details and limits.

## Final regression results

- The API rejects old-boot duplicate ownership changes and advances snapshot ETags when review or session state changes.
- Historical alerts recover only after valid evidence meets the recovery rule. Historical readings leave the live sensor state intact.
- Starting a replay and accepting its first frame are one transaction. Stop and reset join any in-flight replay write before releasing the session.
- All three Playwright browser tests passed. They check public labels, the station directory with map tiles blocked, keyboard selection in the 2D fallback, the axe scan, staff replay controls, notifications for new alerts, and sign-out. The CI workflow is configured to run them against PostgreSQL 16.
- The original `main` checkout tracks `.env` and `.env.local` from an earlier demo. This worktree generates fresh credentials in an ignored file.
