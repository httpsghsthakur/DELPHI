from typing import List, Dict, Any, Tuple
from .schemas import HistoricalAnalogue, HistoricalEventDocument

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
                "semantic": 0.50,
                "event_type": 0.20,
                "actor": 0.10,
                "target": 0.10,
                "location": 0.05,
                "domain": 0.05,
                "temporal": 0.00
            }
        else:
            self.weights = config
            
    def rerank(self, query: Dict[str, Any], candidates: List[Tuple[float, HistoricalEventDocument]]) -> List[HistoricalAnalogue]:
        """
        candidates: List of (faiss_similarity, HistoricalEventDocument)
        """
        analogues = []
        for i, (sim, cand) in enumerate(candidates):
            # Check for absent features
            q_type = query.get("event_type")
            c_type = cand.event_type
            if q_type and c_type:
                event_type_match = (q_type == c_type)
                event_type_sim = 1.0 if event_type_match else 0.0
            else:
                event_type_match = False
                event_type_sim = 0.5 # Neutral contribution if absent
                
            q_domain = query.get("domain")
            c_domain = cand.domain
            if q_domain and c_domain:
                domain_match = (q_domain == c_domain)
                domain_sim = 1.0 if domain_match else 0.0
            else:
                domain_match = False
                domain_sim = 0.5
            
            actor_sim = compute_overlap(query.get("actors", []), cand.actor_ids)
            target_sim = compute_overlap(query.get("targets", []), cand.target_ids)
            location_sim = compute_overlap(query.get("locations", []), cand.location_ids)
            temporal_sim = 0.0
            
            rerank_score = (
                self.weights.get("semantic", 0.0) * sim +
                self.weights.get("event_type", 0.0) * event_type_sim +
                self.weights.get("domain", 0.0) * domain_sim +
                self.weights.get("actor", 0.0) * actor_sim +
                self.weights.get("target", 0.0) * target_sim +
                self.weights.get("location", 0.0) * location_sim +
                self.weights.get("temporal", 0.0) * temporal_sim
            )
            
            similarities = []
            differences = []
            
            if q_type and c_type:
                if event_type_match:
                    similarities.append(f"Same event type ({c_type})")
                else:
                    differences.append(f"Different event type ({q_type} vs {c_type})")
            else:
                differences.append("Event type information absent in query or candidate")
                
            if actor_sim > 0:
                similarities.append(f"Shared actors ({int(actor_sim*100)}% overlap)")
            elif query.get("actors") and cand.actor_ids:
                differences.append("No shared actors")
            else:
                differences.append("Actor metadata absent")
                
            if target_sim > 0:
                similarities.append(f"Shared targets ({int(target_sim*100)}% overlap)")
                
            analogue = HistoricalAnalogue(
                analogue_id=f"ana_{cand.event_id}",
                query_event_id=query.get("event_id", ""),
                historical_event_id=cand.event_id,
                semantic_similarity=sim,
                final_rank_score=rerank_score,
                event_type_similarity=event_type_sim,
                actor_similarity=actor_sim,
                target_similarity=target_sim,
                location_similarity=location_sim,
                temporal_relevance=temporal_sim,
                event_type_match=event_type_match,
                domain_match=domain_match,
                historical_event_date=cand.event_date,
                similarities=similarities,
                differences=differences,
                outcome_timeline=[], 
                historical_context=cand.text,
                evidence=[cand.source_id] if cand.source_id else []
            )
            analogues.append(analogue)
            
        # Sort descending by rerank score. Break ties using semantic similarity, then string ID to be fully deterministic.
        analogues.sort(key=lambda x: (x.final_rank_score, x.semantic_similarity, x.historical_event_id), reverse=True)
        return analogues
