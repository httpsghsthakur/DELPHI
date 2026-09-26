from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchResult(BaseModel):
    result_id: str
    query: str
    title: str
    url: str
    snippet: str
    source_domain: str
    source_name: str
    published_at: str
    retrieved_at: str
    provider: str
    rank: int
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)

class ResearchDocument(BaseModel):
    document_id: str
    url: str
    canonical_url: str
    title: str
    source: str
    source_domain: str
    published_at: str
    retrieved_at: str
    text: str
    language: str
    content_type: str
    word_count: int
    checksum: str

class EvidenceItem(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    evidence_id: str
    document_id: str
    claim: str
    excerpt: str
    timestamp: str
    source: str
    credibility_score: float
    relevance_score: float
    temporal_valid: bool
    direction: str # "supporting", "conflicting", "neutral"
    linked_event: str
    linked_scenario: str

class ResearchRun(BaseModel):
    run_id: str
    analysis_id: Optional[str] = None
    started_at: str
    completed_at: str
    cutoff: str
    status: str
    provider_metadata: Dict[str, Any] = Field(default_factory=dict)

class ResearchReport(BaseModel):
    run_id: str
    queries_executed: List[str]
    providers_used: List[str]
    documents_discovered: int
    documents_fetched: int
    documents_rejected: int
    source_clusters: int
    supporting_evidence: List[EvidenceItem]
    conflicting_evidence: List[EvidenceItem]
    source_credibility_avg: float
    source_diversity: float
    temporal_validity_status: str
    limitations: List[str]
    status: str
