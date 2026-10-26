from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class APIHealthResponse(BaseModel):
    status: str
    api_version: str
    models_loaded: bool
    temporal_mode: str
    execution_mode: str  # REAL or SYNTHETIC
    dependencies: Dict[str, str]

class APIModelStatus(BaseModel):
    tokenizer_version: str
    eventembed_version: str
    eventnet_version: str
    crednet_version: str
    causalseq_version: str
    retrieval_index_version: str
    calibration_version: str
    checkpoint_timestamps: Dict[str, str]

class APIProvenance(BaseModel):
    prediction_cutoff: str
    tokenizer_version: str
    eventembed_version: str
    eventnet_version: str
    crednet_version: str
    causalseq_version: str
    retrieval_index_version: str
    calibration_version: str
    dataset_version: str
    checkpoint_training_bounds: Dict[str, str]
    temporal_validation_status: str

class APIScenario(BaseModel):
    scenario_id: str
    trajectory: List[Dict[str, Any]]
    raw_score: float
    normalized_weight: float
    probability: Optional[float] = None

class APIForecastReport(BaseModel):
    current_event: Dict[str, Any]
    credibility_assessment: Dict[str, Any]
    historical_analogues: List[Dict[str, Any]]
    scenarios: List[APIScenario]
    indicators: List[str]
    evidence: List[Dict[str, Any]]
    live_research_report: Optional[Dict[str, Any]] = None
    intelligence_report: Optional[Dict[str, Any]] = None
    calibration_status: str
    provenance: APIProvenance
    limitations: List[str]
