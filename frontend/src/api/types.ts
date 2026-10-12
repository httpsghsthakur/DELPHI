// Contracts checked against src/delphi/api/schemas and the mounted routes.
export type JsonValue =
  string | number | boolean | null | JsonObject | JsonValue[];
export interface JsonObject {
  [key: string]: JsonValue | undefined;
}
export interface HealthResponse {
  status: string;
  api_version: string;
  models_loaded: boolean;
  temporal_mode: string;
  execution_mode: string;
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
  checkpoint_timestamps: Record<string, string>;
}
export interface AnalysisRequest {
  text: string;
  source_id?: string;
  article_id?: string;
  publication_timestamp: string;
  prediction_information_cutoff: string;
  domain: string;
  forecast_horizon?: number;
  live_research?: boolean;
}
export interface APIProvenance {
  prediction_cutoff: string;
  tokenizer_version: string;
  eventembed_version: string;
  eventnet_version: string;
  crednet_version: string;
  causalseq_version: string;
  retrieval_index_version: string;
  calibration_version: string;
  dataset_version: string;
  checkpoint_training_bounds: Record<string, string>;
  temporal_validation_status: string;
}
export interface APIScenario {
  scenario_id: string;
  trajectory: JsonObject[];
  raw_score: number;
  normalized_weight: number;
  probability?: number | null;
}
export interface ResearchEvidence {
  evidence_id: string;
  document_id: string;
  claim: string;
  excerpt: string;
  timestamp: string;
  source: string;
  credibility_score: number;
  relevance_score: number;
  temporal_valid: boolean;
  direction: string;
  linked_event: string;
  linked_scenario: string;
}
export interface ResearchReport {
  run_id: string;
  queries_executed: string[];
  providers_used: string[];
  documents_discovered: number;
  documents_fetched: number;
  documents_rejected: number;
  source_clusters: number;
  supporting_evidence: ResearchEvidence[];
  conflicting_evidence: ResearchEvidence[];
  source_credibility_avg: number;
  source_diversity: number;
  temporal_validity_status: string;
  limitations: string[];
  status: string;
}
export interface ForecastReport {
  current_event: JsonObject;
  credibility_assessment: JsonObject;
  historical_analogues: JsonObject[];
  scenarios: APIScenario[];
  indicators: string[];
  evidence: JsonObject[];
  live_research_report?: ResearchReport | null;
  calibration_status: string;
  provenance: APIProvenance;
  limitations: string[];
}
export interface HistoricalSearchRequest {
  text: string;
  cutoff: string;
  top_k: number;
  domain?: string;
}
export interface HistoricalSearchResponse {
  analogues: JsonObject[];
  similarity_components: JsonObject;
  historical_outcomes: JsonValue[];
  retrieval_metadata: JsonObject;
  temporal_safety_status: string;
}
export interface BacktestRequest {
  domain: string;
  window_days: number;
}
export interface BacktestRunResponse {
  run_id: string;
  status: string;
  configuration?: BacktestRequest;
  created_at?: string;
  metrics?: JsonObject | null;
  provenance?: JsonObject | null;
  completed_at?: string | null;
}
export interface APIError {
  error_code: string;
  message: string;
  timestamp?: string;
  request_id?: string;
}
// Graph data is optional. The current API does not return this structure.
export interface GraphNode {
  id: string;
  label: string;
  kind: "observed" | "inferred" | "hypothetical";
  evidence?: JsonObject;
}
export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  kind: GraphNode["kind"];
  evidence?: JsonObject;
}
export interface CausalGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
