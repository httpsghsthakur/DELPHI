import { CredibilityInfo } from '../../api/types';
import { ShieldCheck, AlertTriangle } from 'lucide-react';
import { formatPercent } from '../../utils/formatting';

interface Props {
  credibility: CredibilityInfo;
}

export function CredibilityPanel({ credibility }: Props) {
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-400';
    if (score >= 0.4) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number) => {
    if (score >= 0.7) return 'bg-green-400';
    if (score >= 0.4) return 'bg-yellow-400';
    return 'bg-red-400';
  };

  return (
    <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
      <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2 flex justify-between items-center">
        <span>Source Credibility</span>
        {credibility.calibrated ? (
          <span className="flex items-center gap-1 text-[10px] text-green-400 border border-green-500/30 bg-green-500/10 px-2 py-0.5 rounded">
            <ShieldCheck className="w-3 h-3" /> CALIBRATED
          </span>
        ) : (
          <span className="flex items-center gap-1 text-[10px] text-yellow-400 border border-yellow-500/30 bg-yellow-500/10 px-2 py-0.5 rounded">
            <AlertTriangle className="w-3 h-3" /> UNCALIBRATED
          </span>
        )}
      </h3>

      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">Credibility Signal</div>
          <div className={`text-3xl font-bold ${getScoreColor(credibility.final_credibility_score)}`}>
            {formatPercent(credibility.final_credibility_score)}
          </div>
        </div>
        <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden">
          <div 
            className={`h-full ${getScoreBg(credibility.final_credibility_score)} transition-all duration-1000`} 
            style={{ width: `${credibility.final_credibility_score * 100}%` }} 
          />
        </div>
      </div>

      <div className="space-y-3 text-sm">
        <div className="flex justify-between items-center p-2 rounded bg-slate-900/50 border border-slate-800">
          <span className="text-slate-400">Source Reliability</span>
          <span className="font-medium">{formatPercent(credibility.source_reliability)}</span>
        </div>
        <div className="flex justify-between items-center p-2 rounded bg-slate-900/50 border border-slate-800">
          <span className="text-slate-400">Content Consistency</span>
          <span className="font-medium">{formatPercent(credibility.content_credibility)}</span>
        </div>
      </div>
      
      <p className="mt-4 text-[10px] text-slate-500 leading-tight">
        * The credibility signal reflects measurable source and structural characteristics. It is a modeled estimate, not a guarantee of absolute factual truth.
      </p>
    </div>
  );
}
