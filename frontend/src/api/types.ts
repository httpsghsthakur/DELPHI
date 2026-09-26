// DELPHI API Types

export interface HealthResponse {
  status: string;
  api_version: string;
  models_loaded: boolean;
  temporal_mode: string;
  execution_mode: 'REAL' | 'SYNTHETIC' | 'UNKNOWN';
  dependencies: Record<string, string>;
}

export interface ModelStatus {
  tokenizer_version: string;
  eventembed_version: string;
  eventnet_version: string;
  crednet_version: string;
  causalseq_version: string;
  retrieval_index_version: string;
  calibration_version: string;
}

export interface AnalysisRequest {
  text: string;
  source_id?: string;
  article_id?: string;
  publication_timestamp?: string;
  prediction_information_cutoff?: string;
  domain?: string;
  forecast_horizon?: number;
  live_research?: boolean;
}

export interface CurrentEventInfo {
  event_id: string;
  extracted_event: {
    event_type: number;
    actor: number;
    target: number;
    domain: number;
    spans: Record<string, any>;
  };
}

export interface CredibilityInfo {
  source_reliability: number;
  content_credibility: number;
  final_credibility_score: number;
  calibrated: boolean;
}

export interface HistoricalAnalogue {
  event_id: string;
  date: string;
  similarity_score: number;
  event_details: Record<string, any>;
  outcomes: any[];
}

export interface FutureEventPrediction {
  event_type: number;
  actor?: number;
  target?: number;
  time_to_event_bin: number;
  domain?: number;
  indicators?: number[];
  step_index: number;
}

export interface ScenarioCandidate {
  scenario_id: string;
  title: string;
  trajectory: any[]; // Kept for compatibility, backend sends dicts
  events: FutureEventPrediction[];
  sequence_score: number;
  generation_length: number;
  model_version: string;
  probability?: number;
  uncalibrated_weight?: number;
}

export interface IndicatorData {
  indicator_id: string;
  description: string;
  expected_event_type: number;
  time_window: string;
  associated_scenario: string;
  importance: number;
}

export interface EvidenceData {
  evidence_id: string;
  source_id: string;
  timestamp: string;
  evidence_type: string;
  scenario_linkage: string;
  role: 'SUPPORTING' | 'CONFLICTING' | 'NEUTRAL';
}

export interface ProvenanceInfo {
  tokenizer_version: string;
  eventembed_version: string;
  eventnet_version: string;
  crednet_version: string;
  causalseq_version: string;
  retrieval_index: string;
  calibration_version: string;
  dataset_version: string;
  prediction_cutoff: string;
}

export interface ForecastReport {
  analysis_id: string;
  timestamp: string;
  current_event: CurrentEventInfo;
  credibility: CredibilityInfo;
  historical_analogues: HistoricalAnalogue[];
  scenarios: ScenarioCandidate[];
  indicators: IndicatorData[];
  provenance: ProvenanceInfo;
  supporting_evidence: EvidenceData[];
  contradictory_evidence: EvidenceData[];
  live_research_report?: any;
}

export interface APIError {
  error_code: string;
  message: string;
  timestamp: string;
  request_id: string;
}

export interface BacktestRunResponse {
  run_id: string;
  status: 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  metrics?: Record<string, any>;
  provenance?: ProvenanceInfo;
}
