# CITP Task 3 project introduction and design report

This React, TypeScript and Vite site is the draft introduction and report for Hanoi Water Watch. It is a static, client-side application and can be built and hosted independently from the [HanoiWaterWatch application](../HanoiWaterWatch/README.md).

## Run locally

Use Node.js 22.12 or later. Run these commands from the Git repository root.

```sh
cd website
npm ci
npm run dev
```

Open the URL printed by Vite. Run the checks before previewing the production build.

```sh
npm run check:links
npm run build
npm run preview
```

## Report requirements

The route map in [architecture.md](../docs/website/architecture.md) follows the narrative and section list in the [restructure brief](../WEBSITE_RESTRUCTURE_PROMPT.md). The Task 3 rubric, website template, report skeleton, and agreed reverse brief were unavailable in this checkout. Confirm the scaffold against those originals when they are available.

- **Content and stakeholder consideration (50%)** covers sourced Hanoi context and stakeholder needs, measurable criteria, three options and a documented selection, detailed design and prototype evidence, implementation, lifecycle costs, community considerations, and recommendations.
- **Website design and audience engagement (30%)** covers responsive and keyboard-accessible navigation, a clear reading sequence, plain English, and numbered, captioned figures and tables.
- **Referencing, citations and prompts (20%)** covers APA in-text citations and bibliography, source credits for figures and prices, an AI use or non-use declaration, and the supporting prompts, outputs, and screenshots.

Keep the report within **4,000 words**, excluding only ancillary material permitted by the official template. Record each section’s final copy count and check the combined count against the template before submission. The draft placeholders and helper guidance are outside the final copy.

## Deploy the report separately

In Vercel, import the GitHub repository as a project with Root Directory **`website`** and the Vite preset. Use Node.js 22.12+ (or a supported newer release), install with `npm ci`, build with `npm run build`, and publish `dist`. [vercel.json](vercel.json) sends direct report URLs and browser refreshes to the React Router entrypoint. The other application can use its own project and domain, with `HanoiWaterWatch/` as its build context and its existing container and database setup. [Vercel Vite deployment](https://vercel.com/docs/frameworks/frontend/vite)

Set the public `VITE_HANOI_WATER_WATCH_URL` in Vercel to the verified HTTPS application URL and redeploy. For local development, copy [.env.example](.env.example) to `.env.local` and set the same variable. Development also accepts HTTP loopback addresses for testing against a locally running application. Vite embeds the value at build time. With no valid URL, the launch control displays **Application link pending**.

**Submission platform approval required.** The restructure brief records a Google Sites requirement in the assignment template. Confirm approval for a Vercel submission with teaching staff before using it for assessment.

See the [team handoff](TEAM_README.md), [release checklist](../docs/website/release-checklist.md), and [verification checklist](tests/checklist.md).
