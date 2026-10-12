import { useState, type FormEvent } from "react";
import {
  ArrowRight,
  FileText,
  Globe,
  Loader2,
  Plus,
  ShieldCheck,
  X,
} from "lucide-react";
import { apiClient } from "../../api/client";
import type { AnalysisRequest, ResearchReport } from "../../api/types";
import { useAnalysisStore } from "../../state/analysisStore";
import { localDateTime, validateTemporal } from "../../utils/validation";
import { ErrorState } from "../ui/Primitives";
export function InputPanel({
  researchOnly = false,
  onComplete,
}: {
  researchOnly?: boolean;
  onComplete?: (report?: ResearchReport) => void;
}) {
  const [text, setText] = useState(""),
    [pubDate, setPubDate] = useState(localDateTime),
    [cutoffDate, setCutoffDate] = useState(localDateTime);
  const [horizon, setHorizon] = useState(30),
    [domains, setDomains] = useState<string[]>(["geopolitics"]),
    [domainInput, setDomainInput] = useState("");
  const [liveResearch, setLiveResearch] = useState(false),
    [validationError, setValidationError] = useState<string | null>(null),
    [researchLoading, setResearchLoading] = useState(false);
  const {
    setLoading,
    setReport,
    setError,
    loading: analysisLoading,
    error,
    addResearch,
  } = useAnalysisStore();
  const loading = researchOnly ? researchLoading : analysisLoading;
  function addDomain() {
    const d = domainInput.trim().toLowerCase();
    if (d && !domains.includes(d)) setDomains([...domains, d]);
    setDomainInput("");
  }
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const problem = !text.trim()
      ? "Article or event text is required."
      : validateTemporal(pubDate, cutoffDate) ||
        (!domains.length ? "Add at least one domain." : "") ||
        (!Number.isInteger(horizon) || horizon < 1
          ? "Forecast horizon must be a positive whole number of days."
          : "");
    if (problem) {
      setValidationError(problem);
      return;
    }
    setValidationError(null);
    setError(null);
    const request: AnalysisRequest = {
      text: text.trim(),
      publication_timestamp: new Date(pubDate).toISOString(),
      prediction_information_cutoff: new Date(cutoffDate).toISOString(),
      domain: domains.join(", "),
      forecast_horizon: horizon,
      live_research: researchOnly || liveResearch,
    };
    if (researchOnly) setResearchLoading(true);
    else setLoading(true);
    try {
      if (researchOnly) {
        const result = await apiClient.research(request);
        addResearch(result);
        onComplete?.(result);
      } else {
        const result = await apiClient.analyze(request, crypto.randomUUID());
        setReport(result, request);
        onComplete?.();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "The operation failed.");
    } finally {
      if (researchOnly) setResearchLoading(false);
      else setLoading(false);
    }
  }
  return (
    <form onSubmit={handleSubmit} className="composer" noValidate>
      <div className="composer-heading">
        <span>
          <FileText size={18} />
          {researchOnly ? "Research context" : "Event context"}
        </span>
        <span className="muted">Text input</span>
      </div>
      <div className="composer-body">
        <label htmlFor="event-text">
          Article or event description <span className="required">*</span>
        </label>
        <p className="field-helper" id="event-help">
          Include the actors, actions, and context you want to investigate.
        </p>
        <textarea
          id="event-text"
          placeholder="Paste article text or describe an event to begin…"
          aria-describedby="event-help"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={loading}
        />
        <div className="editor-footer">
          <span>Article URL import is unavailable in this API.</span>
          <span className="mono">
            {text.length.toLocaleString()} characters
          </span>
        </div>
        <div className="form-section-title">
          <span>Temporal boundaries</span>
          <small>
            Dates use your local timezone; requests are sent in UTC.
          </small>
        </div>
        <div className="field-grid">
          <div>
            <label htmlFor="publication">Publication date</label>
            <input
              id="publication"
              type="datetime-local"
              value={pubDate}
              onChange={(e) => setPubDate(e.target.value)}
              disabled={loading}
            />
            <p className="field-helper">
              When the article or event was published.
            </p>
          </div>
          <div>
            <label htmlFor="cutoff">Prediction cutoff</label>
            <input
              id="cutoff"
              type="datetime-local"
              value={cutoffDate}
              onChange={(e) => setCutoffDate(e.target.value)}
              disabled={loading}
            />
            <p className="field-helper">
              Latest information permitted in the analysis.
            </p>
          </div>
        </div>
        <div className="form-section-title">
          <span>
            {researchOnly ? "Research scope" : "Forecast configuration"}
          </span>
        </div>
        <div className="field-grid configuration-grid">
          {!researchOnly && (
            <div>
              <label htmlFor="horizon">Forecast horizon</label>
              <div className="input-suffix">
                <input
                  id="horizon"
                  type="number"
                  min="1"
                  step="1"
                  value={horizon}
                  onChange={(e) => setHorizon(Number(e.target.value))}
                  disabled={loading}
                />
                <span>days</span>
              </div>
              <p className="field-helper">
                A positive integer, as accepted by the API.
              </p>
            </div>
          )}
          <div>
            <label htmlFor="domain">Domains</label>
            <div className="domains">
              {domains.map((d) => (
                <span key={d}>
                  {d}
                  <button
                    type="button"
                    aria-label={`Remove ${d}`}
                    onClick={() => setDomains(domains.filter((x) => x !== d))}
                    disabled={loading}
                  >
                    <X size={12} />
                  </button>
                </span>
              ))}
            </div>
            <div className="domain-add">
              <input
                id="domain"
                placeholder="Add a domain"
                value={domainInput}
                onChange={(e) => setDomainInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addDomain();
                  }
                }}
                disabled={loading}
              />
              <button
                className="button secondary small"
                type="button"
                onClick={addDomain}
                disabled={loading || !domainInput.trim()}
              >
                <Plus size={14} />
                Add
              </button>
            </div>
          </div>
        </div>
        <div className="composer-options">
          {!researchOnly && (
            <label className="toggle-row">
              <Globe size={17} />
              <span>
                Live web research
                <small>
                  Retrieve evidence through configured research providers.
                </small>
              </span>
              <input
                type="checkbox"
                checked={liveResearch}
                onChange={(e) => setLiveResearch(e.target.checked)}
                disabled={loading}
              />
            </label>
          )}
          <div className="toggle-row">
            <ShieldCheck size={17} />
            <span>
              Temporal validation
              <small>
                Publication must precede cutoff. Strict model validation is
                controlled by the server.
              </small>
            </span>
            <span className="option-lock">Enforced</span>
          </div>
        </div>
        {(validationError || error) && (
          <ErrorState message={validationError || error || ""} />
        )}
      </div>
      <div className="composer-footer">
        <span>
          {loading
            ? "Request submitted. The API does not expose stage progress."
            : "Results are generated from the connected DELPHI engine."}
        </span>
        <button className="button primary" type="submit" disabled={loading}>
          {loading ? (
            <Loader2 className="spin" size={16} />
          ) : (
            <ArrowRight size={16} />
          )}{" "}
          {loading
            ? "Waiting for response…"
            : researchOnly
              ? "Run Research"
              : "Run Analysis"}
        </button>
      </div>
    </form>
  );
}
