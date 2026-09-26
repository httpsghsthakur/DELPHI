import { useState, useEffect } from 'react';
import { 
  LineChart, Activity, ShieldAlert, Scale, 
  Map, Database, Play, Calendar, ChevronDown, 
  AlertCircle, Search, X, Loader2
} from 'lucide-react';
import { useAnalysisStore } from '../state/analysisStore';
import { apiClient } from '../api/client';
import { HealthResponse } from '../api/types';

export function Dashboard() {
  const [activeTab, setActiveTab] = useState('Overview');
  
  // Form State
  const [inputText, setInputText] = useState('');
  const [pubDate, setPubDate] = useState(new Date().toISOString().split('T')[0]);
  const [cutoffDate, setCutoffDate] = useState(() => {
    const d = new Date();
    d.setMonth(d.getMonth() + 3);
    return d.toISOString().split('T')[0];
  });
  const [horizon, setHorizon] = useState('3 months');
  const [domains, setDomains] = useState<string[]>(['Geopolitics', 'Security']);
  
  // Store
  const { report, loading, error, setReport, setLoading, setError } = useAnalysisStore();
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    apiClient.getHealth().then(setHealth).catch(console.error);
  }, []);

  const handleRunAnalysis = async () => {
    if (!inputText.trim()) return;
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.analyze({
        text: inputText,
        publication_timestamp: pubDate,
        prediction_information_cutoff: cutoffDate,
        domain: domains.join(', '),
      });
      setReport(res);
    } catch (err: any) {
      setError(err.message || 'An error occurred during analysis');
    } finally {
      setLoading(false);
    }
  };

  const removeDomain = (d: string) => setDomains(domains.filter(x => x !== d));
  const addDomain = () => {
    const d = prompt("Enter domain name:");
    if (d && !domains.includes(d)) setDomains([...domains, d]);
  };

  return (
    <div className="flex flex-col gap-4 max-w-[1600px] mx-auto w-full pb-10">
      
      {/* Header Card: New Forecast Analysis */}
      <div className="glass-card rounded-xl p-4 glow-border">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-8 h-8 rounded-lg bg-delphi-blue flex items-center justify-center">
            <LineChart className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white leading-tight">New Forecast Analysis</h2>
            <p className="text-xs text-slate-400">Enter a news article, headline, or description to generate event intelligence and forecast scenarios.</p>
          </div>
        </div>
        
        <div className="flex flex-wrap lg:flex-nowrap gap-4 items-start">
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <textarea 
                className="w-full bg-slate-900/50 border border-slate-700/50 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-delphi-accent min-h-[60px] custom-scrollbar"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Enter event context here..."
                disabled={loading}
              />
              <div className="absolute bottom-2 right-2 text-[10px] text-slate-500">{inputText.length}/2000</div>
            </div>
          </div>
          
          <div className="w-[160px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Publication Date</label>
            <div className="relative">
              <Calendar className="w-4 h-4 text-slate-500 absolute left-2 top-1/2 -translate-y-1/2" />
              <input type="date" value={pubDate} onChange={e => setPubDate(e.target.value)} disabled={loading} className="w-full bg-slate-900/50 border border-slate-700/50 rounded-md pl-8 pr-2 py-2 text-xs text-white" />
            </div>
          </div>
          
          <div className="w-[160px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Prediction Cutoff</label>
            <div className="relative">
              <Calendar className="w-4 h-4 text-slate-500 absolute left-2 top-1/2 -translate-y-1/2" />
              <input type="date" value={cutoffDate} onChange={e => setCutoffDate(e.target.value)} disabled={loading} className="w-full bg-slate-900/50 border border-slate-700/50 rounded-md pl-8 pr-2 py-2 text-xs text-white" />
            </div>
          </div>
          
          <div className="w-[120px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Forecast Horizon</label>
            <div className="relative">
              <select value={horizon} onChange={e => setHorizon(e.target.value)} disabled={loading} className="w-full bg-slate-900/50 border border-slate-700/50 rounded-md pl-2 pr-6 py-2 text-xs text-white appearance-none">
                <option>3 months</option>
                <option>6 months</option>
                <option>12 months</option>
              </select>
              <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
          
          <div className="w-[200px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Domains</label>
            <div className="flex flex-wrap gap-1 mb-1">
              {domains.map(d => (
                <span key={d} className="bg-slate-800 text-slate-300 border border-slate-700 text-[10px] px-2 py-0.5 rounded flex items-center gap-1">
                  {d} <X className="w-3 h-3 cursor-pointer hover:text-white" onClick={() => !loading && removeDomain(d)} />
                </span>
              ))}
            </div>
            <div className="text-[10px] text-delphi-accent cursor-pointer" onClick={() => !loading && addDomain()}>+ Add domain</div>
          </div>
          
          <div className="pt-4 shrink-0">
            <button 
              onClick={handleRunAnalysis}
              disabled={loading || !inputText.trim()}
              className="bg-delphi-blue hover:bg-delphi-blueHover disabled:bg-slate-700 disabled:text-slate-400 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 shadow-lg shadow-delphi-blue/20 transition-all"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              {loading ? 'Analyzing...' : 'Run Analysis'}
            </button>
          </div>
        </div>
        
        {error && (
          <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded text-sm text-red-400 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <div>
              <div className="font-semibold">Analysis Failed</div>
              <div className="text-xs opacity-80">{error}</div>
            </div>
          </div>
        )}
      </div>
      
      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-white/5 overflow-x-auto custom-scrollbar pb-px">
        {[
          { name: 'Overview', icon: <Activity className="w-4 h-4" /> },
          { name: 'Current Event', icon: <Activity className="w-4 h-4" /> },
          { name: 'Live Research', icon: <Search className="w-4 h-4" /> },
          { name: 'Historical Analogues', icon: <Scale className="w-4 h-4" /> },
          { name: 'Scenarios', icon: <LineChart className="w-4 h-4" /> },
          { name: 'Indicators', icon: <Activity className="w-4 h-4" /> },
          { name: 'Sources', icon: <Database className="w-4 h-4" /> },
          { name: 'Provenance', icon: <Database className="w-4 h-4" /> }
        ].map(tab => (
          <button 
            key={tab.name}
            onClick={() => setActiveTab(tab.name)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
              activeTab === tab.name 
                ? 'border-delphi-accent text-delphi-accent bg-delphi-accent/10 rounded-t-md' 
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/5 rounded-t-md'
            }`}
          >
            {tab.icon} {tab.name}
          </button>
        ))}
      </div>
      
      {/* Dashboard Grid Content */}
      {activeTab === 'Overview' && !report && !loading && (
        <div className="min-h-[400px] border border-dashed border-slate-700 rounded-xl bg-slate-900/20 flex flex-col items-center justify-center text-slate-500 p-8 text-center">
          <Activity className="w-12 h-12 mb-4 text-slate-700" />
          <h3 className="text-lg font-medium text-slate-400 mb-2">No analysis loaded</h3>
          <p className="text-sm max-w-md">Enter event text and click "Run Analysis" to generate intelligence, assess credibility, and forecast scenarios.</p>
        </div>
      )}

      {activeTab === 'Overview' && loading && (
        <div className="min-h-[400px] border border-delphi-border rounded-xl bg-slate-900/20 flex flex-col items-center justify-center text-delphi-blue p-8 text-center">
          <Loader2 className="w-12 h-12 mb-4 animate-spin mx-auto" />
          <h3 className="text-lg font-medium text-slate-300 mb-2">Generating Intelligence...</h3>
          <p className="text-sm text-slate-500">Event extraction, historical retrieval, and causal reasoning in progress.</p>
        </div>
      )}

      {activeTab === 'Overview' && report && (
        <div className="grid grid-cols-12 gap-4">
          
          {/* Top Row */}
          
          {/* Current Event Analysis */}
          <div className="col-span-12 xl:col-span-4 glass-card rounded-xl p-4 flex flex-col glow-border relative overflow-hidden">
             <div className="flex items-center gap-2 mb-4">
               <div className="p-1.5 bg-indigo-500/20 rounded text-indigo-400">
                 <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
               </div>
               <h3 className="text-sm font-semibold text-white">Current Event Analysis</h3>
             </div>
             
             <div className="flex gap-4 mb-4">
               <div className="flex-1 text-sm text-slate-300 leading-relaxed">
                 Event ID: {report.current_event?.event_id || 'Unknown'}
               </div>
             </div>
             
             <div className="flex flex-wrap gap-2 mb-4">
               {report.current_event?.extracted_event?.spans && Object.entries(report.current_event.extracted_event.spans).map(([key, val]: [string, any], i: number) => (
                 <span key={i} className="flex items-center gap-1 text-[10px] text-slate-400">
                   <div className="w-1.5 h-1.5 rounded-full bg-blue-400" /> 
                   {key}: {val}
                 </span>
               ))}
             </div>
          </div>
          
          {/* Credibility Assessment */}
          <div className="col-span-12 xl:col-span-4 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center gap-2 mb-6">
               <div className="p-1.5 bg-blue-500/20 rounded text-blue-400">
                 <ShieldAlert className="w-4 h-4" />
               </div>
               <h3 className="text-sm font-semibold text-white">Credibility Assessment</h3>
            </div>
            
            {health?.dependencies?.crednet === 'ok' && report.credibility ? (
              <>
                <div className="flex items-center gap-8 mb-6">
                  {/* Circular Progress */}
                  <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="8" />
                      <circle cx="50" cy="50" r="45" fill="none" stroke="#10b981" strokeWidth="8" strokeDasharray="283" strokeDashoffset={283 - (283 * (report.credibility.final_credibility_score || 0))} className="drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" strokeLinecap="round" />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <div className="text-3xl font-bold text-white">{(report.credibility.final_credibility_score || 0).toFixed(2)}</div>
                      <div className="text-[9px] text-slate-400 text-center uppercase leading-tight">Overall<br/>Credibility</div>
                    </div>
                  </div>
                  
                  <div className="flex-1 space-y-4">
                    <h4 className="text-xs font-semibold text-slate-200">Credibility Signals</h4>
                    <div className="space-y-3">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-400">Source Reliability</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                              <div className={`h-full bg-blue-500`} style={{width: `${(report.credibility.source_reliability || 0)*100}%`}} />
                            </div>
                            <span className="text-slate-300 w-6 text-right">{(report.credibility.source_reliability || 0).toFixed(2)}</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-400">Content Credibility</span>
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                              <div className={`h-full bg-blue-500`} style={{width: `${(report.credibility.content_credibility || 0)*100}%`}} />
                            </div>
                            <span className="text-slate-300 w-6 text-right">{(report.credibility.content_credibility || 0).toFixed(2)}</span>
                          </div>
                        </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center">
                <ShieldAlert className="w-8 h-8 text-slate-600 mb-2" />
                <div className="text-sm font-medium text-slate-400">MODEL NOT TRAINED</div>
                <div className="text-xs text-slate-500">CredNet checkpoint unavailable.</div>
              </div>
            )}
          </div>
          
          {/* Scenario Forecast */}
          <div className="col-span-12 xl:col-span-4 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-purple-500/20 rounded text-purple-400">
                   <LineChart className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Scenario Forecast</h3>
              </div>
              {health?.dependencies?.calibration !== 'ok' && (
                <div className="bg-yellow-500/20 border border-yellow-500/30 text-yellow-300 px-2 py-1 rounded text-[9px] font-medium flex flex-col items-center leading-tight">
                  <span>⚠️ UNCALIBRATED</span>
                  <span className="opacity-70 text-[8px]">Scenario weights (not probabilities)</span>
                </div>
              )}
            </div>
            
            {health?.dependencies?.causalseq === 'ok' && report.scenarios ? (
              <div className="space-y-3 flex-1 flex flex-col justify-center overflow-y-auto custom-scrollbar pr-2">
                {report.scenarios?.map((s: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 border border-transparent hover:border-white/10 transition-colors">
                    <div className="w-6 h-6 rounded flex items-center justify-center text-xs font-bold text-white shrink-0 bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]">
                      {idx + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-semibold text-white truncate">{s.title || s.scenario_id}</div>
                      <div className="text-[10px] text-slate-400 truncate">Timeframe: {horizon}</div>
                    </div>
                    <div className="w-16 flex flex-col items-end shrink-0 gap-1">
                      <div className="text-sm font-bold text-white">{((s.probability || s.uncalibrated_weight || 0) * 100).toFixed(0)}%</div>
                      <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{width: `${(s.probability || s.uncalibrated_weight || 0) * 100}%`}} />
                      </div>
                    </div>
                  </div>
                ))}
                {(!report.scenarios || report.scenarios.length === 0) && (
                  <div className="text-sm text-slate-500 text-center py-4">No scenarios generated</div>
                )}
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center">
                <LineChart className="w-8 h-8 text-slate-600 mb-2" />
                <div className="text-sm font-medium text-slate-400">CausalSeq model unavailable</div>
                <div className="text-xs text-slate-500">No forecast generated</div>
              </div>
            )}
          </div>
          
          {/* Middle Row */}
          
          {/* Supporting Evidence */}
          <div className="col-span-12 xl:col-span-3 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-delphi-green/20 rounded text-delphi-green">
                   <Database className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Supporting Evidence <span className="ml-1 bg-delphi-green/20 text-delphi-green text-[10px] px-1.5 py-0.5 rounded-full">{report.supporting_evidence?.length || 0}</span></h3>
              </div>
            </div>
            
            <div className="space-y-3 overflow-y-auto max-h-[300px] custom-scrollbar pr-2">
              {report.supporting_evidence?.length ? report.supporting_evidence.map((ev: any, i: number) => (
                <div key={i} className="flex gap-3">
                  <div className="w-6 h-6 rounded bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <Database className="w-3 h-3 text-slate-400" />
                  </div>
                  <div>
                    <a href={ev.url || '#'} target="_blank" rel="noreferrer" className="text-xs text-slate-200 font-medium leading-snug mb-0.5 hover:text-delphi-accent cursor-pointer block">{ev.summary || 'Evidence Item'}</a>
                    <div className="text-[10px] text-slate-500">{ev.source_id} • {ev.timestamp}</div>
                  </div>
                </div>
              )) : (
                <div className="text-xs text-slate-500 text-center py-4">No supporting evidence found.</div>
              )}
            </div>
          </div>
          
          {/* Conflicting Evidence */}
          <div className="col-span-12 xl:col-span-3 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-red-500/20 rounded text-red-400">
                   <AlertCircle className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Conflicting Evidence <span className="ml-1 bg-red-500/20 text-red-400 text-[10px] px-1.5 py-0.5 rounded-full">{report.contradictory_evidence?.length || 0}</span></h3>
              </div>
            </div>
            
            <div className="space-y-3 overflow-y-auto max-h-[300px] custom-scrollbar pr-2">
              {report.contradictory_evidence?.length ? report.contradictory_evidence.map((ev: any, i: number) => (
                <div key={i} className="flex gap-3">
                  <div className="w-6 h-6 rounded bg-red-900/20 border border-red-500/30 flex items-center justify-center shrink-0 mt-0.5">
                    <AlertCircle className="w-3 h-3 text-red-400" />
                  </div>
                  <div>
                    <a href={ev.url || '#'} target="_blank" rel="noreferrer" className="text-xs text-slate-200 font-medium leading-snug mb-0.5 hover:text-delphi-accent cursor-pointer block">{ev.summary || 'Evidence Item'}</a>
                    <div className="text-[10px] text-slate-500">{ev.source_id} • {ev.timestamp}</div>
                  </div>
                </div>
              )) : (
                <div className="text-xs text-slate-500 text-center py-4">No conflicting evidence found.</div>
              )}
            </div>
          </div>
          
          {/* Historical Analogues */}
          <div className="col-span-12 xl:col-span-6 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-blue-500/20 rounded text-blue-400">
                   <Scale className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Historical Analogues</h3>
              </div>
            </div>
            
            <div className="space-y-4 overflow-y-auto max-h-[300px] custom-scrollbar pr-2">
              {report.historical_analogues?.length ? report.historical_analogues.map((analogue: any, i: number) => (
                <div key={i} className="flex gap-4 p-3 bg-slate-900/50 rounded-lg border border-slate-800 hover:border-slate-600 transition-colors cursor-pointer group">
                  <div className="w-16 h-16 bg-slate-800 rounded flex items-center justify-center shrink-0">
                    <Scale className="w-6 h-6 text-slate-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="text-xs font-semibold text-white">{analogue.event_id || 'Analogue'}</h4>
                      <span className="text-[10px] font-medium text-delphi-green bg-delphi-green/10 px-1.5 py-0.5 rounded border border-delphi-green/20">Similarity {analogue.similarity_score?.toFixed(2)}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 mb-1">Date: {analogue.date}</p>
                    <p className="text-[10px] text-slate-300"><span className="font-semibold text-white">Outcome:</span> {analogue.outcomes?.length ? analogue.outcomes[0] : 'Unknown'}</p>
                  </div>
                </div>
              )) : (
                <div className="text-sm text-slate-500 text-center py-8">No historical analogues available.</div>
              )}
            </div>
          </div>
          
          {/* Bottom Row */}
          
          {/* Scenario Trajectories (Disabled when no calibration/data) */}
          <div className="col-span-12 xl:col-span-4 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center gap-2 mb-4">
               <div className="p-1.5 bg-purple-500/20 rounded text-purple-400">
                 <LineChart className="w-4 h-4" />
               </div>
               <h3 className="text-sm font-semibold text-white">Scenario Trajectories</h3>
            </div>
            <div className="flex-1 flex flex-col items-center justify-center text-center">
              <LineChart className="w-8 h-8 text-slate-600 mb-2" />
              <div className="text-sm font-medium text-slate-400">No verified trajectory data available.</div>
            </div>
          </div>
          
          {/* Key Indicators */}
          <div className="col-span-12 xl:col-span-3 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center gap-2 mb-4">
               <div className="p-1.5 bg-blue-500/20 rounded text-blue-400">
                 <Activity className="w-4 h-4" />
               </div>
               <h3 className="text-sm font-semibold text-white">Key Indicators to Watch</h3>
            </div>
            <div className="flex-1 flex flex-col items-center justify-center text-center">
              <div className="text-sm font-medium text-slate-400">No verified indicator data available.</div>
            </div>
          </div>
          
          {/* Source Map */}
          <div className="col-span-12 xl:col-span-3 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-blue-500/20 rounded text-blue-400">
                   <Map className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Source Map</h3>
              </div>
            </div>
            <div className="flex-1 flex flex-col items-center justify-center text-center">
              <Map className="w-8 h-8 text-slate-600 mb-2" />
              <div className="text-sm font-medium text-slate-400">Location unavailable</div>
            </div>
          </div>
          
          {/* Model Provenance */}
          <div className="col-span-12 xl:col-span-2 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center gap-2 mb-4">
               <div className="p-1.5 bg-blue-500/20 rounded text-blue-400">
                 <Database className="w-4 h-4" />
               </div>
               <h3 className="text-sm font-semibold text-white">Model Provenance</h3>
            </div>
            
            <div className="space-y-2 mb-4 flex-1 overflow-y-auto">
              <div className="text-[10px] text-slate-300">
                <span className="text-slate-500">EventEmbed:</span> {health?.dependencies?.eventembed || 'Unavailable'}
              </div>
              <div className="text-[10px] text-slate-300">
                <span className="text-slate-500">EventNet:</span> {health?.dependencies?.eventnet || 'Unavailable'}
              </div>
              <div className="text-[10px] text-slate-300">
                <span className="text-slate-500">CredNet:</span> {health?.dependencies?.crednet || 'Unavailable'}
              </div>
              <div className="text-[10px] text-slate-300">
                <span className="text-slate-500">CausalSeq:</span> {health?.dependencies?.causalseq || 'Unavailable'}
              </div>
            </div>
            
            <div className="mt-auto pt-3 border-t border-slate-800">
              <div className="flex flex-col gap-1 text-[8px]">
                <div className="flex justify-between"><span className="text-slate-500">Analysis ID</span><span className="text-slate-300 truncate w-24 text-right" title={report.analysis_id}>{report.analysis_id}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Generated</span><span className="text-slate-300">{report.timestamp}</span></div>
              </div>
            </div>
          </div>
          
        </div>
      )}
      
      {activeTab !== 'Overview' && (
        <div className="min-h-[400px] border border-delphi-border rounded-lg bg-delphi-card/50 flex flex-col items-center justify-center text-slate-500 p-8 text-center">
          <p>Tab content for {activeTab} is not implemented yet.</p>
        </div>
      )}
      
    </div>
  );
}
