import { ScenarioCandidate } from '../api/types';
import { formatPercent } from '../utils/formatting';

interface Props {
  scenarios: ScenarioCandidate[];
}

export function ScenarioDistribution({ scenarios }: Props) {
  if (!scenarios || scenarios.length === 0) {
    return <div className="text-sm text-slate-500 italic">No scenarios generated.</div>;
  }

  // Sort by weight
  const sorted = [...scenarios].sort((a, b) => {
    const aVal = a.probability ?? a.uncalibrated_weight ?? 0;
    const bVal = b.probability ?? b.uncalibrated_weight ?? 0;
    return bVal - aVal;
  });

  const isCalibrated = sorted[0].probability !== undefined;

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          {isCalibrated ? 'Probability Distribution' : 'Normalized Scenario Weight'}
        </span>
        {!isCalibrated && (
          <span className="text-[10px] text-yellow-500 border border-yellow-500/30 bg-yellow-500/10 px-1.5 py-0.5 rounded uppercase font-medium">
            Uncalibrated / Research Mode
          </span>
        )}
      </div>

      <div className="space-y-3">
        {sorted.map((scenario) => {
          const value = scenario.probability ?? scenario.uncalibrated_weight ?? 0;
          return (
            <div key={scenario.scenario_id} className="relative">
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium text-slate-200 truncate pr-4" title={scenario.title}>
                  {scenario.title}
                </span>
                <span className="font-mono font-medium text-delphi-accent">
                  {formatPercent(value)}
                </span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-delphi-accent/80 transition-all duration-1000" 
                  style={{ width: `${value * 100}%` }}
                />
              </div>
              <div className="mt-2 pl-2 border-l-2 border-slate-700/50 space-y-2">
                {scenario.events?.map((ev, i) => (
                   <div key={i} className="text-xs text-slate-400 flex items-center gap-2">
                     <span className="w-1.5 h-1.5 rounded-full bg-slate-600 shrink-0" />
                     <span>Step {ev.step_index}: Type {ev.event_type}</span>
                   </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
