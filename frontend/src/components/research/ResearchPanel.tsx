import { researchEvidence } from "../../utils/evidence";
import type { ResearchReport } from "../../api/types";
import { Badge, CopyButton, EmptyState, Metadata } from "../ui/Primitives";
import { EvidencePanel } from "../evidence/EvidencePanel";
export function ResearchPanel({
  research,
}: {
  research?: ResearchReport | null;
}) {
  if (!research)
    return (
      <EmptyState
        compact
        title="No research report available"
        description="Run live research or enable it when submitting an analysis to see provider activity and returned evidence."
      />
    );
  return (
    <>
      <div className="section-intro">
        <Badge>{research.status}</Badge>
        <CopyButton value={research.run_id} />
      </div>
      <Metadata
        data={{
          run_id: research.run_id,
          documents_discovered: research.documents_discovered,
          documents_fetched: research.documents_fetched,
          documents_rejected: research.documents_rejected,
          source_clusters: research.source_clusters,
          providers_used: research.providers_used,
          temporal_validity_status: research.temporal_validity_status,
        }}
      />
      <h3 className="subheading">Executed queries</h3>
      {research.queries_executed.length ? (
        <ol className="query-list">
          {research.queries_executed.map((q, i) => (
            <li key={i}>
              <span className="mono">{String(i + 1).padStart(2, "0")}</span>
              {q}
            </li>
          ))}
        </ol>
      ) : (
        <p className="muted">No queries reported.</p>
      )}
      <p className="notice">
        The research response does not expose document titles, URLs, publisher
        dates, or provider health. Only returned source references are shown.
      </p>
      {research.limitations.map((l, i) => (
        <p className="notice warning" key={i}>
          {l}
        </p>
      ))}
      <EvidencePanel evidence={researchEvidence(research)} />
    </>
  );
}
