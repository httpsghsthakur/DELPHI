from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class FutureEventPrediction(BaseModel):
    event_type: int
    actor: Optional[int] = None
    target: Optional[int] = None
    time_to_event_bin: int # e.g. 0=hours, 1=1d, 2=3d, 3=7d, 4=14d, 5=30d, 6=90d, 7=180d, 8=365+d
    domain: Optional[int] = None
    indicators: Optional[List[int]] = None
    step_index: int

class FutureEventSequence(BaseModel):
    sequence_id: str
    originating_event_id: str
    prediction_cutoff: str
    events: List[FutureEventPrediction]
    model_version: str
    dataset_version: str

class ScenarioCandidate(BaseModel):
    candidate_id: str
    originating_event_id: str
    events: List[FutureEventPrediction]
    cumulative_log_likelihood: float
    sequence_score: float # Normalized sequence score (length normalized)
    generation_length: int
    model_version: str
