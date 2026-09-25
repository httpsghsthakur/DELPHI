import pytest
from delphi.retrieval.reranker import DeterministicReranker
from delphi.retrieval.schemas import HistoricalEventDocument

def test_deterministic_reranker_ordering():
    reranker = DeterministicReranker({
        "semantic": 0.5,
        "event_type": 0.5,
        "domain": 0.0,
        "actor_overlap": 0.0,
        "target_overlap": 0.0,
        "location_overlap": 0.0
    })
    
    query = {
        "event_id": "Q1",
        "event_type": "TRADE"
    }
    
    cand1 = HistoricalEventDocument(event_id="C1", event_date="2020-01-01", event_type="TRADE", event_embedding=[0.0])
    cand2 = HistoricalEventDocument(event_id="C2", event_date="2020-01-02", event_type="CONFLICT", event_embedding=[0.0])
    
    # Sim is 0.8 for both
    # Cand1 gets +0.5 for event_type match -> 0.4 + 0.5 = 0.9
    # Cand2 gets +0.0 -> 0.4
    
    analogues = reranker.rerank(query, [(0.8, cand1), (0.8, cand2)])
    
    assert len(analogues) == 2
    assert analogues[0].historical_event_id == "C1"
    assert analogues[1].historical_event_id == "C2"
    assert analogues[0].final_rank_score > analogues[1].final_rank_score
    
    # Check similarities extraction
    assert "Same event type (TRADE)" in analogues[0].similarities
    assert "Different event type (TRADE vs CONFLICT)" in analogues[1].differences
