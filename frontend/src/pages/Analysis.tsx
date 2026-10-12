import { ExecutionNotice } from "../components/report/ExecutionNotice";
import { parseGraph } from "../utils/graph";
import { researchEvidence } from "../utils/evidence";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, ShieldCheck } from "lucide-react";
import { useAnalysisStore } from "../state/analysisStore";
import { InputPanel } from "../components/input/InputPanel";
import {
  PageHeader,
  Panel,
  Badge,
  EmptyState,
} from "../components/ui/Primitives";
import { CurrentEventCard } from "../components/event/CurrentEventCard";
import { CredibilityPanel } from "../components/event/CredibilityPanel";
import { HistoricalAnalogueView } from "../components/historical/HistoricalAnalogueView";
import { EvidencePanel } from "../components/evidence/EvidencePanel";
import { ResearchPanel } from "../components/research/ResearchPanel";
import { ScenarioDistribution } from "../charts/ScenarioDistribution";
import { IndicatorsPanel } from "../components/indicators/IndicatorsPanel";
import { ProvenancePanel } from "../components/provenance/ProvenancePanel";
import { CausalGraph } from "../components/report/CausalGraph";
export function NewAnalysis() {
  const navigate = useNavigate();
  return (
    <>
      <PageHeader
        title="New analysis"
        description="Establish the event. Define the boundaries. Investigate what follows."
        eyebrow="Research / New analysis"
      />
      <div className="composer-layout">
        <InputPanel onComplete={() => navigate("/analysis/results")} />
        <aside className="composer-guide">
          <div className="eyebrow">Before you begin</div>
          <h2>A clear input makes a better investigation.</h2>
          <div className="guide-step">
            <span>01</span>
            <div>
              <h3>Describe the event</h3>
              <p>
                Use the source article or a precise description. Include
                relevant actors and actions.
              </p>
            </div>
          </div>
          <div className="guide-step">
            <span>02</span>
            <div>
              <h3>Set an information boundary</h3>
              <p>
                The cutoff defines what the engine is allowed to know at
                prediction time.
              </p>
            </div>
          </div>
          <div className="guide-step">
            <span>03</span>
            <div>
              <h3>Review the evidence</h3>
              <p>
                Inspect supporting and conflicting signals alongside every
                returned scenario.
              </p>
            </div>
          </div>
          <div className="guide-note">
            <ShieldCheck size={18} />
            <p>
              Missing models and uncalibrated results remain visible. No example
              results are substituted.
            </p>
          </div>
          <Link to="/status" className="text-link">
            Inspect engine readiness
            <ArrowRight size={14} />
          </Link>
        </aside>
      </div>
    </>
  );
}
export function AnalysisResults() {
  const { report, history } = useAnalysisStore(),
    [tab, setTab] = useState("Summary");
  const entry = history.find((h) => h.report === report);
  if (!report)
    return (
      <>
        <PageHeader
          title="Analysis report"
          description="A research document built from the engine response."
        />
        <EmptyState
          title="No analysis selected"
          description="Run an analysis or select a result from the session history."
          action={
            <Link className="button primary" to="/analysis/new">
              New Analysis
              <ArrowRight size={15} />
            </Link>
          }
        />
      </>
    );
  return (
    <>
      <PageHeader
        eyebrow="Research / Analysis report"
        title="Analysis report"
        description={`Information cutoff: ${report.provenance.prediction_cutoff}`}
        action={
          <Link to="/" className="button secondary">
            <ArrowLeft size={15} />
            Overview
          </Link>
        }
      />
      <ExecutionNotice />
      <div className="report-meta">
        <span>
          Received in this session{" "}
          <time className="mono">{entry?.receivedAt || "Not recorded"}</time>
        </span>
        <span>
          Calibration <Badge tone="warning">{report.calibration_status}</Badge>
        </span>
      </div>
      <div className="tabs" role="tablist" aria-label="Report sections">
        {[
          "Summary",
          "Current Event",
          "Credibility",
          "Live Research",
          "Evidence",
          "Historical Analogues",
          "Causal Graph",
          "Scenarios",
          "Indicators",
          "Provenance",
        ].map((t) => (
          <button
            role="tab"
            tabIndex={tab === t ? 0 : -1}
            aria-selected={tab === t}
            onKeyDown={(e) => {
              const names = [
                "Summary",
                "Current Event",
                "Credibility",
                "Live Research",
                "Evidence",
                "Historical Analogues",
                "Causal Graph",
                "Scenarios",
                "Indicators",
                "Provenance",
              ];
              let index = names.indexOf(t);
              if (e.key === "ArrowRight") index = (index + 1) % names.length;
              else if (e.key === "ArrowLeft")
                index = (index + names.length - 1) % names.length;
              else if (e.key === "Home") index = 0;
              else if (e.key === "End") index = names.length - 1;
              else return;
              e.preventDefault();
              setTab(names[index]);
              document
                .getElementById(`tab-${names[index].replace(/ /g, "-")}`)
                ?.focus();
            }}
            aria-controls="report-section"
            id={`tab-${t.replace(/ /g, "-")}`}
            key={t}
            onClick={() => setTab(t)}
            className={tab === t ? "active" : ""}
          >
            {t}
          </button>
        ))}
      </div>
      <div
        id="report-section"
        role="tabpanel"
        aria-labelledby={`tab-${tab.replace(/ /g, "-")}`}
      >
        {tab === "Summary" && (
          <>
            <div className="two-column">
              <Panel title="Current event">
                <CurrentEventCard event={report.current_event} />
              </Panel>
              <Panel title="Credibility assessment">
                <CredibilityPanel credibility={report.credibility_assessment} />
              </Panel>
            </div>
            <Panel
              title="Scenario forecasts"
              aside={
                <Link to="/scenarios" className="text-link">
                  Explore
                  <ArrowRight size={13} />
                </Link>
              }
            >
              <ScenarioDistribution
                scenarios={report.scenarios}
                report={report}
              />
            </Panel>
          </>
        )}
        {tab === "Current Event" && (
          <Panel title="Current event">
            <CurrentEventCard event={report.current_event} />
          </Panel>
        )}
        {tab === "Credibility" && (
          <Panel title="Credibility assessment">
            <CredibilityPanel credibility={report.credibility_assessment} />
          </Panel>
        )}
        {tab === "Live Research" && (
          <Panel title="Live research">
            <ResearchPanel research={report.live_research_report} />
          </Panel>
        )}
        {tab === "Evidence" && (
          <Panel title="Supporting and conflicting evidence">
            <EvidencePanel
              evidence={[
                ...report.evidence,
                ...researchEvidence(report.live_research_report),
              ]}
            />
          </Panel>
        )}
        {tab === "Historical Analogues" && (
          <Panel title="Historical analogues">
            <HistoricalAnalogueView analogues={report.historical_analogues} />
          </Panel>
        )}
        {tab === "Causal Graph" && (
          <Panel title="Causal graph">
            <CausalGraph graph={parseGraph(report.current_event)} />
          </Panel>
        )}
        {tab === "Scenarios" && (
          <Panel title="Scenario forecasts">
            <ScenarioDistribution
              scenarios={report.scenarios}
              report={report}
            />
          </Panel>
        )}
        {tab === "Indicators" && (
          <Panel title="Indicators">
            <IndicatorsPanel indicators={report.indicators} />
          </Panel>
        )}
        {tab === "Provenance" && (
          <Panel title="Analysis provenance">
            <ProvenancePanel provenance={report.provenance} />
          </Panel>
        )}
      </div>
      {report.limitations.length > 0 && (
        <Panel title="Reported limitations">
          <ul className="limitations">
            {report.limitations.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        </Panel>
      )}
    </>
  );
}
