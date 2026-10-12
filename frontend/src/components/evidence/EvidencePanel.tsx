import { uniqueEvidence } from "../../utils/evidence";
import { display } from "../../utils/presentation";
import { useCallback, useState } from "react";
import { ArrowUpDown, Search } from "lucide-react";
import type { JsonObject } from "../../api/types";
import {
  Badge,
  CopyButton,
  Drawer,
  EmptyState,
  Metadata,
  RawDetails,
  SourceLink,
} from "../ui/Primitives";
export function EvidencePanel({ evidence }: { evidence: JsonObject[] }) {
  const [query, setQuery] = useState(""),
    [direction, setDirection] = useState("all"),
    [sort, setSort] = useState(false),
    [selected, setSelected] = useState<JsonObject | null>(null);
  const close = useCallback(() => setSelected(null), []);
  const rows = uniqueEvidence(evidence)
    .filter(
      (e) =>
        (direction === "all" ||
          String(e.direction || e.role).toLowerCase() === direction) &&
        JSON.stringify(e).toLowerCase().includes(query.toLowerCase()),
    )
    .sort((a, b) =>
      sort
        ? String(b.timestamp || "").localeCompare(String(a.timestamp || ""))
        : 0,
    );
  return (
    <>
      <div className="table-toolbar">
        <div className="filter-input">
          <Search size={15} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search claims, sources, or IDs…"
            aria-label="Search evidence"
          />
        </div>
        <select
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
          aria-label="Evidence direction"
        >
          <option value="all">All evidence</option>
          <option value="supporting">Supporting</option>
          <option value="conflicting">Conflicting</option>
          <option value="neutral">Neutral</option>
        </select>
        <span className="result-count">{rows.length} records</span>
      </div>
      {!rows.length ? (
        <EmptyState
          compact
          title={
            evidence.length ? "No matching evidence" : "No evidence returned"
          }
          description={
            evidence.length
              ? "Try another search or direction filter."
              : "Source-attributed evidence will appear here when the engine returns it."
          }
        />
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Evidence / claim</th>
                <th>Source</th>
                <th>Direction</th>
                <th>
                  <button className="table-sort" onClick={() => setSort(!sort)}>
                    Timestamp
                    <ArrowUpDown size={12} />
                  </button>
                </th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((ev, i) => (
                <tr
                  key={String(
                    ev.evidence_id || `${ev.source_id || "source"}-${i}`,
                  )}
                >
                  <td>
                    <span className="cell-title">
                      {display(
                        ev.claim || ev.summary || ev.role || ev.evidence_id,
                      )}
                    </span>
                    <small className="mono">
                      {display(ev.evidence_id || ev.document_id)}
                    </small>
                  </td>
                  <td>
                    <SourceLink
                      url={ev.url || ev.canonical_url}
                      children={display(ev.source || ev.source_id)}
                    />
                  </td>
                  <td>
                    <Badge
                      tone={
                        String(ev.direction).toLowerCase() === "conflicting"
                          ? "warning"
                          : ""
                      }
                    >
                      {display(ev.direction || ev.role)}
                    </Badge>
                  </td>
                  <td className="mono">{display(ev.timestamp)}</td>
                  <td>
                    <button
                      className="button secondary small"
                      onClick={() => setSelected(ev)}
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {selected && (
        <Drawer title="Evidence detail" onClose={close}>
          <Badge>{display(selected.direction || selected.role)}</Badge>
          <h3>
            {display(
              selected.claim ||
                selected.summary ||
                selected.evidence_id ||
                selected.source_id,
            )}
          </h3>
          {selected.excerpt && (
            <blockquote>{display(selected.excerpt)}</blockquote>
          )}
          <SourceLink url={selected.url || selected.canonical_url} />
          {typeof selected.evidence_id === "string" && (
            <CopyButton value={selected.evidence_id} />
          )}
          <Metadata data={selected} />
          <RawDetails data={selected} />
        </Drawer>
      )}
    </>
  );
}
