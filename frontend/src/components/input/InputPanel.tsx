import { useState } from 'react';
import { useAnalysisStore } from '../../state/analysisStore';
import { apiClient } from '../../api/client';
import { validateTemporal } from '../../utils/validation';

export function InputPanel() {
  const { setLoading, setReport, setError, loading } = useAnalysisStore();
  
  const [text, setText] = useState('');
  const [pubDate, setPubDate] = useState(new Date().toISOString().slice(0, 16));
  const [cutoffDate, setCutoffDate] = useState(new Date().toISOString().slice(0, 16));
  const [domain, setDomain] = useState('geopolitics');
  const [liveResearch, setLiveResearch] = useState(false);
  
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!text.trim()) {
      setValidationError("Article text is required.");
      return;
    }

    const temporalError = validateTemporal(pubDate, cutoffDate);
    if (temporalError) {
      setValidationError(temporalError);
      return;
    }
    
    setValidationError(null);
    setLoading(true);
    
    try {
      // Create UTC strings for API
      const pubUtc = new Date(pubDate).toISOString();
      const cutoffUtc = new Date(cutoffDate).toISOString();
      
      const response = await apiClient.analyze({
        text,
        publication_timestamp: pubUtc,
        prediction_information_cutoff: cutoffUtc,
        domain,
        live_research: liveResearch
      });
      
      setReport(response);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-delphi-card border border-delphi-border rounded-lg p-5">
      <h3 className="text-lg font-medium text-slate-200 mb-4 border-b border-delphi-border pb-2">Analysis Input</h3>
      
      {validationError && (
        <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded text-red-400 text-sm">
          {validationError}
        </div>
      )}
      
      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Intelligence Source / Article</label>
          <textarea 
            value={text}
            onChange={e => setText(e.target.value)}
            className="w-full h-32 bg-slate-900 border border-slate-700 rounded-md p-3 text-sm text-slate-200 focus:outline-none focus:border-delphi-accent focus:ring-1 focus:ring-delphi-accent custom-scrollbar"
            placeholder="Paste article text or intelligence report here..."
            disabled={loading}
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Publication Date</label>
            <input 
              type="datetime-local" 
              value={pubDate}
              onChange={e => setPubDate(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-sm text-slate-200 focus:outline-none focus:border-delphi-accent"
              disabled={loading}
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Prediction Cutoff</label>
            <input 
              type="datetime-local" 
              value={cutoffDate}
              onChange={e => setCutoffDate(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-sm text-slate-200 focus:outline-none focus:border-delphi-accent"
              disabled={loading}
            />
          </div>
        </div>
        
        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1 uppercase tracking-wider">Domain</label>
          <select 
            value={domain}
            onChange={e => setDomain(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-sm text-slate-200 focus:outline-none focus:border-delphi-accent"
            disabled={loading}
          >
            <option value="geopolitics">Geopolitics</option>
            <option value="economics">Economics</option>
            <option value="security">Security</option>
          </select>
        </div>
        
        <div className="flex items-center mt-2 mb-4">
          <input
            type="checkbox"
            id="liveResearch"
            checked={liveResearch}
            onChange={(e) => setLiveResearch(e.target.checked)}
            disabled={loading}
            className="h-4 w-4 rounded border-slate-700 bg-slate-900 text-delphi-accent focus:ring-delphi-accent focus:ring-offset-slate-900"
          />
          <label htmlFor="liveResearch" className="ml-2 block text-sm text-slate-300">
            Enable Live Web Research
          </label>
        </div>
        
        <button 
          type="submit" 
          disabled={loading}
          className="w-full bg-delphi-blue hover:bg-blue-800 text-white font-medium py-2 px-4 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Processing...
            </>
          ) : (
            'Analyze'
          )}
        </button>
      </div>
    </form>
  );
}
