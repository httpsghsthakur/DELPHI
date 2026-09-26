import { 
  Globe, Activity, Search, Clock, BarChart3, Database, 
  Settings, CheckCircle2, Check, Bell, XCircle, AlertTriangle
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';
import { HealthResponse } from '../../api/types';

export function Layout({ children }: { children: React.ReactNode }) {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    apiClient.getHealth().then(setHealth).catch(console.error);
  }, []);

  const getStatusIcon = (status?: string) => {
    if (status === 'ok') return <div className="w-3.5 h-3.5 bg-delphi-green/20 rounded-sm flex items-center justify-center"><Check className="w-2.5 h-2.5 text-delphi-green" /></div>;
    if (status === 'missing') return <div className="w-3.5 h-3.5 bg-red-900/40 rounded-sm flex items-center justify-center"><XCircle className="w-2.5 h-2.5 text-red-500" /></div>;
    return <div className="w-3.5 h-3.5 bg-yellow-900/40 rounded-sm flex items-center justify-center"><AlertTriangle className="w-2.5 h-2.5 text-yellow-500" /></div>;
  };
  
  const getDot = (status?: string) => {
    if (status === 'ok') return <div className="w-2 h-2 rounded-full bg-delphi-green" />;
    if (status === 'missing') return <div className="w-2 h-2 rounded-full bg-red-500" />;
    return <div className="w-2 h-2 rounded-full bg-yellow-500" />;
  };

  return (
    <div className="flex h-screen w-full bg-delphi-bg overflow-hidden text-slate-300 font-sans">
      
      {/* Background Image (Globe) - absolute positioned at top */}
      <div 
        className="absolute top-0 right-0 w-full h-[400px] bg-globe bg-no-repeat bg-right-top bg-cover opacity-60 pointer-events-none z-0"
        style={{ mixBlendMode: 'screen', maskImage: 'linear-gradient(to bottom, black 20%, transparent 100%)' }}
      />
      
      {/* Sidebar */}
      <div className="w-[260px] bg-delphi-sidebar/95 backdrop-blur-md border-r border-delphi-border flex flex-col z-10 shrink-0">
        
        {/* Logo Area */}
        <div className="p-6 pb-4">
          <div className="flex items-center gap-3 mb-1">
            <Globe className="w-8 h-8 text-delphi-blue" />
            <h1 className="text-2xl font-bold tracking-wider text-white">DELPHI</h1>
          </div>
          <p className="text-[10px] text-slate-400 leading-tight">
            Structured Intelligence<br/>for a More Predictable World
          </p>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 px-3 space-y-1 mt-4">
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 bg-delphi-blue text-white rounded-md font-medium text-sm">
            <Activity className="w-4 h-4" /> New Analysis
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-md font-medium text-sm transition-colors">
            <Search className="w-4 h-4" /> Live Research
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-md font-medium text-sm transition-colors">
            <Search className="w-4 h-4" /> Historical Search
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-md font-medium text-sm transition-colors">
            <Clock className="w-4 h-4" /> Backtests
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-md font-medium text-sm transition-colors mt-4">
            <BarChart3 className="w-4 h-4" /> Model Performance
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-md font-medium text-sm transition-colors">
            <Database className="w-4 h-4" /> Data Sources
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-md font-medium text-sm transition-colors">
            <CheckCircle2 className="w-4 h-4" /> System Status
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2.5 text-slate-400 hover:text-white hover:bg-white/5 rounded-md font-medium text-sm transition-colors">
            <Settings className="w-4 h-4" /> Settings
          </a>
        </nav>
        
        {/* System Status Panel */}
        <div className="p-5 border-t border-delphi-border">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">System Status</h3>
          <div className="space-y-1.5 mb-6">
            {[
              { label: 'Tokenizer', key: 'tokenizer' },
              { label: 'EventEmbed', key: 'eventembed' },
              { label: 'EventNet', key: 'eventnet' },
              { label: 'CredNet', key: 'crednet' },
              { label: 'CausalSeq', key: 'causalseq' },
              { label: 'Historical Index', key: 'retrieval_index' },
              { label: 'Calibration', key: 'calibration' }
            ].map(sys => {
              const statusVal = health?.dependencies?.[sys.key] || 'missing';
              return (
                <div key={sys.label} className="flex justify-between items-center text-[11px] text-slate-300">
                  <div className="flex items-center gap-2">
                    {getDot(statusVal)}
                    {sys.label}
                    {statusVal === 'missing' && <span className="text-[8px] text-red-500">NOT READY</span>}
                  </div>
                  {getStatusIcon(statusVal)}
                </div>
              );
            })}
          </div>
          
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Execution Mode</h3>
          <div className="flex items-center gap-2 mb-4">
            <div className={`w-2 h-2 rounded-full ${health?.execution_mode === 'REAL' ? 'bg-delphi-green' : 'bg-delphi-orange'}`} />
            <div>
              <div className="text-sm font-medium text-white">{health?.execution_mode || 'UNKNOWN'}</div>
              <div className="text-[10px] text-slate-400">{health?.execution_mode === 'REAL' ? '(using trained models)' : '(synthetic mode)'}</div>
            </div>
          </div>
          
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Calibration</h3>
          <div className="flex items-center gap-2 mb-4">
            <div className={`w-2 h-2 rounded-full ${health?.dependencies?.calibration === 'ok' ? 'bg-delphi-green' : 'bg-red-500'}`} />
            <div>
              <div className="text-sm font-medium text-white">{health?.dependencies?.calibration === 'ok' ? 'CALIBRATED' : 'UNCALIBRATED'}</div>
              <div className="text-[10px] text-slate-400">{health?.dependencies?.calibration === 'ok' ? '(ready for production)' : '(research mode)'}</div>
            </div>
          </div>
          
          <div className="text-[10px] text-slate-500 mt-2">DELPHI {health?.api_version || 'v0.1.0'}</div>
        </div>
      </div>
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 z-10 relative">
        
        {/* Top Header Bar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-white/5 bg-transparent">
          <div className="flex-1 max-w-xl relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Search past analyses, topics, or events..." 
              className="w-full bg-white/5 border border-white/10 rounded-full pl-10 pr-4 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-delphi-accent focus:bg-white/10 transition-colors"
            />
          </div>
          <div className="flex items-center gap-6">
            <div className="text-sm font-medium text-slate-300">Jan 8, 2025 14:32 UTC</div>
            <div className="relative">
              <Bell className="w-5 h-5 text-slate-300" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-pink-500 rounded-full border-2 border-delphi-bg flex items-center justify-center text-[8px] text-white font-bold">3</div>
            </div>
            <div className="w-8 h-8 rounded-full bg-slate-700 border border-slate-600 flex items-center justify-center text-white font-semibold">
              D
            </div>
          </div>
        </header>
        
        {/* Page Content */}
        <main className="flex-1 overflow-auto custom-scrollbar p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
