// Contracts checked against src/delphi/api/schemas and the mounted routes.
export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonObject
  | JsonValue[];
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
export interface DossierClaim {
  claim_id: string;
  claim_text: string;
  document_id: string;
  source_url: string;
  source_domain: string;
  source_name: string;
  published_at: string;
  claim_type: string;
  direction: string;
  credibility_score: number;
}
export interface DossierSource {
  document_id: string;
  url: string;
  title: string;
  source_name: string;
  source_domain: string;
  published_at: string;
  retrieved_at: string;
  credibility_score: number;
  word_count: number;
  summary_snippet: string;
  status: string;
}
export interface ResearchDossier {
  research_question: string;
  search_queries: string[];
  research_cutoff: string;
  sources: DossierSource[];
  extracted_claims: DossierClaim[];
  corroborating_reports: JsonObject[];
  conflicting_reports: JsonObject[];
  historical_context: string[];
  quantitative_findings: string[];
  unresolved_questions: string[];
  provider_statuses: Record<string, string>;
  wire_repetition_count: number;
  independent_sources_count: number;
  limitations: string[];
}
export interface SourceReadingItem {
  num: number;
  label: string;
  domain: string;
  name: string;
  url: string;
  title: string;
  published_at: string;
  credibility: number;
}
export interface IntelligenceReport {
  title: string;
  executive_summary: string;
  background_and_context: string;
  current_developments: string;
  evidence_and_sources: string;
  historical_comparisons: string;
  causal_analysis: string;
  future_scenarios: string;
  risks_and_uncertainties: string;
  conclusion: string;
  sources_and_reading: SourceReadingItem[];
  confidence_statement: string;
  generated_at: string;
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
  dossier?: ResearchDossier | null;
  intelligence_report?: IntelligenceReport | null;
  provider_statuses?: Record<string, string>;
}
export interface ForecastReport {
  current_event: JsonObject;
  credibility_assessment: JsonObject;
  historical_analogues: JsonObject[];
  scenarios: APIScenario[];
  indicators: string[];
  evidence: JsonObject[];
  live_research_report?: ResearchReport | null;
  intelligence_report?: IntelligenceReport | null;
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

export interface PastAnalysisSummary {
  id: number;
  request_id: string;
  created_at: string | null;
  publication_timestamp: string;
  prediction_cutoff: string;
  domain: string;
  status: string;
  temporal_status: string;
  topic: string;
  scenarios_count: number;
}
