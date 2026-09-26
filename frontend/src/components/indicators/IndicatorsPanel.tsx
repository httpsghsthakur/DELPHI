import { IndicatorData } from '../../api/types';
import { Target } from 'lucide-react';
import { mapEventType } from '../../utils/formatting';

interface Props {
  indicators: IndicatorData[];
}

export function IndicatorsPanel({ indicators }: Props) {
  if (!indicators || indicators.length === 0) {
    return <div className="text-sm text-slate-500 italic">No indicators extracted.</div>;
  }

  return (
    <div className="space-y-3">
      {indicators.map(indicator => (
        <div key={indicator.indicator_id} className="bg-slate-900/50 border border-slate-800 rounded p-3">
          <div className="flex items-start gap-3">
            <Target className="w-4 h-4 text-delphi-accent mt-0.5 shrink-0" />
            <div className="flex-1">
              <h4 className="text-sm font-medium text-slate-200 mb-1">{indicator.description}</h4>
              <div className="flex flex-wrap gap-2 text-[10px] font-mono text-slate-400">
                <span className="bg-slate-800 px-1.5 py-0.5 rounded">Event: {mapEventType(indicator.expected_event_type)}</span>
                <span className="bg-slate-800 px-1.5 py-0.5 rounded">Window: {indicator.time_window}</span>
                {indicator.associated_scenario && (
                  <span className="bg-slate-800 px-1.5 py-0.5 rounded text-delphi-accent">Scenario ID: {indicator.associated_scenario.substring(0,8)}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
