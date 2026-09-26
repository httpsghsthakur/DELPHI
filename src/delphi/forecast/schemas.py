from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Provenance(BaseModel):
    tokenizer_version: str = "v1"
    eventembed_version: str = "v1"
    eventnet_version: str = "v1"
    retrieval_index_version: str = "v1"
    crednet_version: str = "v1"
    causalseq_version: str = "v1"
    calibration_version: str = "v1"
    dataset_manifest_version: str = "v1"
    prediction_cutoff: str
    checkpoint_training_end_time: str
    
class ForecastRequest(BaseModel):
    article_text: str
    source_id: Optional[str] = None
    article_id: Optional[str] = None
    publication_timestamp: str
    prediction_information_cutoff: str
    domain: str
    requested_forecast_horizon: str
    config_version: str = "v1"

class EvidenceItem(BaseModel):
    source_id: str
    timestamp: str
    role: str # "historical_analogue", "crednet_signal", "causalseq_trajectory", "eventnet_extraction"
    direction: str # "supporting", "conflicting", "neutral"
    model_version: str
    content: Dict[str, Any]

class ScenarioCandidate(BaseModel):
    scenario_id: str
    title: str
    trajectory: List[Dict[str, Any]]
    supporting_evidence: List[EvidenceItem]
    contradictory_evidence: List[EvidenceItem]
    sequence_score: float = 0.0
    evidence_score: float = 0.0
    historical_support_score: float = 0.0
    model_support_score: float = 0.0
    raw_scenario_score: float = 0.0

class Indicator(BaseModel):
    indicator_id: str
    description: str
    event_type: int
    actor: int
    target: int
    time_window: str
    source_requirement: str
    expected_direction: str
    scenario_linkage: str
    importance: str

class ConfidenceAssessment(BaseModel):
    confidence_status: str # e.g. "insufficient_evidence", "calibrated", "uncalibrated"
    calibration_status: str
    historical_evaluation_quality: float = 0.0
    evidence_coverage: float = 0.0
    model_agreement: float = 0.0
    scenario_separation: float = 0.0

class ForecastReport(BaseModel):
    request_metadata: ForecastRequest
    current_event: Dict[str, Any]
    credibility_assessment: Dict[str, Any]
    historical_analogues: List[Dict[str, Any]]
    observed_historical_outcomes: List[Dict[str, Any]]
    candidate_scenarios: List[ScenarioCandidate]
    scenario_probabilities: Dict[str, float]
    indicators_to_watch: List[Indicator]
    supporting_evidence: List[EvidenceItem]
    contradictory_evidence: List[EvidenceItem]
    confidence_metadata: ConfidenceAssessment
    provenance: Provenance
    temporal_safety_status: str
    limitations: List[str]
    forecast_status: str = "UNCALIBRATED / RESEARCH MODE"
