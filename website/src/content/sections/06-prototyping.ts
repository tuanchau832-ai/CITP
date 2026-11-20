import type { ReportSection } from '../types';

export default {
  title: "Prototyping",
  label: "Prototyping",
  summary: "Describe what the prototype demonstrates, how it was evaluated, and what evidence is still needed for a physical deployment.",
  topics: [
    {
      id: "prototype-scope",
      title: "Prototype and simulation",
      pending: "Describe the tested prototype scope, configuration, and demonstration scenario.",
      stationDemo: {
        id: "station-demo",
        caption: "Figure 4. Virtual sensor station: ESP32 simulator page linked to the 3D station page.",
        simulatorPath: "/simulator",
        stationPath: "/station",
        note: "Evidence type: simulation. Readings come from the simulator and are not field measurements. The two pages are linked: while linked, the 3D station uses the simulator's readings and limits.",
      },
      figure: {
        id: "prototype-figure",
        caption: "Figure 3. Simulator or prototype demonstration",
        pending: "Add a labelled simulator or 3D prototype screenshot, provide context and alt text, and identify the evidence type.",
      },
    },
    {
      id: "prototype-evaluation",
      title: "Evaluation and iteration",
      pending: "Explain the method, test conditions, observed limitations, and design changes. Identify simulated values and any actual measured results explicitly.",
      table: {
        id: "prototype-results",
        caption: "Table 3. Prototype evaluation record",
        columns: ["Test", "Criterion", "Test conditions", "Evidence type", "Observed result", "Limitations / changes"],
        rows: [],
        pending: "Add only documented test results and label planned tests as future work.",
      },
    },
  ],
} satisfies ReportSection;
