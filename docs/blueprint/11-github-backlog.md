# 11: GitHub backlog

← [10 Testing, demonstration and deployment](10-testing-demo-deploy.md) · Next: [README](README.md)

This document covers deliverable 13: the backlog as small GitHub issues, each one testable on its own, with the files it creates or changes. It is generated from the same data as the roadmap in [08](08-roadmap.md) and the timeline in [09](09-team-and-timeline.md), so phases, dates, owners and dependencies agree across the three documents.

## 11.1 How to use the backlog

* There are 60 core issues (B-01 to B-60), 46.25 person-days in total, plus 3 stretch issues (B-61 to B-63) that start only after M4 and only if the owner's track is finished.
* `B-nn` is the stable name of an issue. It is used in branch names, PR titles, commit subjects and these documents. GitHub gives the issues its own numbers (`#1`, `#2`, …); the import script in §11.7 keeps the `B-nn` in each title and links dependencies by their GitHub numbers.
* Each issue is small enough for one branch and one PR (or, for the integrator, a few commits on `main`; see [09 §9.6](09-team-and-timeline.md#96-git-branching-and-review-plan)): the largest is 1.5 person-days, most are 0.5 to 1.
* **Labels** say the track (who), the phase (when, in [08](08-roadmap.md)), the area (what kind of work, as in the responsibility matrix in [09 §9.3](09-team-and-timeline.md#93-responsibility-matrix)) and the tier (how important).
* **Planned** gives the week and the working days from the schedule in [09 §9.9](09-team-and-timeline.md#99-week-by-week-plan). Issues carry tracks, not names: the import script assigns them to the people who take each track at the kickoff ([09 §9.2](09-team-and-timeline.md#92-the-two-tracks)).
* **Files and directories** are suggestions for where the work lives. A PR or commit may add helper files; it must not move work to a different layer without updating this document.
* **Done when** is the acceptance check for the issue. **Proven by** names the automated tests and acceptance criteria that must pass; the IDs (`T-…`, `AC-…`) are defined in [10 §10.2](10-testing-demo-deploy.md#102-test-catalogue) and [10 §10.3](10-testing-demo-deploy.md#103-acceptance-criteria).
* Tier `mvd` issues are never cut. Issues that may be cut, and in which order, are listed in [08 §8.12](08-roadmap.md#812-what-to-cut-if-time-runs-short).

## 11.2 Labels and milestones

| Label | Meaning |
|-------|---------|
| `track:A` | Track A: Device → Data |
| `track:B` | Track B: Model → Experience |
| `track:AB` | Joint issue, both developers |
| `phase:1` | Phase 1: Project setup and contracts |
| `phase:2` | Phase 2: 3D model preparation |
| `phase:3` | Phase 3: Wokwi simulation |
| `phase:4` | Phase 4: Backend integration |
| `phase:5` | Phase 5: Frontend development |
| `phase:6` | Phase 6: End-to-end synchronisation |
| `phase:7` | Phase 7: Testing and deployment |
| `area:setup` | Repository, CI and shared contracts |
| `area:3d` | 3D model and viewer |
| `area:wokwi` | Wokwi simulation and device communication |
| `area:backend` | Backend, database and APIs |
| `area:rules` | Anomaly detection and alerts |
| `area:frontend` | UI/UX and frontend |
| `area:testing` | Integration and end-to-end testing |
| `area:deploy` | Deployment and demo operations |
| `tier:mvd` | Needed for the minimum viable demonstration (M3) |
| `tier:core` | MVP scope after the MVD (M4–M5) |
| `tier:plus` | MVP+: first to cut |
| `tier:stretch` | Only after M4 |
| `type:spike` | Time-boxed investigation with a written report |
| `contract` | Changes a shared contract: both developers approve |

| Milestone | Due | Meaning | Issues |
|-----------|-----|---------|--------|
| M0 | Fri 27 Nov | Contracts, skeletons, CI, staging, spikes | 12: B-01, B-02, B-03, B-04, B-05, B-06, B-07, B-08, B-09, B-15, B-19, B-22 |
| M1 | Fri 4 Dec | Components work on their own | 12: B-10, B-11, B-12, B-13, B-14, B-16, B-17, B-18, B-20, B-23, B-24, B-38 |
| M2 | Fri 11 Dec | First live link | 10: B-21, B-25, B-28, B-30, B-31, B-35, B-39, B-40, B-41, B-51 |
| M3 | Fri 18 Dec | Minimum viable demonstration | 10: B-26, B-27, B-29, B-34, B-36, B-43, B-45, B-47, B-52, B-53 |
| M4 | Thu 24 Dec | Feature-complete | 9: B-32, B-33, B-37, B-42, B-44, B-46, B-54, B-55, B-56 |
| M5 | Wed 30 Dec | Release v1.0-demo | 7: B-48, B-49, B-50, B-57, B-58, B-59, B-60 |

Create the labels and milestones once, from the repository root, before running the import script. `--force` makes the label commands safe to re-run; the milestone commands fail with "already_exists" on a second run, which is harmless. `{owner}` and `{repo}` are filled in by `gh` from the current repository.

```bash
# Run once from the repository root after `gh auth login`.
gh label create "track:A" --color 1d76db --description "Track A: Device → Data" --force
gh label create "track:B" --color 5319e7 --description "Track B: Model → Experience" --force
gh label create "track:AB" --color 0e8a16 --description "Joint issue, both developers" --force
gh label create "phase:1" --color c5def5 --description "Phase 1: Project setup and contracts" --force
gh label create "phase:2" --color c5def5 --description "Phase 2: 3D model preparation" --force
gh label create "phase:3" --color c5def5 --description "Phase 3: Wokwi simulation" --force
gh label create "phase:4" --color c5def5 --description "Phase 4: Backend integration" --force
gh label create "phase:5" --color c5def5 --description "Phase 5: Frontend development" --force
gh label create "phase:6" --color c5def5 --description "Phase 6: End-to-end synchronisation" --force
gh label create "phase:7" --color c5def5 --description "Phase 7: Testing and deployment" --force
gh label create "area:setup" --color fef2c0 --description "Repository, CI and shared contracts" --force
gh label create "area:3d" --color fef2c0 --description "3D model and viewer" --force
gh label create "area:wokwi" --color fef2c0 --description "Wokwi simulation and device communication" --force
gh label create "area:backend" --color fef2c0 --description "Backend, database and APIs" --force
gh label create "area:rules" --color fef2c0 --description "Anomaly detection and alerts" --force
gh label create "area:frontend" --color fef2c0 --description "UI/UX and frontend" --force
gh label create "area:testing" --color fef2c0 --description "Integration and end-to-end testing" --force
gh label create "area:deploy" --color fef2c0 --description "Deployment and demo operations" --force
gh label create "tier:mvd" --color b60205 --description "Needed for the minimum viable demonstration (M3)" --force
gh label create "tier:core" --color d93f0b --description "MVP scope after the MVD (M4–M5)" --force
gh label create "tier:plus" --color fbca04 --description "MVP+: first to cut" --force
gh label create "tier:stretch" --color ededed --description "Only after M4" --force
gh label create "type:spike" --color f9d0c4 --description "Time-boxed investigation with a written report" --force
gh label create "contract" --color 000000 --description "Changes a shared contract: both developers approve" --force

gh api repos/{owner}/{repo}/milestones -f title="M0" -f due_on="2026-11-27T23:59:59Z" -f description="Contracts, skeletons, CI, staging, spikes"
gh api repos/{owner}/{repo}/milestones -f title="M1" -f due_on="2026-12-04T23:59:59Z" -f description="Components work on their own"
gh api repos/{owner}/{repo}/milestones -f title="M2" -f due_on="2026-12-11T23:59:59Z" -f description="First live link"
gh api repos/{owner}/{repo}/milestones -f title="M3" -f due_on="2026-12-18T23:59:59Z" -f description="Minimum viable demonstration"
gh api repos/{owner}/{repo}/milestones -f title="M4" -f due_on="2026-12-24T23:59:59Z" -f description="Feature-complete"
gh api repos/{owner}/{repo}/milestones -f title="M5" -f due_on="2026-12-30T23:59:59Z" -f description="Release v1.0-demo"
```

## 11.3 Summary

"Est." is in person-days; joint issues (Track A + B) take that time from each person.

| Issue | Title | Track | Phase | Est. | Week | Milestone | Tier | Depends on |
|-------|-------|-------|-------|------|------|-----------|------|------------|
| [B-01](#b-01-repository-skeleton-and-team-conventions) | Repository skeleton and team conventions | B | 1 | 0.25 | W1 | M0 | mvd | — |
| [B-02](#b-02-backend-skeleton-with-postgresql-in-docker-compose) | Backend skeleton with PostgreSQL in Docker Compose | A | 1 | 0.5 | W1 | M0 | mvd | B-01 |
| [B-03](#b-03-frontend-skeleton-app-shell-and-spike-s3) | Frontend skeleton, app shell and spike S3 | B | 1 | 1 | W1 | M0 | mvd | B-01 |
| [B-04](#b-04-shared-registry-files-and-registry-schema) | Shared registry files and registry schema | A | 1 | 0.5 | W1 | M0 | mvd | B-01 |
| [B-05](#b-05-registry-code-generation-and-consistency-check) | Registry code generation and consistency check | A | 1 | 0.5 | W1 | M0 | mvd | B-04 |
| [B-06](#b-06-payload-and-snapshot-contracts-with-fixtures) | Payload and snapshot contracts with fixtures | A | 1 | 0.5 | W1 | M0 | mvd | B-04 |
| [B-07](#b-07-ci-pipeline) | CI pipeline | A | 1 | 0.5 | W1 | M0 | mvd | B-02, B-03 |
| [B-08](#b-08-choose-the-host-and-deploy-the-skeleton-to-staging) | Choose the host and deploy the skeleton to staging | A | 1 | 0.5 | W1 | M0 | mvd | B-02 |
| [B-09](#b-09-spike-s1-find-out-how-tinkercad-exports) | Spike S1: find out how Tinkercad exports | B | 2 | 0.5 | W1 | M0 | mvd | — |
| [B-10](#b-10-tinkercad-station-model) | Tinkercad station model | B | 2 | 1.5 | W1 | M1 | mvd | B-09, B-04 |
| [B-11](#b-11-blender-preparation-script) | Blender preparation script | B | 2 | 1 | W2 | M1 | mvd | B-10 |
| [B-12](#b-12-glb-optimisation-budgets-and-node-check) | GLB optimisation, budgets and node check | B | 2 | 0.5 | W2 | M1 | mvd | B-11, B-05 |
| [B-13](#b-13-react-three-fiber-viewer) | React Three Fiber viewer | B | 2 | 1 | W2 | M1 | mvd | B-03, B-12 |
| [B-14](#b-14-3d-selection-hover-and-sensor-list) | 3D selection, hover and sensor list | B | 2 | 1 | W2 | M1 | mvd | B-13 |
| [B-15](#b-15-spike-s2-https-from-wokwi-through-the-public-gateway) | Spike S2: HTTPS from Wokwi through the public gateway | A | 3 | 1 | W1 | M0 | mvd | B-08 |
| [B-16](#b-16-firmware-project-skeleton-and-wokwi-web-bundler) | Firmware project skeleton and Wokwi web bundler | A | 3 | 0.5 | W2 | M1 | mvd | B-05 |
| [B-17](#b-17-pure-firmware-modules-with-native-tests) | Pure firmware modules with native tests | A | 3 | 1 | W2 | M1 | mvd | B-16 |
| [B-18](#b-18-timekeeper-and-boot-identity) | Timekeeper and boot identity | A | 3 | 0.5 | W2 | M1 | mvd | B-16, B-02 |
| [B-19](#b-19-wokwi-circuit-build) | Wokwi circuit build | A | 3 | 0.5 | W1 | M0 | mvd | B-04 |
| [B-20](#b-20-sampling-scenarios-and-local-display) | Sampling, scenarios and local display | A | 3 | 1 | W2 | M1 | mvd | B-17, B-19 |
| [B-21](#b-21-uplink-task-batching-https-post-and-ack-handling) | Uplink task: batching, HTTPS POST and ack handling | A | 3 | 1 | W3 | M2 | mvd | B-06, B-15, B-17, B-18 |
| [B-22](#b-22-software-device-sim_devicepy) | Software device `sim_device.py` | B | 3 | 0.5 | W1 | M0 | mvd | B-06 |
| [B-23](#b-23-database-models-and-migration-0001) | Database models and migration 0001 | A | 4 | 1 | W2 | M1 | mvd | B-02, B-04 |
| [B-24](#b-24-registry-loader-seed-cli-and-rule-seeds) | Registry loader, seed CLI and rule seeds | A | 4 | 0.5 | W2 | M1 | mvd | B-23, B-05 |
| [B-25](#b-25-ingest-endpoint-with-device-authentication) | Ingest endpoint with device authentication | A | 4 | 1 | W3 | M2 | mvd | B-24, B-06 |
| [B-26](#b-26-simulation-sessions-and-station-takeover) | Simulation sessions and station takeover | A | 4 | 0.5 | W4 | M3 | mvd | B-25 |
| [B-27](#b-27-rule-engine-six-rules-alert-opening-and-clearing) | Rule engine, six rules, alert opening and clearing | A | 4 | 1.5 | W4 | M3 | mvd | B-25 |
| [B-28](#b-28-state-service-event-bus-and-snapshot-api) | State service, event bus and snapshot API | A | 4 | 1 | W3 | M2 | mvd | B-25 |
| [B-29](#b-29-freshness-monitor-and-offline-detection) | Freshness monitor and offline detection | A | 4 | 0.5 | W4 | M3 | mvd | B-28, B-27 |
| [B-30](#b-30-alerts-and-rules-read-api) | Alerts and rules read API | B | 4 | 0.75 | W3 | M2 | mvd | B-23 |
| [B-31](#b-31-history-timeline-and-link-apis) | History, timeline and link APIs | B | 4 | 0.75 | W3 | M2 | mvd | B-28 |
| [B-32](#b-32-sign-in-sessions-and-role-checks) | Sign-in, sessions and role checks | A | 4 | 1 | W5 | M4 | core | B-23 |
| [B-33](#b-33-alert-actions-and-incident-review-api) | Alert actions and incident review API | B | 4 | 1 | W5 | M4 | core | B-30, B-32 |
| [B-34](#b-34-sessions-api-and-session-export) | Sessions API and session export | A | 4 | 0.5 | W4 | M3 | core | B-26 |
| [B-35](#b-35-openapi-types-and-api-client) | OpenAPI types and API client | A | 4 | 0.5 | W3 | M2 | mvd | B-28 |
| [B-36](#b-36-replay-service-and-replay-api) | Replay service and replay API | A | 4 | 1 | W4 | M3 | mvd | B-25, B-26, B-22 |
| [B-37](#b-37-admin-endpoints-and-data-maintenance) | Admin endpoints and data maintenance | A | 4 | 0.5 | W5 | M4 | core | B-32, B-27 |
| [B-38](#b-38-status-primitives-formatting-and-evidence-helpers) | Status primitives, formatting and evidence helpers | B | 5 | 1 | W2 | M1 | mvd | B-05 |
| [B-39](#b-39-station-state-hooks-and-connection-indicator) | Station-state hooks and connection indicator | B | 5 | 1 | W3 | M2 | mvd | B-35, B-06 |
| [B-40](#b-40-page-1-monitoring-overview) | Page 1: Monitoring Overview | B | 5 | 1 | W3 | M2 | mvd | B-38, B-39 |
| [B-41](#b-41-3d-status-binding-and-sensor-detail-panel) | 3D status binding and sensor detail panel | B | 5 | 1 | W3 | M2 | mvd | B-14, B-38, B-39 |
| [B-42](#b-42-2d-schematic-fallback) | 2D schematic fallback | B | 5 | 0.75 | W5 | M4 | core | B-41 |
| [B-43](#b-43-page-3-dashboard-cards-and-history-charts) | Page 3: dashboard cards and history charts | B | 5 | 1.5 | W4 | M3 | mvd | B-38, B-39, B-31 |
| [B-44](#b-44-event-timeline-and-availability) | Event timeline and availability | B | 5 | 0.5 | W5 | M4 | core | B-43, B-31 |
| [B-45](#b-45-page-4-alert-list-and-alert-detail-read-only) | Page 4: alert list and alert detail (read only) | B | 5 | 1 | W4 | M3 | mvd | B-30, B-38 |
| [B-46](#b-46-sign-in-role-gates-and-review-ui) | Sign-in, role gates and review UI | B | 5 | 1 | W5 | M4 | core | B-33, B-45, B-32 |
| [B-47](#b-47-page-5-simulation-demonstration) | Page 5: Simulation Demonstration | B | 5 | 1 | W4 | M3 | mvd | B-31, B-38 |
| [B-48](#b-48-in-app-notifications) | In-app notifications | A | 5 | 0.5 | W6 | M5 | core | B-45, B-46 |
| [B-49](#b-49-accessibility-pass) | Accessibility pass | B | 5 | 0.75 | W6 | M5 | core | B-40, B-41, B-42, B-43, B-45, B-46, B-47 |
| [B-50](#b-50-vietnamese-copy-and-native-speaker-review) | Vietnamese copy and native-speaker review | B | 5 | 0.5 | W6 | M5 | plus | B-49 |
| [B-51](#b-51-live-wokwi--staging-end-to-end) | Live Wokwi → staging end to end | A | 6 | 0.75 | W3 | M2 | mvd | B-21, B-28, B-08 |
| [B-52](#b-52-device-lamps-mirror-the-server-status) | Device lamps mirror the server status | A | 6 | 0.25 | W4 | M3 | mvd | B-21, B-28 |
| [B-53](#b-53-cross-view-consistency-e2e) | Cross-view consistency E2E | B | 6 | 1 | W4 | M3 | mvd | B-41, B-43, B-22, B-27, B-29 |
| [B-54](#b-54-latency-measurement-and-report) | Latency measurement and report | A | 6 | 0.5 | W5 | M4 | core | B-51, B-41 |
| [B-55](#b-55-sse-nudge) | SSE nudge | A | 6 | 1 | W5 | M4 | plus | B-28, B-39 |
| [B-56](#b-56-scenario-rehearsal-on-staging-sc1sc7) | Scenario rehearsal on staging (SC1–SC7) | A + B | 6 | 0.25 each | W5 | M4 | core | B-51, B-36, B-47 |
| [B-57](#b-57-e2e-suite-in-ci) | E2E suite in CI | B | 7 | 0.5 | W6 | M5 | core | B-53, B-22 |
| [B-58](#b-58-production-deployment-and-operations) | Production deployment and operations | A | 7 | 0.75 | W6 | M5 | core | B-08, B-57 |
| [B-59](#b-59-golden-recording-and-demo-runbook) | Golden recording and demo runbook | A | 7 | 0.75 | W6 | M5 | core | B-34, B-36, B-56 |
| [B-60](#b-60-final-acceptance-run-and-release) | Final acceptance run and release | A + B | 7 | 0.5 each | W6 | M5 | core | B-57, B-58, B-59 |
| [B-61](#b-61-exploded-view-and-labels-toggle) | Exploded view and labels toggle | B | 5 | 0.75 | after M4 | — | stretch | B-41 |
| [B-62](#b-62-wokwi-custom-chip-hww-probe) | Wokwi custom chip `hww-probe` | A | 3 | 1.5 | after M4 | — | stretch | B-20 |
| [B-63](#b-63-wokwi-ci-scenario-tests) | Wokwi CI scenario tests | A | 7 | 1 | after M4 | — | stretch | B-56 |

## 11.4 Definition of Done

An issue is closed only when all of these are true. The same list is in `.github/pull_request_template.md` (B-01).

1. The PR title starts with the issue ID (`B-25: …`) and the body contains `Closes #<number>`. For work the integrator commits directly to `main`, every commit subject starts with the issue ID and the last commit's body contains `Closes #<number>`.
2. CI is green on the PR, or on `main` after the integrator's push: lint, type checks, unit and integration tests, contract checks, `check_literals.py` and gitleaks.
3. Reviewed as in [09 §9.6](09-team-and-timeline.md#96-git-branching-and-review-plan): the integrator has reviewed and merged the PR (the author does not merge it), or the other developer has read the integrator's commits. Issues labelled `contract` always go through a PR in which both developers have written "contract OK".
4. The tests named under **Proven by** exist and pass. An end-to-end test (`T-E-…`) whose spec file is only written later, in B-53 or B-57, is run by hand from its description in [10 §10.2](10-testing-demo-deploy.md#end-to-end-t-e) and the result is recorded in the PR (or, for the integrator's own work, in a comment on the issue). A manual check is recorded the same way, with a screenshot or log extract.
5. No sensor value, threshold, status colour, station ID or GPIO pin is typed into the code by hand; all of them come from the registry, the snapshot or `status_visuals.json` ([05 §5.12](05-synchronisation.md#512-banned-patterns-checked-in-review-and-ci)).
6. Every user-facing string is in `frontend/src/locales/en.json` and `vi.json`.
7. Simulated-data labelling still works: the banner, the source badges and the "Preliminary" and "Simulated anomaly" labels are visible wherever readings or alerts appear ([01 §1.5](01-mvp-and-stack.md#15-data-honesty-rules)).
8. No secret, device key or password is in the diff, in the public Wokwi project or in the logs.
9. Documentation is updated: the relevant blueprint section, an ADR if a decision changed, and `README.md` if a command changed.
10. If the issue changes what the deployed site does, it has been deployed to staging and checked there.

## 11.5 Issues

### Phase 1: Project setup and contracts

#### B-01: Repository skeleton and team conventions

**Labels:** `track:B` `phase:1` `area:setup` `tier:mvd`  
**Estimate:** 0.25 person-days · **Planned:** W1 (Mon, from Mon 23 Nov) · **Milestone:** M0  
**Depends on:** none · **Unblocks:** [B-02](#b-02-backend-skeleton-with-postgresql-in-docker-compose), [B-03](#b-03-frontend-skeleton-app-shell-and-spike-s3), [B-04](#b-04-shared-registry-files-and-registry-schema)

**Files and directories**

* `README.md`
* `CONTRIBUTING.md` (the team GitHub workflow, [09 §9.6](09-team-and-timeline.md#96-git-branching-and-review-plan))
* `LICENSE`
* `Makefile`
* `.editorconfig`
* `.gitattributes` (eol=lf)
* `.gitignore`
* `.env.example`
* `.github/CODEOWNERS`
* `.github/pull_request_template.md`
* `.github/ISSUE_TEMPLATE/{task.yml,bug.yml}`
* `docs/adr/0001…0006` (stubs)
* `tools/import_backlog.py` (from [11 §11.7](11-github-backlog.md#117-import-script))

**Done when.** Both developers can clone and run `make help`; the integrator chosen at the kickoff has admin rights; `CONTRIBUTING.md` and the Git rules in [09 §9.6](09-team-and-timeline.md#96-git-branching-and-review-plan) agree; squash merge is the only merge method for PRs; `main` is protected as in 9.6 if the GitHub plan offers it; the six ADR stubs from [02 §2.9](02-architecture.md#29-architecture-decision-records-to-create-in-phase-1) exist.

**Proven by.** Manual check of the "done when" list, recorded in the PR description (or on the issue, for commits the integrator pushes to main).

#### B-02: Backend skeleton with PostgreSQL in Docker Compose

**Labels:** `track:A` `phase:1` `area:backend` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Mon, from Mon 23 Nov) · **Milestone:** M0  
**Depends on:** [B-01](#b-01-repository-skeleton-and-team-conventions) · **Unblocks:** [B-07](#b-07-ci-pipeline), [B-08](#b-08-choose-the-host-and-deploy-the-skeleton-to-staging), [B-18](#b-18-timekeeper-and-boot-identity), [B-23](#b-23-database-models-and-migration-0001)

**Files and directories**

* `docker-compose.yml`
* `backend/pyproject.toml`
* `backend/alembic.ini`
* `backend/alembic/env.py`
* `backend/app/{main.py,config.py,db.py}`
* `backend/app/core/{errors.py,logging.py,time.py}`
* `backend/app/api/v1/{health.py,meta.py}`
* `backend/tests/integration/test_health_meta.py`

**Done when.** `make dev` starts PostgreSQL and the API; E01 returns `"db": "ok"`; E02 returns `server_time`; errors are `application/problem+json`; logs are JSON lines.

**Proven by.** T-B-02

#### B-03: Frontend skeleton, app shell and spike S3

**Labels:** `track:B` `phase:1` `area:frontend` `tier:mvd` `type:spike`  
**Estimate:** 1 person-day · **Planned:** W1 (Mon–Tue, from Mon 23 Nov) · **Milestone:** M0  
**Depends on:** [B-01](#b-01-repository-skeleton-and-team-conventions) · **Unblocks:** [B-07](#b-07-ci-pipeline), [B-13](#b-13-react-three-fiber-viewer)

**Files and directories**

* `frontend/{package.json,package-lock.json,vite.config.ts,tsconfig.json,index.html}`
* `frontend/src/{main.tsx,App.tsx,routes.tsx,i18n.ts,index.css}`
* `frontend/src/components/layout/{AppShell,NavBar,SimulatedDataBanner,Footer}.tsx`
* `frontend/src/locales/{en,vi}.json`
* `docs/reports/spike-s3.md`

**Done when.** Every route in [06 §6.2](06-ui-ux.md#62-routes-and-access) renders a placeholder inside the shell with the simulated-data banner; Vite proxies `/api`; a test page with an R3F cube and a Leaflet map runs on one Android phone and one iPhone (Safari); exact versions are pinned in the lockfile.

**Proven by.** T-E-09

#### B-04: Shared registry files and registry schema

**Labels:** `track:A` `phase:1` `area:setup` `tier:mvd` `contract`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Mon–Tue, from Mon 23 Nov) · **Milestone:** M0  
**Depends on:** [B-01](#b-01-repository-skeleton-and-team-conventions) · **Unblocks:** [B-05](#b-05-registry-code-generation-and-consistency-check), [B-06](#b-06-payload-and-snapshot-contracts-with-fixtures), [B-10](#b-10-tinkercad-station-model), [B-19](#b-19-wokwi-circuit-build), [B-23](#b-23-database-models-and-migration-0001)

**Files and directories**

* `shared/registry/{sensor_types,status_visuals,HWW-KNG-001,HWW-TLH-001,HWW-NHU-001}.json`
* `shared/schemas/registry.schema.json`

**Done when.** The files contain every identifier in [05 §5.2](05-synchronisation.md#52-identifiers) and every row of [05 §5.4](05-synchronisation.md#54-master-mapping-table); both developers approve the PR (contract files).

**Proven by.** T-C-01

#### B-05: Registry code generation and consistency check

**Labels:** `track:A` `phase:1` `area:setup` `tier:mvd` `contract`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Tue, from Tue 24 Nov) · **Milestone:** M0  
**Depends on:** [B-04](#b-04-shared-registry-files-and-registry-schema) · **Unblocks:** [B-12](#b-12-glb-optimisation-budgets-and-node-check), [B-16](#b-16-firmware-project-skeleton-and-wokwi-web-bundler), [B-24](#b-24-registry-loader-seed-cli-and-rule-seeds), [B-38](#b-38-status-primitives-formatting-and-evidence-helpers)

**Files and directories**

* `tools/gen_registry.py`
* `tools/check_registry.py`
* `firmware/src/generated/registry.h`
* `frontend/src/generated/registry.ts`
* `backend/tests/contract/test_registry.py`

**Done when.** `make gen` regenerates both files byte for byte; CI fails if a generated file is stale, a pin is used twice, a unit differs from `sensor_types.json`, or a sensor has no `model_node`.

**Proven by.** T-C-01, T-C-02

#### B-06: Payload and snapshot contracts with fixtures

**Labels:** `track:A` `phase:1` `area:setup` `tier:mvd` `contract`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Tue–Wed, from Tue 24 Nov) · **Milestone:** M0  
**Depends on:** [B-04](#b-04-shared-registry-files-and-registry-schema) · **Unblocks:** [B-21](#b-21-uplink-task-batching-https-post-and-ack-handling), [B-22](#b-22-software-device-sim_devicepy), [B-25](#b-25-ingest-endpoint-with-device-authentication), [B-39](#b-39-station-state-hooks-and-connection-indicator)

**Files and directories**

* `shared/schemas/{frame-batch.v1,station-state.v1}.schema.json`
* `shared/fixtures/payloads/{valid_batch,duplicate_batch,fault_frame,backlog_batch,invalid_unit}.json`
* `backend/tests/contract/test_fixtures.py`

**Done when.** The schemas match [04 §4.8](04-wokwi-integration.md#48-payload-contract-hwwframesv1) and the E05 example in [07 §7.9](07-backend-database-api.md#79-endpoint-catalogue); valid fixtures pass and invalid ones fail for the expected reason. `v1` is frozen at M0; later changes need both approvals.

**Proven by.** T-C-04

#### B-07: CI pipeline

**Labels:** `track:A` `phase:1` `area:setup` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Wed, from Wed 25 Nov) · **Milestone:** M0  
**Depends on:** [B-02](#b-02-backend-skeleton-with-postgresql-in-docker-compose), [B-03](#b-03-frontend-skeleton-app-shell-and-spike-s3) · **Unblocks:** none

**Files and directories**

* `.github/workflows/ci.yml`
* `tools/check_literals.py`
* `.gitleaks.toml`

**Done when.** Every PR and every push to `main` runs ruff, mypy, pytest (unit and contract), eslint, `tsc --noEmit`, Vitest, `check_registry.py`, `check_literals.py` and gitleaks in under 10 minutes; a PostgreSQL service container is ready for integration tests.

**Proven by.** T-C-05, T-S-05

#### B-08: Choose the host and deploy the skeleton to staging

**Labels:** `track:A` `phase:1` `area:deploy` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Wed–Thu, from Wed 25 Nov) · **Milestone:** M0  
**Depends on:** [B-02](#b-02-backend-skeleton-with-postgresql-in-docker-compose) · **Unblocks:** [B-15](#b-15-spike-s2-https-from-wokwi-through-the-public-gateway), [B-51](#b-51-live-wokwi--staging-end-to-end), [B-58](#b-58-production-deployment-and-operations)

**Files and directories**

* `Dockerfile`
* `.github/workflows/deploy.yml` (manual trigger)
* `docs/adr/0004-single-instance-runtime.md`
* `docs/reports/hosting.md`

**Done when.** Host chosen against the criteria in [10 §10.6](10-testing-demo-deploy.md#106-deployment-plan); `https://<staging-host>/api/v1/health` returns 200 over HTTPS with managed PostgreSQL; secrets live only in the host's secret store. Spike S2 needs this URL.

**Proven by.** T-D-01

### Phase 2: 3D model preparation

#### B-09: Spike S1: find out how Tinkercad exports

**Labels:** `track:B` `phase:2` `area:3d` `tier:mvd` `type:spike`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Tue, from Tue 24 Nov) · **Milestone:** M0  
**Depends on:** none · **Unblocks:** [B-10](#b-10-tinkercad-station-model)

**Files and directories**

* `blender/README.md`
* `blender/scripts/material_map.json`
* `docs/adr/0003-3d-format-and-pipeline.md`

**Done when.** The five questions in [03 §3.4.1](03-3d-integration.md#341-spike-s1-week-1-half-a-day-find-out-how-tinkercad-exports) are answered with screenshots; ADR-0003 confirms or adjusts the pipeline.

**Proven by.** Manual check of the "done when" list, recorded in the PR description (or on the issue, for commits the integrator pushes to main).

#### B-10: Tinkercad station model

**Labels:** `track:B` `phase:2` `area:3d` `tier:mvd`  
**Estimate:** 1.5 person-days · **Planned:** W1 (Tue–Thu, from Tue 24 Nov) · **Milestone:** M1  
**Depends on:** [B-09](#b-09-spike-s1-find-out-how-tinkercad-exports), [B-04](#b-04-shared-registry-files-and-registry-schema) · **Unblocks:** [B-11](#b-11-blender-preparation-script)

**Files and directories**

* `blender/source/station-tinkercad.{obj,mtl}`
* `docs/assets/tinkercad-station.png`
* `blender/README.md` (link to the Tinkercad design)

**Done when.** Every component in [03 §3.2](03-3d-integration.md#32-component-inventory-and-node-names) exists, with one unique colour per clickable part, following [03 §3.4.2](03-3d-integration.md#342-tinkercad-modelling-rules).

**Proven by.** Manual check of the "done when" list, recorded in the PR description (or on the issue, for commits the integrator pushes to main).

#### B-11: Blender preparation script

**Labels:** `track:B` `phase:2` `area:3d` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W2 (Mon, from Mon 30 Nov) · **Milestone:** M1  
**Depends on:** [B-10](#b-10-tinkercad-station-model) · **Unblocks:** [B-12](#b-12-glb-optimisation-budgets-and-node-check)

**Files and directories**

* `blender/scripts/prepare_station.py`
* `blender/station.blend`

**Done when.** One command (`blender -b -P …`) turns the OBJ into a GLB whose node names equal the registry `model.components[].node` values; metres, Y-up, origin at the base.

**Proven by.** T-C-03

#### B-12: GLB optimisation, budgets and node check

**Labels:** `track:B` `phase:2` `area:3d` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W2 (Tue, from Tue 1 Dec) · **Milestone:** M1  
**Depends on:** [B-11](#b-11-blender-preparation-script), [B-05](#b-05-registry-code-generation-and-consistency-check) · **Unblocks:** [B-13](#b-13-react-three-fiber-viewer)

**Files and directories**

* Makefile (target `glb`)
* `frontend/public/models/station-v1.glb`
* `frontend/scripts/check-glb-nodes.mjs`

**Done when.** `make glb` produces a meshopt-compressed GLB within the budgets in [03 §3.4.5](03-3d-integration.md#345-budgets); CI fails when a registry node is missing from the committed GLB.

**Proven by.** T-C-03

#### B-13: React Three Fiber viewer

**Labels:** `track:B` `phase:2` `area:3d` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W2 (Tue–Wed, from Tue 1 Dec) · **Milestone:** M1  
**Depends on:** [B-03](#b-03-frontend-skeleton-app-shell-and-spike-s3), [B-12](#b-12-glb-optimisation-budgets-and-node-check) · **Unblocks:** [B-14](#b-14-3d-selection-hover-and-sensor-list)

**Files and directories**

* `frontend/src/features/model/{ModelPage,StationCanvas,StationModel,CanvasErrorBoundary}.tsx`
* `frontend/src/features/model/useWebGLSupport.ts`

**Done when.** The model loads with orbit, zoom limits and a reset-view button; a WebGL or GLB error shows the error boundary instead of a blank page; the `__hww3d` hook exists only when `VITE_E2E=1`.

**Proven by.** T-E-07

#### B-14: 3D selection, hover and sensor list

**Labels:** `track:B` `phase:2` `area:3d` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W2 (Wed–Thu, from Wed 2 Dec) · **Milestone:** M1  
**Depends on:** [B-13](#b-13-react-three-fiber-viewer) · **Unblocks:** [B-41](#b-41-3d-status-binding-and-sensor-detail-panel)

**Files and directories**

* `frontend/src/features/model/{SensorHotspot,SensorList,ModelControls}.tsx`
* `frontend/src/state/uiStore.ts`

**Done when.** Clicking a part, choosing it in `SensorList` or using the keyboard selects the same component in `uiStore`; hover shows the name; the selection survives a model reload.

**Proven by.** T-F-05, AC-11

### Phase 3: Wokwi simulation

#### B-15: Spike S2: HTTPS from Wokwi through the public gateway

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:mvd` `type:spike`  
**Estimate:** 1 person-day · **Planned:** W1 (Thu–Fri, from Thu 26 Nov) · **Milestone:** M0  
**Depends on:** [B-08](#b-08-choose-the-host-and-deploy-the-skeleton-to-staging) · **Unblocks:** [B-21](#b-21-uplink-task-batching-https-post-and-ack-handling)

**Files and directories**

* `firmware/spikes/s2_https/{sketch.ino,diagram.json}`
* `docs/reports/spike-s2.md`
* `docs/adr/0001-device-transport.md`

**Done when.** Every measurement listed in [04 §4.11.1](04-wokwi-integration.md#4111-spike-s2-week-1-one-day-prove-the-risky-parts-first) is recorded for a 10-minute run against staging; ADR-0001 is accepted, or the fallback in that section is triggered.

**Proven by.** Manual check of the "done when" list, recorded in the PR description (or on the issue, for commits the integrator pushes to main).

#### B-16: Firmware project skeleton and Wokwi web bundler

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W2 (Tue, from Tue 1 Dec) · **Milestone:** M1  
**Depends on:** [B-05](#b-05-registry-code-generation-and-consistency-check) · **Unblocks:** [B-17](#b-17-pure-firmware-modules-with-native-tests), [B-18](#b-18-timekeeper-and-boot-identity)

**Files and directories**

* `firmware/platformio.ini`
* `firmware/wokwi.toml`
* `firmware/include/config.example.h`
* `firmware/src/main.cpp`
* `tools/bundle_wokwi_web.py`
* `tools/tests/test_bundle.py`
* `firmware/wokwi-web/`

**Done when.** `pio run -e esp32` and `pio test -e native` succeed; `python tools/bundle_wokwi_web.py` produces a folder that compiles unchanged on wokwi.com; `config.h` is git-ignored.

**Proven by.** T-S-05

#### B-17: Pure firmware modules with native tests

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W2 (Wed, from Wed 2 Dec) · **Milestone:** M1  
**Depends on:** [B-16](#b-16-firmware-project-skeleton-and-wokwi-web-bundler) · **Unblocks:** [B-20](#b-20-sampling-scenarios-and-local-display), [B-21](#b-21-uplink-task-batching-https-post-and-ack-handling)

**Files and directories**

* `firmware/src/{transfer,backoff,frame_buffer}.{h,cpp}`
* `firmware/test/test_{transfer,backoff,frame_buffer}/test_main.cpp`

**Done when.** Transfer functions reproduce the table in [04 §4.4](04-wokwi-integration.md#44-transfer-functions-raw--engineering-units) (raw 555 → 18.4 NTU, 1546 → 142.5 NTU); the ring buffer keeps 600 frames and drops the oldest; backoff follows 1, 2, 4, 8, 16, 30 s ± 20 %.

**Proven by.** T-W-01, T-W-02, T-W-03

#### B-18: Timekeeper and boot identity

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W2 (Thu, from Thu 3 Dec) · **Milestone:** M1  
**Depends on:** [B-16](#b-16-firmware-project-skeleton-and-wokwi-web-bundler), [B-02](#b-02-backend-skeleton-with-postgresql-in-docker-compose) · **Unblocks:** [B-21](#b-21-uplink-task-batching-https-post-and-ack-handling)

**Files and directories**

* `firmware/src/timekeeper.{h,cpp}`

**Done when.** `boot_id` is random per boot; the time source falls back from NTP to the `/meta` server offset to uptime, and every frame carries `time_source`.

**Proven by.** T-W-04

#### B-19: Wokwi circuit build

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Fri, from Fri 27 Nov) · **Milestone:** M0  
**Depends on:** [B-04](#b-04-shared-registry-files-and-registry-schema) · **Unblocks:** [B-20](#b-20-sampling-scenarios-and-local-display)

**Files and directories**

* `firmware/diagram.json`
* `firmware/wokwi-web/diagram.json`
* `docs/assets/circuit.png`

**Done when.** Every part and wire in [04 §4.3.1](04-wokwi-integration.md#431-pin-map) is present and checked in the editor; `check_registry.py` confirms the pins match `HWW-KNG-001.json`; analog inputs use ADC1 pins only.

**Proven by.** T-C-02

#### B-20: Sampling, scenarios and local display

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W2 (Thu–Fri, from Thu 3 Dec) · **Milestone:** M1  
**Depends on:** [B-17](#b-17-pure-firmware-modules-with-native-tests), [B-19](#b-19-wokwi-circuit-build) · **Unblocks:** [B-62](#b-62-wokwi-custom-chip-hww-probe)

**Files and directories**

* `firmware/src/{sensors,scenario,display}.{h,cpp}`

**Done when.** 4 Hz sampling averaged over 2 s; DIP SW1–SW4 produce `q:"fault"`; MODE cycles M0–M3 with the profiles in [04 §4.6](04-wokwi-integration.md#46-demonstration-scenarios); the OLED shows values with the registry decimals.

**Proven by.** T-W-06 (SC1–SC4 on the device)

#### B-21: Uplink task: batching, HTTPS POST and ack handling

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W3 (Wed–Thu, from Wed 9 Dec) · **Milestone:** M2  
**Depends on:** [B-06](#b-06-payload-and-snapshot-contracts-with-fixtures), [B-15](#b-15-spike-s2-https-from-wokwi-through-the-public-gateway), [B-17](#b-17-pure-firmware-modules-with-native-tests), [B-18](#b-18-timekeeper-and-boot-identity) · **Unblocks:** [B-51](#b-51-live-wokwi--staging-end-to-end), [B-52](#b-52-device-lamps-mirror-the-server-status)

**Files and directories**

* `firmware/src/uplink.{h,cpp}`
* `firmware/test/test_uplink/test_main.cpp`

**Done when.** Batches validate against `frame-batch.v1`; `setCACert` is used, never `setInsecure`; per-seq acks free buffer slots; 401/403/409/413/422/429/503 are handled as in [04 §4.8](04-wokwi-integration.md#48-payload-contract-hwwframesv1); sampling never waits for a POST.

**Proven by.** T-W-04, T-W-06 (SC5, SC7)

#### B-22: Software device `sim_device.py`

**Labels:** `track:B` `phase:3` `area:wokwi` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W1 (Thu, from Thu 26 Nov) · **Milestone:** M0  
**Depends on:** [B-06](#b-06-payload-and-snapshot-contracts-with-fixtures) · **Unblocks:** [B-36](#b-36-replay-service-and-replay-api), [B-53](#b-53-cross-view-consistency-e2e), [B-57](#b-57-e2e-suite-in-ci)

**Files and directories**

* `tools/sim_device.py`
* `tools/tests/test_sim_device.py`

**Done when.** Produces the same payloads as the firmware for every scenario (`--scenario normal|gradual_ph|spike_turb|do_drop`, `--fault turbidity`, `--outage 60`), validated against `frame-batch.v1`; `--out <file>.jsonl` writes a replay file instead of posting; used for local development (topology T-B) and CI E2E. Written by the developer who did *not* write the firmware, so it doubles as a contract check.

**Proven by.** T-C-04

### Phase 4: Backend integration

#### B-23: Database models and migration 0001

**Labels:** `track:A` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W2 (Mon, from Mon 30 Nov) · **Milestone:** M1  
**Depends on:** [B-02](#b-02-backend-skeleton-with-postgresql-in-docker-compose), [B-04](#b-04-shared-registry-files-and-registry-schema) · **Unblocks:** [B-24](#b-24-registry-loader-seed-cli-and-rule-seeds), [B-30](#b-30-alerts-and-rules-read-api), [B-32](#b-32-sign-in-sessions-and-role-checks)

**Files and directories**

* `backend/app/models/*.py`
* `backend/alembic/versions/0001_initial.py`
* `backend/tests/integration/test_migrations.py`

**Done when.** Every table, check and index in [07 §7.6](07-backend-database-api.md#76-tables) exists; `alembic upgrade head` works on an empty database; the evidence-class checks reject a simulated `verified_incident`.

**Proven by.** T-B-01, T-B-15

#### B-24: Registry loader, seed CLI and rule seeds

**Labels:** `track:A` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W2 (Tue, from Tue 1 Dec) · **Milestone:** M1  
**Depends on:** [B-23](#b-23-database-models-and-migration-0001), [B-05](#b-05-registry-code-generation-and-consistency-check) · **Unblocks:** [B-25](#b-25-ingest-endpoint-with-device-authentication)

**Files and directories**

* `backend/app/services/registry_loader.py`
* `backend/app/cli.py`
* `backend/alembic/versions/0002_seed_rules.py`
* `backend/tests/integration/test_seed.py`

**Done when.** `python -m app.cli seed` is idempotent and does not overwrite rule edits made by an admin; `devices rotate-key` prints the key once and stores only its hash and prefix; demo users come from env vars.

**Proven by.** T-B-02

#### B-25: Ingest endpoint with device authentication

**Labels:** `track:A` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W3 (Mon, from Mon 7 Dec) · **Milestone:** M2  
**Depends on:** [B-24](#b-24-registry-loader-seed-cli-and-rule-seeds), [B-06](#b-06-payload-and-snapshot-contracts-with-fixtures) · **Unblocks:** [B-26](#b-26-simulation-sessions-and-station-takeover), [B-27](#b-27-rule-engine-six-rules-alert-opening-and-clearing), [B-28](#b-28-state-service-event-bus-and-snapshot-api), [B-36](#b-36-replay-service-and-replay-api)

**Files and directories**

* `backend/app/api/v1/ingest.py`
* `backend/app/services/{ingest_service,device_auth}.py`
* `backend/app/core/rate_limit.py`
* `backend/app/schemas/ingest.py`
* `backend/tests/integration/test_ingest_api.py`

**Done when.** Steps 1–9 and 11 of [07 §7.2](07-backend-database-api.md#72-ingest-pipeline) work (rules plug in with B-27); every error code has a test; duplicates are reported per seq; provenance is stored on every measurement.

**Proven by.** T-B-03, T-B-04, AC-07, AC-12

#### B-26: Simulation sessions and station takeover

**Labels:** `track:A` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W4 (Tue, from Tue 15 Dec) · **Milestone:** M3  
**Depends on:** [B-25](#b-25-ingest-endpoint-with-device-authentication) · **Unblocks:** [B-34](#b-34-sessions-api-and-session-export), [B-36](#b-36-replay-service-and-replay-api)

**Files and directories**

* `backend/app/services/session_service.py`
* `backend/tests/integration/test_sessions.py`

**Done when.** A new `boot_id` opens a new session and supersedes the old one; idle sessions end after 60 s; a second device gets 409 `station_busy` while another session holds the station.

**Proven by.** T-B-12

#### B-27: Rule engine, six rules, alert opening and clearing

**Labels:** `track:A` `phase:4` `area:rules` `tier:mvd`  
**Estimate:** 1.5 person-days · **Planned:** W4 (Mon–Tue, from Mon 14 Dec) · **Milestone:** M3  
**Depends on:** [B-25](#b-25-ingest-endpoint-with-device-authentication) · **Unblocks:** [B-29](#b-29-freshness-monitor-and-offline-detection), [B-37](#b-37-admin-endpoints-and-data-maintenance), [B-53](#b-53-cross-view-consistency-e2e)

**Files and directories**

* `backend/app/services/{rule_engine,alert_service}.py`
* `backend/app/rules/{base,validity,reference_band,change,freshness}.py`
* `backend/tests/unit/test_rules_*.py`

**Done when.** The rules, baseline and evaluation order in [07 §7.4](07-backend-database-api.md#74-rule-engine) are implemented; the worked numbers in §7.4.4 are unit tests; faults never count towards water-quality rules; one alert per episode; `cleared_at` is set without closing the alert.

**Proven by.** T-B-06 … T-B-10, T-B-16

#### B-28: State service, event bus and snapshot API

**Labels:** `track:A` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W3 (Tue, from Tue 8 Dec) · **Milestone:** M2  
**Depends on:** [B-25](#b-25-ingest-endpoint-with-device-authentication) · **Unblocks:** [B-29](#b-29-freshness-monitor-and-offline-detection), [B-31](#b-31-history-timeline-and-link-apis), [B-35](#b-35-openapi-types-and-api-client), [B-51](#b-51-live-wokwi--staging-end-to-end), [B-52](#b-52-device-lamps-mirror-the-server-status), [B-55](#b-55-sse-nudge)

**Files and directories**

* `backend/app/services/{state_service,event_bus}.py`
* `backend/app/api/v1/stations.py` (E03–E05)
* `backend/app/schemas/{station,state}.py`
* `backend/tests/integration/test_state_api.py`

**Done when.** E05 matches `station-state.v1`; `version` increases once per accepted batch in the ingest transaction; the snapshot is read in one `REPEATABLE READ` transaction; ETag and 304 work; `value` is null for fault, offline and unavailable, with `last_valid` separate.

**Proven by.** T-B-05, T-B-13

#### B-29: Freshness monitor and offline detection

**Labels:** `track:A` `phase:4` `area:rules` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W4 (Thu, from Thu 17 Dec) · **Milestone:** M3  
**Depends on:** [B-28](#b-28-state-service-event-bus-and-snapshot-api), [B-27](#b-27-rule-engine-six-rules-alert-opening-and-clearing) · **Unblocks:** [B-53](#b-53-cross-view-consistency-e2e)

**Files and directories**

* `backend/app/services/freshness_monitor.py`
* `backend/tests/integration/test_offline.py`

**Done when.** Station and sensors go `offline` 15 s after the last `received_at` (never device time); `STN_OFFLINE` opens and clears; back-filled frames never rewind `sensor_state`.

**Proven by.** T-B-11

#### B-30: Alerts and rules read API

**Labels:** `track:B` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 0.75 person-days · **Planned:** W3 (Mon, from Mon 7 Dec) · **Milestone:** M2  
**Depends on:** [B-23](#b-23-database-models-and-migration-0001) · **Unblocks:** [B-33](#b-33-alert-actions-and-incident-review-api), [B-45](#b-45-page-4-alert-list-and-alert-detail-read-only)

**Files and directories**

* `backend/app/api/v1/{alerts,rules}.py` (E08–E10)
* `backend/app/schemas/alert.py`
* `backend/tests/integration/test_alerts_api.py`

**Done when.** Filters, cursor pagination and the E09 detail shape in [07 §7.9](07-backend-database-api.md#79-endpoint-catalogue) work against seeded alerts; anonymous responses never contain notes or user names.

**Proven by.** T-B-16, T-S-03

#### B-31: History, timeline and link APIs

**Labels:** `track:B` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 0.75 person-days · **Planned:** W3 (Wed, from Wed 9 Dec) · **Milestone:** M2  
**Depends on:** [B-28](#b-28-state-service-event-bus-and-snapshot-api) · **Unblocks:** [B-43](#b-43-page-3-dashboard-cards-and-history-charts), [B-44](#b-44-event-timeline-and-availability), [B-47](#b-47-page-5-simulation-demonstration)

**Files and directories**

* `backend/app/api/v1/stations.py` (E06, E07, E31)
* `backend/app/schemas/measurement.py`
* `backend/tests/integration/test_history_api.py`

**Done when.** `date_bin` buckets follow the `auto` table; at most 5,000 points; gaps are left out, not interpolated; the timeline returns `availability`; `/link` returns the last accepted batch, session counters, diagnostics and the last error.

**Proven by.** T-B-17

#### B-32: Sign-in, sessions and role checks

**Labels:** `track:A` `phase:4` `area:backend` `tier:core`  
**Estimate:** 1 person-day · **Planned:** W5 (Mon, from Mon 21 Dec) · **Milestone:** M4  
**Depends on:** [B-23](#b-23-database-models-and-migration-0001) · **Unblocks:** [B-33](#b-33-alert-actions-and-incident-review-api), [B-37](#b-37-admin-endpoints-and-data-maintenance), [B-46](#b-46-sign-in-role-gates-and-review-ui)

**Files and directories**

* `backend/app/services/auth_service.py`
* `backend/app/api/v1/{auth,deps}.py`
* `backend/app/core/security.py`
* `backend/tests/integration/{test_auth,test_roles}.py`

**Done when.** E15, E16 and E32 work as specified; the cookie is `HttpOnly; Secure; SameSite=Strict`; state-changing requests need JSON and `X-Requested-With: hww`; sign-in is rate-limited; `deps.py` enforces the role matrix in [07 §7.8](07-backend-database-api.md#78-conventions-auth-errors-pagination).

**Proven by.** T-S-01, T-S-02, T-S-03

#### B-33: Alert actions and incident review API

**Labels:** `track:B` `phase:4` `area:backend` `tier:core`  
**Estimate:** 1 person-day · **Planned:** W5 (Tue–Wed, from Tue 22 Dec) · **Milestone:** M4  
**Depends on:** [B-30](#b-30-alerts-and-rules-read-api), [B-32](#b-32-sign-in-sessions-and-role-checks) · **Unblocks:** [B-46](#b-46-sign-in-role-gates-and-review-ui)

**Files and directories**

* `backend/app/api/v1/{alerts,incident_reviews}.py` (E17, E18, E23–E27)
* `backend/app/schemas/review.py`
* `backend/tests/integration/test_reviews.py`

**Done when.** Transitions follow [07 §7.7](07-backend-database-api.md#77-alert-lifecycle); invalid ones return 409; simulated alerts accept only the demo outcomes; every action writes an `alert_events` row.

**Proven by.** T-B-18, AC-13

#### B-34: Sessions API and session export

**Labels:** `track:A` `phase:4` `area:backend` `tier:core`  
**Estimate:** 0.5 person-days · **Planned:** W4 (Thu, from Thu 17 Dec) · **Milestone:** M3  
**Depends on:** [B-26](#b-26-simulation-sessions-and-station-takeover) · **Unblocks:** [B-59](#b-59-golden-recording-and-demo-runbook)

**Files and directories**

* `backend/app/api/v1/sessions.py` (E11, E12, E19)
* `tools/record_session.py`

**Done when.** `python tools/record_session.py --session <id>` writes a `.jsonl` file that replays to the same alerts.

**Proven by.** T-B-14

#### B-35: OpenAPI types and API client

**Labels:** `track:A` `phase:4` `area:frontend` `tier:mvd`  
**Estimate:** 0.5 person-days · **Planned:** W3 (Wed, from Wed 9 Dec) · **Milestone:** M2  
**Depends on:** [B-28](#b-28-state-service-event-bus-and-snapshot-api) · **Unblocks:** [B-39](#b-39-station-state-hooks-and-connection-indicator)

**Files and directories**

* `frontend/src/api/{client.ts,schema.d.ts}`
* Makefile (target `gen`)

**Done when.** `make gen` regenerates `schema.d.ts` from `/api/v1/openapi.json`; CI fails when it is stale; `client.ts` sends `X-Requested-With: hww`, parses problem+json and reads the `Date` header for the clock offset.

**Proven by.** T-C-06

#### B-36: Replay service and replay API

**Labels:** `track:A` `phase:4` `area:backend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W4 (Wed, from Wed 16 Dec) · **Milestone:** M3  
**Depends on:** [B-25](#b-25-ingest-endpoint-with-device-authentication), [B-26](#b-26-simulation-sessions-and-station-takeover), [B-22](#b-22-software-device-sim_devicepy) · **Unblocks:** [B-56](#b-56-scenario-rehearsal-on-staging-sc1sc7), [B-59](#b-59-golden-recording-and-demo-runbook)

**Files and directories**

* `backend/app/services/replay_service.py`
* `backend/app/api/v1/replays.py` (E20–E22)
* `shared/fixtures/replays/{demo-golden,turbidity-spike,gradual-ph,sensor-fault,network-gap,tlh-loop}.jsonl`
* `backend/tests/integration/test_replay.py`

**Done when.** The first fixtures are written by `sim_device.py --out`; replays go through the same ingest pipeline with `source = simulated_replay`; takeover blocks the live device with 409 and releases the station at the end; `tlh-loop` drives `HWW-TLH-001`; the same alerts open at speed 1 and speed 5.

**Proven by.** T-B-14, AC-08

#### B-37: Admin endpoints and data maintenance

**Labels:** `track:A` `phase:4` `area:backend` `tier:core`  
**Estimate:** 0.5 person-days · **Planned:** W5 (Tue, from Tue 22 Dec) · **Milestone:** M4  
**Depends on:** [B-32](#b-32-sign-in-sessions-and-role-checks), [B-27](#b-27-rule-engine-six-rules-alert-opening-and-clearing) · **Unblocks:** none

**Files and directories**

* `backend/app/api/v1/admin.py` (E28–E30)
* `backend/app/services/maintenance.py`
* `backend/tests/integration/test_admin.py`

**Done when.** Rule edits are schema-validated; key rotation invalidates the old key at once; demo reset needs `{"confirm": "RESET"}` and `DEMO_MODE=true`; the retention purge runs daily.

**Proven by.** T-S-04

### Phase 5: Frontend development

#### B-38: Status primitives, formatting and evidence helpers

**Labels:** `track:B` `phase:5` `area:frontend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W2 (Thu–Fri, from Thu 3 Dec) · **Milestone:** M1  
**Depends on:** [B-05](#b-05-registry-code-generation-and-consistency-check) · **Unblocks:** [B-40](#b-40-page-1-monitoring-overview), [B-41](#b-41-3d-status-binding-and-sensor-detail-panel), [B-43](#b-43-page-3-dashboard-cards-and-history-charts), [B-45](#b-45-page-4-alert-list-and-alert-detail-read-only), [B-47](#b-47-page-5-simulation-demonstration)

**Files and directories**

* `frontend/src/domain/{statusVisuals,format,evidence}.ts`
* `frontend/src/components/status/{StatusBadge,FreshnessLabel,EvidenceClassBadge,SourceBadge}.tsx`
* `frontend/src/index.css` (status tokens)

**Done when.** Colour, icon and text come only from `status_visuals.json`; `formatValue` and `formatTime` (ICT) are the only formatters; fault and offline render "—" with the last valid value as secondary text.

**Proven by.** T-F-01, T-F-03, T-F-04, T-A-02

#### B-39: Station-state hooks and connection indicator

**Labels:** `track:B` `phase:5` `area:frontend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W3 (Mon–Tue, from Mon 7 Dec) · **Milestone:** M2  
**Depends on:** [B-35](#b-35-openapi-types-and-api-client), [B-06](#b-06-payload-and-snapshot-contracts-with-fixtures) · **Unblocks:** [B-40](#b-40-page-1-monitoring-overview), [B-41](#b-41-3d-status-binding-and-sensor-detail-panel), [B-43](#b-43-page-3-dashboard-cards-and-history-charts), [B-55](#b-55-sse-nudge)

**Files and directories**

* `frontend/src/api/hooks.ts`
* `frontend/src/components/layout/ConnectionIndicator.tsx`

**Done when.** `useStationState`, `useSensorState`, `useStationStates`, `useHistory` (tail merge) and `useConnection` behave as in [05 §5.7](05-synchronisation.md#57-frontend-state); older versions are ignored; polling every 2 s.

**Proven by.** T-F-02, T-F-06

#### B-40: Page 1: Monitoring Overview

**Labels:** `track:B` `phase:5` `area:frontend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W3 (Wed–Thu, from Wed 9 Dec) · **Milestone:** M2  
**Depends on:** [B-38](#b-38-status-primitives-formatting-and-evidence-helpers), [B-39](#b-39-station-state-hooks-and-connection-indicator) · **Unblocks:** [B-49](#b-49-accessibility-pass)

**Files and directories**

* `frontend/src/features/overview/{OverviewPage,StationMap,StationMarker,StationListPanel,RecentAlertsPanel}.tsx`

**Done when.** Three stations with status markers (NHU shows `unavailable`), "Illustrative location" labels, recent alerts, and a list view that works without the map.

**Proven by.** T-E-01

#### B-41: 3D status binding and sensor detail panel

**Labels:** `track:B` `phase:5` `area:3d` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W3 (Thu–Fri, from Thu 10 Dec) · **Milestone:** M2  
**Depends on:** [B-14](#b-14-3d-selection-hover-and-sensor-list), [B-38](#b-38-status-primitives-formatting-and-evidence-helpers), [B-39](#b-39-station-state-hooks-and-connection-indicator) · **Unblocks:** [B-42](#b-42-2d-schematic-fallback), [B-49](#b-49-accessibility-pass), [B-53](#b-53-cross-view-consistency-e2e), [B-54](#b-54-latency-measurement-and-report), [B-61](#b-61-exploded-view-and-labels-toggle)

**Files and directories**

* `frontend/src/features/model/{StationModel,SensorDetailPanel}.tsx`

**Done when.** Node materials, beacon and LED meshes follow the snapshot statuses through `status_visuals.json`; pulses run only on a new `measured_at`; the detail panel shows value, unit, time, status, source and the active alert.

**Proven by.** T-F-07

#### B-42: 2D schematic fallback

**Labels:** `track:B` `phase:5` `area:3d` `tier:core`  
**Estimate:** 0.75 person-days · **Planned:** W5 (Mon, from Mon 21 Dec) · **Milestone:** M4  
**Depends on:** [B-41](#b-41-3d-status-binding-and-sensor-detail-panel) · **Unblocks:** [B-49](#b-49-accessibility-pass)

**Files and directories**

* `frontend/src/features/model/StationSchematic2D.tsx`

**Done when.** With WebGL disabled, or after a canvas error, the page shows the 2D schematic with a real `<button>` per sensor and the same snapshot data; a "2D view" toggle selects it too.

**Proven by.** T-F-08, T-E-08, AC-10

#### B-43: Page 3: dashboard cards and history charts

**Labels:** `track:B` `phase:5` `area:frontend` `tier:mvd`  
**Estimate:** 1.5 person-days · **Planned:** W4 (Mon–Tue, from Mon 14 Dec) · **Milestone:** M3  
**Depends on:** [B-38](#b-38-status-primitives-formatting-and-evidence-helpers), [B-39](#b-39-station-state-hooks-and-connection-indicator), [B-31](#b-31-history-timeline-and-link-apis) · **Unblocks:** [B-44](#b-44-event-timeline-and-availability), [B-49](#b-49-accessibility-pass), [B-53](#b-53-cross-view-consistency-e2e)

**Files and directories**

* `frontend/src/features/dashboard/{DashboardPage,SensorCard,SensorChart,TimeRangePicker}.tsx`

**Done when.** Four cards from the snapshot; charts for 15 min, 1 h, 6 h and 24 h with abnormal periods shaded from the timeline; lines break at gaps; the tail point appears with the card update.

**Proven by.** T-E-02, T-F-06

#### B-44: Event timeline and availability

**Labels:** `track:B` `phase:5` `area:frontend` `tier:core`  
**Estimate:** 0.5 person-days · **Planned:** W5 (Mon–Tue, from Mon 21 Dec) · **Milestone:** M4  
**Depends on:** [B-43](#b-43-page-3-dashboard-cards-and-history-charts), [B-31](#b-31-history-timeline-and-link-apis) · **Unblocks:** none

**Files and directories**

* `frontend/src/features/dashboard/EventTimeline.tsx`

**Done when.** Status changes, alerts, sessions and gaps are listed in ICT; availability % is shown for the selected range.

**Proven by.** T-E-02

#### B-45: Page 4: alert list and alert detail (read only)

**Labels:** `track:B` `phase:5` `area:frontend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W4 (Tue–Wed, from Tue 15 Dec) · **Milestone:** M3  
**Depends on:** [B-30](#b-30-alerts-and-rules-read-api), [B-38](#b-38-status-primitives-formatting-and-evidence-helpers) · **Unblocks:** [B-46](#b-46-sign-in-role-gates-and-review-ui), [B-48](#b-48-in-app-notifications), [B-49](#b-49-accessibility-pass)

**Files and directories**

* `frontend/src/features/alerts/{AlertsPage,AlertList,AlertFilters,AlertDetailPage}.tsx`

**Done when.** Filters live in the URL; every alert shows severity, category, the evidence class "Simulated anomaly", "Preliminary", opened and cleared times and the rule's basis text; anonymous users see no notes.

**Proven by.** T-E-05 (read part)

#### B-46: Sign-in, role gates and review UI

**Labels:** `track:B` `phase:5` `area:frontend` `tier:core`  
**Estimate:** 1 person-day · **Planned:** W5 (Wed–Thu, from Wed 23 Dec) · **Milestone:** M4  
**Depends on:** [B-33](#b-33-alert-actions-and-incident-review-api), [B-45](#b-45-page-4-alert-list-and-alert-detail-read-only), [B-32](#b-32-sign-in-sessions-and-role-checks) · **Unblocks:** [B-48](#b-48-in-app-notifications), [B-49](#b-49-accessibility-pass)

**Files and directories**

* `frontend/src/features/auth/{LoginPage.tsx,useAuth.ts,RequireRole.tsx}`
* `frontend/src/features/alerts/{ReviewForm,ReviewHistory}.tsx`

**Done when.** Operators can acknowledge and add notes; reviewers can group alerts, choose an allowed outcome and submit; disallowed outcomes are not offered; the history shows every event.

**Proven by.** T-E-05, AC-13

#### B-47: Page 5: Simulation Demonstration

**Labels:** `track:B` `phase:5` `area:frontend` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W4 (Wed–Thu, from Wed 16 Dec) · **Milestone:** M3  
**Depends on:** [B-31](#b-31-history-timeline-and-link-apis), [B-38](#b-38-status-primitives-formatting-and-evidence-helpers) · **Unblocks:** [B-49](#b-49-accessibility-pass), [B-56](#b-56-scenario-rehearsal-on-staging-sc1sc7)

**Files and directories**

* `frontend/src/features/simulation/{SimulationPage,PipelineDiagram,LinkStatusPanel,PayloadInspector,ScenarioGuide,ReplayControls}.tsx`

**Done when.** The Wokwi project opens in a new tab from `wokwi_project_url`; the link-status states follow [06 §6.4.5](06-ui-ux.md#645-page-5-simulation-demonstration-simulation); the payload inspector shows the last accepted batch; replay controls appear for operators and call E20–E22 once B-36 is merged.

**Proven by.** T-E-04

#### B-48: In-app notifications

**Labels:** `track:A` `phase:5` `area:frontend` `tier:core`  
**Estimate:** 0.5 person-days · **Planned:** W6 (Mon, from Mon 28 Dec) · **Milestone:** M5  
**Depends on:** [B-45](#b-45-page-4-alert-list-and-alert-detail-read-only), [B-46](#b-46-sign-in-role-gates-and-review-ui) · **Unblocks:** none

**Files and directories**

* `frontend/src/components/layout/AlertToaster.tsx`
* `frontend/src/components/layout/NavBar.tsx` (bell)

**Done when.** New alerts raise a toast and a bell count for signed-in staff, and the tab title shows the open count; no sound; reduced motion is respected.

**Proven by.** T-E-05

#### B-49: Accessibility pass

**Labels:** `track:B` `phase:5` `area:frontend` `tier:core`  
**Estimate:** 0.75 person-days · **Planned:** W6 (Mon–Tue, from Mon 28 Dec) · **Milestone:** M5  
**Depends on:** [B-40](#b-40-page-1-monitoring-overview), [B-41](#b-41-3d-status-binding-and-sensor-detail-panel), [B-42](#b-42-2d-schematic-fallback), [B-43](#b-43-page-3-dashboard-cards-and-history-charts), [B-45](#b-45-page-4-alert-list-and-alert-detail-read-only), [B-46](#b-46-sign-in-role-gates-and-review-ui), [B-47](#b-47-page-5-simulation-demonstration) · **Unblocks:** [B-50](#b-50-vietnamese-copy-and-native-speaker-review)

**Files and directories**

* `frontend/e2e/a11y.spec.ts`
* `docs/reports/accessibility.md`

**Done when.** axe finds no serious or critical issue on any route; journey J6 works with the keyboard only; one NVDA pass is recorded.

**Proven by.** T-A-01, T-A-03, T-A-04, AC-14

#### B-50: Vietnamese copy and native-speaker review

**Labels:** `track:B` `phase:5` `area:frontend` `tier:plus`  
**Estimate:** 0.5 person-days · **Planned:** W6 (Tue, from Tue 29 Dec) · **Milestone:** M5  
**Depends on:** [B-49](#b-49-accessibility-pass) · **Unblocks:** none

**Files and directories**

* `frontend/src/locales/vi.json`
* `docs/reports/vi-review.md`

**Done when.** Every key has a Vietnamese string checked by a native speaker; numbers and dates follow `vi-VN`; the locale parity check passes.

**Proven by.** T-F-09

### Phase 6: End-to-end synchronisation

#### B-51: Live Wokwi → staging end to end

**Labels:** `track:A` `phase:6` `area:testing` `tier:mvd`  
**Estimate:** 0.75 person-days · **Planned:** W3 (Thu–Fri, from Thu 10 Dec) · **Milestone:** M2  
**Depends on:** [B-21](#b-21-uplink-task-batching-https-post-and-ack-handling), [B-28](#b-28-state-service-event-bus-and-snapshot-api), [B-08](#b-08-choose-the-host-and-deploy-the-skeleton-to-staging) · **Unblocks:** [B-54](#b-54-latency-measurement-and-report), [B-56](#b-56-scenario-rehearsal-on-staging-sc1sc7)

**Files and directories**

* `docs/reports/e2e-live.md`
* `firmware/wokwi-web/` (published Wokwi project)

**Done when.** The public Wokwi project posts to staging for 10 minutes with all four channels every 2 s; the Overview and Model pages show the live values; `WOKWI_PROJECT_URL` is set.

**Proven by.** AC-02

#### B-52: Device lamps mirror the server status

**Labels:** `track:A` `phase:6` `area:wokwi` `tier:mvd`  
**Estimate:** 0.25 person-days · **Planned:** W4 (Fri, from Fri 18 Dec) · **Milestone:** M3  
**Depends on:** [B-21](#b-21-uplink-task-batching-https-post-and-ack-handling), [B-28](#b-28-state-service-event-bus-and-snapshot-api) · **Unblocks:** none

**Files and directories**

* `firmware/src/display.cpp`
* `firmware/src/uplink.cpp`
* `firmware/test/test_display/test_main.cpp`

**Done when.** The green, yellow and red LEDs and the beacon follow the ack's `station_status` as in [04 §4.5.4](04-wokwi-integration.md#454-local-indicators-mirror-the-server); the firmware contains no thresholds.

**Proven by.** T-W-05, AC-03

#### B-53: Cross-view consistency E2E

**Labels:** `track:B` `phase:6` `area:testing` `tier:mvd`  
**Estimate:** 1 person-day · **Planned:** W4 (Thu–Fri, from Thu 17 Dec) · **Milestone:** M3  
**Depends on:** [B-41](#b-41-3d-status-binding-and-sensor-detail-panel), [B-43](#b-43-page-3-dashboard-cards-and-history-charts), [B-22](#b-22-software-device-sim_devicepy), [B-27](#b-27-rule-engine-six-rules-alert-opening-and-clearing), [B-29](#b-29-freshness-monitor-and-offline-detection) · **Unblocks:** [B-57](#b-57-e2e-suite-in-ci)

**Files and directories**

* `frontend/e2e/consistency.spec.ts`
* `frontend/e2e/offline.spec.ts`
* `frontend/playwright.config.ts`

**Done when.** With `sim_device.py` driving the spike, fault and outage scenarios, the cards, the 3D model (`__hww3d`), the map marker and the detail panel show the same `version` and statuses at every step.

**Proven by.** T-E-03, T-E-06, AC-06

#### B-54: Latency measurement and report

**Labels:** `track:A` `phase:6` `area:testing` `tier:core`  
**Estimate:** 0.5 person-days · **Planned:** W5 (Tue, from Tue 22 Dec) · **Milestone:** M4  
**Depends on:** [B-51](#b-51-live-wokwi--staging-end-to-end), [B-41](#b-41-3d-status-binding-and-sensor-detail-panel) · **Unblocks:** none

**Files and directories**

* `tools/measure_latency.py`
* `docs/reports/latency.md`

**Done when.** The p95 of (render time − `measured_at`) over 10 minutes is reported for Wokwi and for `sim_device.py`, plus the slider-to-red time for SC3a.

**Proven by.** AC-01, AC-03

#### B-55: SSE nudge

**Labels:** `track:A` `phase:6` `area:backend` `tier:plus`  
**Estimate:** 1 person-day · **Planned:** W5 (Wed, from Wed 23 Dec) · **Milestone:** M4  
**Depends on:** [B-28](#b-28-state-service-event-bus-and-snapshot-api), [B-39](#b-39-station-state-hooks-and-connection-indicator) · **Unblocks:** none

**Files and directories**

* `backend/app/api/v1/stream.py`
* `frontend/src/api/useStationStream.ts`
* `backend/tests/integration/test_stream.py`

**Done when.** Events are published only after commit and carry no values; 15 s heartbeat; the client refetches on `state_changed`, polls every 15 s while the stream is open, and goes back to 2 s if it closes.

**Proven by.** T-B-19

#### B-56: Scenario rehearsal on staging (SC1–SC7)

**Labels:** `track:AB` `phase:6` `area:testing` `tier:core`  
**Estimate:** 0.25 person-days each (joint session) · **Planned:** W5 (Thu, from Thu 24 Dec) · **Milestone:** M4  
**Depends on:** [B-51](#b-51-live-wokwi--staging-end-to-end), [B-36](#b-36-replay-service-and-replay-api), [B-47](#b-47-page-5-simulation-demonstration) · **Unblocks:** [B-59](#b-59-golden-recording-and-demo-runbook), [B-63](#b-63-wokwi-ci-scenario-tests)

**Files and directories**

* `docs/reports/wokwi-scenarios.md`

**Done when.** Each scenario in [04 §4.6](04-wokwi-integration.md#46-demonstration-scenarios) is run on staging in one joint session (each developer drives half the scenarios while the other watches the UI), with expected and observed results and screenshots.

**Proven by.** T-W-06, AC-02 … AC-05, AC-12

### Phase 7: Testing and deployment

#### B-57: E2E suite in CI

**Labels:** `track:B` `phase:7` `area:testing` `tier:core`  
**Estimate:** 0.5 person-days · **Planned:** W6 (Mon, from Mon 28 Dec) · **Milestone:** M5  
**Depends on:** [B-53](#b-53-cross-view-consistency-e2e), [B-22](#b-22-software-device-sim_devicepy) · **Unblocks:** [B-58](#b-58-production-deployment-and-operations), [B-60](#b-60-final-acceptance-run-and-release)

**Files and directories**

* `frontend/e2e/{overview,model,dashboard,alerts,simulation,fallback,banner}.spec.ts`
* .github/workflows/ci.yml (job `e2e`)

**Done when.** The `e2e` job starts PostgreSQL, the API and `sim_device.py`, runs every spec headless, and is green five runs in a row.

**Proven by.** T-E-01 … T-E-09

#### B-58: Production deployment and operations

**Labels:** `track:A` `phase:7` `area:deploy` `tier:core`  
**Estimate:** 0.75 person-days · **Planned:** W6 (Tue, from Tue 29 Dec) · **Milestone:** M5  
**Depends on:** [B-08](#b-08-choose-the-host-and-deploy-the-skeleton-to-staging), [B-57](#b-57-e2e-suite-in-ci) · **Unblocks:** [B-60](#b-60-final-acceptance-run-and-release)

**Files and directories**

* `.github/workflows/deploy.yml` (on tag)
* `docs/demo/runbook.md` (operations part)

**Done when.** A `v*` tag builds the image, runs migrations and deploys; rollback to the previous image takes under 5 minutes; database backups are on; the post-demo key rotation is written down.

**Proven by.** T-D-01, T-D-02

#### B-59: Golden recording and demo runbook

**Labels:** `track:A` `phase:7` `area:deploy` `tier:core`  
**Estimate:** 0.75 person-days · **Planned:** W6 (Mon–Tue, from Mon 28 Dec) · **Milestone:** M5  
**Depends on:** [B-34](#b-34-sessions-api-and-session-export), [B-36](#b-36-replay-service-and-replay-api), [B-56](#b-56-scenario-rehearsal-on-staging-sc1sc7) · **Unblocks:** [B-60](#b-60-final-acceptance-run-and-release)

**Files and directories**

* `shared/fixtures/replays/demo-golden.jsonl`
* `docs/demo/runbook.md`
* `docs/demo/script.md`

**Done when.** `demo-golden.jsonl` is re-recorded with `record_session.py` from a live Wokwi session on the final firmware (it replaces the `sim_device.py` version used at M3); the runbook in [10 §10.5](10-testing-demo-deploy.md#105-demonstration-runbook) is rehearsed twice, once with the replay fallback.

**Proven by.** AC-08

#### B-60: Final acceptance run and release

**Labels:** `track:AB` `phase:7` `area:testing` `tier:core`  
**Estimate:** 0.5 person-days each (joint session) · **Planned:** W6 (Wed, from Wed 30 Dec) · **Milestone:** M5  
**Depends on:** [B-57](#b-57-e2e-suite-in-ci), [B-58](#b-58-production-deployment-and-operations), [B-59](#b-59-golden-recording-and-demo-runbook) · **Unblocks:** none

**Files and directories**

* `docs/reports/acceptance.md`
* git tag `v1.0-demo`

**Done when.** AC-01 … AC-14 pass on the production URL and the evidence is recorded; `v1.0-demo` is tagged; device keys are rotated after the demo.

**Proven by.** AC-01 … AC-14

## 11.6 Stretch issues

Start these only after M4, only if the owner's track has no open core issue, and never during the code freeze after M5. They have no milestone.

#### B-61: Exploded view and labels toggle

**Labels:** `track:B` `phase:5` `area:3d` `tier:stretch`  
**Estimate:** 0.75 person-days · **Planned:** after M4, only if the owner's track is done · **Milestone:** —  
**Depends on:** [B-41](#b-41-3d-status-binding-and-sensor-detail-panel) · **Unblocks:** none

**Files and directories**

* `frontend/src/features/model/{ModelControls,StationModel}.tsx`

**Done when.** Animated exploded view and labels toggle, reachable by keyboard, switched off under reduced motion.

**Proven by.** T-F-05

#### B-62: Wokwi custom chip `hww-probe`

**Labels:** `track:A` `phase:3` `area:wokwi` `tier:stretch`  
**Estimate:** 1.5 person-days · **Planned:** after M4, only if the owner's track is done · **Milestone:** —  
**Depends on:** [B-20](#b-20-sampling-scenarios-and-local-display) · **Unblocks:** none

**Files and directories**

* `firmware/chips/hww-probe.chip.json`
* `firmware/chips/hww-probe.chip.c`

**Done when.** Labelled pH/DO/NTU `range` controls drive `pin_dac_write`; works on wokwi.com; the slide potentiometers stay as the fallback.

**Proven by.** T-W-06

#### B-63: Wokwi CI scenario tests

**Labels:** `track:A` `phase:7` `area:testing` `tier:stretch`  
**Estimate:** 1 person-day · **Planned:** after M4, only if the owner's track is done · **Milestone:** —  
**Depends on:** [B-56](#b-56-scenario-rehearsal-on-staging-sc1sc7) · **Unblocks:** none

**Files and directories**

* `.github/workflows/wokwi.yml`
* `firmware/test/scenarios/*.yaml`

**Done when.** `wokwi-cli` runs SC1 and SC4 headless and checks the serial log. Needs a paid plan with CI minutes.

**Proven by.** T-W-06

## 11.7 Import script

Save this as `tools/import_backlog.py` (issue B-01). It reads the `#### B-nn:` blocks above and creates one GitHub issue per block with the `gh` command-line tool, then rewrites each issue body so that dependencies point to GitHub issue numbers.

```bash
# from the repository root, after `gh auth login` and the commands in §11.2
python tools/import_backlog.py --dry-run
python tools/import_backlog.py --assign-a <github-login-track-a> --assign-b <github-login-track-b>
```

Running it twice creates every issue twice. If a run stops part-way, the numbers created so far are in `tools/issue_map.json`: run again with `--resume`, which skips the issues already in that file.

```python
#!/usr/bin/env python3
"""Create GitHub issues from docs/blueprint/11-github-backlog.md (see 11 §11.7)."""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DOC = Path("docs/blueprint/11-github-backlog.md")
MAP = Path("tools/issue_map.json")
# One block: "#### B-nn: Title" up to the next heading of level 1-4 or the end of the file.
BLOCK = re.compile(r"^#### (B-\d\d): (.+?)\n(.*?)(?=^#{1,4} |\Z)", re.M | re.S)
LABELS_LINE = re.compile(r"^\*\*Labels:\*\* (.+?)\s*$", re.M)
MILESTONE = re.compile(r"\*\*Milestone:\*\* (\S+)")
ISSUE_LINK = re.compile(r"\[(B-\d\d)\]\(#[^)]*\)")
RELATIVE_LINK = re.compile(r"\]\((?!https?://)([^)\s]+)\)")


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], check=True, capture_output=True,
                            text=True, encoding="utf-8")
    return result.stdout.strip()


def parse(include_stretch: bool) -> list[dict]:
    text = DOC.read_text(encoding="utf-8")
    issues = []
    for key, title, body in BLOCK.findall(text):
        labels = re.findall(r"`([^`]+)`", LABELS_LINE.search(body).group(1))
        if "tier:stretch" in labels and not include_stretch:
            continue
        milestone = MILESTONE.search(body).group(1)
        body = LABELS_LINE.sub("", body, count=1).strip()
        issues.append({"key": key, "title": f"{key}: {title}", "labels": labels,
                       "milestone": None if milestone == "—" else milestone,
                       "body": body})
    return issues


def render(body: str, numbers: dict, base: str) -> str:
    # Dependencies: "#12" once the issue exists; until then the link to the
    # blueprint anchor stays and is made absolute below.
    def issue(m):
        n = numbers.get(m.group(1))
        return f"#{n}" if n else m.group(0)
    body = ISSUE_LINK.sub(issue, body)

    # Links to other blueprint files and anchors must work from the issue page.
    def absolute(m):
        target = m.group(1)
        if target.startswith("#"):
            target = DOC.name + target
        return f"]({base}/{target})"
    body = RELATIVE_LINK.sub(absolute, body)
    return body + f"\n\n---\nFrom [{DOC.name}]({base}/{DOC.name}). Edit the blueprint, not only this issue."


def write_temp(text: str) -> str:
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


def assignees(labels: list, a: str | None, b: str | None) -> list:
    who = {"track:A": [a], "track:B": [b], "track:AB": [a, b]}
    return [x for t in labels if t in who for x in who[t] if x]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # titles contain "→" and "–"
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="print what would be created")
    p.add_argument("--include-stretch", action="store_true", help="also create B-61 to B-63")
    p.add_argument("--assign-a", help="GitHub login of the Track A owner")
    p.add_argument("--assign-b", help="GitHub login of the Track B owner")
    p.add_argument("--resume", action="store_true", help=f"skip issues already in {MAP}")
    args = p.parse_args()

    issues = parse(args.include_stretch)
    if args.dry_run:
        for i in issues:
            print(f"{i['title']}\n  labels: {', '.join(i['labels'])}\n"
                  f"  milestone: {i['milestone'] or 'none'}\n"
                  f"  assignees: {', '.join(assignees(i['labels'], args.assign_a, args.assign_b)) or 'none'}")
        print(f"{len(issues)} issues")
        return

    repo = gh("repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner")
    base = f"https://github.com/{repo}/blob/main/docs/blueprint"
    numbers = json.loads(MAP.read_text()) if args.resume and MAP.exists() else {}

    # Pass 1: create the issues; dependencies still point to the blueprint.
    for i in issues:
        if i["key"] in numbers:
            continue
        cmd = ["issue", "create", "--title", i["title"],
               "--body-file", write_temp(render(i["body"], {}, base))]
        for label in i["labels"]:
            cmd += ["--label", label]
        if i["milestone"]:
            cmd += ["--milestone", i["milestone"]]
        for login in assignees(i["labels"], args.assign_a, args.assign_b):
            cmd += ["--assignee", login]
        url = gh(*cmd)
        numbers[i["key"]] = int(url.rstrip("/").rsplit("/", 1)[1])
        MAP.write_text(json.dumps(numbers, indent=2))
        print(f"{i['key']} -> #{numbers[i['key']]}")

    # Pass 2: rewrite every body so that "Depends on" and "Unblocks" use issue numbers.
    for i in issues:
        gh("issue", "edit", str(numbers[i["key"]]),
           "--body-file", write_temp(render(i["body"], numbers, base)))
    print(f"Done: {len(issues)} issues. Map saved to {MAP}.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(f"gh failed: {' '.join(e.cmd)}\n{e.stderr}")
```

After the import, add every issue to the GitHub Projects board described in [09 §9.11](09-team-and-timeline.md#911-working-rhythm) (the board's "auto-add" workflow can do this for new issues in the repository).
