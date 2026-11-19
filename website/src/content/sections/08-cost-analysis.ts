import type { ReportSection } from '../types';

export default {
  title: "Cost analysis",
  label: "Cost analysis",
  summary: "Explain the expected lifecycle costs and who would pay. Record assumptions and cite dated price evidence.",
  topics: [
    {
      id: "cost-scope",
      title: "Costing scope and assumptions",
      pending: "Confirm the currency, costing date, analysis period, scale, taxes, and what the estimates cover.",
    },
    {
      id: "lifecycle-cost",
      title: "Lifecycle cost schedule",
      table: {
        id: "cost-schedule",
        caption: "Table 4. Lifecycle costs and funding responsibility",
        columns: ["Item", "Unit", "Quantity", "Unit cost", "CAPEX / OPEX", "Frequency", "Subtotal", "Source and date", "Payer", "Maintenance / end-of-life"],
        rows: [],
        pending: "Add sourced costs for acquisition, deployment, operation, maintenance, replacement, and end-of-life. Include totals over the agreed period.",
      },
    },
    {
      id: "funding",
      title: "Affordability and uncertainty",
      pending: "Explain likely funding responsibilities, key uncertainties, and the assumptions most likely to change the totals.",
    },
  ],
} satisfies ReportSection;
