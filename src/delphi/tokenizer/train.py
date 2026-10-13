import json
import os
from pathlib import Path
from delphi.tokenizer.vocabulary import VocabularyBuilder
from delphi.tokenizer.tokenizer import CustomTokenizer
from delphi.tokenizer.special_tokens import SPECIAL_TOKENS

def train_tokenizer():
    print("Training custom tokenizer from corpus...")
    data_path = "data/processed/gdelt_real_large.json"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing {data_path}")
    
    with open(data_path, "r") as f:
        records = json.load(f)
        
    corpus = [record.get("headline", "") for record in records[:10000]]
    
    print(f"Loaded {len(corpus)} records for vocabulary building.")
    
    # Actually build vocabulary
    vocab = VocabularyBuilder(min_frequency=1).build(corpus)
    
    config = {
        "sequence": {"max_length": 256, "add_bos": True, "add_eos": True}, 
        "normalization": {}
    }
    tokenizer = CustomTokenizer(vocab, config)
    
    out_dir = Path("models/vocab")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    tokenizer.save(str(out_dir))
    
    print(f"Tokenizer saved to {out_dir}")
    print(f"Vocab size: {len(tokenizer.vocab._token_to_id)}")

if __name__ == "__main__":
    train_tokenizer()
