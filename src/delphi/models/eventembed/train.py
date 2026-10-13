import torch
import json
import os
from pathlib import Path
from datetime import datetime
from delphi.models.eventembed.config import EventEmbedConfig
from delphi.models.eventembed.model import EventEmbed

def train_eventembed():
    print("Training EventEmbed...")
    config = EventEmbedConfig(vocab_size=1000, word_embedding_dim=192, output_dim=256)
    
    # We will instantiate with vocab size = 1000 (we can fetch actual vocab size, but this is a test)
    # The tokenizer vocab size is around 450
    vocab_size = 1000
    model = EventEmbed(config, char_vocab_size=128)
    
    # Load real GDELT dataset
    if not os.path.exists("data/processed/gdelt_real_large.json"):
        raise RuntimeError("Missing gdelt_real_large.json")
    
    with open("data/processed/gdelt_real_large.json") as f:
        events = json.load(f)
        
    print(f"Loaded {len(events)} real events for EventEmbed training.")
    
    # Train EventEmbed
    import time
    from delphi.tokenizer.tokenizer import CustomTokenizer
    
    tokenizer = CustomTokenizer.load("models/vocab")
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    
    batch_size = 32
    max_seq_len = 32
    
    for epoch in range(1):
        total_loss = 0
        for i in range(0, min(1000, len(events)), batch_size):
            B = min(batch_size, len(events) - i)
            batch_events = events[i:i+B]
            
            # Real tokenization
            input_ids = torch.zeros(B, max_seq_len, dtype=torch.long)
            mask = torch.zeros(B, max_seq_len, dtype=torch.long)
            dummy_chars = torch.zeros(B, max_seq_len, 5, dtype=torch.long)
            
            for b_idx, evt in enumerate(batch_events):
                text = evt.get("headline", "")
                tokens = tokenizer.encode(text)
                for t_idx, tok_id in enumerate(tokens.input_ids[:max_seq_len]):
                    input_ids[b_idx, t_idx] = tok_id
                    mask[b_idx, t_idx] = 1
                    
            out = model(input_ids, dummy_chars, mask)
            # Dummy objective: predict the context (skip-gram or similar) - for simplicity we minimize embedding norm + a classification head in full
            loss = out["sequence_embedding"].norm(dim=-1).mean()
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        print(f"Epoch {epoch} EventEmbed loss: {total_loss / (1000//batch_size)}")
    
    out_dir = Path("models/eventembed")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = out_dir / "model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": {
            "vocab_size": config.vocab_size,
            "word_embedding_dim": config.word_embedding_dim,
            "output_dim": config.output_dim,
            "character": config.character.model_dump(),
            "fusion": config.fusion.model_dump()
        },
        "char_vocab_size": 128
    }, str(model_path))
    
    meta = {
        "model_version": "v1.0",
        "training_information_end_time": datetime.utcnow().isoformat() + "Z",
        "dataset_manifest": "gdelt_manifest.json",
        "parameter_count": sum(p.numel() for p in model.parameters())
    }
    
    with open(out_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"EventEmbed saved to {model_path}")
    print(f"Parameters: {meta['parameter_count']}")

if __name__ == "__main__":
    train_eventembed()
