import { APIProvenance } from '../../api/types';
import { formatTimestamp } from '../../utils/formatting';
import { ShieldCheck, Database, FileCode, CheckCircle2 } from 'lucide-react';
import { useAnalysisStore } from '../../state/analysisStore';

interface Props {
  provenance: APIProvenance;
}

export function ProvenancePanel({ provenance }: Props) {
  const { systemStatus } = useAnalysisStore();
  const isStrict = systemStatus?.temporal_mode === 'strict';

  return (
    <div className="bg-delphi-card border border-delphi-border rounded-lg p-5">
      <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2 flex justify-between items-center">
        <span>Analysis Provenance</span>
        {isStrict && (
          <span className="flex items-center gap-1 text-[10px] text-green-400 border border-green-500/30 bg-green-500/10 px-2 py-0.5 rounded">
            <ShieldCheck className="w-3 h-3" /> TEMPORAL VALIDATION: VERIFIED
          </span>
        )}
      </h3>

      <div className="space-y-4">
        <div className="bg-slate-900/50 rounded-md p-3 border border-slate-800">
          <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-2 flex items-center gap-2">
            <Database className="w-3 h-3" /> Data & Cutoff
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-slate-400">Cutoff: </span>
              <span className="font-mono text-delphi-accent">{formatTimestamp(provenance.prediction_cutoff)}</span>
            </div>
            <div>
              <span className="text-slate-400">Dataset: </span>
              <span className="font-mono text-slate-300">{provenance.dataset_version}</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900/50 rounded-md p-3 border border-slate-800">
          <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-2 flex items-center gap-2">
            <FileCode className="w-3 h-3" /> Models & Weights
          </div>
          <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs font-mono">
            <div className="flex justify-between items-center border-b border-slate-800/50 pb-1">
              <span className="text-slate-500">Tokenizer</span>
              <span className="text-slate-300 flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-green-500" /> {provenance.tokenizer_version}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800/50 pb-1">
              <span className="text-slate-500">EventEmbed</span>
              <span className="text-slate-300 flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-green-500" /> {provenance.eventembed_version}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800/50 pb-1">
              <span className="text-slate-500">EventNet</span>
              <span className="text-slate-300 flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-green-500" /> {provenance.eventnet_version}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800/50 pb-1">
              <span className="text-slate-500">CredNet</span>
              <span className="text-slate-300 flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-green-500" /> {provenance.crednet_version}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800/50 pb-1">
              <span className="text-slate-500">Retrieval</span>
              <span className="text-slate-300 flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-green-500" /> {provenance.retrieval_index_version}</span>
            </div>
            <div className="flex justify-between items-center border-b border-slate-800/50 pb-1">
              <span className="text-slate-500">CausalSeq</span>
              <span className="text-slate-300 flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-green-500" /> {provenance.causalseq_version}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
