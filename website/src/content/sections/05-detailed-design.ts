import type { ReportSection } from '../types';

export default {
  title: "Detailed design",
  label: "Detailed design",
  summary: "Explain how the proposed system would work and trace major decisions to the agreed design criteria.",
  topics: [
    {
      id: "architecture",
      title: "System overview and data flow",
      pending: "Describe the station, software, intended users, and how readings would move through the system. Cite verified design specifications.",
      figure: {
        id: "system-diagram",
        caption: "Figure 2. Proposed system and data flow",
        pending: "Add the reviewed diagram and identify implemented prototype elements and proposed elements.",
      },
    },
    {
      id: "readings-alerts",
      title: "Readings, thresholds, and alerts",
      pending: "List reading types, units, and threshold sources. Explain how alerts would be interpreted and acted on. Label simulated inputs and any assumptions.",
    },
    {
      id: "design-tradeoffs",
      title: "Design decisions and limitations",
      pending: "Explain verified component choices, installation constraints, and the design's response to stakeholder criteria.",
    },
  ],
} satisfies ReportSection;
