from typing import List, Dict, Any, Optional
from .faiss_index import FaissHistoricalIndex
from .filters import TemporalHistoricalFilter, MetadataFilter
from .reranker import DeterministicReranker
from .schemas import HistoricalAnalogue, HistoricalEventDocument

class HistoricalMatcher:
    def __init__(self, index_path: str, dimension: int = 256, config: dict = None):
        self.index = FaissHistoricalIndex(dimension=dimension)
        self.index.load(index_path)
        self.reranker = DeterministicReranker(config=config.get("reranking") if config else None)
        
        # Validate compatibility
        manifest = getattr(self.index, "manifest", {})
        if config and config.get("eventembed_version"):
            if manifest.get("eventembed_version") != config.get("eventembed_version"):
                raise ValueError("Index EventEmbed version mismatch")
                
    def search(
        self, 
        query_event: Dict[str, Any], 
        prediction_time: str, 
        candidate_k: int = 100, 
        top_k: int = 10
    ) -> List[HistoricalAnalogue]:
        """
        query_event must contain:
        - event_embedding
        - event_id
        - event_type (optional)
        - domain (optional)
        - actors (optional)
        - targets (optional)
        - locations (optional)
        """
        if "event_embedding" not in query_event:
            raise ValueError("query_event must contain event_embedding")
            
        # Stage 1: Semantic FAISS Retrieval
        candidates = self.index.search(query_event["event_embedding"], top_k=candidate_k)
        
        if not candidates:
            return []
            
        # Extract HistoricalEventDocuments for filtering
        docs = [cand for _, cand in candidates]
        
        # Stage 2: Temporal Filtering (Strict)
        docs = TemporalHistoricalFilter.filter(docs, prediction_time)
        
        # Stage 2.5: Metadata Filtering (Domain, self-match prevention)
        meta_filter = MetadataFilter(
            query_event_id=query_event.get("event_id")
        )
        docs = meta_filter.filter(docs)
        
        # Re-associate with semantic similarity scores
        doc_id_to_sim = {cand.event_id: sim for sim, cand in candidates}
        valid_candidates = [(doc_id_to_sim[doc.event_id], doc) for doc in docs]
        
        # Stage 3: Reranking
        analogues = self.reranker.rerank(query_event, valid_candidates)
        
        # Stage 4: Attach Outcomes
        # If we had a database of historical events, we would pass it to HistoricalOutcomeBuilder
        # Since we don't hold the full DB in memory by default, we'll leave it to the consumer
        # or a dedicated retrieval endpoint that orchestrates Matcher + OutcomeBuilder.
        
        return analogues[:top_k]
