# Report verification checklist

- Install with `npm ci`, then run `npm run check:links` and `npm run build`.
- Preview with `npm run preview`. Open a nested section directly and refresh it. Repeat on the Vercel preview deployment after publishing it.
- On desktop, check the active contents link and previous and next links. On a narrow viewport, open the contents menu and verify it closes when a section is selected.
- Use Tab and Enter to exercise the skip link, report contents, next and previous links, and the configured app launch. Confirm that changing pages moves focus to the report and that wide tables can scroll without moving the whole page horizontally.
- Check the CTA with the environment value unset and with the verified application URL set. Ensure the configured destination opens the independent application.
- Confirm all draft sections carry the visible draft status. Review figure alternatives, captions, evidence types, and source links once the corresponding content is supplied.
- From the repository root, run `git status --short -- HanoiWaterWatch` and `git diff HEAD --name-status -- HanoiWaterWatch` to confirm the report edits did not affect the application.
