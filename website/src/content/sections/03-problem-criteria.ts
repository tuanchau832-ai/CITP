import type { ReportSection } from '../types';

export default {
  title: "Problem and criteria",
  label: "Problem and criteria",
  summary: "Turn the agreed problem into measurable requirements. Explain how each criterion follows from a stakeholder need or a constraint.",
  topics: [
    {
      id: "problem-definition",
      title: "Problem definition and scope",
      pending: "Add the agreed problem statement, affected users, scope boundaries, and assumptions from the reverse brief.",
    },
    {
      id: "measurable-criteria",
      title: "Measurable design criteria",
      table: {
        id: "criteria-table",
        caption: "Table 1. Design criteria and verification",
        columns: ["Criterion", "Stakeholder need / source", "Measure and unit", "Target", "Verification method"],
        rows: [],
        pending: "Add approved criteria, measurable targets, stakeholder rationale, and verification methods.",
      },
    },
  ],
} satisfies ReportSection;
