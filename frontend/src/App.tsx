import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { Dashboard } from "./pages/Dashboard";
import { Layout } from "./components/layout/Layout";
import { NewAnalysis, AnalysisResults } from "./pages/Analysis";
import { Research } from "./pages/Research";
import { Historical } from "./pages/Historical";
import { Intelligence } from "./pages/Intelligence";
import { Operations } from "./pages/Operations";
import { Backtests } from "./pages/Backtests";
import { WorkspaceSearch } from "./pages/Search";
import { EmptyState } from "./components/ui/Primitives";
function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analysis/new" element={<NewAnalysis />} />
          <Route path="/analysis/results" element={<AnalysisResults />} />
          <Route path="/research" element={<Research />} />
          <Route path="/historical" element={<Historical />} />
          <Route path="/graph" element={<Intelligence view="graph" />} />
          <Route
            path="/scenarios"
            element={<Intelligence view="scenarios" />}
          />
          <Route
            path="/indicators"
            element={<Intelligence view="indicators" />}
          />
          <Route path="/evidence" element={<Intelligence view="evidence" />} />
          <Route path="/backtests" element={<Backtests />} />
          <Route path="/models" element={<Operations view="models" />} />
          <Route path="/sources" element={<Operations view="sources" />} />
          <Route path="/status" element={<Operations view="status" />} />
          <Route path="/settings" element={<Operations view="settings" />} />
          <Route path="/search" element={<WorkspaceSearch />} />
          <Route
            path="*"
            element={
              <EmptyState
                title="Page not found"
                description="This destination is not part of the DELPHI workspace."
                action={
                  <Link to="/" className="button secondary">
                    Return to overview
                  </Link>
                }
              />
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
export default App;
