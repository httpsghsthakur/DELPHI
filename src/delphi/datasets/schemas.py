from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
    article_id: str
    source_id: str
    title: str
    body: str
    url: str
    author: Optional[str] = None
    publication_datetime: datetime
    language: str
    country: Optional[str] = None
    domain: str
    content_hash: str
    source_dataset: str
    ingestion_timestamp: datetime
    dataset_version: str
    section: Optional[str] = None
    location: Optional[str] = None
    keywords: Optional[List[str]] = None
    raw_metadata: Optional[Dict[str, Any]] = None

class EventRecord(BaseModel):
    event_id: str
    article_id: str
    event_date: Optional[datetime] = None
    actor: Optional[str] = None
    action: Optional[str] = None
    target: Optional[str] = None
    location: Optional[str] = None
    domain: Optional[str] = None
    event_type: Optional[str] = None
    trigger: Optional[str] = None
    severity: Optional[float] = None
    source_id: Optional[str] = None
    confidence: Optional[float] = None

class EventRelation(BaseModel):
    relation_id: str
    source_event_id: str
    target_event_id: str
    relation_type: str
    relation_date: Optional[datetime] = None
    confidence: Optional[float] = None
    source_dataset: str
    evidence_id: Optional[str] = None

class SourceRecord(BaseModel):
    source_id: str
    domain: str
    publisher: Optional[str] = None
    country: Optional[str] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    author_available: Optional[bool] = None
    citation_available: Optional[bool] = None
    source_dataset: str

class CredibilityFeatures(BaseModel):
    source_id: str
    article_id: str = ""
    timestamp: str = ""
    
    author_identifiable: float = 0.0
    article_length_normalized: float = 0.0
    citation_density: float = 0.0
    title_sensationalism: float = 0.5
    historical_source_reliability: float = 0.5
    corroboration_count_normalized: float = 0.0
    correction_history_signal: float = 0.5
    publication_consistency: float = 0.5
    primary_source_presence: float = 0.0
    attribution_completeness: float = 0.5
    author_history_availability: float = 0.0
    domain_reputation: float = 0.5
    
    dataset_version: str

class EconomicObservation(BaseModel):
    country: str
    indicator: str
    indicator_code: str
    date: datetime
    value: float
    unit: str
    source: str
    dataset_version: str

class TradeObservation(BaseModel):
    reporter_country: str
    partner_country: str
    product_code: str
    product_description: str
    flow: str
    period: str
    value: float
    quantity: Optional[float] = None
    unit: Optional[str] = None
    source: str
    dataset_version: str

class EventSequence(BaseModel):
    anchor_event_id: str
    future_event_ids: List[str]
    time_deltas_days: List[int]
    sequence_end: datetime
