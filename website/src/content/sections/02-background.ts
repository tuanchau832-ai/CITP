import type { ReportSection } from '../types';

export default {
  title: "Background",
  label: "Background",
  summary: "Explain why the project matters in Hanoi and whose needs informed the brief. Cite local evidence and attribute stakeholder input.",
  topics: [
    {
      id: "local-context",
      title: "Hanoi context",
      pending: "Identify relevant waterways and sites. Describe the challenge and existing monitoring or reporting approaches using verified local sources.",
    },
    {
      id: "stakeholders",
      title: "Stakeholders and community needs",
      pending: "Record who was consulted and how. Describe priorities, effects, and unresolved questions. Distinguish consultation findings from assumptions.",
    },
    {
      id: "context-map",
      title: "Site and community context",
      figure: {
        id: "figure-site-context",
        caption: "Figure 1. Site and community context",
        pending: "Add a sourced map or photograph with a date, permission, and descriptive alternative text.",
      },
    },
  ],
} satisfies ReportSection;
