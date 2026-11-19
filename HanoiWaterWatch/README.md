# Hanoi WaterWatch

A simulated water-monitoring platform for the CITP final assignment. React presents a station map, monitoring dashboard, digital station model, preliminary alerts and staff review, and a simulation demonstration. FastAPI validates incoming device frames, stores measurements, evaluates rules, and provides the shared versioned station snapshot.

**Simulated data.** All readings on this site come from a Wokwi electronics simulation or a recorded replay. They are not measurements of water in Hanoi. Station locations are illustrative.

## Run locally on Windows

Requires Python 3.10+ and Node.js 22+. Python 3.12 is used in the container.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1 -Python "C:/path/to/python.exe"
```

The launcher creates a project virtual environment, installs dependencies, builds the frontend, migrates and seeds a local SQLite database, and starts the app at **http://127.0.0.1:8000**. It generates random local account passwords in the ignored `.env.local` file. Read that file privately to sign in; credentials are never included in source or shown in the application. Subsequent launches can use `-SkipInstall -SkipBuild` when dependencies and frontend source have not changed.

SQLite supports local development without Docker. PostgreSQL 16 is the deployment database; PostgreSQL-specific deployment checks require a running database.

## Run with PostgreSQL

1. Start Docker Desktop.
2. Copy `.env.example` to `.env`. Supply a random `POSTGRES_PASSWORD` and `JWT_SECRET`, and set staff usernames and passwords.
3. For HTTP localhost development, set `COOKIE_SECURE=false`. Keep it `true` behind HTTPS in deployment.
4. Run `docker compose up --build` and open **http://localhost:8000**.

The image builds the React app and serves it from FastAPI. The API runs one worker to keep the freshness and replay tasks coordinated. The database volume persists across restarts. The app binds to loopback locally; production requires an HTTPS container host and a separately configured database.

## Development

```powershell
# API (with environment variables loaded and backend dependencies installed)
cd backend
python -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000

# In another terminal
cd frontend
npm ci
npm run dev
```

Vite proxies `/api` to port 8000. Public pages need no account. Operators can acknowledge alerts and run replays; reviewers can classify simulated anomalies; admins manage rules and device keys.

## Verify

```powershell
python -m pytest backend/tests -q
python -m unittest discover -s tools/tests
python scripts/test_contracts.py
python scripts/generate_contracts.py --check
cd frontend
npm test
npm run build
```

To run the browser checks, install Chromium with `npx playwright install chromium` in `frontend/`. Run `npm run test:e2e` after building. The test runner starts a separate API with a temporary database and fresh test credentials. Set `HWW_PYTHON` to the Python executable with the backend dependencies installed if `python` is unavailable. The CI workflow runs these browser checks with PostgreSQL 16 and builds the Docker image.

Run `python scripts/smoke.py` from the repository root against a running production build. See the [local demonstration runbook](docs/demo/runbook.md) for the complete replay and review exercise.

## Connect a simulated device

Use the seed/key CLI in `backend/` to create a scoped key for `wokwi-esp32-01`:

```powershell
python -m app.cli devices rotate-key wokwi-esp32-01
```

Store the returned key privately. Follow [firmware setup](firmware/README.md) to configure the firmware or use the software-device CLI in [tools/sim_device.py](tools/sim_device.py). Wokwi needs a reachable HTTPS endpoint and a trusted root CA. Set `WOKWI_PROJECT_URL` when the hosted simulation exists. The application links to Wokwi; it does not embed it.

The Simulation page provides operator-controlled replay takeover when Wokwi is unavailable. The Tô Lịch station uses a looping replay; the Nhuệ station is planned and remains unavailable.

The team’s earlier standalone simulator remains available in `Simulation.html`. Its five-input threshold experiment is documented in [the simulator guide](SIMULATOR_GUIDE.md). The platform’s station snapshots use the four-sensor API contract in the implementation blueprint.

## Add the station model

The supplied model belongs at `frontend/public/models/station-v1.glb`. See [model preparation](blender/README.md) for OBJ/MTL conversion and required node names. Until the model is supplied, the model page displays the functional 2D station schematic with the same readings and sensor selection.

## Project documentation

- [Implementation blueprint](docs/blueprint/README.md)
- [Implementation plan](docs/superpowers/plans/2026-11-18-platform.md)
- [Reviewed source documents](docs/reports/document-review.md)
- [GitHub team workflow](GITHUB_TEAM_WORKFLOW.md)
- [Verification and remaining external checks](docs/reports/verification.md)

This build must be verified with the uploaded model, a published Wokwi project, and the chosen HTTPS deployment before claiming the blueprint's live-demo acceptance criteria.
