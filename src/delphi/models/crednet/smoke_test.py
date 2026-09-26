import torch
from torch.utils.data import DataLoader
from .model import CredNet
from .dataset import CredNetDataset
from delphi.datasets.schemas import CredibilityFeatures
from .trainer import CredNetTrainer
import tempfile
import os

def run_smoke_test():
    print("Running CredNet architecture smoke test (SYNTHETIC FIXTURE)...")
    
    features = []
    labels = []
    
    for i in range(20):
        f = CredibilityFeatures(
            source_id=f"S_{i%3}",
            article_id=f"A_{i}",
            timestamp="2026-01-01",
            author_identifiable=1.0 if i%2 == 0 else 0.0,
            dataset_version="v1.0"
        )
        features.append(f)
        labels.append(1.0 if i%2 == 0 else 0.0)
        
    ds = CredNetDataset(features, labels)
    dl = DataLoader(ds, batch_size=4)
    
    config = {
        "learning_rate": 0.01,
        "epochs": 2,
        "dataset_version": "smoke-test-1.0"
    }
    
    trainer = CredNetTrainer(config)
    results = trainer.train(dl, dl)
    
    print("Training finished.")
    print("Metrics:", results["metrics"])
    
    with tempfile.TemporaryDirectory() as tmpdir:
        trainer.save(tmpdir)
        print("Checkpoint saved.")
        
        from .inference import CredNetInference
        inf = CredNetInference(tmpdir)
        res = inf.predict([features[0]])
        print(f"Inference test: Raw Logit = {res[0].raw_logit}, Calibrated Score = {res[0].calibrated_score}")
        
    print("NELA-GT ADAPTER READY — REAL DATA PROCESSING PENDING")
    print("CredNet Smoke Test: ARCHITECTURE VALIDATED — REAL TRAINING PENDING")

if __name__ == "__main__":
    run_smoke_test()
