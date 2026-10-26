import { useState } from "react";
import {
  ExternalLink,
  Copy,
  Check,
  BookOpen,
  Shield,
  Clock,
  Layers,
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Globe,
} from "lucide-react";
import type {
  IntelligenceReport,
  ResearchDossier,
} from "../../api/types";
import { Badge } from "../ui/Primitives";

interface IntelligenceReportViewProps {
  report?: IntelligenceReport | null;
  dossier?: ResearchDossier | null;
  cutoff?: string;
  calibrationStatus?: string;
}

export function IntelligenceReportView({
  report,
  dossier,
  cutoff,
  calibrationStatus = "Uncalibrated / Research Mode",
}: IntelligenceReportViewProps) {
  const [copied, setCopied] = useState(false);
  const [showDossier, setShowDossier] = useState(false);
  const [activeSection, setActiveSection] = useState("exec-summary");

  if (!report) {
    return (
      <div className="quiet-empty">
        No structured intelligence report generated for this analysis. Enable Live Web Research to produce deep multi-source intelligence briefings.
      </div>
    );
  }

  const activeReport = report;

  const sections = [
    { id: "exec-summary", title: "Executive Summary", content: activeReport.executive_summary },
    { id: "bg-context", title: "Background and Context", content: activeReport.background_and_context },
    { id: "current-dev", title: "Current Developments", content: activeReport.current_developments },
    { id: "evidence-assessment", title: "Evidence and Source Assessment", content: activeReport.evidence_and_sources },
    { id: "historical-comp", title: "Historical Comparisons", content: activeReport.historical_comparisons },
    { id: "causal-analysis", title: "Causal Analysis", content: activeReport.causal_analysis },
    { id: "future-scenarios", title: "Possible Future Scenarios", content: activeReport.future_scenarios },
    { id: "risks-uncertainties", title: "Risks and Uncertainties", content: activeReport.risks_and_uncertainties },
    { id: "conclusion", title: "Conclusion", content: activeReport.conclusion },
  ];

  function copyAsMarkdown() {
    const md = [
      `# ${activeReport.title}`,
      `*Information Cutoff: ${cutoff || "Current"} · Calibration: ${calibrationStatus}*`,
      "",
      `## 1. Executive Summary\n${activeReport.executive_summary}`,
      "",
      `## 2. Background and Context\n${activeReport.background_and_context}`,
      "",
      `## 3. Current Developments\n${activeReport.current_developments}`,
      "",
      `## 4. Evidence and Source Assessment\n${activeReport.evidence_and_sources}`,
      "",
      `## 5. Historical Comparisons\n${activeReport.historical_comparisons}`,
      "",
      `## 6. Causal Analysis\n${activeReport.causal_analysis}`,
      "",
      `## 7. Possible Future Scenarios\n${activeReport.future_scenarios}`,
      "",
      `## 8. Risks and Uncertainties\n${activeReport.risks_and_uncertainties}`,
      "",
      `## 9. Conclusion\n${activeReport.conclusion}`,
      "",
      `## 10. Sources and Further Reading`,
      ...(activeReport.sources_and_reading || []).map(
        (s) => `[${s.num}] [${s.title}](${s.url}) — ${s.name} (${s.domain})`
      ),
    ].join("\n\n");

    navigator.clipboard.writeText(md).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  // Render paragraphs with clickable citation chips
  function renderParagraphs(text: string) {
    if (!text) return null;
    const paras = text.split("\n\n").filter(Boolean);

    return paras.map((p, pIdx) => {
      // Split on citations like [[1]](url) or [1](<url>) or [1](url)
      const parts = p.split(/(\[\[?\d+\]?\]\(<?[^>)]+>?\))/g);

      return (
        <p key={pIdx} className="briefing-paragraph">
          {parts.map((part, partIdx) => {
            const match = part.match(/\[\[?(\d+)\]?\]\(<?([^>)]+)>?\)/);
            if (match) {
              const num = match[1];
              const url = match[2];
              const src = activeReport.sources_and_reading?.find((s) => String(s.num) === num);
              return (
                <a
                  key={partIdx}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="citation-chip"
                  title={`${src?.title || "Source"} (${src?.domain || url}) — CredNet Score: ${src ? (src.credibility * 100).toFixed(0) + "%" : "N/A"}`}
                >
                  [{num}]
                </a>
              );
            }
            return <span key={partIdx}>{part}</span>;
          })}
        </p>
      );
    });
  }

  return (
    <div className="briefing-workspace">
      {/* Header bar */}
      <div className="briefing-header">
        <div>
          <div className="briefing-badge-row">
            <Badge tone="primary">INTELLIGENCE BRIEFING</Badge>
            <Badge tone="warning">{calibrationStatus}</Badge>
            {cutoff && (
              <span className="briefing-meta-item">
                <Clock size={13} /> Cutoff: {new Date(cutoff).toLocaleDateString()}
              </span>
            )}
          </div>
          <h1 className="briefing-title">{activeReport.title}</h1>
          <p className="briefing-subtitle">
            Ground-truth synthesized analysis from DELPHI neural models and verified multi-source research.
          </p>
        </div>
        <div className="briefing-actions">
          <button className="button secondary small" onClick={copyAsMarkdown}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? "Copied Markdown" : "Copy Markdown"}
          </button>
          {dossier && (
            <button
              className="button secondary small"
              onClick={() => setShowDossier(!showDossier)}
            >
              <Layers size={14} />
              {showDossier ? "Hide Research Dossier" : "Inspect Research Dossier"}
              {showDossier ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </div>
      </div>

      {/* Research Dossier Inspector (collapsible) */}
      {showDossier && dossier && (
        <div className="dossier-tray">
          <div className="dossier-header">
            <h3>
              <BookOpen size={16} /> Research Dossier & Multi-Source Audit
            </h3>
            <span className="mono">Cutoff: {dossier.research_cutoff}</span>
          </div>

          <div className="dossier-grid">
            <div className="dossier-card">
              <span className="dossier-stat-num">{dossier.sources.length}</span>
              <span className="dossier-stat-label">Verified Sources</span>
            </div>
            <div className="dossier-card">
              <span className="dossier-stat-num">{dossier.independent_sources_count}</span>
              <span className="dossier-stat-label">Independent Clusters</span>
            </div>
            <div className="dossier-card">
              <span className="dossier-stat-num">{dossier.extracted_claims.length}</span>
              <span className="dossier-stat-label">Structured Claims</span>
            </div>
            <div className="dossier-card">
              <span className="dossier-stat-num">{dossier.wire_repetition_count}</span>
              <span className="dossier-stat-label">Wire Repetitions Deduplicated</span>
            </div>
          </div>

          {/* Search Queries Executed */}
          <div className="dossier-queries">
            <h4>Executed Search Queries</h4>
            <div className="query-tag-list">
              {dossier.search_queries.map((q, idx) => (
                <span key={idx} className="query-tag">
                  {idx + 1}. {q}
                </span>
              ))}
            </div>
          </div>

          {/* Provider Statuses */}
          {dossier.provider_statuses && Object.keys(dossier.provider_statuses).length > 0 && (
            <div className="dossier-providers">
              <h4>Search Provider Audit</h4>
              <div className="provider-status-row">
                {Object.entries(dossier.provider_statuses).map(([prov, st]) => (
                  <div key={prov} className="provider-status-pill">
                    <Globe size={13} />
                    <span className="prov-name">{prov}:</span>
                    <span className={`prov-status ${st === "OK" ? "good" : "warn"}`}>{st}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Conflicting claims inspector */}
          {dossier.conflicting_reports && dossier.conflicting_reports.length > 0 && (
            <div className="dossier-conflicts">
              <h4>
                <AlertTriangle size={15} /> Competing Accounts & Counter-Claims Identified
              </h4>
              <ul className="conflict-list">
                {dossier.conflicting_reports.map((cr, idx) => (
                  <li key={idx}>
                    <strong>{String(cr.source || "Source")}:</strong> "{String(cr.claim || "")}"
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Main Report Body with TOC Nav */}
      <div className="briefing-layout">
        <aside className="briefing-toc">
          <div className="toc-title">Table of Contents</div>
          <nav>
            {sections.map((s, idx) => (
              <a
                key={s.id}
                href={`#${s.id}`}
                className={`toc-link ${activeSection === s.id ? "active" : ""}`}
                onClick={() => setActiveSection(s.id)}
              >
                <span className="toc-num">0{idx + 1}</span>
                <span className="toc-text">{s.title}</span>
              </a>
            ))}
            <a
              href="#sources-reading"
              className={`toc-link ${activeSection === "sources-reading" ? "active" : ""}`}
              onClick={() => setActiveSection("sources-reading")}
            >
              <span className="toc-num">10</span>
              <span className="toc-text">Sources & Reading</span>
            </a>
          </nav>
        </aside>

        <article className="briefing-content">
          {sections.map((s, idx) => (
            <section key={s.id} id={s.id} className="briefing-section">
              <div className="section-eyebrow">Section 0{idx + 1}</div>
              <h2 className="section-heading">{s.title}</h2>
              <div className="section-body">{renderParagraphs(s.content)}</div>
            </section>
          ))}

          {/* Sources and Further Reading */}
          <section id="sources-reading" className="briefing-section sources-section">
            <div className="section-eyebrow">Section 10</div>
            <h2 className="section-heading">Sources and Further Reading</h2>
            <p className="briefing-paragraph muted">
              All references link directly to verified publisher URLs retrieved by DELPHI's search providers. Credibility scores reflect CredNet domain assessments.
            </p>

            <div className="source-citation-list">
              {(activeReport.sources_and_reading || []).map((s) => (
                <div key={s.num} className="source-citation-card">
                  <div className="source-citation-badge">[{s.num}]</div>
                  <div className="source-citation-details">
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="source-citation-title"
                    >
                      {s.title}
                      <ExternalLink size={13} />
                    </a>
                    <div className="source-citation-meta">
                      <span className="source-domain">{s.domain}</span>
                      <span className="source-pub">
                        Published: {s.published_at && s.published_at !== "PUBLICATION_TIME_UNKNOWN" ? new Date(s.published_at).toLocaleDateString() : "Timestamp Unrecorded"}
                      </span>
                      <span className="source-cred">
                        CredNet: {(s.credibility * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Provenance footer */}
          <div className="briefing-footer-note">
            <Shield size={16} />
            <span>{activeReport.confidence_statement || "DELPHI Strategic Intelligence Briefing."}</span>
          </div>
        </article>
      </div>
    </div>
  );
}
