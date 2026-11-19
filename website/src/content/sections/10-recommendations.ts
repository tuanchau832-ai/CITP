import type { ReportSection } from '../types';

export default {
  title: "Recommendations",
  label: "Recommendations",
  summary: "Turn the report’s findings and limitations into decisions and practical next steps for the client or community.",
  topics: [
    {
      id: "recommendation",
      title: "Recommended next decision",
      pending: "Add the team’s evidence-backed recommendation and explain how it follows from the criteria, prototype evaluation, costs, and stakeholder concerns.",
    },
    {
      id: "validation",
      title: "Validation and next steps",
      pending: "Set out sequencing, proposed owners, and prerequisites. Label enhancements and milestones as proposed and link to evidence or known gaps.",
    },
  ],
} satisfies ReportSection;
