import { display } from "../../utils/presentation";
import type { JsonObject } from "../../api/types";
import { EmptyState, Metadata } from "../ui/Primitives";
export function HistoricalAnalogueView({
  analogues,
}: {
  analogues: JsonObject[];
}) {
  if (!analogues.length)
    return (
      <EmptyState
        compact
        title="No historical analogues returned"
        description="The engine has not supplied matching events for this query."
      />
    );
  return (
    <div className="analogue-list">
      {analogues.map((a, i) => (
        <details key={String(a.event_id || i)} className="analogue">
          <summary>
            <div>
              <strong>{display(a.event_id)}</strong>
              <small className="mono">{display(a.date || a.timestamp)}</small>
            </div>
            <span className="mono accent">
              Similarity {display(a.similarity_score ?? a.match_score)}
            </span>
          </summary>
          <Metadata data={a} />
        </details>
      ))}
    </div>
  );
}
