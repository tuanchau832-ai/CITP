import type { ReportSection } from '../types';

export default {
  title: "Other considerations",
  label: "Other considerations",
  summary: "Explain how the proposal addresses community concerns and environmental, ethical, and operational impacts.",
  topics: [
    {
      id: "community-impact",
      title: "Community impact and access",
      pending: "Document concerns raised and proposed responses. Consider language, accessible reporting, and who may be excluded or affected.",
    },
    {
      id: "environment",
      title: "Environmental and practical impacts",
      pending: "Add evidence on siting, durability, lifecycle waste, and avoidable disruption. Confirm applicable approvals.",
    },
    {
      id: "privacy-governance",
      title: "Privacy, safety, and governance",
      pending: "Describe data ownership and access, alert responsibility, and risk of misinterpretation. Record responsibilities that still need agreement.",
    },
  ],
} satisfies ReportSection;
