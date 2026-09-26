import pytest
from delphi.research.query_planner import QueryPlanner

def test_query_planner_deterministic():
    planner = QueryPlanner()
    context = {
        "event_type_code": "042_MAKE_A_VISIT",
        "source_text": "The Prime Minister of India visited the United States to discuss trade policy."
    }
    queries = planner.generate_queries(context, max_queries=5)
    assert len(queries) > 0
    assert "visited" in queries[0].lower() or "visit" in queries[0].lower()
    
    # Must be deterministic
    queries2 = planner.generate_queries(context, max_queries=5)
    assert queries == queries2
