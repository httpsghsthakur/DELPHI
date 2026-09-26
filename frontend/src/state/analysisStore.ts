import { create } from 'zustand';
import { ForecastReport, HealthResponse } from '../api/types';

interface AnalysisState {
  report: ForecastReport | null;
  loading: boolean;
  error: string | null;
  systemStatus: HealthResponse | null;
  
  setReport: (report: ForecastReport) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setSystemStatus: (status: HealthResponse) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  report: null,
  loading: false,
  error: null,
  systemStatus: null,
  
  setReport: (report) => set({ report, loading: false, error: null }),
  setLoading: (loading) => set({ loading, error: loading ? null : useAnalysisStore.getState().error }),
  setError: (error) => set({ error, loading: false }),
  setSystemStatus: (status) => set({ systemStatus: status }),
  reset: () => set({ report: null, loading: false, error: null })
}));
