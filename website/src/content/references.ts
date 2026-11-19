import type { Reference, ReportSection } from './types';

export const references: readonly Reference[] = [];

export default {
  title: "References",
  label: "References",
  summary: "Find the sources used for the report’s claims, figures, specifications, and prices.",
  topics: [
    {
      id: "bibliography",
      title: "APA reference list",
      pending: "Add complete, verified APA entries in reference order and link each in-text citation to its entry.",
      bibliography: references,
    },
    {
      id: "source-checks",
      title: "Figure, data, and price sources",
      pending: "Check that each figure or adapted asset, dataset, cost estimate, and substantive claim has a corresponding source, date, and credit where applicable.",
    },
  ],
} satisfies ReportSection;
