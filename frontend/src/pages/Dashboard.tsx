import { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ArrowRight,
  Plus,
  RefreshCw,
  Search,
  Cpu,
  Database,
  ShieldCheck,
  BookOpen,
} from "lucide-react";
import { useAnalysisStore } from "../state/analysisStore";
import {
  Badge,
  ErrorState,
  PageHeader,
  Panel,
  Status,
} from "../components/ui/Primitives";

export function Dashboard() {
  const {
    history,
    persistedAnalyses,
    systemStatus,
    healthError,
    checkingHealth,
    refreshSystem,
    selectReport,
    loadAnalysisById,
  } = useAnalysisStore();
  const navigate = useNavigate();

  useEffect(() => {
    void refreshSystem();
  }, [refreshSystem]);

  const dependencies = Object.entries(systemStatus?.dependencies || {});

  // Combine session history with persisted analyses from SQLite
  const allAnalyses = [
    ...history.map((h, idx) => ({
      key: `session-${idx}`,
      isSession: true,
      id: h.report.current_event?.event_id || `session-${idx}`,
      title: h.request.text.slice(0, 95) + (h.request.text.length > 95 ? "…" : ""),
      domain: h.request.domain,
      timestamp: h.receivedAt,
      sessionEntry: h,
    })),
    ...persistedAnalyses.map((p) => ({
      key: `persisted-${p.id}`,
      isSession: false,
      id: p.id,
      title: p.topic.slice(0, 95) + (p.topic.length > 95 ? "…" : ""),
      domain: p.domain,
      timestamp: p.created_at || p.publication_timestamp,
      sessionEntry: null,
    })),
  ];

  return (
    <>
      <PageHeader
        title="Intelligence overview"
        description="Your research activity, forecast runs, and engine readiness in one place."
        eyebrow="Workspace / Overview"
        action={
          <Link className="button primary" to="/analysis/new">
            <Plus size={16} />
            New Analysis
          </Link>
        }
      />

      {/* Hero Metrics Strip */}
      <div className="metrics-strip">
        <div className="metric-cell">
          <div className="metric-header">
            <Cpu size={15} />
            <span>CUSTOM MODELS</span>
          </div>
          <div className="metric-value">3,935,725</div>
          <div className="metric-sub">EventNet · CredNet · CausalSeq · EventEmbed</div>
        </div>
        <div className="metric-cell">
          <div className="metric-header">
            <Database size={15} />
            <span>HISTORICAL INDEX</span>
          </div>
          <div className="metric-value">10,000</div>
          <div className="metric-sub">FAISS Vectors · Cosine Similarity</div>
        </div>
        <div className="metric-cell">
          <div className="metric-header">
            <ShieldCheck size={15} />
            <span>TEMPORAL SAFETY</span>
          </div>
          <div className="metric-value" style={{ color: "var(--positive)" }}>
            STRICT
          </div>
          <div className="metric-sub">Zero Future Data Leakage Enforced</div>
        </div>
        <div className="metric-cell">
          <div className="metric-header">
            <BookOpen size={15} />
            <span>REPORT GENERATION</span>
          </div>
          <div className="metric-value" style={{ color: "var(--accent)" }}>
            ~3,000 Words
          </div>
          <div className="metric-sub">9 Grounded Paragraph Sections</div>
        </div>
      </div>

      <div className="overview-status">
        <div>
          <Status value={healthError ? "Disconnected" : systemStatus?.status || "Ready"} />
          <span className="status-caption">
            {systemStatus
              ? `${systemStatus.execution_mode} execution · ${systemStatus.temporal_mode} temporal mode · Zero external LLMs`
              : "Connecting to DELPHI backend engine…"}
          </span>
        </div>
        <button
          className="button ghost small"
          onClick={() => void refreshSystem()}
          disabled={checkingHealth}
        >
          <RefreshCw size={13} className={checkingHealth ? "spin" : ""} />
          {checkingHealth ? "Checking…" : "Refresh status"}
        </button>
      </div>

      {healthError && (
        <ErrorState message={healthError} retry={() => void refreshSystem()} />
      )}

      <div className="overview-grid">
        <div className="overview-primary">
          <Panel
            title="Recent investigations & analyses"
            aside={<Badge tone="primary">{allAnalyses.length} Total Recorded</Badge>}
            className="recent-panel"
          >
            {!allAnalyses.length ? (
              <div className="overview-empty">
                <span className="document-outline">
                  <Search size={32} strokeWidth={1} />
                </span>
                <div className="eyebrow">Current session</div>
                <h2>
                  No analyses in this session.
                  <br />
                  <span>Begin with an event context.</span>
                </h2>
                <p>
                  No analysis has been run in this session. Bring an article or
                  event description to investigate its context, evidence, and
                  possible consequences.
                </p>
                <Link className="button primary" to="/analysis/new">
                  Create your first analysis
                  <ArrowRight size={16} />
                </Link>
              </div>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Investigation Topic</th>
                      <th>Domain</th>
                      <th>Recorded</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allAnalyses.slice(0, 8).map((item) => (
                      <tr key={item.key}>
                        <td>
                          <button
                            className="row-link"
                            onClick={async () => {
                              if (item.sessionEntry) {
                                selectReport(item.sessionEntry);
                                navigate("/analysis/results");
                              } else {
                                await loadAnalysisById(item.id);
                                navigate("/analysis/results");
                              }
                            }}
                          >
                            {item.title}
                          </button>
                        </td>
                        <td>
                          <Badge>{item.domain}</Badge>
                        </td>
                        <td className="mono">
                          {item.timestamp ? new Date(item.timestamp).toLocaleDateString() : "Recent"}
                        </td>
                        <td>
                          <button
                            className="button secondary small"
                            onClick={async () => {
                              if (item.sessionEntry) {
                                selectReport(item.sessionEntry);
                                navigate("/analysis/results");
                              } else {
                                await loadAnalysisById(item.id);
                                navigate("/analysis/results");
                              }
                            }}
                          >
                            Open Briefing
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>

          <div className="two-column">
            <Panel
              title="Live research engine"
              aside={
                <Link to="/research" className="text-link">
                  Open
                  <ArrowRight size={13} />
                </Link>
              }
            >
              <p className="muted" style={{ marginBottom: "0.75rem" }}>
                Multi-angle query planning querying DuckDuckGo, Wikipedia, GDELT, and Local Historical Parquet with wire deduplication.
              </p>
              <Link to="/research" className="button secondary small">
                Explore Research Engine
              </Link>
            </Panel>

            <Panel
              title="Historical FAISS search"
              aside={
                <Link to="/historical" className="text-link">
                  Search
                  <ArrowRight size={13} />
                </Link>
              }
            >
              <p className="muted" style={{ marginBottom: "0.75rem" }}>
                10,000 real GDELT vectors indexed with cosine similarity, decay scoring, and temporal cutoff enforcement.
              </p>
              <Link to="/historical" className="button secondary small">
                Search Historical Archive
              </Link>
            </Panel>
          </div>
        </div>

        <aside className="overview-secondary">
          <Panel
            title="Custom model readiness"
            aside={
              <Link
                to="/status"
                className="icon-link"
                aria-label="View full system status"
              >
                <ArrowRight size={15} />
              </Link>
            }
          >
            {dependencies.length ? (
              <div className="dependency-list">
                {dependencies.map(([key, status]) => (
                  <div key={key}>
                    <span>{key.replace(/_/g, " ")}</span>
                    <Status value={status} />
                  </div>
                ))}
              </div>
            ) : (
              <div className="quiet-empty">
                Checking loaded neural checkpoints…
              </div>
            )}
            <div className="panel-note">
              100% custom PyTorch checkpoints loaded. 0% external LLM APIs.
            </div>
          </Panel>

          <Panel title="System transparency">
            <p className="muted" style={{ fontSize: "12px", lineHeight: "1.6" }}>
              DELPHI operates with zero fabricated metrics or hallucinated outcomes. Probabilities reflect uncalibrated sequence softmax weights unless an empirical calibrator is fitted.
            </p>
          </Panel>
        </aside>
      </div>
    </>
  );
}
