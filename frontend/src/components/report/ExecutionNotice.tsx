import { useAnalysisStore } from "../../state/analysisStore";
import { Badge } from "../ui/Primitives";
export function ExecutionNotice() {
  const { report, history } = useAnalysisStore();
  const mode =
    history.find((h) => h.report === report)?.executionMode || "UNKNOWN";
  return (
    <div className="report-banner">
      <Badge tone="warning">{mode} execution</Badge>
      <span>
        {mode === "SYNTHETIC"
          ? "The backend used synthetic components. These results are not real model forecasts."
          : mode === "REAL"
            ? "Execution mode is reported by the server; it does not establish evaluation quality."
            : "Execution mode could not be established. Treat outputs as unverified."}
      </span>
    </div>
  );
}
