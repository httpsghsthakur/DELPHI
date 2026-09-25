import json
import hashlib
from datetime import datetime, timezone
import os

def serialize_tokenizer(vocab_map: dict, config: dict, version: str, path: str):
    os.makedirs(path, exist_ok=True)
    
    with open(os.path.join(path, "vocabulary.json"), "w", encoding="utf-8") as f:
        json.dump(vocab_map, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(path, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        
    vocab_hash = hashlib.sha256(json.dumps(vocab_map, sort_keys=True).encode("utf-8")).hexdigest()
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()
    
    metadata = {
        "tokenizer_name": "DELPHI_CustomTokenizer",
        "tokenizer_version": version,
        "vocabulary_size": len(vocab_map),
        "configuration_hash": config_hash,
        "vocabulary_hash": vocab_hash,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    
    with open(os.path.join(path, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
        
    with open(os.path.join(path, "checksum.txt"), "w", encoding="utf-8") as f:
        f.write(f"VOCAB: {vocab_hash}\nCONFIG: {config_hash}")

def deserialize_tokenizer(path: str):
    with open(os.path.join(path, "vocabulary.json"), "r", encoding="utf-8") as f:
        vocab_map = json.load(f)
        
    with open(os.path.join(path, "config.json"), "r", encoding="utf-8") as f:
        config = json.load(f)
        
    with open(os.path.join(path, "metadata.json"), "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    return vocab_map, config, metadata
