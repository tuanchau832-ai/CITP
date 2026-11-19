# Source document review

Reviewed 18 November 2026 before implementation:

- All 12 Markdown files in `docs/blueprint/`, including the complete 63-issue backlog and import script.
- Root README, MIT licence, and `GITHUB_TEAM_WORKFLOW.md`.
- `../Assignment 2/Assignment 2.docx`, including references and AI declaration.
- `../Assignment 2/Assessment Task 2. rubric-7.docx`.
- Both PDF files: the assignment template (2 pages) and checklist (1 page).

The assignment materials concern individual background research into domestic wastewater. They supply context, not a source of live sensor measurements. The implementation follows the final-assignment blueprint for product requirements and does not present the report's historical claims as current monitoring data.

The user authorised direct blueprint implementation and routine choices. They will upload the station model. The model and any hosted Wokwi project are external inputs; their availability and live performance must be recorded separately from local software tests.

## Resolved specification details

- Blueprint 07's cookie session and CSRF contract governs user authentication, refining 01's earlier bearer-token summary.
- Blueprint 04/07's ingest response is HTTP 200, refining roadmap 08's stray 201 reference.
- Blueprint 04's newest-plus-oldest buffered upload governs firmware transport, refining earlier oldest-only summaries.
- Python 3.12 is the container target. Local verification uses the available Python 3.10 interpreter with compatible source syntax.
- PostgreSQL 16 is the deploy database. SQLite permits local development when Docker Desktop is unavailable; PostgreSQL-specific checks are tracked separately.
