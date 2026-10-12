// Test-only responses. No fixture data is imported by runtime components.
import type {
  ForecastReport,
  HealthResponse,
  ModelStatus,
  ResearchReport,
} from "../api/types";
export const health: HealthResponse = {
  status: "ok",
  api_version: "test-api",
  models_loaded: true,
  temporal_mode: "strict",
  execution_mode: "SYNTHETIC",
  dependencies: { database: "ok", crednet: "missing" },
};
export const models: ModelStatus = {
  tokenizer_version: "",
  eventembed_version: "",
  eventnet_version: "",
  crednet_version: "",
  causalseq_version: "",
  retrieval_index_version: "",
  calibration_version: "",
  checkpoint_timestamps: {},
};
export const research: ResearchReport = {
  run_id: "test-research",
  queries_executed: ["test query"],
  providers_used: ["test provider"],
  documents_discovered: 1,
  documents_fetched: 1,
  documents_rejected: 0,
  source_clusters: 1,
  supporting_evidence: [],
  conflicting_evidence: [],
  source_credibility_avg: 0,
  source_diversity: 1,
  temporal_validity_status: "VALID",
  limitations: [],
  status: "COMPLETE",
};
export const report: ForecastReport = {
  current_event: {
    event_id: "test-event",
    event_type: 4,
    actors: [1],
    timestamp: "2026-08-01T00:00:00Z",
  },
  credibility_assessment: { credibility_score: 0.42, calibrated_score: null },
  historical_analogues: [
    {
      event_id: "test-historical",
      match_score: 0.4,
      timestamp: "2020-01-01T00:00:00Z",
    },
  ],
  scenarios: [
    {
      scenario_id: "test-scenario",
      trajectory: [{ event_type: 3, time_bin: 2 }],
      raw_score: -0.5,
      normalized_weight: 0.7,
      probability: 0.7,
    },
  ],
  indicators: ["test-indicator"],
  evidence: [
    {
      evidence_id: "test-evidence",
      claim: "Test evidence claim",
      direction: "supporting",
      source_id: "test-source",
      timestamp: "2026-01-01T00:00:00Z",
      url: "https://example.com/evidence",
    },
  ],
  live_research_report: research,
  calibration_status: "UNCALIBRATED",
  provenance: {
    prediction_cutoff: "2026-09-01T00:00:00Z",
    tokenizer_version: "",
    eventembed_version: "",
    eventnet_version: "",
    crednet_version: "",
    causalseq_version: "",
    retrieval_index_version: "",
    calibration_version: "",
    dataset_version: "test-dataset",
    checkpoint_training_bounds: {},
    temporal_validation_status: "VALID",
  },
  limitations: ["Test limitation"],
};
