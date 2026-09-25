import os
import tempfile
from delphi.retrieval import HistoricalMatcher, HistoricalEventDocument, HistoricalIndexBuilder

def test_retrieval_pipeline():
    dim = 256
    builder = HistoricalIndexBuilder(dimension=dim)
    
    # We want vector 1 and vector 3 to be similar
    events = [
        HistoricalEventDocument(
            event_id="E1", event_date="2020-01-01", event_type="TRADE", event_embedding=[0.5] * dim
        ),
        HistoricalEventDocument(
            event_id="E2", event_date="2020-06-01", event_type="CONFLICT", event_embedding=[-0.5] * dim
        ),
        HistoricalEventDocument(
            event_id="E3", event_date="2021-01-01", event_type="TRADE", event_embedding=[0.5 if i % 2 == 0 else 0.4 for i in range(dim)]
        )
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        builder.build(events, tmpdir, {"environment": "development"})
        
        matcher = HistoricalMatcher(tmpdir, dimension=dim)
        
        query = {
            "event_id": "Q1",
            "event_type": "TRADE",
            "event_embedding": [0.5] * dim
        }
        
        # Predict at end of 2021 -> should return both E1 and E3
        results = matcher.search(query, prediction_time="2021-12-31", top_k=5)
        
        assert len(results) == 3
        # E1 should be top (identical vector, ignoring self-match as query is Q1)
        assert results[0].historical_event_id == "E1"
        assert results[1].historical_event_id == "E3"
        
        # Predict at mid 2020 -> E3 should be temporally filtered!
        results_early = matcher.search(query, prediction_time="2020-03-01", top_k=5)
        
        assert len(results_early) == 1
        assert results_early[0].historical_event_id == "E1"
        
        del matcher
        import gc
        gc.collect()
