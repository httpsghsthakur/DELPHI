import pytest
from delphi.retrieval.filters import TemporalHistoricalFilter, MetadataFilter
from delphi.retrieval.schemas import HistoricalEventDocument

def test_temporal_filter():
    events = [
        HistoricalEventDocument(event_id="1", event_date="2020-01-01", event_type="TEST", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="2", event_date="2020-01-05", event_type="TEST", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="3", event_date="2020-01-10", event_type="TEST", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="4", event_date="2020-01-11", event_type="TEST", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="5", event_date="2020-01-20", event_type="TEST", event_embedding=[0.0])
    ]
    
    filtered = TemporalHistoricalFilter.filter(events, "2020-01-10")
    
    assert len(filtered) == 3
    ids = [e.event_id for e in filtered]
    assert "1" in ids
    assert "2" in ids
    assert "3" in ids
    assert "4" not in ids
    assert "5" not in ids

def test_self_match_prevention():
    events = [
        HistoricalEventDocument(event_id="EVT001", event_date="2020-01-01", event_type="TEST", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="EVT002", event_date="2020-01-05", event_type="TEST", event_embedding=[0.0]),
    ]
    
    meta_filter = MetadataFilter(query_event_id="EVT001")
    filtered = meta_filter.filter(events)
    
    assert len(filtered) == 1
    assert filtered[0].event_id == "EVT002"
