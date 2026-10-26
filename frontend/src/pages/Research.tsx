import { useState } from "react";
import { useAnalysisStore } from "../state/analysisStore";
import { InputPanel } from "../components/input/InputPanel";
import { ResearchPanel } from "../components/research/ResearchPanel";
import { IntelligenceReportView } from "../components/report/IntelligenceReportView";
import { PageHeader, Panel } from "../components/ui/Primitives";
import type { ResearchReport } from "../api/types";
export function Research() {
  const { researchHistory, report } = useAnalysisStore();
  const [selected, setSelected] = useState<ResearchReport | null>(null);
  const research =
    selected || researchHistory[0] || report?.live_research_report;
  return (
    <>
      <PageHeader
        title="Live research"
        eyebrow="Research / Provider workspace"
        description="Investigate event context with the configured research engine."
      />
      <div className="notice">
        Standalone research depends on the server's event extractor and provider
        configuration. A server failure is shown as returned; no results are
        substituted.
      </div>
      <InputPanel
        researchOnly
        onComplete={(r) => {
          if (r) setSelected(r);
        }}
      />
      {researchHistory.length > 0 && (
        <div className="table-toolbar">
          <label htmlFor="research-run">Session query history</label>
          <select
            id="research-run"
            value={research?.run_id}
            onChange={(e) =>
              setSelected(
                researchHistory.find((r) => r.run_id === e.target.value) ||
                  null,
              )
            }
          >
            {researchHistory.map((r) => (
              <option key={r.run_id} value={r.run_id}>
                {r.run_id} · {r.status}
              </option>
            ))}
          </select>
        </div>
      )}
      {research?.intelligence_report && (
        <IntelligenceReportView
          report={research.intelligence_report}
          dossier={research.dossier}
          cutoff={research.dossier?.research_cutoff}
        />
      )}
      <Panel title="Raw research audit & evidence graph">
        <ResearchPanel research={research} />
      </Panel>
    </>
  );
}
