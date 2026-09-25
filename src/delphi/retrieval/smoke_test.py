import os
import tempfile
import json
from delphi.retrieval import HistoricalEventDocument, HistoricalIndexBuilder, HistoricalMatcher

def run_smoke_test():
    print("Running Historical Intelligence Smoke Test...")
    
    # 1. Build a deterministic development fixture
    dim = 256
    events = [
        HistoricalEventDocument(
            event_id="EVT001",
            event_date="2020-01-01",
            event_type="TRADE",
            actor_ids=["USA", "CHN"],
            domain="ECONOMICS",
            event_embedding=[0.8] * dim
        ),
        HistoricalEventDocument(
            event_id="EVT002",
            event_date="2020-06-01",
            event_type="CONFLICT",
            actor_ids=["RUS", "UKR"],
            domain="MILITARY",
            event_embedding=[-0.8] * dim
        ),
        HistoricalEventDocument(
            event_id="EVT003",
            event_date="2021-03-15",
            event_type="TRADE",
            actor_ids=["USA", "EU"],
            domain="ECONOMICS",
            event_embedding=[0.75] * dim
        )
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Build Index
        builder = HistoricalIndexBuilder(dimension=dim)
        config = {
            "environment": "development",
            "eventembed_version": "v1.0.0"
        }
        manifest = builder.build(events, tmpdir, config)
        print(f"Index built with {manifest['record_count']} records.")
        
        # Initialize Matcher
        matcher = HistoricalMatcher(tmpdir, dimension=dim, config={"eventembed_version": "v1.0.0"})
        print("Historical Matcher initialized.")
        
        # Test 1: Self Match Prevention and Reranking
        query = {
            "event_id": "EVT001",
            "event_type": "TRADE",
            "domain": "ECONOMICS",
            "actors": ["USA"],
            "event_embedding": [0.8] * dim
        }
        
        results = matcher.search(query, prediction_time="2022-01-01")
        
        assert len(results) == 2, "Self-match EVT001 should be filtered out"
        assert results[0].historical_event_id == "EVT003", "EVT003 should be the most similar analogue"
        assert "Same event type (TRADE)" in results[0].similarities
        print("Self-match prevention and reranking tested successfully.")
        
        # Test 2: Strict Temporal Filtering
        results_early = matcher.search(query, prediction_time="2020-03-01")
        assert len(results_early) == 0, "EVT003 and EVT002 occur after prediction_time, should return 0 results (EVT001 is self)"
        print("Temporal Leakage Guard tested successfully.")
        
    print("Historical Intelligence Smoke Test: COMPLETE")

if __name__ == "__main__":
    run_smoke_test()
