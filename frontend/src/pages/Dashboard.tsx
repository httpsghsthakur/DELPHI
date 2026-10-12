import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Plus, RefreshCw, Search } from "lucide-react";
import { useAnalysisStore } from "../state/analysisStore";
import {
  Badge,
  EmptyState,
  ErrorState,
  PageHeader,
  Panel,
  Status,
} from "../components/ui/Primitives";
export function Dashboard() {
  const {
    history,
    systemStatus,
    healthError,
    checkingHealth,
    refreshSystem,
    selectReport,
    researchHistory,
  } = useAnalysisStore();
  const navigate = useNavigate();
  const dependencies = Object.entries(systemStatus?.dependencies || {});
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
      <div className="overview-status">
        <div>
          <Status value={healthError ? "Disconnected" : systemStatus?.status} />
          <span className="status-caption">
            {systemStatus
              ? `${systemStatus.execution_mode} execution · ${systemStatus.temporal_mode} temporal mode`
              : "Waiting for a connection to the DELPHI engine"}
          </span>
        </div>
        <button
          className="button ghost small"
          onClick={() => void refreshSystem()}
          disabled={checkingHealth}
        >
          <RefreshCw size={13} className={checkingHealth ? "spin" : ""} />
          {checkingHealth ? "Checking" : "Refresh status"}
        </button>
      </div>
      {healthError && (
        <ErrorState message={healthError} retry={() => void refreshSystem()} />
      )}
      <div className="overview-grid">
        <div className="overview-primary">
          <Panel
            title="Recent analyses"
            aside={<Badge>Current session</Badge>}
            className="recent-panel"
          >
            {!history.length ? (
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
                <Link to="/status" className="text-link">
                  Check model availability
                  <ArrowRight size={14} />
                </Link>
              </div>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Event context</th>
                      <th>Domain</th>
                      <th>Received</th>
                      <th>Execution</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((h, i) => (
                      <tr key={i}>
                        <td>
                          <button
                            className="row-link"
                            onClick={() => {
                              selectReport(h);
                              navigate("/analysis/results");
                            }}
                          >
                            {h.request.text.slice(0, 100)}
                            {h.request.text.length > 100 ? "…" : ""}
                          </button>
                        </td>
                        <td>{h.request.domain}</td>
                        <td className="mono">
                          {new Date(h.receivedAt).toLocaleTimeString()}
                        </td>
                        <td>
                          <Badge
                            tone={h.executionMode === "REAL" ? "" : "warning"}
                          >
                            {h.executionMode}
                          </Badge>
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
              title="Research activity"
              aside={
                <Link to="/research" className="text-link">
                  Open
                  <ArrowRight size={13} />
                </Link>
              }
            >
              {researchHistory.length ? (
                researchHistory.slice(0, 4).map((r) => (
                  <div className="activity-row" key={r.run_id}>
                    <span className="mono">{r.run_id}</span>
                    <Status value={r.status} />
                  </div>
                ))
              ) : (
                <EmptyState
                  compact
                  title="No research runs yet"
                  description="Queries and provider activity appear after research completes."
                />
              )}
            </Panel>
            <Panel
              title="Historical retrieval"
              aside={
                <Link to="/historical" className="text-link">
                  Search
                  <ArrowRight size={13} />
                </Link>
              }
            >
              <EmptyState
                compact
                title="Historical search is limited"
                description="The current search endpoint returns an empty placeholder. Analysis analogues are available within returned reports."
              />
            </Panel>
          </div>
          <Panel title="Recent forecast runs">
            <div className="table-scroll">
              {history.length ? (
                <table>
                  <thead>
                    <tr>
                      <th>Received in session</th>
                      <th>Scenarios returned</th>
                      <th>Calibration</th>
                      <th>Inspect</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map((h, i) => (
                      <tr key={i}>
                        <td className="mono">{h.receivedAt}</td>
                        <td>{h.report.scenarios.length}</td>
                        <td>{h.report.calibration_status}</td>
                        <td>
                          <button
                            className="button secondary small"
                            onClick={() => {
                              selectReport(h);
                              navigate("/scenarios");
                            }}
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="quiet-empty">
                  No forecast responses received in this session.
                </div>
              )}
            </div>
          </Panel>
          <p className="session-note">
            History is held in this browser session only. The API does not
            expose a persisted analysis-history endpoint.
          </p>
        </div>
        <aside className="overview-secondary">
          <Panel
            title="Engine readiness"
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
                Readiness has not been reported by the API.
              </div>
            )}
            <div className="panel-note">
              Availability indicates loaded artifacts, not trained or evaluated
              model quality.
            </div>
          </Panel>
          <Panel title="Data-source health">
            <p className="muted">
              No source registry or provider-health endpoint is exposed.
            </p>
            <Link to="/sources" className="text-link">
              View available source information
              <ArrowRight size={13} />
            </Link>
          </Panel>
          <div className="workspace-note">
            <div className="eyebrow">Research standard</div>
            <h3>Evidence and provenance.</h3>
            <p>
              Returned evidence and provenance remain accessible alongside model
              outputs. Missing data stays visible.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}
