import { useState } from 'react';
import { 
  LineChart, Activity, ShieldAlert, Scale, 
  Map, Database, Play, Calendar, ChevronDown, 
  ChevronRight, AlertCircle, Search, X
} from 'lucide-react';

export function Dashboard() {
  const [activeTab, setActiveTab] = useState('Overview');
  
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
                defaultValue="Escalation risk between Israel and Iran following recent military activities"
              />
              <div className="absolute bottom-2 right-2 text-[10px] text-slate-500">72/2000</div>
            </div>
          </div>
          
          <div className="w-[160px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Publication Date</label>
            <div className="relative">
              <Calendar className="w-4 h-4 text-slate-500 absolute left-2 top-1/2 -translate-y-1/2" />
              <input type="date" defaultValue="2024-12-15" className="w-full bg-slate-900/50 border border-slate-700/50 rounded-md pl-8 pr-2 py-2 text-xs text-white" />
            </div>
          </div>
          
          <div className="w-[160px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Prediction Cutoff</label>
            <div className="relative">
              <Calendar className="w-4 h-4 text-slate-500 absolute left-2 top-1/2 -translate-y-1/2" />
              <input type="date" defaultValue="2025-01-01" className="w-full bg-slate-900/50 border border-slate-700/50 rounded-md pl-8 pr-2 py-2 text-xs text-white" />
            </div>
          </div>
          
          <div className="w-[120px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Forecast Horizon</label>
            <div className="relative">
              <select className="w-full bg-slate-900/50 border border-slate-700/50 rounded-md pl-2 pr-6 py-2 text-xs text-white appearance-none">
                <option>3 months</option>
                <option>6 months</option>
              </select>
              <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
          
          <div className="w-[200px]">
            <label className="block text-[10px] font-medium text-slate-400 mb-1">Domains</label>
            <div className="flex flex-wrap gap-1 mb-1">
              <span className="bg-delphi-blue/20 text-delphi-accent border border-delphi-blue/30 text-[10px] px-2 py-0.5 rounded flex items-center gap-1">Geopolitics <X className="w-3 h-3" /></span>
              <span className="bg-slate-800 text-slate-300 border border-slate-700 text-[10px] px-2 py-0.5 rounded flex items-center gap-1">Security <X className="w-3 h-3" /></span>
              <span className="bg-slate-800 text-slate-300 border border-slate-700 text-[10px] px-2 py-0.5 rounded flex items-center gap-1">Energy <X className="w-3 h-3" /></span>
            </div>
            <div className="text-[10px] text-delphi-accent cursor-pointer">+ Add domain</div>
          </div>
          
          <div className="pt-4 shrink-0">
            <button className="bg-delphi-blue hover:bg-delphi-blueHover text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 shadow-lg shadow-delphi-blue/20 transition-all">
              <Play className="w-4 h-4 fill-white" /> Run Analysis
            </button>
          </div>
        </div>
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
      {activeTab === 'Overview' && (
        <div className="grid grid-cols-12 gap-4">
          
          {/* Top Row */}
          
          {/* Current Event Analysis */}
          <div className="col-span-12 xl:col-span-4 glass-card rounded-xl p-4 flex flex-col glow-border relative overflow-hidden">
             <div className="flex items-center gap-2 mb-4">
               <div className="p-1.5 bg-indigo-500/20 rounded text-indigo-400">
                 <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
               </div>
               <h3 className="text-sm font-semibold text-white">Current Event Analysis</h3>
               <div className="ml-auto flex items-center gap-2 bg-slate-900/80 rounded-full pl-2 pr-1 py-0.5 border border-slate-700">
                 <span className="text-[10px] text-slate-400">Confidence</span>
                 <span className="bg-delphi-green/20 text-delphi-green text-xs font-bold px-1.5 py-0.5 rounded">0.87</span>
               </div>
             </div>
             
             <div className="flex gap-4 mb-4">
               <div className="flex-1 text-sm text-slate-300 leading-relaxed">
                 <span className="bg-yellow-500/20 text-yellow-300 px-1 rounded mx-0.5 border border-yellow-500/30">Iran</span> has 
                 <span className="bg-blue-500/20 text-blue-300 px-1 rounded mx-0.5 border border-blue-500/30">Israel</span> 
                 <span className="bg-purple-500/20 text-purple-300 px-1 rounded mx-0.5 border border-purple-500/30">increased</span> uranium enrichment activities, prompting 
                 <span className="bg-yellow-500/20 text-yellow-300 px-1 rounded mx-0.5 border border-yellow-500/30">Israel</span> to 
                 <span className="bg-purple-500/20 text-purple-300 px-1 rounded mx-0.5 border border-purple-500/30">place</span> its military on higher alert, according to regional sources.
               </div>
               <div className="w-24 h-16 rounded border border-slate-700 bg-[url('https://images.unsplash.com/photo-1579273166152-d725a4e2b755?q=80&w=200&auto=format&fit=crop')] bg-cover bg-center shrink-0" />
             </div>
             
             <div className="flex flex-wrap gap-2 mb-4">
               <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-1.5 h-1.5 rounded-full bg-yellow-400" /> Actor: Iran</span>
               <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-1.5 h-1.5 rounded-full bg-yellow-400" /> Actor: Israel</span>
               <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-1.5 h-1.5 rounded-full bg-purple-400" /> Action: increased</span>
               <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-1.5 h-1.5 rounded-full bg-purple-400" /> Action: place</span>
               <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-1.5 h-1.5 rounded-full bg-orange-400" /> Object: uranium enrichment</span>
               <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-1.5 h-1.5 rounded-full bg-blue-400" /> Object: military</span>
               <span className="flex items-center gap-1 text-[10px] text-slate-400"><div className="w-1.5 h-1.5 rounded-full bg-teal-400" /> Location: Middle East</span>
             </div>
             
             <div className="mt-auto">
               <h4 className="text-xs font-semibold text-slate-200 mb-2">Event Graph</h4>
               <div className="flex items-center justify-between mt-4 pb-2 relative">
                 {/* Connectors */}
                 <div className="absolute top-4 left-[10%] right-[10%] h-px bg-slate-700 -z-10" />
                 
                 <div className="flex flex-col items-center">
                   <div className="w-8 h-8 rounded-full bg-red-900 border border-red-500 flex items-center justify-center text-xs shadow-[0_0_10px_rgba(239,68,68,0.3)] mb-1">🇮🇷</div>
                   <div className="text-[10px] font-medium text-white">Iran</div>
                   <div className="text-[9px] text-slate-500">(Actor)</div>
                 </div>
                 
                 <div className="text-[9px] text-slate-400 bg-delphi-card px-1 -mt-4">increased</div>
                 
                 <div className="flex flex-col items-center">
                   <div className="w-8 h-8 rounded-full bg-yellow-900 border border-yellow-500 flex items-center justify-center text-xs shadow-[0_0_10px_rgba(234,179,8,0.3)] mb-1">⚛️</div>
                   <div className="text-[10px] font-medium text-white text-center">Uranium<br/>Enrichment</div>
                   <div className="text-[9px] text-slate-500">(Activity)</div>
                 </div>
                 
                 <div className="text-[9px] text-slate-400 bg-delphi-card px-1 -mt-4">prompted</div>
                 
                 <div className="flex flex-col items-center">
                   <div className="w-8 h-8 rounded-full bg-blue-900 border border-blue-500 flex items-center justify-center text-xs shadow-[0_0_10px_rgba(59,130,246,0.3)] mb-1">🇮🇱</div>
                   <div className="text-[10px] font-medium text-white">Israel</div>
                   <div className="text-[9px] text-slate-500">(Actor)</div>
                 </div>
                 
                 <div className="text-[9px] text-slate-400 bg-delphi-card px-1 -mt-4">place</div>
                 
                 <div className="flex flex-col items-center">
                   <div className="w-8 h-8 rounded-full bg-green-900 border border-green-500 flex items-center justify-center text-xs shadow-[0_0_10px_rgba(34,197,94,0.3)] mb-1"><ShieldAlert className="w-4 h-4 text-white" /></div>
                   <div className="text-[10px] font-medium text-white text-center">Military on<br/>Higher Alert</div>
                   <div className="text-[9px] text-slate-500">(Outcome)</div>
                 </div>
               </div>
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
            
            <div className="flex items-center gap-8 mb-6">
              {/* Circular Progress */}
              <div className="relative w-32 h-32 flex items-center justify-center shrink-0">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" strokeWidth="8" />
                  <circle cx="50" cy="50" r="45" fill="none" stroke="#10b981" strokeWidth="8" strokeDasharray="283" strokeDashoffset="79" className="drop-shadow-[0_0_8px_rgba(16,185,129,0.8)]" strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <div className="text-3xl font-bold text-white">0.72</div>
                  <div className="text-[9px] text-slate-400 text-center uppercase leading-tight">Overall<br/>Credibility</div>
                </div>
                <div className="absolute -bottom-6 text-xs text-delphi-green font-medium whitespace-nowrap left-1/2 -translate-x-1/2">
                  (Moderately High)
                </div>
              </div>
              
              <div className="flex-1 space-y-4">
                <h4 className="text-xs font-semibold text-slate-200">Credibility Signals</h4>
                <div className="space-y-3">
                  {[
                    { label: 'Source Reliability', val: 0.81, w: '81%', color: 'bg-blue-500' },
                    { label: 'Content Consistency', val: 0.68, w: '68%', color: 'bg-blue-500' },
                    { label: 'Cross-Source Agreement', val: 0.74, w: '74%', color: 'bg-delphi-green' },
                    { label: 'Temporal Plausibility', val: 0.78, w: '78%', color: 'bg-delphi-green' }
                  ].map(s => (
                    <div key={s.label} className="flex items-center justify-between text-xs">
                      <span className="text-slate-400">{s.label}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div className={`h-full ${s.color}`} style={{width: s.w}} />
                        </div>
                        <span className="text-slate-300 w-6 text-right">{s.val.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="mt-auto flex items-start gap-4 pt-4 border-t border-slate-800">
              <div>
                <div className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">Classification</div>
                <div className="bg-delphi-green/20 border border-delphi-green/30 text-delphi-green px-3 py-1.5 rounded text-sm font-medium">Likely Factual</div>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed pt-1">
                This event is likely factual based on source reliability, content consistency, and multi-source corroboration.
              </p>
            </div>
          </div>
          
          {/* Scenario Forecast */}
          <div className="col-span-12 xl:col-span-4 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-purple-500/20 rounded text-purple-400">
                   <LineChart className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Scenario Forecast (3 Months)</h3>
              </div>
              <div className="bg-yellow-500/20 border border-yellow-500/30 text-yellow-300 px-2 py-1 rounded text-[9px] font-medium flex flex-col items-center leading-tight">
                <span>⚠️ UNCALIBRATED</span>
                <span className="opacity-70 text-[8px]">Scenario weights (not probabilities)</span>
              </div>
            </div>
            
            <div className="space-y-3 flex-1 flex flex-col justify-center">
              {[
                { n: 1, title: 'Limited Military Escalation', desc: 'Localized strikes or proxy conflicts without full-scale war.', pct: '42%', w: '42%', color: 'bg-blue-500', img: 'https://images.unsplash.com/photo-1596728479262-67c4df2d6342?q=80&w=100&auto=format&fit=crop' },
                { n: 2, title: 'Diplomatic De-escalation', desc: 'Renewed negotiations reduce immediate tensions.', pct: '28%', w: '28%', color: 'bg-delphi-green', img: 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?q=80&w=100&auto=format&fit=crop' },
                { n: 3, title: 'Continued Status Quo', desc: 'Tensions persist without major changes.', pct: '18%', w: '18%', color: 'bg-orange-500', img: 'https://images.unsplash.com/photo-1447023340578-83b6324a0dff?q=80&w=100&auto=format&fit=crop' },
                { n: 4, title: 'Full-Scale Conflict', desc: 'Direct military confrontation between Israel and Iran.', pct: '12%', w: '12%', color: 'bg-pink-500', img: 'https://images.unsplash.com/photo-1533596739773-45bb9cc233d6?q=80&w=100&auto=format&fit=crop' },
              ].map(s => (
                <div key={s.n} className="flex items-center gap-3 p-2 rounded-lg hover:bg-white/5 border border-transparent hover:border-white/10 transition-colors">
                  <div className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-[0_0_8px_rgba(0,0,0,0.5)]`} style={{backgroundColor: s.color === 'bg-blue-500' ? '#3b82f6' : s.color === 'bg-delphi-green' ? '#10b981' : s.color === 'bg-orange-500' ? '#f97316' : '#ec4899'}}>
                    {s.n}
                  </div>
                  <div className="w-10 h-10 rounded overflow-hidden shrink-0">
                    <img src={s.img} alt={s.title} className="w-full h-full object-cover" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-white truncate">{s.title}</div>
                    <div className="text-[10px] text-slate-400 truncate">{s.desc}</div>
                  </div>
                  <div className="w-16 flex flex-col items-end shrink-0 gap-1">
                    <div className="text-sm font-bold text-white">{s.pct}</div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div className={`h-full ${s.color}`} style={{width: s.w}} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Middle Row */}
          
          {/* Supporting Evidence */}
          <div className="col-span-12 xl:col-span-3 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-delphi-green/20 rounded text-delphi-green">
                   <Database className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Supporting Evidence <span className="ml-1 bg-delphi-green/20 text-delphi-green text-[10px] px-1.5 py-0.5 rounded-full">12</span></h3>
              </div>
              <div className="text-[10px] text-delphi-accent flex items-center cursor-pointer">View All <ChevronRight className="w-3 h-3" /></div>
            </div>
            
            <div className="space-y-3">
              {[
                { title: 'IAEA reports increased uranium enrichment at Fordow', source: 'Reuters', date: 'Dec 14, 2024', tag: 'High', color: 'text-delphi-green border-delphi-green/30', bg: 'bg-delphi-green/10' },
                { title: 'Israel military on high alert, officials say', source: 'BBC', date: 'Dec 13, 2024', tag: 'High', color: 'text-delphi-green border-delphi-green/30', bg: 'bg-delphi-green/10' },
                { title: 'Satellite images show activity at Fordow facility', source: 'CSIS', date: 'Dec 12, 2024', tag: 'Medium', color: 'text-yellow-400 border-yellow-400/30', bg: 'bg-yellow-400/10' }
              ].map((ev, i) => (
                <div key={i} className="flex gap-3">
                  <div className="w-6 h-6 rounded bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-3 h-3 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5L18.5 7H20z" /></svg>
                  </div>
                  <div>
                    <div className="text-xs text-slate-200 font-medium leading-snug mb-0.5 hover:text-delphi-accent cursor-pointer">{ev.title}</div>
                    <div className="text-[10px] text-slate-500">{ev.source} • {ev.date}</div>
                  </div>
                  <div className="ml-auto shrink-0">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded border ${ev.color} ${ev.bg}`}>{ev.tag}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Conflicting Evidence */}
          <div className="col-span-12 xl:col-span-3 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                 <div className="p-1.5 bg-red-500/20 rounded text-red-400">
                   <AlertCircle className="w-4 h-4" />
                 </div>
                 <h3 className="text-sm font-semibold text-white">Conflicting Evidence <span className="ml-1 bg-red-500/20 text-red-400 text-[10px] px-1.5 py-0.5 rounded-full">5</span></h3>
              </div>
              <div className="text-[10px] text-delphi-accent flex items-center cursor-pointer">View All <ChevronRight className="w-3 h-3" /></div>
            </div>
            
            <div className="space-y-3">
              {[
                { title: 'IAEA finds no significant change in enrichment levels', source: 'Al Jazeera', date: 'Dec 14, 2024', tag: 'Medium', color: 'text-yellow-400 border-yellow-400/30', bg: 'bg-yellow-400/10' },
                { title: 'Iran denies increased enrichment activities', source: 'PressTV', date: 'Dec 13, 2024', tag: 'Low', color: 'text-slate-400 border-slate-600', bg: 'bg-slate-800' },
                { title: 'Analysts believe escalation unlikely in near term', source: 'Brookings', date: 'Dec 11, 2024', tag: 'Medium', color: 'text-yellow-400 border-yellow-400/30', bg: 'bg-yellow-400/10' }
              ].map((ev, i) => (
                <div key={i} className="flex gap-3">
                  <div className="w-6 h-6 rounded bg-red-900/20 border border-red-500/30 flex items-center justify-center shrink-0 mt-0.5">
                    <svg className="w-3 h-3 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9.5L18.5 7H20z" /></svg>
                  </div>
                  <div>
                    <div className="text-xs text-slate-200 font-medium leading-snug mb-0.5 hover:text-delphi-accent cursor-pointer">{ev.title}</div>
                    <div className="text-[10px] text-slate-500">{ev.source} • {ev.date}</div>
                  </div>
                  <div className="ml-auto shrink-0">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded border ${ev.color} ${ev.bg}`}>{ev.tag}</span>
                  </div>
                </div>
              ))}
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
              <div className="text-[10px] text-delphi-accent flex items-center cursor-pointer">View All <ChevronRight className="w-3 h-3" /></div>
            </div>
            
            <div className="space-y-4">
              <div className="flex gap-4 p-3 bg-slate-900/50 rounded-lg border border-slate-800 hover:border-slate-600 transition-colors cursor-pointer group">
                <div className="w-24 h-16 rounded overflow-hidden shrink-0">
                  <img src="https://images.unsplash.com/photo-1541888062948-435520847932?q=80&w=200&auto=format&fit=crop" alt="Analogue" className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-xs font-semibold text-white">2012 Iran Nuclear Tensions</h4>
                    <span className="text-[10px] font-medium text-delphi-green bg-delphi-green/10 px-1.5 py-0.5 rounded border border-delphi-green/20">Similarity 0.78</span>
                  </div>
                  <p className="text-[10px] text-slate-400 mb-1">Similar pattern of enrichment activity and international response.</p>
                  <p className="text-[10px] text-slate-300"><span className="font-semibold text-white">Outcome:</span> Increased sanctions, no military conflict</p>
                </div>
                <div className="flex items-center text-slate-600 group-hover:text-white transition-colors">
                  <ChevronRight className="w-4 h-4" />
                </div>
              </div>
              
              <div className="flex gap-4 p-3 bg-slate-900/50 rounded-lg border border-slate-800 hover:border-slate-600 transition-colors cursor-pointer group">
                <div className="w-24 h-16 rounded overflow-hidden shrink-0">
                  <img src="https://images.unsplash.com/photo-1599839619722-39751411ea63?q=80&w=200&auto=format&fit=crop" alt="Analogue" className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-xs font-semibold text-white">2006 Israeli-Lebanese Conflict</h4>
                    <span className="text-[10px] font-medium text-delphi-green bg-delphi-green/10 px-1.5 py-0.5 rounded border border-delphi-green/20">Similarity 0.62</span>
                  </div>
                  <p className="text-[10px] text-slate-400 mb-1">Similar regional dynamics and proxy involvement.</p>
                  <p className="text-[10px] text-slate-300"><span className="font-semibold text-white">Outcome:</span> Limited conflict, diplomatic resolution</p>
                </div>
                <div className="flex items-center text-slate-600 group-hover:text-white transition-colors">
                  <ChevronRight className="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>
          
          {/* Bottom Row */}
          
          {/* Scenario Trajectories */}
          <div className="col-span-12 xl:col-span-4 glass-card rounded-xl p-4 flex flex-col glow-border">
            <div className="flex items-center gap-2 mb-4">
               <div className="p-1.5 bg-purple-500/20 rounded text-purple-400">
                 <LineChart className="w-4 h-4" />
               </div>
               <h3 className="text-sm font-semibold text-white">Scenario Trajectories</h3>
            </div>
            
            <div className="flex-1 flex relative items-end pl-6 pb-6 pt-2">
              {/* Y Axis */}
              <div className="absolute left-0 top-0 bottom-6 w-6 flex flex-col justify-between items-end pr-2 text-[8px] text-slate-500">
                <span>0.6</span><span>0.4</span><span>0.2</span><span>0.0</span>
              </div>
              <div className="absolute left-6 top-0 bottom-6 w-px bg-slate-700" />
              <div className="absolute left-6 bottom-6 right-0 h-px bg-slate-700" />
              
              {/* X Axis labels */}
              <div className="absolute bottom-0 left-6 right-32 flex justify-between text-[8px] text-slate-500 pt-2">
                <span>Jan 2025</span><span>Feb 2025</span><span>Mar 2025</span><span>Apr 2025</span>
              </div>
              
              {/* Grid lines */}
              <div className="absolute left-6 top-1/4 right-32 h-px bg-slate-800/50" />
              <div className="absolute left-6 top-2/4 right-32 h-px bg-slate-800/50" />
              <div className="absolute left-6 top-3/4 right-32 h-px bg-slate-800/50" />
              
              {/* Fake SVG lines to match visual */}
              <svg className="w-full h-full pr-32 overflow-visible" preserveAspectRatio="none" viewBox="0 0 100 100">
                <polyline points="0,50 10,45 20,60 30,55 40,30 50,45 60,35 70,25 80,40 90,30 100,20" fill="none" stroke="#3b82f6" strokeWidth="2" />
                <polyline points="0,70 10,65 20,70 30,60 40,55 50,65 60,60 70,70 80,55 90,60 100,50" fill="none" stroke="#10b981" strokeWidth="2" />
                <polyline points="0,85 10,80 20,85 30,85 40,80 50,85 60,80 70,85 80,80 90,85 100,80" fill="none" stroke="#f97316" strokeWidth="2" />
                <polyline points="0,95 10,95 20,90 30,95 40,90 50,95 60,90 70,95 80,85 90,90 100,80" fill="none" stroke="#ec4899" strokeWidth="2" />
                
                {/* Dots on the ends */}
                <circle cx="100" cy="20" r="3" fill="#3b82f6" />
                <circle cx="100" cy="50" r="3" fill="#10b981" />
                <circle cx="100" cy="80" r="3" fill="#f97316" />
                <circle cx="100" cy="80" r="3" fill="#ec4899" />
              </svg>
              
              {/* Legend right side */}
              <div className="absolute right-0 top-1/2 -translate-y-1/2 flex flex-col gap-2">
                <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /><span className="text-[9px] text-slate-300">Limited Escalation</span></div>
                <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-delphi-green" /><span className="text-[9px] text-slate-300">Diplomatic Resolution</span></div>
                <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-orange-500" /><span className="text-[9px] text-slate-300">Status Quo</span></div>
                <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-pink-500" /><span className="text-[9px] text-slate-300">Full-Scale Conflict</span></div>
              </div>
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
            
            <div className="space-y-3">
              {[
                { icon: '🪖', title: 'Military Activity', desc: 'Troop movements, strikes, exercises', tag: 'High', color: 'text-red-400 border-red-500/30 bg-red-900/20' },
                { icon: '🤝', title: 'Diplomatic Engagement', desc: 'Negotiations, mediator involvement', tag: 'Medium', color: 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10' },
                { icon: '⚛️', title: 'Nuclear Activity', desc: 'Enrichment levels, IAEA reports', tag: 'Medium', color: 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10' },
                { icon: '⚖️', title: 'International Sanctions', desc: 'New sanctions or policy changes', tag: 'Low', color: 'text-delphi-green border-delphi-green/30 bg-delphi-green/10' }
              ].map(ind => (
                <div key={ind.title} className="flex gap-3 items-center">
                  <div className="w-8 h-8 rounded bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-sm">
                    {ind.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-white">{ind.title}</div>
                    <div className="text-[9px] text-slate-400 truncate">{ind.desc}</div>
                  </div>
                  <div className="shrink-0">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded border ${ind.color}`}>{ind.tag}</span>
                  </div>
                </div>
              ))}
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
              <div className="text-[10px] text-delphi-accent flex items-center cursor-pointer">View Interactive <ChevronRight className="w-3 h-3" /></div>
            </div>
            
            <div className="flex-1 relative flex flex-col justify-center pb-8 pt-2">
              <div className="h-24 w-full bg-[url('https://upload.wikimedia.org/wikipedia/commons/8/80/World_map_-_low_resolution.svg')] bg-contain bg-no-repeat bg-center opacity-30 invert-[.8]" />
              {/* Fake pins */}
              <div className="absolute top-[40%] left-[30%] w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_5px_#3b82f6]" />
              <div className="absolute top-[35%] left-[50%] w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_5px_#ec4899]" />
              <div className="absolute top-[45%] left-[55%] w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_5px_#facc15]" />
              <div className="absolute top-[30%] left-[45%] w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_5px_#3b82f6]" />
              <div className="absolute top-[50%] left-[65%] w-2 h-2 rounded-full bg-delphi-green shadow-[0_0_5px_#10b981]" />
              
              {/* Legend */}
              <div className="absolute top-0 right-0 flex flex-col gap-1">
                <div className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /><span className="text-[8px] text-slate-300">News Media</span></div>
                <div className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-yellow-400" /><span className="text-[8px] text-slate-300">Official Sources</span></div>
                <div className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-pink-500" /><span className="text-[8px] text-slate-300">Think Tanks</span></div>
                <div className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-red-500" /><span className="text-[8px] text-slate-300">Academic</span></div>
                <div className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" /><span className="text-[8px] text-slate-300">Social Media</span></div>
              </div>
              
              <div className="absolute bottom-0 left-0 right-0">
                <div className="text-[9px] text-slate-400 mb-1 font-medium">Source Distribution</div>
                <div className="w-full h-2 rounded-full overflow-hidden flex bg-slate-800">
                  <div className="h-full bg-blue-500" style={{width: '45%'}} />
                  <div className="h-full bg-yellow-400" style={{width: '25%'}} />
                  <div className="h-full bg-pink-500" style={{width: '15%'}} />
                  <div className="h-full bg-red-500" style={{width: '10%'}} />
                  <div className="h-full bg-purple-500" style={{width: '5%'}} />
                </div>
                <div className="flex text-[8px] text-slate-500 mt-0.5 justify-between px-1">
                  <span>45%</span><span>25%</span><span>15%</span><span>10%</span><span>5%</span>
                </div>
              </div>
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
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 text-slate-400">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                </div>
                <div>
                  <div className="text-[10px] font-semibold text-white">EventEmbed</div>
                  <div className="text-[9px] text-slate-400">v1.2.0</div>
                  <div className="text-[8px] text-slate-500">Trained: 2024-06-01</div>
                  <div className="text-[8px] text-slate-500 truncate w-24">Data: GDELT (2018-2023)</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-purple-900/40 border border-purple-500/30 flex items-center justify-center shrink-0 text-purple-400">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                </div>
                <div>
                  <div className="text-[10px] font-semibold text-white">EventNet</div>
                  <div className="text-[9px] text-slate-400">v1.1.0</div>
                  <div className="text-[8px] text-slate-500">Trained: 2024-06-15</div>
                  <div className="text-[8px] text-slate-500 truncate w-24">Data: GDELT (2018-2023)</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-red-900/40 border border-red-500/30 flex items-center justify-center shrink-0 text-red-400">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                </div>
                <div>
                  <div className="text-[10px] font-semibold text-white">CredNet</div>
                  <div className="text-[9px] text-slate-400">v1.0.0</div>
                  <div className="text-[8px] text-slate-500">Trained: 2024-07-01</div>
                  <div className="text-[8px] text-slate-500 truncate w-24">Data: News + FactCheck</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded bg-delphi-green/20 border border-delphi-green/30 flex items-center justify-center shrink-0 text-delphi-green">
                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
                </div>
                <div>
                  <div className="text-[10px] font-semibold text-white">CausalSeq</div>
                  <div className="text-[9px] text-slate-400">v1.0.0</div>
                  <div className="text-[8px] text-slate-500">Trained: 2024-07-15</div>
                  <div className="text-[8px] text-slate-500 truncate w-24">Data: GDELT (2018-2023)</div>
                </div>
              </div>
            </div>
            
            <div className="mt-auto pt-3 border-t border-slate-800">
              <div className="flex items-center justify-between text-[8px] mb-1">
                <span className="text-slate-500 font-medium">Analysis ID</span>
                <span className="text-slate-300 font-mono">a3f2e1c4-5b6d-7e8f-9a0b-c1d2e3f4g5h6</span>
              </div>
              <div className="flex items-center justify-between text-[8px]">
                <span className="text-slate-500 font-medium">Generated</span>
                <span className="text-slate-300">Jan 8, 2025 14:32 UTC</span>
              </div>
            </div>
          </div>
          
        </div>
      )}
      
      {activeTab !== 'Overview' && (
        <div className="min-h-[400px] border border-delphi-border rounded-lg bg-delphi-card/50 flex flex-col items-center justify-center text-slate-500 p-8 text-center">
          <p>Tab content for {activeTab} is not implemented in this static layout mock.</p>
        </div>
      )}
      
    </div>
  );
}
