import json
import os
import faiss
import numpy as np
from pathlib import Path
from datetime import datetime

def build_index():
    print("Building Historical FAISS Index...")
    data_path = "data/processed/gdelt_real_large.json"
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing {data_path}")
        
    with open(data_path, "r") as f:
        records = json.load(f)
        
    import torch
    from delphi.tokenizer.tokenizer import CustomTokenizer
    from delphi.models.eventembed.model import EventEmbed
    from delphi.models.eventembed.config import EventEmbedConfig
    
    tokenizer = CustomTokenizer.load("models/vocab")
    ee_ckpt = torch.load("models/eventembed/model.pt")
    ee_cfg = EventEmbedConfig(**ee_ckpt["config"])
    ee = EventEmbed(ee_cfg, char_vocab_size=128)
    ee.load_state_dict(ee_ckpt["model_state_dict"])
    ee.eval()
        
    dimension = 256
    index = faiss.IndexFlatL2(dimension)
    
    metadata = []
    vectors = []
    
    print(f"Building index for {min(10000, len(records))} real records...")
    
    for i, r in enumerate(records[:10000]):
        text = r.get("headline", "")
        tokens = tokenizer.encode(text)
        input_ids = torch.zeros(1, 32, dtype=torch.long)
        mask = torch.zeros(1, 32, dtype=torch.long)
        dummy_chars = torch.zeros(1, 32, 5, dtype=torch.long)
        for t_idx, tok_id in enumerate(tokens.input_ids[:32]):
            input_ids[0, t_idx] = tok_id
            mask[0, t_idx] = 1
            
        with torch.no_grad():
            out = ee(input_ids, dummy_chars, mask)
            vec = out["sequence_embedding"].squeeze(0).numpy().astype('float32')
            
        vec = vec / (np.linalg.norm(vec) + 1e-9)
        vectors.append(vec)
        
        metadata.append({
            "event_id": r["event_id"],
            "event_date": r["date"],
            "event_type": r["event_code"],
            "text": text
        })
        
    if vectors:
        vectors_np = np.vstack(vectors)
        index.add(vectors_np)
        
    out_dir = Path("indexes/historical")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    faiss.write_index(index, str(out_dir / "index.faiss"))
    
    import pandas as pd
    df = pd.DataFrame(metadata)
    df.to_parquet(out_dir / "metadata.parquet")
    
    manifest = {
        "index_name": "GDELT_Historical_Index",
        "ntotal": index.ntotal,
        "dimension": dimension,
        "date_range": [min(r["date"] for r in records), max(r["date"] for r in records)] if records else [],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(out_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"FAISS index built. ntotal: {index.ntotal}")

if __name__ == "__main__":
    build_index()
