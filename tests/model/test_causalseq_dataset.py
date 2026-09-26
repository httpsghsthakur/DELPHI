import pytest
import torch
from delphi.models.causalseq.dataset import construct_sequences_with_temporal_guard, create_causal_temporal_split

def test_temporal_leakage_guard():
    raw_events = [
        {"timestamp": "2026-01-01T10:00", "event_id": "1", "embedding": torch.randn(256), "event_type": 1},
        {"timestamp": "2026-01-02T10:00", "event_id": "2", "embedding": torch.randn(256), "event_type": 2},
        {"timestamp": "2026-01-03T10:00", "event_id": "3", "embedding": torch.randn(256), "event_type": 3},
    ]
    
    examples = construct_sequences_with_temporal_guard(raw_events, max_context=2, max_forecast=4, pad_idx=99)
    
    assert len(examples) == 2
    
    ex1 = examples[0]
    assert ex1.cutoff_timestamp == "2026-01-01T10:00"
    # Target must be strictly after cutoff
    assert ex1.target_events[1]["timestamp"] == "2026-01-02T10:00" # BOS is 0



def test_causal_temporal_split():
    raw_events = [
        {"timestamp": f"2026-01-{i:02d}T10:00", "event_id": str(i), "embedding": torch.randn(256), "event_type": 1}
        for i in range(1, 15)
    ]
    
    examples = construct_sequences_with_temporal_guard(raw_events, max_context=3, max_forecast=4, pad_idx=99)
    train_ds, val_ds, test_ds = create_causal_temporal_split(examples, val_ratio=0.2, test_ratio=0.2)
    
    assert len(train_ds) > 0
    assert len(val_ds) > 0
    assert len(test_ds) > 0
    
    # Assert bounds
    assert train_ds.examples[-1].cutoff_timestamp <= val_ds.examples[0].cutoff_timestamp
    assert val_ds.examples[-1].cutoff_timestamp <= test_ds.examples[0].cutoff_timestamp
