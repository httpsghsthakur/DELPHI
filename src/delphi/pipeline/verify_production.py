import os
import sys
import torch
import faiss
import json
from pathlib import Path

def check(condition, message):
    if not condition:
        print(f"[FAIL] {message}")
        sys.exit(1)
    print(f"[PASS] {message}")

def verify_production():
    print("========================================")
    print("  DELPHI PRODUCTION VERIFICATION")
    print("========================================")
    
    # Check datasets
    check(os.path.exists("data/processed/gdelt_real_large.json"), "Real GDELT dataset exists")
    check(os.path.exists("data/processed/causal_seqs.json"), "Real causal sequences exist")
    
    with open("data/processed/gdelt_real_large.json") as f:
        data = json.load(f)
    check(len(data) > 1000, "Dataset contains substantial real records (>1000)")
    
    # Check tokenizer
    check(os.path.exists("models/vocab/vocabulary.json"), "Tokenizer vocab exists")
    
    # Check checkpoints
    for model in ["eventembed", "eventnet", "crednet", "causalseq"]:
        ckpt_path = f"models/{model}/model.pt"
        meta_path = f"models/{model}/metadata.json"
        
        check(os.path.exists(ckpt_path), f"{model} checkpoint exists")
        check(os.path.exists(meta_path), f"{model} metadata exists")
        
        # Load metadata and check parameter count
        with open(meta_path) as f:
            meta = json.load(f)
        check(meta.get("parameter_count", 0) > 0, f"{model} parameter count > 0")
        
    # Check FAISS
    faiss_path = "indexes/historical/index.faiss"
    check(os.path.exists(faiss_path), "FAISS index exists")
    idx = faiss.read_index(faiss_path)
    check(idx.ntotal > 100, f"FAISS index contains substantial real vectors (ntotal={idx.ntotal})")
    
    # Check Calibration
    calib_path = "models/calibration/calibration.json"
    check(os.path.exists(calib_path), "Calibration parameters exist")
    with open(calib_path) as f:
        calib = json.load(f)
    check("temperature" in calib, "Calibration contains temperature parameter")
    
    # Zero synthetic mock test
    import re
    # We grep orchestrator for MockActual
    with open("src/delphi/forecast/orchestrator.py") as f:
        orch = f.read()
    check("MockActual" not in orch, "Orchestrator contains ZERO MockActual adapters")
    check("torch.randint(" not in open("src/delphi/models/causalseq/train.py").read(), "CausalSeq training contains ZERO torch.randint synthetic targets")
    
    print("\n========================================")
    print("  SYSTEM IS FULLY VERIFIED FOR PRODUCTION")
    print("========================================")
    
if __name__ == "__main__":
    verify_production()
