import { useAnalysisStore } from "../state/analysisStore";
import { apiClient } from "../api/client";
import {
  PageHeader,
  Panel,
  EmptyState,
  ErrorState,
  Loading,
  Metadata,
  Status,
  Badge,
  RawDetails,
} from "../components/ui/Primitives";
import { RefreshCw } from "lucide-react";
export function Operations({
  view,
}: {
  view: "models" | "status" | "sources" | "settings";
}) {
  const {
    systemStatus: health,
    models,
    healthError,
    modelsError,
    refreshSystem,
    checkingHealth,
    researchHistory,
    report,
  } = useAnalysisStore();
  const titles = {
    models: "Model performance",
    status: "System status",
    sources: "Data sources",
    settings: "Settings",
  };
  const descriptions = {
    models:
      "Artifact availability and reported registry metadata. Evaluation remains explicit.",
    status:
      "Connectivity, dependencies, and the operating state reported by the engine.",
    sources:
      "Source references and provider information supplied by research runs.",
    settings: "Inspect application configuration and supported capabilities.",
  };
  const providers = [
    ...new Set([
      ...researchHistory.flatMap((r) => r.providers_used),
      ...(report?.live_research_report?.providers_used || []),
    ]),
  ];
  return (
    <>
      <PageHeader
        title={titles[view]}
        description={descriptions[view]}
        eyebrow={`Operations / ${titles[view]}`}
        action={
          <button
            className="button secondary"
            onClick={() => void refreshSystem()}
            disabled={checkingHealth}
          >
            <RefreshCw size={15} className={checkingHealth ? "spin" : ""} />
            {checkingHealth ? "Checking…" : "Refresh"}
          </button>
        }
      />
      {view === "models" && (
        <>
          {modelsError && (
            <ErrorState
              message={modelsError}
              retry={() => void refreshSystem()}
            />
          )}
          <Panel title="Model registry" aside={<Badge>API metadata</Badge>}>
            {checkingHealth && !models ? (
              <Loading />
            ) : models ? (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Artifact</th>
                      <th>Reported version</th>
                      <th>Availability</th>
                      <th>Checkpoint timestamp</th>
                      <th>Evaluation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(models)
                      .filter(([k]) => k.endsWith("_version"))
                      .map(([key, version]) => {
                        const name = key.replace("_version", "");
                        return (
                          <tr key={key}>
                            <td>{name}</td>
                            <td className="mono">
                              {String(version) || "Unavailable"}
                            </td>
                            <td>
                              <Status value={health?.dependencies[name]} />
                            </td>
                            <td className="mono">
                              {models.checkpoint_timestamps?.[name] ||
                                "Not reported"}
                            </td>
                            <td className="muted">Not reported</td>
                          </tr>
                        );
                      })}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState
                compact
                title="Registry unavailable"
                description="Connect the API to retrieve artifact versions and checkpoint metadata."
              />
            )}
          </Panel>
          <div className="notice">
            The registry does not return training completion, evaluation
            metrics, or calibration validation. An artifact version alone cannot
            establish that a model is trained or evaluated.
          </div>
        </>
      )}
      {view === "status" && (
        <>
          {healthError && (
            <ErrorState
              message={healthError}
              retry={() => void refreshSystem()}
            />
          )}
          <div className="two-column">
            <Panel title="API connectivity">
              {health ? (
                <>
                  <Status value={health.status} />
                  <Metadata
                    data={{
                      api_version: health.api_version,
                      models_loaded: health.models_loaded,
                      execution_mode: health.execution_mode,
                      temporal_mode: health.temporal_mode,
                    }}
                  />
                  <p className="notice">
                    Execution mode is a server-reported classification. It is
                    not independent verification of model quality.
                  </p>
                </>
              ) : (
                <EmptyState
                  compact
                  title="API unavailable"
                  description="No readiness response has been received."
                />
              )}
            </Panel>
            <Panel title="Dependency readiness">
              {health ? (
                <div className="dependency-list">
                  {Object.entries(health.dependencies).map(([key, value]) => (
                    <div key={key}>
                      <span>{key.replace(/_/g, " ")}</span>
                      <Status value={value} />
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  compact
                  title="Readiness unknown"
                  description="Dependency states are unavailable while disconnected."
                />
              )}
            </Panel>
          </div>
          <Panel title="Research providers">
            <EmptyState
              compact
              title="Provider health is not exposed"
              description="Provider usage may appear in research reports; live configuration and provider health are not returned by the readiness endpoint."
            />
          </Panel>
          {health && (
            <Panel title="Readiness response">
              <RawDetails data={health} />
            </Panel>
          )}
        </>
      )}
      {view === "sources" && (
        <>
          <Panel title="Configured source registry">
            <EmptyState
              title="Source registry unavailable"
              description="The current API has no configured-source registry endpoint. Operational states and source schedules cannot be inspected here."
            />
          </Panel>
          <Panel title="Providers reported in this session">
            {providers.length ? (
              <div className="provider-list">
                {providers.map((p) => (
                  <div key={p}>
                    <strong>{p}</strong>
                    <span className="muted">
                      Used in a returned research report · Health not reported
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                compact
                title="No providers reported yet"
                description="Provider names appear after research returns a report."
              />
            )}
          </Panel>
        </>
      )}
      {view === "settings" && (
        <>
          <Panel title="Application configuration">
            <Metadata
              data={{
                api_connection: apiClient.baseUrl,
                temporal_mode: health?.temporal_mode,
                execution_mode: health?.execution_mode,
              }}
            />
            <p className="notice">
              API connection is set through VITE_API_URL at build time. The
              local development proxy uses port 8000.
            </p>
          </Panel>
          <Panel title="Server settings">
            <EmptyState
              compact
              title="Configuration editing unavailable"
              description="The backend exposes no settings read/write endpoint. No save operation is offered. Secret keys are never requested or displayed."
            />
          </Panel>
          <Panel title="Frontend session">
            <p className="muted">
              Analysis and research history exist only in memory and are cleared
              when the page reloads. The frontend does not assume an
              authenticated user.
            </p>
          </Panel>
        </>
      )}
    </>
  );
}
