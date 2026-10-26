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

class DossierClaim(BaseModel):
    claim_id: str
    claim_text: str
    document_id: str
    source_url: str
    source_domain: str
    source_name: str
    published_at: str
    claim_type: str # "official_statement", "reported_fact", "expert_analysis", "competing_account"
    direction: str # "supporting", "conflicting", "neutral"
    credibility_score: float

class DossierSource(BaseModel):
    document_id: str
    url: str
    title: str
    source_name: str
    source_domain: str
    published_at: str
    retrieved_at: str
    credibility_score: float
    word_count: int
    summary_snippet: str
    status: str # "extracted", "unreachable", "rejected_temporal", "rate_limited"

class ResearchDossier(BaseModel):
    research_question: str
    search_queries: List[str]
    research_cutoff: str
    sources: List[DossierSource]
    extracted_claims: List[DossierClaim]
    corroborating_reports: List[Dict[str, Any]] = Field(default_factory=list)
    conflicting_reports: List[Dict[str, Any]] = Field(default_factory=list)
    historical_context: List[str] = Field(default_factory=list)
    quantitative_findings: List[str] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    provider_statuses: Dict[str, str] = Field(default_factory=dict)
    wire_repetition_count: int = 0
    independent_sources_count: int = 0
    limitations: List[str] = Field(default_factory=list)

class IntelligenceReport(BaseModel):
    title: str
    executive_summary: str
    background_and_context: str
    current_developments: str
    evidence_and_sources: str
    historical_comparisons: str
    causal_analysis: str
    future_scenarios: str
    risks_and_uncertainties: str
    conclusion: str
    sources_and_reading: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_statement: str = ""
    generated_at: str = ""

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
    dossier: Optional[ResearchDossier] = None
    intelligence_report: Optional[IntelligenceReport] = None
    provider_statuses: Dict[str, str] = Field(default_factory=dict)
