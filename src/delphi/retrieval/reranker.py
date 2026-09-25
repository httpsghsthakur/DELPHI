from typing import List, Dict, Any, Tuple
from .schemas import HistoricalAnalogue, HistoricalEventDocument

def compute_overlap(list1: List[str], list2: List[str]) -> float:
    if not list1 and not list2:
        return 0.0
    set1 = set(list1)
    set2 = set(list2)
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return float(intersection) / float(union) if union > 0 else 0.0

class DeterministicReranker:
    def __init__(self, config: Dict[str, float] = None):
        if config is None:
            self.weights = {
                "semantic": 0.60,
                "event_type": 0.15,
                "domain": 0.10,
                "actor_overlap": 0.05,
                "target_overlap": 0.05,
                "location_overlap": 0.05
            }
        else:
            self.weights = config
            
    def rerank(self, query: Dict[str, Any], candidates: List[Tuple[float, HistoricalEventDocument]]) -> List[HistoricalAnalogue]:
        """
        candidates: List of (faiss_similarity, HistoricalEventDocument)
        """
        analogues = []
        for sim, cand in candidates:
            event_type_match = (query.get("event_type") == cand.event_type) and cand.event_type != ""
            domain_match = (query.get("domain") == cand.domain) and cand.domain != ""
            
            actor_overlap = compute_overlap(query.get("actors", []), cand.actor_ids)
            target_overlap = compute_overlap(query.get("targets", []), cand.target_ids)
            location_overlap = compute_overlap(query.get("locations", []), cand.location_ids)
            
            rerank_score = (
                self.weights.get("semantic", 0.0) * sim +
                self.weights.get("event_type", 0.0) * float(event_type_match) +
                self.weights.get("domain", 0.0) * float(domain_match) +
                self.weights.get("actor_overlap", 0.0) * actor_overlap +
                self.weights.get("target_overlap", 0.0) * target_overlap +
                self.weights.get("location_overlap", 0.0) * location_overlap
            )
            
            # Generate similarities and differences
            similarities = []
            differences = []
            
            if event_type_match:
                similarities.append(f"Same event type ({cand.event_type})")
            else:
                differences.append(f"Different event type ({query.get('event_type')} vs {cand.event_type})")
                
            if actor_overlap > 0:
                similarities.append(f"Shared actors ({int(actor_overlap*100)}% overlap)")
            else:
                differences.append("No shared actors")
                
            if target_overlap > 0:
                similarities.append(f"Shared targets ({int(target_overlap*100)}% overlap)")
                
            analogue = HistoricalAnalogue(
                analogue_id=f"ana_{cand.event_id}",
                query_event_id=query.get("event_id", ""),
                historical_event_id=cand.event_id,
                semantic_similarity=sim,
                final_rank_score=rerank_score,
                event_type_similarity=float(event_type_match),
                actor_similarity=actor_overlap,
                target_similarity=target_overlap,
                location_similarity=location_overlap,
                temporal_relevance=0.0, # Not currently scored
                event_type_match=event_type_match,
                domain_match=domain_match,
                historical_event_date=cand.event_date,
                similarities=similarities,
                differences=differences,
                outcome_timeline=[], # To be filled later if available
                historical_context=cand.text,
                evidence=[cand.source_id] if cand.source_id else []
            )
            analogues.append(analogue)
            
        # Sort descending by rerank score
        analogues.sort(key=lambda x: x.final_rank_score, reverse=True)
        return analogues
