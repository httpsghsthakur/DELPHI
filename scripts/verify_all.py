import os
import json
import torch
import faiss
import requests
from delphi.tokenizer.tokenizer import CustomTokenizer
from delphi.tokenizer.vocabulary import Vocabulary
from delphi.models.eventembed.model import EventEmbed
from delphi.models.eventnet.model import EventNet
from delphi.models.crednet.model import CredNet
from delphi.models.causalseq.model import CausalSeq
from delphi.api.config import settings

def main():
    print("=== 2. DATA VERIFICATION ===")
    with open("data/processed/gdelt_sample.json") as f:
        data = json.load(f)
    print(f"Record count: {len(data)}")
    print(f"Min TS: {min(r['date'] for r in data)}")
    print(f"Max TS: {max(r['date'] for r in data)}")
    print(f"Domains: {len(set(r.get('domain', 1) for r in data))}")
    print(f"Event Types: {len(set(r['event_code'] for r in data))}")
    
    print("\n=== 3. TOKENIZER VERIFICATION ===")
    tok = CustomTokenizer.load("models/vocab")
    print(f"Vocab size: {tok.vocab.size()}")
    
    print("\n=== 4. EVENTEMBED VERIFICATION ===")
    ee_ckpt = torch.load("models/eventembed/model.pt")
    from delphi.models.eventembed.config import EventEmbedConfig
    # Update config loading to ignore missing fields or provide them if we have defaults
    ee_cfg = EventEmbedConfig(**ee_ckpt["config"])
    ee = EventEmbed(ee_cfg, char_vocab_size=128)
    ee.load_state_dict(ee_ckpt["model_state_dict"])
    print(f"EE Params: {sum(p.numel() for p in ee.parameters())}")
    
    print("\n=== 5. EVENTNET VERIFICATION ===")
    en_ckpt = torch.load("models/eventnet/model.pt")
    from delphi.models.eventnet.config import EventNetConfig
    en_cfg = EventNetConfig(**en_ckpt["config"])
    en = EventNet(en_cfg)
    en.load_state_dict(en_ckpt["model_state_dict"])
    print(f"EN Params: {sum(p.numel() for p in en.parameters())}")
    
    print("\n=== 7. CREDNET VERIFICATION ===")
    cn_ckpt = torch.load("models/crednet/model.pt")
    cn = CredNet(input_dim=12)
    cn.load_state_dict(cn_ckpt["model_state_dict"])
    print(f"CN Params: {sum(p.numel() for p in cn.parameters())}")
    
    print("\n=== 8. CAUSALSEQ VERIFICATION ===")
    cs_ckpt = torch.load("models/causalseq/model.pt")
    from delphi.models.causalseq.config import CausalSeqConfig
    cs_cfg = CausalSeqConfig(**cs_ckpt["config"])
    cs = CausalSeq(cs_cfg)
    cs.load_state_dict(cs_ckpt["model_state_dict"])
    print(f"CS Params: {sum(p.numel() for p in cs.parameters())}")
    
    print("\n=== 10. FAISS VERIFICATION ===")
    idx = faiss.read_index("indexes/historical/index.faiss")
    print(f"FAISS ntotal: {idx.ntotal}, dim: {idx.d}")
    
    print("\n=== API PROOF ===")
    try:
        r = requests.get("http://localhost:8000/health/ready")
        print(f"/health/ready: {r.status_code}")
        r = requests.get("http://localhost:8000/models")
        print(f"/models: {r.status_code}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    main()
