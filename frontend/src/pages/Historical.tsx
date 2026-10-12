import { useState, type FormEvent } from "react";
import { Search } from "lucide-react";
import { apiClient } from "../api/client";
import type { HistoricalSearchResponse } from "../api/types";
import { HistoricalAnalogueView } from "../components/historical/HistoricalAnalogueView";
import {
  ErrorState,
  Loading,
  PageHeader,
  Panel,
  RawDetails,
} from "../components/ui/Primitives";
import { localDateTime } from "../utils/validation";
export function Historical() {
  const [text, setText] = useState(""),
    [domain, setDomain] = useState(""),
    [cutoff, setCutoff] = useState(localDateTime),
    [limit, setLimit] = useState(5);
  const [response, setResponse] = useState<HistoricalSearchResponse | null>(
      null,
    ),
    [loading, setLoading] = useState(false),
    [error, setError] = useState<string | null>(null);
  async function submit(e: FormEvent) {
    e.preventDefault();
    if (
      !text.trim() ||
      !cutoff ||
      !Number.isFinite(new Date(cutoff).getTime()) ||
      !Number.isInteger(limit) ||
      limit < 1
    ) {
      setError(
        "Enter event text, a valid cutoff, and a positive integer result limit.",
      );
      return;
    }
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      setResponse(
        await apiClient.historicalSearch({
          text: text.trim(),
          cutoff: new Date(cutoff).toISOString(),
          top_k: limit,
          ...(domain ? { domain } : {}),
        }),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }
  return (
    <>
      <PageHeader
        title="Historical search"
        description="Look for earlier events inside a defined information cutoff."
        eyebrow="Research / Historical retrieval"
      />
      <div className="notice warning">
        Backend limitation: this endpoint currently returns an empty
        placeholder. It does not execute historical retrieval. Actor,
        event-type, similarity, and date-range filters are not supported.
      </div>
      <Panel title="Search parameters">
        <form onSubmit={submit} className="search-form">
          <label htmlFor="historical-text">Event text</label>
          <textarea
            id="historical-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Describe the event to find historical analogues…"
            disabled={loading}
          />
          <div className="field-grid three">
            <div>
              <label htmlFor="historical-domain">Domain (optional)</label>
              <input
                id="historical-domain"
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                disabled={loading}
              />
            </div>
            <div>
              <label htmlFor="historical-cutoff">Cutoff (local time)</label>
              <input
                id="historical-cutoff"
                type="datetime-local"
                value={cutoff}
                onChange={(e) => setCutoff(e.target.value)}
                disabled={loading}
              />
            </div>
            <div>
              <label htmlFor="historical-limit">Result limit</label>
              <input
                id="historical-limit"
                type="number"
                min="1"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                disabled={loading}
              />
            </div>
          </div>
          <div className="form-action">
            <button className="button primary" disabled={loading}>
              <Search size={15} />
              {loading ? "Searching…" : "Search Historical Events"}
            </button>
          </div>
        </form>
        {error && <ErrorState message={error} />}
      </Panel>
      <Panel title="Retrieved events">
        {loading ? (
          <Loading />
        ) : (
          <HistoricalAnalogueView analogues={response?.analogues || []} />
        )}{" "}
        {response && (
          <RawDetails data={response} title="Actual retrieval response" />
        )}
      </Panel>
    </>
  );
}
