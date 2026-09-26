import { HistoricalAnalogue } from '../../api/types';
import { formatTimestamp, formatPercent } from '../../utils/formatting';
import { useState } from 'react';
import { ChevronDown, ChevronRight, Activity } from 'lucide-react';

interface Props {
  analogues: HistoricalAnalogue[];
}

export function HistoricalAnalogueView({ analogues }: Props) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (!analogues || analogues.length === 0) {
    return <div className="text-sm text-slate-500 italic">No historical analogues retrieved for this event.</div>;
  }

  return (
    <div className="space-y-3">
      {analogues.map(analogue => (
        <div key={analogue.event_id} className="border border-slate-700 rounded-md overflow-hidden bg-slate-900/30">
          <button
            onClick={() => setExpandedId(expandedId === analogue.event_id ? null : analogue.event_id)}
            className="w-full flex items-center justify-between p-3 hover:bg-slate-800/50 transition-colors text-left"
          >
            <div className="flex items-center gap-3">
              {expandedId === analogue.event_id ? (
                <ChevronDown className="w-4 h-4 text-slate-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-slate-400" />
              )}
              <div>
                <div className="font-medium text-sm text-slate-200">
                  {analogue.event_details?.title || 'Historical Event'}
                </div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                  {formatTimestamp(analogue.date)} | ID: {analogue.event_id.substring(0, 8)}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] uppercase text-slate-500">Match</span>
              <span className="font-mono text-sm text-delphi-accent bg-delphi-accent/10 px-2 py-0.5 rounded">
                {formatPercent(analogue.similarity_score)}
              </span>
            </div>
          </button>
          
          {expandedId === analogue.event_id && (
            <div className="p-4 border-t border-slate-700 bg-slate-900/80 text-sm">
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <h4 className="text-[10px] font-semibold text-green-400 uppercase tracking-wider mb-2">Similarities</h4>
                  <ul className="list-disc list-inside text-slate-300 space-y-1 text-xs">
                    {analogue.event_details?.similarities?.map((s: string, i: number) => (
                      <li key={i}>{s}</li>
                    )) || <li>Contextual embedding match</li>}
                  </ul>
                </div>
                <div>
                  <h4 className="text-[10px] font-semibold text-red-400 uppercase tracking-wider mb-2">Differences</h4>
                  <ul className="list-disc list-inside text-slate-300 space-y-1 text-xs">
                    {analogue.event_details?.differences?.map((d: string, i: number) => (
                      <li key={i}>{d}</li>
                    )) || <li>Temporal divergence</li>}
                  </ul>
                </div>
              </div>
              
              <div>
                <h4 className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1">
                  <Activity className="w-3 h-3" /> Historical Timeline
                </h4>
                <div className="relative border-l-2 border-slate-700 ml-2 pl-4 space-y-4 py-2">
                  {analogue.outcomes?.map((outcome, i) => (
                    <div key={i} className="relative">
                      <div className="absolute w-2 h-2 bg-slate-400 rounded-full -left-[21px] top-1.5" />
                      <div className="text-[10px] font-mono text-slate-500 mb-0.5">
                        {outcome.time_offset || '+T days'}
                      </div>
                      <div className="text-slate-300 text-xs">
                        {outcome.description}
                      </div>
                    </div>
                  ))}
                  {(!analogue.outcomes || analogue.outcomes.length === 0) && (
                    <div className="text-xs text-slate-500 italic">No structured timeline available.</div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
