from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class HistoricalOutcome(BaseModel):
    outcome_id: str
    event_id: str
    outcome_event_ids: List[str]
    outcome_timestamp: str
    days_after_event: int
    outcome_event_type: str
    actors: List[str] = Field(default_factory=list)
    targets: List[str] = Field(default_factory=list)
    description: str = ""
    source_reference: str = ""

class HistoricalEventDocument(BaseModel):
    event_id: str
    document_id: str = ""
    event_date: str
    timestamp: str = ""
    event_type: str
    action: str = ""
    actor_ids: List[str] = Field(default_factory=list)
    target_ids: List[str] = Field(default_factory=list)
    location_ids: List[str] = Field(default_factory=list)
    domain: str = ""
    text: str = ""
    event_embedding: List[float]
    outcome_event_ids: List[str] = Field(default_factory=list)
    source_id: str = ""
    embedding_version: str = ""
    eventnet_version: str = ""
    dataset_split: str = ""
    prediction_information_cutoff: str = ""
    vector_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OutcomeTimeline(BaseModel):
    event_id: str
    time_horizon: str # e.g. "7 days", "30 days"
    future_events: List[str] = Field(default_factory=list)
    outcomes: List[HistoricalOutcome] = Field(default_factory=list)

class HistoricalAnalogue(BaseModel):
    analogue_id: str
    query_event_id: str = ""
    historical_event_id: str = ""
    semantic_similarity: float
    event_type_similarity: float = 0.0
    actor_similarity: float = 0.0
    target_similarity: float = 0.0
    location_similarity: float = 0.0
    temporal_relevance: float = 0.0
    final_rank_score: float
    event_type_match: bool
    domain_match: bool
    historical_event_date: str
    similarities: List[str] = Field(default_factory=list)
    differences: List[str] = Field(default_factory=list)
    historical_context: str = ""
    outcome_timeline: List[OutcomeTimeline] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
