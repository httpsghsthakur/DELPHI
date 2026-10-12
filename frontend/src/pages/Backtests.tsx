import { useEffect, useState, type FormEvent } from "react";
import { FlaskConical, RefreshCw } from "lucide-react";
import { apiClient } from "../api/client";
import type { BacktestRunResponse } from "../api/types";
import {
  Badge,
  CopyButton,
  EmptyState,
  ErrorState,
  Metadata,
  PageHeader,
  Panel,
  RawDetails,
  Status,
} from "../components/ui/Primitives";
export function Backtests() {
  const [domain, setDomain] = useState("geopolitics"),
    [days, setDays] = useState(7),
    [run, setRun] = useState<BacktestRunResponse | null>(null);
  const [runId, setRunId] = useState(""),
    [loading, setLoading] = useState(false),
    [error, setError] = useState<string | null>(null),
    [acknowledged, setAcknowledged] = useState(false);
  const active = run && ["QUEUED", "RUNNING"].includes(run.status);
  useEffect(() => {
    if (!active || !run) return;
    let cancelled = false;
    const id = window.setTimeout(async () => {
      try {
        const next = await apiClient.getBacktest(run.run_id);
        if (!cancelled) setRun(next);
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Status check failed");
      }
    }, 2500);
    return () => {
      cancelled = true;
      window.clearTimeout(id);
    };
  }, [active, run]);
  async function start(e: FormEvent) {
    e.preventDefault();
    if (!domain.trim() || !Number.isInteger(days) || days < 1) {
      setError("Enter a domain and a positive integer window.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.startBacktest({
        domain: domain.trim(),
        window_days: days,
      });
      setRun(result);
      setRunId(result.run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Backtest submission failed");
    } finally {
      setLoading(false);
    }
  }
  async function inspect(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setRun(await apiClient.getBacktest(runId.trim()));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Run not found");
    } finally {
      setLoading(false);
    }
  }
  return (
    <>
      <PageHeader
        title="Backtests"
        eyebrow="Operations / Evaluation"
        description="Submit supported runs and inspect their returned execution status."
      />
      <div className="notice warning">
        <strong>Simulation only.</strong> The backend backtest task currently
        sleeps and returns a fixed accuracy value. Its metrics are simulated
        placeholders, not an evaluation of DELPHI.
      </div>
      <div className="two-column">
        <Panel title="Start a simulation run">
          <form onSubmit={start}>
            <div className="field-grid">
              <div>
                <label htmlFor="backtest-domain">Domain</label>
                <input
                  id="backtest-domain"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                  disabled={loading}
                />
              </div>
              <div>
                <label htmlFor="backtest-window">Window (days)</label>
                <input
                  id="backtest-window"
                  type="number"
                  min="1"
                  value={days}
                  onChange={(e) => setDays(Number(e.target.value))}
                  disabled={loading}
                />
              </div>
            </div>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={acknowledged}
                onChange={(e) => setAcknowledged(e.target.checked)}
              />
              I understand this run produces simulated metrics.
            </label>
            <button
              className="button primary"
              disabled={loading || !acknowledged || !!active}
            >
              <FlaskConical size={15} />
              {loading ? "Submitting…" : "Start Simulation Run"}
            </button>
          </form>
        </Panel>
        <Panel title="Inspect an existing run">
          <form onSubmit={inspect}>
            <label htmlFor="backtest-id">Run identifier</label>
            <input
              id="backtest-id"
              value={runId}
              onChange={(e) => setRunId(e.target.value)}
              placeholder="Paste a returned run ID"
            />
            <div className="form-action">
              <button
                className="button secondary"
                disabled={loading || !runId.trim()}
              >
                <RefreshCw size={15} />
                Fetch status
              </button>
            </div>
          </form>
        </Panel>
      </div>
      {error && <ErrorState message={error} />}
      <Panel
        title="Execution status"
        aside={<Badge tone="warning">Simulation</Badge>}
      >
        {run ? (
          <>
            <div className="section-intro">
              <Status value={run.status} />
              <CopyButton value={run.run_id} />
            </div>
            <Metadata
              data={{
                run_id: run.run_id,
                created_at: run.created_at,
                completed_at: run.completed_at,
              }}
            />
            {active && (
              <p className="notice">
                Polling the actual server status. No completion is simulated in
                this frontend.
              </p>
            )}
            {run.metrics && (
              <>
                <h3 className="subheading">Returned simulated metrics</h3>
                <Metadata data={run.metrics} />
              </>
            )}
            <RawDetails data={run} title="Full backtest response" />
          </>
        ) : (
          <EmptyState
            compact
            title="No backtest run selected"
            description="Submit a simulation or fetch an existing run by its returned ID."
          />
        )}
      </Panel>
    </>
  );
}
