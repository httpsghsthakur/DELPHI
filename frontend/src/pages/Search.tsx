import { Link, useSearchParams } from "react-router-dom";
import { useAnalysisStore } from "../state/analysisStore";
import { navigation } from "../components/layout/navigation";
import { EmptyState, PageHeader, Panel } from "../components/ui/Primitives";
export function WorkspaceSearch() {
  const [params, setParams] = useSearchParams();
  const query = params.get("q") || "";
  const { history, selectReport } = useAnalysisStore();
  const pages = navigation.filter((n) =>
    n.label.toLowerCase().includes(query.toLowerCase()),
  );
  const analyses = query
    ? history.filter((h) =>
        JSON.stringify(h).toLowerCase().includes(query.toLowerCase()),
      )
    : [];
  return (
    <>
      <PageHeader
        title="Workspace search"
        description="Search navigation and analysis responses received in this session."
      />
      <form
        className="table-toolbar"
        onSubmit={(e) => {
          e.preventDefault();
          setParams({
            q: String(new FormData(e.currentTarget).get("query") || ""),
          });
        }}
      >
        <input
          key={query}
          name="query"
          defaultValue={query}
          aria-label="Search query"
          placeholder="Search workspace…"
        />
        <button className="button primary">Search</button>
      </form>
      <Panel title="Matching destinations">
        {pages.length ? (
          <div className="search-results">
            {pages.map(({ path, label, icon: Icon }) => (
              <Link to={path} key={path}>
                <Icon size={17} />
                {label}
                <span>{path}</span>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState
            compact
            title="No matching destinations"
            description="Try a feature name such as research, evidence, or backtests."
          />
        )}
      </Panel>
      <Panel title="Session analyses">
        {analyses.length ? (
          <div className="search-results">
            {analyses.map((entry, i) => (
              <Link
                to="/analysis/results"
                key={i}
                onClick={() => selectReport(entry)}
              >
                {entry.request.text.slice(0, 100)}
                <span className="mono">{entry.receivedAt}</span>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState
            compact
            title="No matching session analyses"
            description="Analysis responses become searchable after a successful run. Server-side history search is not available."
          />
        )}
      </Panel>
    </>
  );
}
