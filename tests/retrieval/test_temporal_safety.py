import pytest
from delphi.retrieval.filters import TemporalHistoricalFilter
from delphi.retrieval.schemas import HistoricalEventDocument

def test_temporal_safety_obvious_future():
    events = [HistoricalEventDocument(event_id="1", event_date="2022-01-01", event_type="TEST", event_embedding=[0.0])]
    assert len(TemporalHistoricalFilter.filter(events, "2021-01-01")) == 0

def test_temporal_safety_same_day():
    events = [HistoricalEventDocument(event_id="1", event_date="2021-01-01", event_type="TEST", event_embedding=[0.0])]
    assert len(TemporalHistoricalFilter.filter(events, "2021-01-01")) == 1

def test_temporal_safety_train_test_separation():
    # If prediction is 2021-06-01
    events = [
        HistoricalEventDocument(event_id="E_TRAIN", event_date="2020-01-01", event_type="TEST", event_embedding=[0.0]),
        HistoricalEventDocument(event_id="E_TEST", event_date="2022-01-01", event_type="TEST", event_embedding=[0.0])
    ]
    filtered = TemporalHistoricalFilter.filter(events, "2021-06-01")
    assert len(filtered) == 1
    assert filtered[0].event_id == "E_TRAIN"
