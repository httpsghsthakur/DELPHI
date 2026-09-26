import { useAnalysisStore } from '../../state/analysisStore';

export function ResearchPanel() {
  const { report } = useAnalysisStore();
  
  if (!report || !report.live_research_report) {
    return null;
  }
  
  const research = report.live_research_report;

  return (
    <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
      <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2 flex justify-between items-center">
        <span>Live Web Research</span>
        <span className={`text-xs px-2 py-1 rounded ${research.status === 'COMPLETE' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
          {research.status}
        </span>
      </h3>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900 rounded p-3 text-center">
          <div className="text-2xl text-delphi-accent mb-1">{research.documents_fetched}</div>
          <div className="text-xs text-slate-400 uppercase">Docs Fetched</div>
        </div>
        <div className="bg-slate-900 rounded p-3 text-center">
          <div className="text-2xl text-delphi-accent mb-1">{research.source_clusters}</div>
          <div className="text-xs text-slate-400 uppercase">Independent Clusters</div>
        </div>
        <div className="bg-slate-900 rounded p-3 text-center">
          <div className="text-2xl text-delphi-accent mb-1">{research.supporting_evidence.length}</div>
          <div className="text-xs text-slate-400 uppercase">Supporting Claims</div>
        </div>
        <div className="bg-slate-900 rounded p-3 text-center">
          <div className="text-2xl text-delphi-accent mb-1">{research.conflicting_evidence.length}</div>
          <div className="text-xs text-slate-400 uppercase">Conflicting Claims</div>
        </div>
      </div>
      
      <div className="mb-4">
        <h4 className="text-sm font-medium text-slate-300 mb-2">Queries Executed</h4>
        <div className="flex flex-wrap gap-2">
          {research.queries_executed?.map((q: string, i: number) => (
            <span key={i} className="text-xs bg-slate-800 text-slate-300 px-2 py-1 rounded">
              {q}
            </span>
          ))}
        </div>
      </div>
      
      <div>
        <h4 className="text-sm font-medium text-slate-300 mb-2">Providers Used</h4>
        <div className="flex flex-wrap gap-2">
          {research.providers_used?.map((p: string, i: number) => (
            <span key={i} className="text-xs bg-blue-900/30 text-blue-300 px-2 py-1 rounded border border-blue-800/50">
              {p}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
