import type { ReportSection } from './types';

export default {
  title: "Supporting documents",
  label: "Supporting documents",
  summary: "Find the project records, supporting evidence, AI documentation, and group declaration that accompany the report.",
  topics: [
    {
      id: "brief-and-evidence",
      title: "Reverse brief and evidence records",
      pending: "Add the agreed reverse brief and approved supporting material, including criteria rationale, options scoring, test evidence, and dated price records. Remove personal details that are not approved for release.",
    },
    {
      id: "ai-declaration",
      title: "AI use or non-use declaration",
      pending: "Add the team’s actual declaration. Record what was used, where, why, and how the team checked the output.",
    },
    {
      id: "prompt-log",
      title: "Prompts, outputs, and screenshots",
      table: {
        id: "ai-prompt-log",
        caption: "Table 5. AI prompt and output register",
        columns: ["Date", "Tool / model", "Purpose and section", "Prompt", "Output or screenshot", "Verification / edits"],
        rows: [],
        pending: "Document actual prompts and outputs or record confirmed non-use as required.",
      },
    },
    {
      id: "group-declaration",
      title: "Group contribution declaration",
      table: {
        id: "contributions",
        caption: "Table 6. Group contribution declaration",
        columns: ["Team member", "Actual contribution", "Supporting evidence", "Confirmation"],
        rows: [],
        pending: "Record actual contributions and obtain team confirmation before submission.",
      },
    },
  ],
} satisfies ReportSection;
