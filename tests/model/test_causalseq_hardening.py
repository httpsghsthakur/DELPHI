import pytest
import torch
import numpy as np
from delphi.models.causalseq.dataset import construct_sequences_with_temporal_guard
from delphi.models.causalseq.config import CausalSeqConfig
from delphi.models.causalseq.model import CausalSeq
from delphi.models.causalseq.backtesting import CausalSeqBacktester
from delphi.models.causalseq.losses import CausalSeqLoss
from delphi.models.causalseq.metrics import compute_sequence_metrics

def test_same_timestamp_ordering():
    raw_events = [
        {"timestamp": "2026-01-01T10:00", "event_id": "B", "embedding": torch.randn(256), "event_type": 1},
        {"timestamp": "2026-01-01T10:00", "event_id": "A", "embedding": torch.randn(256), "event_type": 2},
        {"timestamp": "2026-01-02T10:00", "event_id": "C", "embedding": torch.randn(256), "event_type": 3},
        {"timestamp": "2026-01-02T10:00", "event_id": "D", "embedding": torch.randn(256), "event_type": 4},
    ]
    
    examples = construct_sequences_with_temporal_guard(raw_events, max_context=3, max_forecast=4, pad_idx=99)
    # The tiebreaker is event_id, so the sort order should be A -> B -> C -> D
    
    assert raw_events[0]["event_id"] == "A"
    assert raw_events[1]["event_id"] == "B"
    assert raw_events[2]["event_id"] == "C"
    assert raw_events[3]["event_id"] == "D"

def test_temporal_provenance_guard():
    config = CausalSeqConfig()
    config.checkpoint_training_end_time = "2026-01-05T00:00Z"
    model = CausalSeq(config)
    
    raw_events = [
        {"timestamp": "2026-01-01T10:00", "event_id": "1", "embedding": torch.randn(256), "event_type": 1},
        {"timestamp": "2026-01-02T10:00", "event_id": "2", "embedding": torch.randn(256), "event_type": 2},
        {"timestamp": "2026-01-03T10:00", "event_id": "3", "embedding": torch.randn(256), "event_type": 3},
    ]
    
    backtester = CausalSeqBacktester(model, raw_events, max_context=2, max_forecast=2)
    results = backtester.evaluate_cutoffs(["2026-01-02T10:00"])
    
    cutoff_res = results.get("2026-01-02T10:00")
    assert cutoff_res is not None
    assert cutoff_res["leakage_validation_status"] == "STRICT_TEMPORAL_BACKTEST_UNVERIFIED"

def test_missing_labels_loss():
    config = CausalSeqConfig()
    loss_fn = CausalSeqLoss(config)
    
    # Simulate a missing label (-1) for actor
    preds = {
        "event_type": torch.randn(1, 2, config.num_event_types + 3),
        "time_bin": torch.randn(1, 2, config.num_time_bins + 3),
        "actor": torch.randn(1, 2, config.num_actors),
        "target": torch.randn(1, 2, config.num_targets),
        "domain": torch.randn(1, 2, config.num_domains),
    }
    
    targets = {
        "event_type": torch.tensor([[1, 2]]),
        "time_bin": torch.tensor([[1, 2]]),
        "actor": torch.tensor([[-1, 2]]), # -1 is missing
        "target": torch.tensor([[1, -1]]),
        "domain": torch.tensor([[-1, -1]]), # both missing
    }
    mask = torch.ones(1, 2, dtype=torch.bool)
    
    total_loss, metrics = loss_fn(preds, targets, mask)
    
    assert total_loss.item() > 0
    assert not torch.isnan(total_loss)
    assert metrics["actor"] > 0
    
def test_metrics_edge_cases():
    # Test undefined states when no valid targets exist
    preds = {
        "event_type": torch.randn(1, 2, 10),
        "time_bin": torch.randn(1, 2, 10)
    }
    # Targets are PAD_IDX (e.g. 5)
    targets = {
        "event_type": torch.tensor([[5, 5]]),
        "time_bin": torch.tensor([[5, 5]])
    }
    mask = torch.tensor([[True, True]])
    
    metrics = compute_sequence_metrics(preds, targets, mask, pad_idx=5)
    
    assert metrics["event_nll"] == "undefined"
    assert metrics["event_brier"] == "undefined"
    assert metrics["event_acc_top1"] == 0.0
