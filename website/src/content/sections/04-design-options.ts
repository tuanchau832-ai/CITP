import type { ReportSection } from '../types';

export default {
  title: "Design options and selection",
  label: "Design options and selection",
  summary: "Present three comparable options and show how the design criteria informed the selection.",
  topics: [
    {
      id: "water-watch-option",
      title: "Hanoi Water Watch",
      pending: "Describe the concept, users, operating assumptions, strengths, and limitations using verified design records.",
    },
    {
      id: "citizen-reports",
      title: "Citizen reports",
      pending: "Describe how reports would be submitted and reviewed. Document accessibility, participation, and verification trade-offs.",
    },
    {
      id: "digital-twin",
      title: "AI-driven digital twin",
      pending: "Describe the concept, data needs, operating constraints, and feasibility. Cite evidence for the comparison.",
    },
    {
      id: "design-selection",
      title: "Selection rationale",
      pending: "Record the selected option, trade-offs, scoring rationale, and whether the choice changes under plausible alternative weights.",
      matrix: {
        id: "decision-matrix",
        caption: "Table 2. Weighted design decision matrix",
        options: ["Hanoi Water Watch", "Citizen reports", "AI-driven digital twin"],
        criteria: [],
        explanation: "Use a consistent scoring scale and record its anchors. Each weighted total is the sum of the scores multiplied by their criterion weights as fractions of 100%.",
        pending: "Add approved criteria, weights that total 100%, and evidence-backed scores for each option.",
      },
    },
  ],
} satisfies ReportSection;
