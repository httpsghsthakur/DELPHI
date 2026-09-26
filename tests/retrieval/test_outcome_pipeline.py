import pytest
from delphi.retrieval.schemas import HistoricalEventDocument
from delphi.retrieval.outcome_timeline import HistoricalOutcomeBuilder

def test_outcome_temporal_safety():
    # Database of events
    db_events = [
        HistoricalEventDocument(event_id="PAST", event_date="2018-03-01", event_type="TRADE", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="OUT_1", event_date="2018-03-05", event_type="CONFLICT", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="OUT_2", event_date="2018-03-25", event_type="TRADE", event_embedding=[0.0]),
        # Future event that happens AFTER the query prediction cutoff
        HistoricalEventDocument(event_id="FUTURE", event_date="2026-01-02", event_type="CONFLICT", event_embedding=[0.0])
    ]
    
    builder = HistoricalOutcomeBuilder(historical_events=db_events, horizons=[7, 30, 365, 3000]) # 3000 to catch 2026 if it leaks
    
    analogue = db_events[0] # PAST
    
    # Query cutoff is 2026-01-01
    timelines = builder.build(analogue, prediction_cutoff="2026-01-01")
    
    # We should have horizons for 7 days (OUT_1) and 30 days (OUT_2), but NOT 3000 days (FUTURE)
    # Wait, 3000 days from 2018 is 2026. FUTURE happens in 2026-01-02, which is > prediction_cutoff!
    
    horizon_7 = next((t for t in timelines if t.time_horizon == "7 days"), None)
    assert horizon_7 is not None
    assert len(horizon_7.outcomes) == 1
    assert horizon_7.outcomes[0].event_id == "OUT_1"
    
    horizon_30 = next((t for t in timelines if t.time_horizon == "30 days"), None)
    assert horizon_30 is not None
    assert len(horizon_30.outcomes) == 2 # OUT_1 and OUT_2 are both <= 30 days
    assert "OUT_2" in [o.event_id for o in horizon_30.outcomes]
    
    horizon_3000 = next((t for t in timelines if t.time_horizon == "3000 days"), None)
    if horizon_3000 is not None:
        assert "FUTURE" not in [o.event_id for o in horizon_3000.outcomes]
    
    # Let's verify FUTURE is not in any timeline
    for t in timelines:
        for o in t.outcomes:
            assert o.event_id != "FUTURE", "Temporal leakage! Future event included in historical outcomes."

def test_no_fabrication():
    # If no events exist in horizon, no timeline should be created or it should be empty
    db_events = [
        HistoricalEventDocument(event_id="PAST", event_date="2018-03-01", event_type="TRADE", event_embedding=[0.0]),
    ]
    
    builder = HistoricalOutcomeBuilder(historical_events=db_events, horizons=[7])
    timelines = builder.build(db_events[0], prediction_cutoff="2026-01-01")
    
    assert len(timelines) == 0, "No timelines should be fabricated if no data exists."
