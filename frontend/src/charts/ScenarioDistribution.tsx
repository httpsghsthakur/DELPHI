import { useCallback, useState } from "react";
import type { APIScenario, ForecastReport } from "../api/types";
import {
  Badge,
  CopyButton,
  Drawer,
  EmptyState,
  Metadata,
  RawDetails,
} from "../components/ui/Primitives";
export function ScenarioDistribution({
  scenarios,
  report,
}: {
  scenarios: APIScenario[];
  report?: ForecastReport | null;
}) {
  const [query, setQuery] = useState(""),
    [selected, setSelected] = useState<APIScenario | null>(null),
    [sort, setSort] = useState("weight");
  const close = useCallback(() => setSelected(null), []);
  const items = scenarios
    .filter((s) =>
      JSON.stringify(s).toLowerCase().includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sort === "weight"
        ? b.normalized_weight - a.normalized_weight
        : a.scenario_id.localeCompare(b.scenario_id),
    );
  return (
    <>
      <div className="notice warning">
        Normalized scenario weights are model outputs, not validated
        probabilities. Calibration status:{" "}
        {report?.calibration_status || "Not reported"}.
      </div>
      <div className="table-toolbar">
        <input
          aria-label="Search scenarios"
          placeholder="Search scenario IDs or trajectories…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          aria-label="Sort scenarios"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="weight">Highest weight</option>
          <option value="id">Scenario ID</option>
        </select>
      </div>
      {!items.length ? (
        <EmptyState
          compact
          title="No scenarios to display"
          description={
            scenarios.length
              ? "No scenario matches your search."
              : "Forecast trajectories will appear when the engine supplies them."
          }
        />
      ) : (
        <div className="scenario-list">
          {items.map((s, i) => (
            <button
              className="scenario-row"
              key={s.scenario_id}
              onClick={() => setSelected(s)}
            >
              <span className="scenario-number mono">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div className="scenario-main">
                <strong>{s.scenario_id}</strong>
                <span>
                  {s.trajectory.length} returned trajectory steps · Raw score{" "}
                  {s.raw_score}
                </span>
                <div className="weight-track">
                  <i
                    style={{
                      width: `${Math.max(0, Math.min(1, s.normalized_weight)) * 100}%`,
                    }}
                  />
                </div>
              </div>
              <div className="scenario-weight mono">
                <strong>{s.normalized_weight.toFixed(3)}</strong>
                <small>normalized weight</small>
              </div>
            </button>
          ))}
        </div>
      )}
      {selected && (
        <Drawer title="Scenario detail" onClose={close}>
          <Badge tone="warning">Model-generated trajectory</Badge>
          <h3>{selected.scenario_id}</h3>
          <CopyButton value={selected.scenario_id} />
          <Metadata
            data={{
              raw_score: selected.raw_score,
              normalized_weight: selected.normalized_weight,
              calibration_status: report?.calibration_status,
            }}
          />
          <h3>Trajectory</h3>
          <div className="timeline">
            {selected.trajectory.map((step, i) => (
              <div className="timeline-step" key={i}>
                <span className="mono">{String(i + 1).padStart(2, "0")}</span>
                <Metadata data={step} />
              </div>
            ))}
          </div>
          <p className="notice">
            Trigger conditions, mechanisms, and validated probabilities are not
            provided by this API.
          </p>
          {report && (
            <RawDetails data={report.provenance} title="Forecast provenance" />
          )}
        </Drawer>
      )}
    </>
  );
}
