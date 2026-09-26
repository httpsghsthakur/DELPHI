import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from .schemas import ResearchReport, ResearchDocument, EvidenceItem, SearchResult
from .query_planner import QueryPlanner
from .search.registry import registry as search_registry
from .deduplication import Deduplicator, SourceClusterer
from .fetch import HttpClient, ContentExtractor

class LiveResearchEngine:
    def __init__(self, cred_net_model=None):
        self.planner = QueryPlanner()
        self.http = HttpClient(
            timeout=int(os.environ.get("RESEARCH_TIMEOUT", "10")),
            max_size_bytes=int(os.environ.get("MAX_DOCUMENT_BYTES", "5242880"))
        )
        self.extractor = ContentExtractor()
        self.cred_net_model = cred_net_model
        
    def _is_temporally_valid(self, published_at: str, cutoff: str, strict_mode: bool) -> bool:
        """Enforce strict temporal validity."""
        if published_at == "PUBLICATION_TIME_UNKNOWN":
            return not strict_mode
        try:
            return published_at <= cutoff
        except Exception:
            return not strict_mode

    def run_research(self, event: Dict[str, Any], cutoff: str) -> ResearchReport:
        run_id = str(uuid.uuid4())
        strict_mode = os.environ.get("STRICT_TEMPORAL_MODE", "true").lower() == "true"
        max_queries = int(os.environ.get("MAX_RESEARCH_QUERIES", "5"))
        max_results = int(os.environ.get("MAX_RESULTS_PER_QUERY", "5"))
        max_docs = int(os.environ.get("MAX_RESEARCH_DOCUMENTS", "10"))
        
        # 1. Query Generation
        queries = self.planner.generate_queries(event, max_queries)
        providers = search_registry.get_default_fallback_chain()
        
        if not providers:
            return self._build_empty_report(run_id, "FAILED - No Search Providers")
            
        all_search_results: List[SearchResult] = []
        providers_used = []
        
        # 2. Search Execution (Fallback logic per query)
        for q in queries:
            query_success = False
            for provider in providers:
                res = provider.search(q, max_results=max_results)
                if res:
                    all_search_results.extend(res)
                    if provider.__class__.__name__ not in providers_used:
                        providers_used.append(provider.__class__.__name__)
                    query_success = True
                    break # Stop fallback if we got results
                    
        # 3. Deduplicate Search Results
        unique_results = Deduplicator.deduplicate_results(all_search_results)
        
        # 4. Filter Temporally & Fetch
        fetched_docs = []
        rejected_count = 0
        now_str = datetime.now(timezone.utc).isoformat()
        
        for sr in unique_results:
            if len(fetched_docs) >= max_docs:
                break
                
            if not self._is_temporally_valid(sr.published_at, cutoff, strict_mode):
                rejected_count += 1
                continue
                
            resp = self.http.fetch(sr.url)
            if not resp:
                rejected_count += 1
                continue
                
            clean_text = self.extractor.extract_text(resp["text"])
            if len(clean_text) < 100:
                rejected_count += 1
                continue
                
            doc = ResearchDocument(
                document_id=str(uuid.uuid4()),
                url=sr.url,
                canonical_url=resp["canonical_url"],
                title=sr.title,
                source=sr.source_name,
                source_domain=sr.source_domain,
                published_at=sr.published_at,
                retrieved_at=now_str,
                text=clean_text,
                language="en", # Defaulting for prototype
                content_type=resp["content_type"],
                word_count=len(clean_text.split()),
                checksum=resp["checksum"]
            )
            fetched_docs.append(doc)
            
        # 5. Deduplicate Documents
        unique_docs = Deduplicator.deduplicate_documents(fetched_docs)
        
        # 6. Source Clustering
        clusters = SourceClusterer.cluster(unique_docs)
        
        # 7. Credibility Assessment & Claim Extraction
        supporting = []
        conflicting = []
        total_cred = 0.0
        
        for c in clusters:
            leader_doc = c[0]
            # CredNet logic
            cred_score = 0.5
            if self.cred_net_model:
                try:
                    cred_result = self.cred_net_model.predict({"domain": leader_doc.source_domain})
                    cred_score = cred_result.get("credibility_score", 0.5)
                except Exception:
                    pass
                    
            total_cred += cred_score
            
            # Deterministic Claim Extraction
            claims = self.extractor.extract_claims(leader_doc.text)
            for idx, claim in enumerate(claims[:3]): # Max 3 claims per doc
                # Naive logic: just assign direction
                direction = "conflicting" if "not" in claim.lower() or "deny" in claim.lower() else "supporting"
                
                ev = EvidenceItem(
                    evidence_id=str(uuid.uuid4()),
                    document_id=leader_doc.document_id,
                    claim=claim,
                    excerpt=claim,
                    timestamp=leader_doc.published_at,
                    source=leader_doc.source_domain,
                    credibility_score=cred_score,
                    relevance_score=0.8,
                    temporal_valid=True,
                    direction=direction,
                    linked_event=event.get("event_id", "unknown"),
                    linked_scenario=""
                )
                
                if direction == "supporting":
                    supporting.append(ev)
                else:
                    conflicting.append(ev)
                    
        num_clusters = len(clusters)
        avg_cred = total_cred / num_clusters if num_clusters > 0 else 0.5
        diversity = min(num_clusters / max_docs, 1.0) if max_docs > 0 else 0.0
        
        return ResearchReport(
            run_id=run_id,
            queries_executed=queries,
            providers_used=providers_used,
            documents_discovered=len(all_search_results),
            documents_fetched=len(unique_docs),
            documents_rejected=rejected_count,
            source_clusters=num_clusters,
            supporting_evidence=supporting,
            conflicting_evidence=conflicting,
            source_credibility_avg=avg_cred,
            source_diversity=diversity,
            temporal_validity_status="VERIFIED",
            limitations=[],
            status="COMPLETE" if unique_docs else "FAILED"
        )
        
    def _build_empty_report(self, run_id: str, status: str) -> ResearchReport:
        return ResearchReport(
            run_id=run_id,
            queries_executed=[],
            providers_used=[],
            documents_discovered=0,
            documents_fetched=0,
            documents_rejected=0,
            source_clusters=0,
            supporting_evidence=[],
            conflicting_evidence=[],
            source_credibility_avg=0.0,
            source_diversity=0.0,
            temporal_validity_status="UNVERIFIED",
            limitations=["Search execution failed"],
            status=status
        )
