import { create } from "zustand";
import { apiClient } from "../api/client";
import type {
  AnalysisRequest,
  ForecastReport,
  HealthResponse,
  ModelStatus,
  ResearchReport,
} from "../api/types";
export interface SessionAnalysis {
  report: ForecastReport;
  request: AnalysisRequest;
  receivedAt: string;
  executionMode: string;
}
interface AnalysisState {
  report: ForecastReport | null;
  history: SessionAnalysis[];
  researchHistory: ResearchReport[];
  loading: boolean;
  error: string | null;
  systemStatus: HealthResponse | null;
  models: ModelStatus | null;
  healthError: string | null;
  modelsError: string | null;
  checkingHealth: boolean;
  setReport: (report: ForecastReport, request: AnalysisRequest) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  selectReport: (entry: SessionAnalysis) => void;
  addResearch: (report: ResearchReport) => void;
  refreshSystem: () => Promise<void>;
  reset: () => void;
}
const message = (e: unknown) =>
  e instanceof Error ? e.message : "Request failed";
export const useAnalysisStore = create<AnalysisState>((set, get) => ({
  report: null,
  history: [],
  researchHistory: [],
  loading: false,
  error: null,
  systemStatus: null,
  models: null,
  healthError: null,
  modelsError: null,
  checkingHealth: false,
  setReport: (report, request) =>
    set((s) => ({
      report,
      loading: false,
      error: null,
      history: [
        {
          report,
          request,
          receivedAt: new Date().toISOString(),
          executionMode: s.systemStatus?.execution_mode || "UNKNOWN",
        },
        ...s.history,
      ],
    })),
  selectReport: (entry) => set({ report: entry.report }),
  addResearch: (report) =>
    set((s) => ({ researchHistory: [report, ...s.researchHistory] })),
  setLoading: (loading) =>
    set({ loading, ...(loading ? { error: null } : {}) }),
  setError: (error) => set({ error, loading: false }),
  refreshSystem: async () => {
    if (get().checkingHealth) return;
    set({ checkingHealth: true });
    const [health, models] = await Promise.allSettled([
      apiClient.getHealth(),
      apiClient.getModels(),
    ]);
    set({
      checkingHealth: false,
      systemStatus: health.status === "fulfilled" ? health.value : null,
      healthError: health.status === "rejected" ? message(health.reason) : null,
      models: models.status === "fulfilled" ? models.value : null,
      modelsError: models.status === "rejected" ? message(models.reason) : null,
    });
  },
  reset: () => set({ report: null, loading: false, error: null }),
}));
