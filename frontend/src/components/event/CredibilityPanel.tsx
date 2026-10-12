import type { JsonObject } from "../../api/types";
import { Badge, EmptyState, Metadata } from "../ui/Primitives";
export function CredibilityPanel({ credibility }: { credibility: JsonObject }) {
  if (!Object.keys(credibility).length)
    return (
      <EmptyState
        compact
        title="Credibility output unavailable"
        description="No model score was returned. Model availability can be inspected in System Status."
      />
    );
  const score =
    credibility.credibility_score ?? credibility.final_credibility_score;
  const calibrated =
    typeof credibility.calibrated_score === "number" ||
    credibility.calibrated === true;
  return (
    <>
      <div className="score-row">
        <div>
          <span className="muted">Returned model score</span>
          <strong className="score mono">
            {typeof score === "number" ? score.toFixed(3) : "Not reported"}
          </strong>
        </div>
        <Badge tone={calibrated ? "" : "warning"}>
          {calibrated ? "Calibration reported" : "Uncalibrated"}
        </Badge>
      </div>
      <p className="notice">
        A model score is not verified factual truth. Calibration alone does not
        establish evaluation quality.
      </p>
      <Metadata data={credibility} />
    </>
  );
}
