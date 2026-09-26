import { EvidenceData } from '../../api/types';
import { formatTimestamp } from '../../utils/formatting';
import { CheckCircle2, XCircle, ExternalLink } from 'lucide-react';

interface Props {
  supporting: EvidenceData[];
  contradictory: EvidenceData[];
}

export function EvidencePanel({ supporting, contradictory }: Props) {
  const renderEvidence = (items: EvidenceData[], type: 'supporting' | 'contradictory') => {
    if (!items || items.length === 0) {
      return <div className="text-sm text-slate-500 italic px-4 py-2">No {type} evidence.</div>;
    }

    return (
      <div className="space-y-2 px-4 py-2">
        {items.map(item => (
          <div key={item.evidence_id} className="flex items-start gap-3 bg-slate-900/50 p-2 rounded">
            {type === 'supporting' ? (
              <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-slate-300 uppercase tracking-wider">{item.evidence_type}</span>
                <span className="text-[10px] text-slate-500">{formatTimestamp(item.timestamp)}</span>
              </div>
              <div className="text-[10px] font-mono text-slate-400 mt-1 flex items-center gap-1">
                Source: {item.source_id.substring(0,8)} 
                <ExternalLink className="w-3 h-3 cursor-pointer hover:text-delphi-accent" />
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-0 border border-slate-700 rounded-md overflow-hidden bg-slate-900/30">
      <div className="border-r border-slate-700 md:border-b-0 border-b">
        <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wider p-3 border-b border-slate-700 bg-slate-900/50">
          Supporting Evidence
        </h4>
        <div className="max-h-60 overflow-y-auto custom-scrollbar">
          {renderEvidence(supporting, 'supporting')}
        </div>
      </div>
      <div>
        <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wider p-3 border-b border-slate-700 bg-slate-900/50">
          Conflicting Evidence
        </h4>
        <div className="max-h-60 overflow-y-auto custom-scrollbar">
          {renderEvidence(contradictory, 'contradictory')}
        </div>
      </div>
    </div>
  );
}
