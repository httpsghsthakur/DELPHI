import torch
import json
import os
from pathlib import Path
from datetime import datetime
from delphi.models.eventnet.config import EventNetConfig
from delphi.models.eventnet.model import EventNet

def train_eventnet():
    print("Training EventNet...")
    config = EventNetConfig(
        input_dim=256,
        num_event_types=250,
        num_token_labels=9
    )
    
    model = EventNet(config)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    model.train()
    
    # Load real GDELT dataset
    if not os.path.exists("data/processed/gdelt_real_large.json"):
        raise RuntimeError("Missing gdelt_real_large.json")
    
    with open("data/processed/gdelt_real_large.json") as f:
        events = json.load(f)
        
    print(f"Loaded {len(events)} real events for EventNet training.")
    
    import time
    from delphi.tokenizer.tokenizer import CustomTokenizer
    from delphi.models.eventembed.model import EventEmbed
    from delphi.models.eventembed.config import EventEmbedConfig
    
    tokenizer = CustomTokenizer.load("models/vocab")
    ee_ckpt = torch.load("models/eventembed/model.pt")
    ee_cfg = EventEmbedConfig(**ee_ckpt["config"])
    ee = EventEmbed(ee_cfg, char_vocab_size=128)
    ee.load_state_dict(ee_ckpt["model_state_dict"])
    ee.eval() # freeze EE for EN training
    
    model.train()
    batch_size = 32
    max_seq_len = 32
    
    event_labels = []
    texts = []
    for e in events:
        c = e.get("event_code", "000")
        try:
            val = int(c)
            event_labels.append(min(val, 249))
            texts.append(e.get("headline", ""))
        except:
            pass
            
    for epoch in range(1):
        total_loss = 0
        for i in range(0, min(1000, len(event_labels)), batch_size):
            batch_labels = event_labels[i:i+batch_size]
            batch_texts = texts[i:i+batch_size]
            B = len(batch_labels)
            if B == 0: continue
            
            input_ids = torch.zeros(B, max_seq_len, dtype=torch.long)
            mask = torch.zeros(B, max_seq_len, dtype=torch.long)
            dummy_chars = torch.zeros(B, max_seq_len, 5, dtype=torch.long)
            
            for b_idx, text in enumerate(batch_texts):
                tokens = tokenizer.encode(text)
                for t_idx, tok_id in enumerate(tokens.input_ids[:max_seq_len]):
                    input_ids[b_idx, t_idx] = tok_id
                    mask[b_idx, t_idx] = 1
            
            with torch.no_grad():
                ee_out = ee(input_ids, dummy_chars, mask)
                real_input = ee_out["sequence_embedding"].unsqueeze(1).expand(-1, 32, -1) # expand to seq len 32 for EN
            
            tgt_labels = torch.tensor(batch_labels, dtype=torch.long)
            
            out = model(real_input, mask)
            
            loss_evt = torch.nn.functional.cross_entropy(out["event_logits"], tgt_labels)
            
            optimizer.zero_grad()
            loss_evt.backward()
            optimizer.step()
            
            total_loss += loss_evt.item()
            
        print(f"Epoch {epoch} loss: {total_loss / (len(event_labels)//batch_size + 1)}")
    
    out_dir = Path("models/eventnet")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = out_dir / "model.pt"
    
    # Event type mapping (dummy for testing)
    event_type_to_id = {f"ET_{i}": i for i in range(250)}
    
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": {
            "input_dim": config.input_dim,
            "num_event_types": config.num_event_types,
            "num_token_labels": config.num_token_labels,
            "bilstm": config.bilstm.model_dump(),
            "attention": config.attention.model_dump(),
            "loss": config.loss.model_dump(),
            "eventembed": config.eventembed.model_dump()
        },
        "event_type_to_id": event_type_to_id
    }, str(model_path))
    
    meta = {
        "model_version": "v1.0",
        "training_information_end_time": datetime.utcnow().isoformat() + "Z",
        "dataset_manifest": "gdelt_manifest.json",
        "parameter_count": sum(p.numel() for p in model.parameters())
    }
    
    with open(out_dir / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"EventNet saved to {model_path}")
    print(f"Parameters: {meta['parameter_count']}")

if __name__ == "__main__":
    train_eventnet()
