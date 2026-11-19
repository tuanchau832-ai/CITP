# Contributing to the CITP report

Follow the repository’s [Git and pull request workflow](../GITHUB_TEAM_WORKFLOW.md). Work on the assigned feature branch, stage only the files for that change, open or update a PR targeting `main`, and ask the team lead to review before merging. Keep local environment files and credentials out of commits.

1. Agree on the section and reviewer with the team lead. Edit your section in [src/content/sections](src/content/sections), or update [references](src/content/references.ts) or [supporting documents](src/content/appendices.ts).
2. Keep the assigned section and topic IDs stable so citation and evidence links keep working. Replace `pending` instructions with verified copy in `paragraphs`, sourced figures, or reviewed table rows. Keep unfinished items labelled.
3. Add approved images under `public/images/`. Record their source, date, permission, evidence type and alt text in [figures.csv](content/figures.csv). Track the evidence for claims in [evidence-register.csv](content/evidence-register.csv).
4. Give each APA reference a stable ID in `references.ts`. Use that same reference in paragraph `citations` and figure `source` fields so the rendered text links to the bibliography. Coordinate edits to references and shared components with the team lead.
5. Link approved supporting files in the topic’s `documents` array. For example, a file at `public/documents/reverse-brief.pdf` can use `/documents/reverse-brief.pdf` as its `url`.
6. Run the build and route checks and preview your page on desktop and mobile. In the PR, list the sections changed, sources checked, open draft fields, and the verification performed. Record actual contributions in the group declaration when confirmed.

## Suggested PR order

1. Merge the shared report shell, route map and contributor documentation.
2. Assign separate PRs for context and criteria, options and design, prototype and implementation, and costs and recommendations. Coordinate shared references and evidence records during review.
3. Have the team lead review citations, figures, AI records, contribution declarations, word count, deployment, and the confirmed application link.
