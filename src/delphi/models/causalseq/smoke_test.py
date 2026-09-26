import torch
from torch.utils.data import DataLoader
from .config import CausalSeqConfig
from .model import CausalSeq
from .dataset import construct_sequences_with_temporal_guard, CausalSeqDataset
from .trainer import CausalSeqTrainer
from .generation import generate_greedy, generate_beam_search
import tempfile
import os

def run_smoke_test():
    print("Running CausalSeq architecture smoke test (SYNTHETIC FIXTURE)...")
    
    config = CausalSeqConfig(
        input_dim=256,
        hidden_dim=64,
        encoder_layers=1,
        decoder_layers=1,
        num_event_types=10,
        num_time_bins=5,
        num_actors=10,
        num_targets=10,
        num_domains=10,
        max_context_length=5,
        max_forecast_length=3,
        teacher_forcing_ratio=0.5,
        learning_rate=0.01
    )
    
    # Generate fake chronological events
    raw_events = []
    for i in range(20):
        # We need realistic sequential timestamps
        d = 10 + i
        raw_events.append({
            "event_id": f"E{i}",
            "timestamp": f"2026-01-{d:02d}T12:00:00Z",
            "embedding": torch.randn(256),
            "event_type": i % 10,
            "time_bin": i % 5,
            "actor": i % 10,
            "target": i % 10,
            "domain": i % 10
        })
        
    examples = construct_sequences_with_temporal_guard(
        raw_events, 
        max_context=5, 
        max_forecast=3, 
        pad_idx=config.num_event_types,
        time_pad_idx=config.num_time_bins
    )
    ds = CausalSeqDataset(examples)
    dl = DataLoader(ds, batch_size=2)
    
    trainer = CausalSeqTrainer(config)
    results = trainer.train(dl, dl, epochs=2)
    
    print("Training finished.")
    print("Metrics:", results["metrics"])
    print("Parameter Count:", results["params_count"])
    
    with tempfile.TemporaryDirectory() as tmpdir:
        trainer.save(tmpdir)
        print("Checkpoint saved.")
        
        # Test greedy generation
        src, mask, _, _, _, _, _, _ = next(iter(dl))
        src = src.to(trainer.device)
        mask = mask.to(trainer.device)
        
        greedy_res = generate_greedy(trainer.model, src, mask, max_len=3)
        print("Greedy Output Shape:", greedy_res["event_type"].shape)
        
        # Test beam search
        beam_res = generate_beam_search(trainer.model, src[0:1], mask[0:1], max_len=3, beam_width=3)
        print("Beam Search Output Length:", len(beam_res["event_type"]))
        
    print("CAUSALSEQ ARCHITECTURE VALIDATED — REAL HISTORICAL TRAINING/BACKTESTING PENDING")

if __name__ == "__main__":
    run_smoke_test()
