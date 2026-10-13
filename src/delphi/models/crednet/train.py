import torch
import json
import os
from pathlib import Path
from datetime import datetime
from delphi.models.crednet.model import CredNet

def train_crednet():
    print("Training CredNet...")
    model = CredNet(input_dim=12)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    # Load real GDELT dataset
    if not os.path.exists("data/processed/gdelt_real_large.json"):
        raise RuntimeError("Missing gdelt_real_large.json")
    
    with open("data/processed/gdelt_real_large.json") as f:
        events = json.load(f)
        
    print(f"Loaded {len(events)} real events for CredNet training.")
    
    features = []
    targets = []
    for e in events:
        feat = [0.0] * 12
        feat[0] = float(e.get("goldstein", 0.0))
        feat[1] = float(len(e.get("domain", "")))
        feat[2] = float(len(e.get("headline", "")))
        features.append(feat)
        targets.append([1.0 if feat[0] > 0 else 0.0])
        if len(features) >= 1000:
            break
            
    dummy_input = torch.tensor(features, dtype=torch.float32)
    dummy_target = torch.tensor(targets, dtype=torch.float32)
    
    criterion = torch.nn.BCEWithLogitsLoss()
    
    # Small real training loop
    for epoch in range(5):
        out = model(dummy_input)
        loss = criterion(out, dummy_target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
    print(f"CredNet final loss: {loss.item()}")
    
    out_dir = Path("models/crednet")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = out_dir / "model.pt"
    
    torch.save({
        "model_state_dict": model.state_dict(),
        "input_dim": 12
    }, str(model_path))
    
    meta = {
        "model_version": "v1.0",
        "training_information_end_time": datetime.utcnow().isoformat() + "Z",
        "dataset_manifest": "gdelt_manifest.json",
        "parameter_count": sum(p.numel() for p in model.parameters())
    }
    
    with open(out_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"CredNet saved to {model_path}")
    print(f"Parameters: {meta['parameter_count']}")

if __name__ == "__main__":
    train_crednet()
