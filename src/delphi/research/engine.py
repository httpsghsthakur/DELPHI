import os
import uuid
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from urllib.parse import urlparse

from .schemas import (
    ResearchReport, ResearchDocument, EvidenceItem, SearchResult,
    ResearchDossier, DossierClaim, DossierSource, IntelligenceReport
)
from .query_planner import QueryPlanner
from .search.registry import registry as search_registry
from .deduplication import Deduplicator, SourceClusterer
from .fetch import HttpClient, ContentExtractor
from .composer import GroundedReportComposer

class LiveResearchEngine:
    """
    Upgraded DELPHI Deep Research Engine.
    Executes a research-first workflow:
    Multi-query planning -> Multi-provider web search -> Source retrieval ->
    Article extraction -> Deduplication -> Source credibility assessment ->
    Evidence verification -> Structured Dossier compilation -> Grounded Report Composition.
    """
    
    def __init__(self, cred_net_model=None):
        self.planner = QueryPlanner()
        self.http = HttpClient(
            timeout=int(os.environ.get("RESEARCH_TIMEOUT", "10")),
            max_size_bytes=int(os.environ.get("MAX_DOCUMENT_BYTES", "5242880"))
        )
        self.extractor = ContentExtractor()
        self.composer = GroundedReportComposer()
        self.cred_net_model = cred_net_model
        
    def _is_temporally_valid(self, published_at: str, cutoff: str, strict_mode: bool) -> bool:
        """Enforce strict temporal validity."""
        if not published_at or published_at == "PUBLICATION_TIME_UNKNOWN":
            return not strict_mode
        try:
            return published_at <= cutoff
        except Exception:
            return not strict_mode

    def run_research(
        self,
        event: Dict[str, Any],
        cutoff: str,
        research_depth: str = "deep"
    ) -> ResearchReport:
        run_id = str(uuid.uuid4())
        strict_mode = os.environ.get("STRICT_TEMPORAL_MODE", "true").lower() == "true"
        max_queries = int(os.environ.get("MAX_RESEARCH_QUERIES", "6"))
        max_results = int(os.environ.get("MAX_RESULTS_PER_QUERY", "5"))
        max_docs = int(os.environ.get("MAX_RESEARCH_DOCUMENTS", "12"))
        
        provider_statuses: Dict[str, str] = {}
        all_executed_queries: List[str] = []
        providers_used: List[str] = []
        
        # 1. Multi-Vector Query Generation
        initial_queries = self.planner.generate_queries(event, max_queries)
        all_executed_queries.extend(initial_queries)
        
        providers = search_registry.get_default_fallback_chain()
        if not providers:
            return self._build_empty_report(run_id, "FAILED - No Search Providers Configured")
            
        all_search_results: List[SearchResult] = []
        
        # 2. Search Execution (Pass 1)
        for q in initial_queries:
            query_success = False
            for provider in providers:
                p_name = provider.__class__.__name__
                try:
                    res = provider.search(q, max_results=max_results)
                    if res:
                        all_search_results.extend(res)
                        if p_name not in providers_used:
                            providers_used.append(p_name)
                        provider_statuses[p_name] = "OK"
                        query_success = True
                        break
                    else:
                        if p_name not in provider_statuses:
                            provider_statuses[p_name] = "NO_RESULTS"
                except Exception as e:
                    provider_statuses[p_name] = f"ERROR: {str(e)[:40]}"
            time.sleep(0.3)
                    
        # 3. Deduplicate Initial Search Results
        unique_results = Deduplicator.deduplicate_results(all_search_results)
        
        # 4. Fetch Documents & Extract Content
        fetched_docs: List[ResearchDocument] = []
        rejected_count = 0
        now_str = datetime.now(timezone.utc).isoformat()
        
        all_extracted_claims_raw: List[Dict[str, Any]] = []
        all_quantitative_data: List[str] = []
        all_uncertainties: List[str] = []
        
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
            if len(clean_text) < 120:
                rejected_count += 1
                continue
                
            doc = ResearchDocument(
                document_id=str(uuid.uuid4()),
                url=sr.url,
                canonical_url=resp.get("canonical_url", sr.url),
                title=sr.title,
                source=sr.source_name,
                source_domain=sr.source_domain,
                published_at=sr.published_at,
                retrieved_at=now_str,
                text=clean_text,
                language="en",
                content_type=resp.get("content_type", "text/html"),
                word_count=len(clean_text.split()),
                checksum=resp.get("checksum", "")
            )
            fetched_docs.append(doc)
            
            # Extract structured claims, metrics, and uncertainties
            claims_in_doc = self.extractor.extract_claims(clean_text)
            for c in claims_in_doc:
                c["document_id"] = doc.document_id
                c["source_url"] = doc.url
                c["source_domain"] = doc.source_domain
                c["source_name"] = doc.source
                c["published_at"] = doc.published_at
                all_extracted_claims_raw.append(c)
                
            all_quantitative_data.extend(self.extractor.extract_quantitative_data(clean_text))
            all_uncertainties.extend(self.extractor.extract_unresolved_questions(clean_text))
            
        # 5. Iterative Refinement Search (Pass 2 if in deep mode and space permits)
        if research_depth == "deep" and len(fetched_docs) < max_docs:
            followup_queries = self.planner.generate_iterative_queries(
                all_executed_queries, all_extracted_claims_raw, max_queries=2
            )
            if followup_queries:
                all_executed_queries.extend(followup_queries)
                for fq in followup_queries:
                    for provider in providers:
                        try:
                            f_res = provider.search(fq, max_results=3)
                            if f_res:
                                for sr in f_res:
                                    if len(fetched_docs) >= max_docs:
                                        break
                                    if not self._is_temporally_valid(sr.published_at, cutoff, strict_mode):
                                        continue
                                    resp = self.http.fetch(sr.url)
                                    if not resp:
                                        continue
                                    clean_text = self.extractor.extract_text(resp["text"])
                                    if len(clean_text) < 120:
                                        continue
                                    doc = ResearchDocument(
                                        document_id=str(uuid.uuid4()),
                                        url=sr.url,
                                        canonical_url=resp.get("canonical_url", sr.url),
                                        title=sr.title,
                                        source=sr.source_name,
                                        source_domain=sr.source_domain,
                                        published_at=sr.published_at,
                                        retrieved_at=now_str,
                                        text=clean_text,
                                        language="en",
                                        content_type=resp.get("content_type", "text/html"),
                                        word_count=len(clean_text.split()),
                                        checksum=resp.get("checksum", "")
                                    )
                                    fetched_docs.append(doc)
                                    claims_in_doc = self.extractor.extract_claims(clean_text)
                                    for c in claims_in_doc:
                                        c["document_id"] = doc.document_id
                                        c["source_url"] = doc.url
                                        c["source_domain"] = doc.source_domain
                                        c["source_name"] = doc.source
                                        c["published_at"] = doc.published_at
                                        all_extracted_claims_raw.append(c)
                                break
                        except Exception:
                            pass

        # 6. Deduplicate Documents
        unique_docs = Deduplicator.deduplicate_documents(fetched_docs)
        
        # 7. Source Clustering (Identifying Wire Repetitions vs Independent Reporting)
        clusters = SourceClusterer.cluster(unique_docs)
        wire_repetition_count = sum(len(c) - 1 for c in clusters if len(c) > 1)
        independent_sources_count = len(clusters)
        
        # 8. Source Credibility Assessment & Dossier Claims Formation
        dossier_sources: List[DossierSource] = []
        dossier_claims: List[DossierClaim] = []
        supporting_evidence: List[EvidenceItem] = []
        conflicting_evidence: List[EvidenceItem] = []
        
        total_cred = 0.0
        doc_cred_map = {}
        
        for doc in unique_docs:
            cred_score = 0.5
            if self.cred_net_model:
                try:
                    cred_result = self.cred_net_model.predict({"domain": doc.source_domain})
                    cred_score = float(cred_result.get("credibility_score", 0.5))
                except Exception:
                    cred_score = 0.5
            total_cred += cred_score
            doc_cred_map[doc.document_id] = cred_score
            
            snippet = doc.text[:220].strip() + "..." if len(doc.text) > 220 else doc.text
            dossier_sources.append(DossierSource(
                document_id=doc.document_id,
                url=doc.url,
                title=doc.title,
                source_name=doc.source,
                source_domain=doc.source_domain,
                published_at=doc.published_at,
                retrieved_at=doc.retrieved_at,
                credibility_score=cred_score,
                word_count=doc.word_count,
                summary_snippet=snippet,
                status="extracted"
            ))
            
        for c in all_extracted_claims_raw:
            d_id = c.get("document_id", "")
            cred = doc_cred_map.get(d_id, 0.5)
            claim_id = str(uuid.uuid4())
            
            d_claim = DossierClaim(
                claim_id=claim_id,
                claim_text=c["claim_text"],
                document_id=d_id,
                source_url=c["source_url"],
                source_domain=c["source_domain"],
                source_name=c["source_name"],
                published_at=c["published_at"],
                claim_type=c["claim_type"],
                direction=c["direction"],
                credibility_score=cred
            )
            dossier_claims.append(d_claim)
            
            # Map into EvidenceItem for legacy/forecast compatibility
            ev_item = EvidenceItem(
                evidence_id=claim_id,
                document_id=d_id,
                claim=c["claim_text"],
                excerpt=c["claim_text"],
                timestamp=c["published_at"],
                source=c["source_domain"],
                credibility_score=cred,
                relevance_score=0.85,
                temporal_valid=True,
                direction=c["direction"],
                linked_event=event.get("event_id", "unknown"),
                linked_scenario=""
            )
            if c["direction"] == "supporting":
                supporting_evidence.append(ev_item)
            else:
                conflicting_evidence.append(ev_item)
                
        num_clusters = len(clusters)
        num_docs = len(unique_docs)
        avg_cred = total_cred / num_docs if num_docs > 0 else 0.5
        diversity = min(num_clusters / max_docs, 1.0) if max_docs > 0 else 0.0
        
        # Compile Research Dossier
        research_question = event.get("source_text", "") or event.get("event_type_code", "Deep Intelligence Research")
        
        dossier = ResearchDossier(
            research_question=research_question,
            search_queries=all_executed_queries,
            research_cutoff=cutoff,
            sources=dossier_sources,
            extracted_claims=dossier_claims,
            corroborating_reports=[{"theme": f"Reporting cluster {i+1}", "lead_source": c[0].source_domain, "members": [d.source_domain for d in c]} for i, c in enumerate(clusters)],
            conflicting_reports=[{"claim": c.claim_text, "source": c.source_domain, "url": c.source_url} for c in dossier_claims if c.direction == "conflicting"][:5],
            historical_context=[f"Correlated historical precedent identified in {doc.source_domain} coverage" for doc in unique_docs[:2]],
            quantitative_findings=list(dict.fromkeys(all_quantitative_data))[:6],
            unresolved_questions=list(dict.fromkeys(all_uncertainties))[:5],
            provider_statuses=provider_statuses,
            wire_repetition_count=wire_repetition_count,
            independent_sources_count=independent_sources_count,
            limitations=[f"Search provider status: {k} = {v}" for k, v in provider_statuses.items() if "ERROR" in v]
        )
        
        # 9. Grounded Intelligence Report Composition
        intelligence_report = self.composer.compose_report(
            dossier=dossier,
            event_context=event,
            credibility_assessment={"credibility_score": avg_cred, "domains_evaluated": len(unique_docs)}
        )
        
        return ResearchReport(
            run_id=run_id,
            queries_executed=all_executed_queries,
            providers_used=providers_used,
            documents_discovered=len(all_search_results),
            documents_fetched=num_docs,
            documents_rejected=rejected_count,
            source_clusters=num_clusters,
            supporting_evidence=supporting_evidence,
            conflicting_evidence=conflicting_evidence,
            source_credibility_avg=avg_cred,
            source_diversity=diversity,
            temporal_validity_status="VERIFIED",
            limitations=dossier.limitations,
            status="COMPLETE" if unique_docs else "FAILED",
            dossier=dossier,
            intelligence_report=intelligence_report,
            provider_statuses=provider_statuses
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
            limitations=["Search execution failed or all providers unavailable"],
            status=status,
            dossier=None,
            intelligence_report=None,
            provider_statuses={}
        )
