import { useAnalysisStore } from '../state/analysisStore';
import { InputPanel } from '../components/input/InputPanel';
import { CurrentEventCard } from '../components/event/CurrentEventCard';
import { CredibilityPanel } from '../components/event/CredibilityPanel';
import { ScenarioDistribution } from '../charts/ScenarioDistribution';
import { IndicatorsPanel } from '../components/indicators/IndicatorsPanel';
import { EvidencePanel } from '../components/evidence/EvidencePanel';
import { ProvenancePanel } from '../components/provenance/ProvenancePanel';
import { HistoricalAnalogueView } from '../components/historical/HistoricalAnalogueView';

export function Dashboard() {
  const { report, loading, error } = useAnalysisStore();

  return (
    <div className="p-6 max-w-[1600px] mx-auto grid grid-cols-12 gap-6 items-start">
      {/* Left Column - Input & Base Analysis */}
      <div className="col-span-12 lg:col-span-4 space-y-6">
        <InputPanel />
        
        {error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 text-red-400">
            <h3 className="font-semibold mb-1">Analysis Failed</h3>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {report && (
          <>
            <CurrentEventCard event={report.current_event} />
            <CredibilityPanel credibility={report.credibility} />
            <ProvenancePanel provenance={report.provenance} />
          </>
        )}
      </div>

      {/* Right Column - Intelligence & Scenarios */}
      <div className="col-span-12 lg:col-span-8 space-y-6">
        {!report && !loading && !error && (
          <div className="h-full min-h-[400px] border border-delphi-border rounded-lg bg-delphi-card/50 flex flex-col items-center justify-center text-slate-500 p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h2 className="text-xl font-medium text-slate-300 mb-2">Awaiting Intelligence Input</h2>
            <p className="max-w-md">
              Enter an article or intelligence report in the left panel to begin DELPHI processing.
              The system will automatically extract events, retrieve historical analogues, and project future scenarios.
            </p>
          </div>
        )}

        {loading && (
          <div className="border border-delphi-border rounded-lg bg-delphi-card p-8 flex flex-col items-center justify-center min-h-[400px]">
            <div className="w-12 h-12 border-4 border-delphi-blue border-t-delphi-accent rounded-full animate-spin mb-4" />
            <p className="text-slate-300 font-medium">Processing Intelligence...</p>
            <p className="text-slate-500 text-sm mt-2">This may take a few moments depending on model availability.</p>
          </div>
        )}

        {report && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              {/* Scenarios Visualization */}
              <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
                <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2">Future Scenarios</h3>
                <ScenarioDistribution scenarios={report.scenarios} />
              </div>
              
              {/* Indicators */}
              <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
                 <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2">Indicators To Watch</h3>
                 <IndicatorsPanel indicators={report.indicators} />
              </div>
            </div>

            {/* Historical Analogues */}
            <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
              <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2">Historical Analogues</h3>
              <HistoricalAnalogueView analogues={report.historical_analogues} />
            </div>

            {/* Evidence Explorer */}
            <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
               <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2">Evidence Explorer</h3>
               <EvidencePanel 
                 supporting={report.supporting_evidence} 
                 contradictory={report.contradictory_evidence} 
               />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
