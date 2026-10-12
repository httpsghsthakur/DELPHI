import type {
  AnalysisRequest,
  ForecastReport,
  HealthResponse,
  ModelStatus,
  BacktestRequest,
  BacktestRunResponse,
  APIError,
  ResearchReport,
  HistoricalSearchRequest,
  HistoricalSearchResponse,
} from "./types";

export class DelphiAPIError extends Error {
  constructor(
    public apiError: APIError,
    public status: number,
  ) {
    super(apiError.message);
    this.name = "DelphiAPIError";
  }
}
export class APIClient {
  readonly baseUrl: string;
  constructor(baseUrl = import.meta.env.VITE_API_URL || "/api") {
    this.baseUrl = baseUrl.replace(/\/$/, "");
  }
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<T> {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 120_000);
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        signal: controller.signal,
        headers: {
          ...(options.body ? { "Content-Type": "application/json" } : {}),
          ...options.headers,
        },
      });
      if (!response.ok) {
        const body: unknown = await response.json().catch(() => null);
        const data =
          body && typeof body === "object"
            ? (body as Record<string, unknown>)
            : {};
        const message =
          typeof data.message === "string"
            ? data.message
            : typeof data.detail === "string"
              ? data.detail
              : Array.isArray(data.detail)
                ? data.detail
                    .map((d: { msg?: string }) => d.msg || "Invalid request")
                    .join("; ")
                : response.statusText || `HTTP ${response.status}`;
        throw new DelphiAPIError(
          {
            error_code: String(data.error_code || `HTTP_${response.status}`),
            message,
            request_id:
              typeof data.request_id === "string" ? data.request_id : undefined,
          },
          response.status,
        );
      }
      return (await response.json()) as T;
    } catch (error) {
      if (error instanceof DelphiAPIError) throw error;
      if (controller.signal.aborted)
        throw new Error(
          "The API did not respond within two minutes. The operation may still be running on the server.",
          { cause: error },
        );
      throw new Error(
        `Cannot reach the DELPHI API. ${error instanceof Error ? error.message : "Connection failed"}`,
        { cause: error },
      );
    } finally {
      window.clearTimeout(timeout);
    }
  }
  analyze(request: AnalysisRequest, idempotencyKey?: string) {
    return this.request<ForecastReport>("/analysis", {
      method: "POST",
      body: JSON.stringify(request),
      headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {},
    });
  }
  getHealth() {
    return this.request<HealthResponse>("/health/ready");
  }
  getModels() {
    return this.request<ModelStatus>("/models");
  }
  research(request: AnalysisRequest) {
    return this.request<ResearchReport>("/research", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }
  historicalSearch(request: HistoricalSearchRequest) {
    return this.request<HistoricalSearchResponse>("/historical/search", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }
  startBacktest(request: BacktestRequest) {
    return this.request<BacktestRunResponse>("/backtests", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }
  getBacktest(runId: string) {
    return this.request<BacktestRunResponse>(
      `/backtests/${encodeURIComponent(runId)}`,
    );
  }
}
export const apiClient = new APIClient();
