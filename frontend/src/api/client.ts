import { 
    AnalysisRequest, 
    ForecastReport, 
    HealthResponse, 
    ModelStatus, 
    BacktestRunResponse, 
    APIError 
  } from './types';
  
  export class DelphiAPIError extends Error {
    constructor(public apiError: APIError, public status: number) {
      super(apiError.message);
      this.name = 'DelphiAPIError';
    }
  }
  
  export class APIClient {
    private baseUrl: string;
  
    constructor(baseUrl: string = import.meta.env.VITE_API_URL || 'http://localhost:8000') {
      this.baseUrl = baseUrl;
    }
  
    private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
      const url = `${this.baseUrl}${endpoint}`;
      
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });
  
      if (!response.ok) {
        let apiError: APIError;
        try {
          apiError = await response.json();
        } catch {
          apiError = {
            error_code: 'UNKNOWN_ERROR',
            message: response.statusText,
            timestamp: new Date().toISOString(),
            request_id: 'unknown'
          };
        }
        throw new DelphiAPIError(apiError, response.status);
      }
  
      return response.json();
    }
  
    async analyze(request: AnalysisRequest, idempotencyKey?: string): Promise<ForecastReport> {
      const headers: Record<string, string> = {};
      if (idempotencyKey) {
        headers['Idempotency-Key'] = idempotencyKey;
      }
      return this.request<ForecastReport>('/analysis', {
        method: 'POST',
        body: JSON.stringify(request),
        headers
      });
    }
  
    async getHealth(): Promise<HealthResponse> {
      return this.request<HealthResponse>('/health/ready');
    }
  
    async getModels(): Promise<ModelStatus> {
      return this.request<ModelStatus>('/models');
    }
  
    async startBacktest(request: any): Promise<BacktestRunResponse> {
      return this.request<BacktestRunResponse>('/backtests', {
        method: 'POST',
        body: JSON.stringify(request)
      });
    }
  
    async getBacktest(runId: string): Promise<BacktestRunResponse> {
      return this.request<BacktestRunResponse>(`/backtests/${runId}`);
    }
  }
  
  export const apiClient = new APIClient();
