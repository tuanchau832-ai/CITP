import type { ReportSection } from '../types';

export default {
  title: "Hanoi Water Watch",
  label: "Overview",
  summary: "Introduce the project to the client and community in plain English. Confirm the project details and describe what readers will learn from the report.",
  topics: [
    {
      id: "project-details",
      title: "Project details",
      pending: "Add the confirmed client or partner, team name, team members, subject, and submission details.",
    },
    {
      id: "project-summary",
      title: "Project at a glance",
      pending: "Summarise the agreed challenge, intended audience, project scope, and proposed response. Confirm the wording against the reverse brief.",
    },
    {
      id: "reading-guide",
      title: "How to read this report",
      paragraphs: [
        {
          text: "Start with the Hanoi context and stakeholder needs, then follow how the criteria inform the design choice, prototype, costs and recommendations.",
        },
      ],
    },
  ],
} satisfies ReportSection;
