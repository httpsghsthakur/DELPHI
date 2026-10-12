import { ExecutionNotice } from "../components/report/ExecutionNotice";
import { parseGraph } from "../utils/graph";
import { researchEvidence } from "../utils/evidence";
import { Link } from "react-router-dom";
import { useAnalysisStore } from "../state/analysisStore";
import { PageHeader, Panel } from "../components/ui/Primitives";
import { CausalGraph } from "../components/report/CausalGraph";
import { ScenarioDistribution } from "../charts/ScenarioDistribution";
import { IndicatorsPanel } from "../components/indicators/IndicatorsPanel";
import { EvidencePanel } from "../components/evidence/EvidencePanel";
export function Intelligence({
  view,
}: {
  view: "graph" | "scenarios" | "indicators" | "evidence";
}) {
  const { report, researchHistory } = useAnalysisStore();
  const titles = {
    graph: "Causal graph",
    scenarios: "Scenario forecasts",
    indicators: "Indicators",
    evidence: "Sources & evidence",
  };
  const descriptions = {
    graph:
      "Inspect explicit relationships, mechanisms, and evidence when returned.",
    scenarios:
      "Inspect model-generated trajectories and their reported weights.",
    indicators: "Review the indicator identifiers returned by the engine.",
    evidence:
      "Review source attribution, direction, and available verification metadata.",
  };
  return (
    <>
      <PageHeader
        title={titles[view]}
        description={descriptions[view]}
        eyebrow={`Intelligence / ${titles[view]}`}
        action={
          <Link className="button secondary" to="/analysis/new">
            New Analysis
          </Link>
        }
      />
      {report && <ExecutionNotice />}
      <p className="scope-note">
        {view === "evidence"
          ? "Scope: selected analysis and standalone research in this session."
          : report
            ? "Scope: currently selected analysis."
            : "No analysis selected. Run an analysis to populate this workspace."}
      </p>
      <Panel title={titles[view]}>
        {view === "graph" && (
          <CausalGraph
            graph={report ? parseGraph(report.current_event) : null}
          />
        )}{" "}
        {view === "scenarios" && (
          <ScenarioDistribution
            scenarios={report?.scenarios || []}
            report={report}
          />
        )}{" "}
        {view === "indicators" && (
          <IndicatorsPanel indicators={report?.indicators || []} />
        )}{" "}
        {view === "evidence" && (
          <EvidencePanel
            evidence={[
              ...(report?.evidence || []),
              ...researchEvidence(report?.live_research_report),
              ...researchHistory.flatMap(researchEvidence),
            ]}
          />
        )}
      </Panel>
    </>
  );
}
