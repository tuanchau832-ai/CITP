import type { ReportSection } from '../types';

export default {
  title: "Implementation",
  label: "Implementation",
  summary: "Describe how the proposal could move from reviewed prototype to pilot and ongoing operation.",
  topics: [
    {
      id: "rollout",
      title: "Pilot and rollout",
      pending: "Define the proposed site selection, permissions, installation, commissioning, milestones, dependencies, and acceptance checks. Identify future milestones as planned.",
    },
    {
      id: "responsibilities",
      title: "Operations and responsibilities",
      pending: "Record proposed owners for monitoring, calibration, maintenance, access, incident response, and handover. Identify agreements that need confirmation.",
    },
    {
      id: "risks",
      title: "Risks and contingencies",
      pending: "Add installation and operational risks with mitigation, fallback processes, and review owners.",
    },
  ],
} satisfies ReportSection;
