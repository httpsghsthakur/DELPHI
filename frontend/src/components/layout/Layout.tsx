import { ReactNode, useEffect } from 'react';
import { Activity, Database, ShieldAlert, ShieldCheck, AlertCircle } from 'lucide-react';
import { useAnalysisStore } from '../../state/analysisStore';
import { apiClient } from '../../api/client';
import { Link } from 'react-router-dom';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { systemStatus, setSystemStatus } = useAnalysisStore();

  useEffect(() => {
    apiClient.getHealth()
      .then(setSystemStatus)
      .catch(console.error);
  }, [setSystemStatus]);

  const isReady = systemStatus?.status === 'ok';

  return (
    <div className="min-h-screen flex flex-col bg-delphi-dark text-slate-300">
      <header className="border-b border-delphi-border bg-delphi-card px-6 py-4 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-delphi-accent font-semibold tracking-wider text-xl">
            <Activity className="w-6 h-6" />
            <span>DELPHI</span>
          </div>
          <div className="h-4 w-px bg-slate-700 mx-2" />
          <nav className="flex items-center gap-4 text-sm">
            <Link to="/" className="text-slate-300 hover:text-white transition-colors">Dashboard</Link>
          </nav>
        </div>
        
        <div className="flex items-center gap-6 text-sm">
          {systemStatus && (
            <>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">DATA:</span>
                <span className={systemStatus.execution_mode === 'REAL' ? 'text-green-400 font-medium' : 'text-yellow-400 font-medium'}>
                  {systemStatus.execution_mode}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-slate-400">TEMPORAL VALIDATION:</span>
                {systemStatus.temporal_mode === 'strict' ? (
                   <div className="flex items-center gap-1 text-green-400 font-medium">
                     <ShieldCheck className="w-4 h-4" /> VERIFIED
                   </div>
                ) : (
                   <div className="flex items-center gap-1 text-red-400 font-medium">
                     <ShieldAlert className="w-4 h-4" /> UNVERIFIED
                   </div>
                )}
              </div>
              <div className="h-4 w-px bg-slate-700" />
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-slate-400" />
                {isReady ? (
                  <span className="text-green-400 flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    SYSTEM READY
                  </span>
                ) : (
                  <span className="text-red-400 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    UNAVAILABLE
                  </span>
                )}
              </div>
            </>
          )}
        </div>
      </header>

      <main className="flex-1 overflow-x-hidden">
        {children}
      </main>
    </div>
  );
}
