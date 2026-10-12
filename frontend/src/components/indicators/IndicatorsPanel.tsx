import { useState } from "react";
import { EmptyState } from "../ui/Primitives";
export function IndicatorsPanel({ indicators }: { indicators: string[] }) {
  const [query, setQuery] = useState("");
  const rows = indicators.filter((i) =>
    i.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <>
      <p className="notice">
        The API returns indicator identifiers only. Values, descriptions, source
        metadata, and historical series are unavailable; no trend can be
        calculated.
      </p>
      <div className="table-toolbar">
        <input
          aria-label="Filter indicators"
          placeholder="Filter indicator identifiers…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </div>
      {rows.length ? (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Indicator identifier</th>
                <th>Value</th>
                <th>Source / timestamp</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((id) => (
                <tr key={id}>
                  <td className="mono">{id}</td>
                  <td className="muted">Not returned</td>
                  <td className="muted">Not returned</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState
          compact
          title={
            indicators.length
              ? "No matching indicators"
              : "No indicators returned"
          }
          description="Indicators will be listed when supplied by an analysis."
        />
      )}
    </>
  );
}
