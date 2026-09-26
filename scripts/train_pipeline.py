"""
DELPHI Phase 13 — End-to-End Real Model Training Pipeline

Trains all DELPHI models from random initialization on real data:
1. Tokenizer vocabulary from real corpus
2. EventEmbed (Skip-Gram with Negative Sampling)
3. EventNet (BiLSTM + Attention event extraction)
4. CredNet (Source credibility MLP)
5. CausalSeq (Encoder-Decoder trajectory forecasting)
6. FAISS index from trained EventEmbed
7. Calibration artifact

All training uses strict temporal splits.
All experiments are tracked in MLflow.
"""
import os
import sys
import json
import time
import hashlib
import random
from datetime import datetime
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# DELPHI imports
from delphi.tokenizer.vocabulary import VocabularyBuilder, Vocabulary
from delphi.tokenizer.tokenizer import CustomTokenizer
from delphi.tokenizer.normalization import normalize
from delphi.tokenizer.pretokenizer import PreTokenizer
from delphi.tokenizer.serialization import serialize_tokenizer
from delphi.tokenizer.special_tokens import SPECIAL_TOKENS_MAP, PAD_ID

from delphi.models.eventembed.config import EventEmbedConfig
from delphi.models.eventembed.model import EventEmbed
from delphi.models.eventembed.losses import SkipGramNegativeSamplingLoss
from delphi.models.eventembed.dataset import SkipGramDataset, collate_skipgram
from delphi.models.eventembed.negative_sampling import NegativeSampler

from delphi.models.eventnet.config import EventNetConfig
from delphi.models.eventnet.model import EventNet
from delphi.models.eventnet.losses import EventNetLoss

from delphi.models.crednet.model import CredNet
from delphi.models.crednet.losses import CredibilityLoss
from delphi.models.crednet.metrics import compute_metrics as crednet_metrics

from delphi.models.causalseq.config import CausalSeqConfig
from delphi.models.causalseq.model import CausalSeq
from delphi.models.causalseq.losses import CausalSeqLoss

from delphi.retrieval.faiss_index import FaissHistoricalIndex
from delphi.retrieval.schemas import HistoricalEventDocument
from delphi.retrieval.index_builder import HistoricalIndexBuilder

# ============================================================================
# Configuration
# ============================================================================
SEED = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "gdelt_multi"
MODELS_DIR = PROJECT_ROOT / "models"
INDEXES_DIR = PROJECT_ROOT / "indexes"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

# Temporal split boundaries (based on GDELT event dates)
# Train: events with date <= TRAIN_CUTOFF
# Val:   events with date > TRAIN_CUTOFF and <= VAL_CUTOFF
# Test:  events with date > VAL_CUTOFF
TRAIN_CUTOFF = "20230104"  # First 4 days for training
VAL_CUTOFF = "20230105"    # Day 5 for validation
# Day 6-7 reserved for test / temporal backtest

def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def setup_mlflow():
    """Initialize MLflow tracking."""
    try:
        import mlflow
        mlflow.set_tracking_uri(f"sqlite:///{PROJECT_ROOT / 'mlflow.db'}")
        mlflow.set_experiment("DELPHI_Phase13_RealTraining")
        return mlflow
    except ImportError:
        print("WARNING: MLflow not available. Metrics will be saved to files only.")
        return None


# ============================================================================
# Step 1: Load and Parse Real Data
# ============================================================================
def load_gdelt_corpus():
    """Load the real multi-day GDELT corpus."""
    events_path = DATA_DIR / "events.jsonl"
    if not events_path.exists():
        print("ERROR: Real data not found. Run scripts/acquire_data.py first.")
        sys.exit(1)
    
    records = []
    with open(events_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line.strip()))
    
    print(f"Loaded {len(records)} GDELT records")
    return records


def temporal_split(records, train_cutoff, val_cutoff):
    """Split records by event_date with strict temporal ordering."""
    train, val, test = [], [], []
    for r in records:
        date = r.get("event_date", "")
        if date <= train_cutoff:
            train.append(r)
        elif date <= val_cutoff:
            val.append(r)
        else:
            test.append(r)
    
    # Verify no temporal leakage
    if train and val:
        max_train_date = max(r["event_date"] for r in train)
        min_val_date = min(r["event_date"] for r in val)
        assert max_train_date <= min_val_date, f"Temporal leak: train max {max_train_date} > val min {min_val_date}"
    if val and test:
        max_val_date = max(r["event_date"] for r in val)
        min_test_date = min(r["event_date"] for r in test)
        assert max_val_date <= min_test_date, f"Temporal leak: val max {max_val_date} > test min {min_test_date}"
    
    print(f"Temporal split: train={len(train)}, val={len(val)}, test={len(test)}")
    return train, val, test


# ============================================================================
# Step 2: Real Tokenizer Training
# ============================================================================
def build_text_from_record(record):
    """Build a text representation from a GDELT record for tokenization."""
    parts = []
    if record.get("actor1_name"):
        parts.append(record["actor1_name"])
    if record.get("actor1_country"):
        parts.append(record["actor1_country"])
    if record.get("event_code"):
        parts.append(f"EVENT_{record['event_code']}")
    if record.get("actor2_name"):
        parts.append(record["actor2_name"])
    if record.get("actor2_country"):
        parts.append(record["actor2_country"])
    if record.get("source_domain"):
        parts.append(record["source_domain"])
    if record.get("goldstein_scale"):
        try:
            gs = float(record["goldstein_scale"])
            if gs > 5:
                parts.append("POSITIVE_TONE")
            elif gs < -5:
                parts.append("NEGATIVE_TONE")
            else:
                parts.append("NEUTRAL_TONE")
        except ValueError:
            pass
    return " ".join(parts) if parts else "UNKNOWN_EVENT"


def train_tokenizer(train_records, mlflow_instance=None):
    """Build vocabulary from real training corpus."""
    print("\n" + "=" * 60)
    print("Step 2: Training Real Tokenizer")
    print("=" * 60)
    
    pretokenizer = PreTokenizer()
    
    # Build tokenized corpus
    tokenized_corpus = []
    all_tokens = []
    for r in train_records:
        text = build_text_from_record(r)
        norm_text = normalize(text, {})
        tokens = pretokenizer.pre_tokenize(norm_text)
        tokenized_corpus.append(tokens)
        all_tokens.extend(tokens)
    
    # Build vocabulary
    builder = VocabularyBuilder(min_frequency=2, max_size=10000)
    vocab = builder.build(tokenized_corpus)
    
    # Compute stats
    total_tokens = len(all_tokens)
    token_counter = Counter(all_tokens)
    unk_count = sum(1 for t in all_tokens if not vocab.contains(t))
    unk_rate = unk_count / max(total_tokens, 1)
    avg_seq_len = np.mean([len(seq) for seq in tokenized_corpus])
    special_count = sum(1 for t in SPECIAL_TOKENS_MAP.keys())
    
    stats = {
        "vocabulary_size": vocab.size(),
        "total_tokens": total_tokens,
        "unique_tokens_in_corpus": len(token_counter),
        "unknown_token_rate": f"{unk_rate:.4f}",
        "special_token_count": special_count,
        "average_sequence_length": f"{avg_seq_len:.1f}",
    }
    
    print(f"  Vocabulary size: {vocab.size()}")
    print(f"  Total tokens: {total_tokens}")
    print(f"  UNK rate: {unk_rate:.4f}")
    print(f"  Avg sequence length: {avg_seq_len:.1f}")
    
    # Save tokenizer
    tokenizer_dir = MODELS_DIR / "vocab"
    os.makedirs(tokenizer_dir, exist_ok=True)
    
    config = {
        "normalization": {},
        "sequence": {"max_length": 128, "add_bos": True, "add_eos": True, "truncation": True, "padding": "longest"}
    }
    tokenizer = CustomTokenizer(vocab, config)
    tokenizer.save(str(tokenizer_dir), version="2.0.0")
    
    # Save stats
    with open(tokenizer_dir / "training_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    
    if mlflow_instance:
        with mlflow_instance.start_run(run_name="tokenizer_training", nested=True):
            for k, v in stats.items():
                try:
                    mlflow_instance.log_metric(f"tokenizer_{k}", float(v) if not isinstance(v, str) else float(v.split("%")[0]) if "%" in str(v) else 0)
                except (ValueError, TypeError):
                    mlflow_instance.log_param(f"tokenizer_{k}", str(v))
    
    print(f"  Tokenizer saved to {tokenizer_dir}")
    return tokenizer, vocab, tokenized_corpus, stats


# ============================================================================
# Step 3: Real EventEmbed Training
# ============================================================================
def train_eventembed(tokenizer, vocab, tokenized_corpus, train_records, val_records, mlflow_instance=None):
    """Train EventEmbed from random initialization on real data."""
    print("\n" + "=" * 60)
    print("Step 3: Training Real EventEmbed")
    print("=" * 60)
    
    # Encode all training sequences
    encoded_seqs = []
    for tokens in tokenized_corpus:
        ids = vocab.encode(tokens)
        if len(ids) >= 3:  # Need at least 3 tokens for skip-gram
            encoded_seqs.append(ids)
    
    print(f"  Training sequences: {len(encoded_seqs)}")
    
    config = EventEmbedConfig(
        vocab_size=vocab.size(),
        word_embedding_dim=192,
        output_dim=256,
        context_window=5,
        negative_samples=5,
        min_frequency=2,
    )
    
    # Create skip-gram dataset
    sg_dataset = SkipGramDataset(encoded_seqs, context_window=config.context_window, pad_idx=PAD_ID)
    print(f"  Skip-gram pairs: {len(sg_dataset)}")
    
    if len(sg_dataset) == 0:
        print("  ERROR: No skip-gram pairs generated. Corpus too small.")
        return None, None
    
    sg_loader = DataLoader(sg_dataset, batch_size=256, shuffle=True, collate_fn=collate_skipgram)
    
    # Character vocab (simple ASCII)
    char_vocab_size = 128
    
    # Create model
    model = EventEmbed(config, char_vocab_size=char_vocab_size, pad_idx=PAD_ID, char_pad_idx=0).to(DEVICE)
    loss_fn = SkipGramNegativeSamplingLoss(vocab.size(), config.output_dim, pad_idx=PAD_ID).to(DEVICE)
    # Build token frequency dict from training corpus
    from collections import Counter as _Counter
    token_freq = _Counter()
    for seq in encoded_seqs:
        token_freq.update(seq)
    token_freq_dict = dict(token_freq)
    neg_sampler = NegativeSampler(token_freq_dict, vocab.size(), pad_idx=PAD_ID)
    
    optimizer = optim.Adam(list(model.parameters()) + list(loss_fn.parameters()), lr=1e-3)
    
    params = model.count_parameters()
    print(f"  Model parameters: {params['total']:,} total, {params['trainable']:,} trainable")
    
    # Training loop
    epochs = 15
    history = {"train_loss": []}
    
    for epoch in range(epochs):
        model.train()
        loss_fn.train()
        total_loss = 0.0
        batch_count = 0
        
        for targets, contexts in sg_loader:
            targets = targets.to(DEVICE)
            contexts = contexts.to(DEVICE)
            
            # Create dummy char_ids and attention_mask for the embedding input
            # targets shape: [batch_size]
            batch_size = targets.size(0)
            input_ids = targets.unsqueeze(1)  # [B, 1]
            char_ids = torch.zeros(batch_size, 1, 5, dtype=torch.long, device=DEVICE)
            attention_mask = torch.ones(batch_size, 1, dtype=torch.long, device=DEVICE)
            
            # Forward through EventEmbed
            embeddings = model(input_ids, char_ids, attention_mask)
            target_vectors = embeddings["sequence_embedding"]  # [B, 256]
            
            # Sample negatives
            negative_ids = neg_sampler.sample(batch_size, config.negative_samples).to(DEVICE)
            
            optimizer.zero_grad()
            loss = loss_fn(target_vectors, contexts, negative_ids)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(list(model.parameters()) + list(loss_fn.parameters()), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
            batch_count += 1
        
        avg_loss = total_loss / max(batch_count, 1)
        history["train_loss"].append(avg_loss)
        
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
    
    # Save checkpoint
    checkpoint_dir = MODELS_DIR / "eventembed"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    checkpoint_path = checkpoint_dir / "model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "loss_state_dict": loss_fn.state_dict(),
        "config": config.model_dump(),
        "char_vocab_size": char_vocab_size,
        "training_history": history,
        "epoch": epochs,
        "final_loss": history["train_loss"][-1],
        "seed": SEED,
    }, str(checkpoint_path))
    
    metadata = {
        "model_version": "v2.0",
        "architecture": "Word2Vec+CharCNN",
        "embedding_dim": config.output_dim,
        "vocab_size": vocab.size(),
        "training_epochs": epochs,
        "final_loss": history["train_loss"][-1],
        "training_information_end_time": TRAIN_CUTOFF,
        "dataset_version": "v2.0",
        "parameter_count": params,
        "checkpoint": str(checkpoint_path),
    }
    
    with open(checkpoint_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    if mlflow_instance:
        with mlflow_instance.start_run(run_name="eventembed_training", nested=True):
            mlflow_instance.log_param("epochs", epochs)
            mlflow_instance.log_param("embedding_dim", config.output_dim)
            mlflow_instance.log_param("vocab_size", vocab.size())
            mlflow_instance.log_param("training_cutoff", TRAIN_CUTOFF)
            mlflow_instance.log_metric("final_loss", history["train_loss"][-1])
            for i, loss_val in enumerate(history["train_loss"]):
                mlflow_instance.log_metric("train_loss", loss_val, step=i)
    
    print(f"  EventEmbed checkpoint saved: {checkpoint_path}")
    return model, metadata


# ============================================================================
# Step 4: Real EventNet Training
# ============================================================================
def train_eventnet(eventembed_model, vocab, train_records, val_records, mlflow_instance=None):
    """Train EventNet from random initialization using GDELT event codes as labels."""
    print("\n" + "=" * 60)
    print("Step 4: Training Real EventNet")
    print("=" * 60)
    
    # Build event type vocabulary from GDELT event root codes
    event_root_codes = sorted(set(r.get("event_root_code", "") for r in train_records if r.get("event_root_code")))
    event_type_to_id = {code: i for i, code in enumerate(event_root_codes)}
    num_event_types = len(event_type_to_id)
    
    # BIO labels: we use a simplified scheme
    # O=0, B-EVENT=1, I-EVENT=2
    num_token_labels = 3
    
    print(f"  Event types: {num_event_types}")
    print(f"  Event root codes: {event_root_codes[:10]}...")
    
    config = EventNetConfig(
        input_dim=256,
        num_token_labels=num_token_labels,
        num_event_types=num_event_types,
    )
    
    model = EventNet(config).to(DEVICE)
    loss_fn = EventNetLoss(num_token_labels=num_token_labels)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    params = model.count_parameters()
    print(f"  Model parameters: {params['total']:,}")
    
    # Prepare training data: encode records, create fake token labels from event codes
    def prepare_eventnet_batch(records, batch_size=32):
        """Create batches of EventNet training data from GDELT records."""
        batches = []
        for i in range(0, len(records), batch_size):
            batch_records = records[i:i+batch_size]
            batch_embeddings = []
            batch_token_labels = []
            batch_event_labels = []
            batch_masks = []
            
            max_len = 0
            for r in batch_records:
                text = build_text_from_record(r)
                tokens = vocab.encode(normalize(text, {}).split())
                max_len = max(max_len, len(tokens))
            
            max_len = min(max_len, 64)  # Cap at 64 tokens
            
            for r in batch_records:
                text = build_text_from_record(r)
                tokens = vocab.encode(normalize(text, {}).split())[:max_len]
                seq_len = len(tokens)
                
                # Generate embeddings from EventEmbed (frozen)
                input_ids = torch.tensor([tokens], dtype=torch.long, device=DEVICE)
                char_ids = torch.zeros(1, seq_len, 5, dtype=torch.long, device=DEVICE)
                mask = torch.ones(1, seq_len, dtype=torch.long, device=DEVICE)
                
                with torch.no_grad():
                    emb = eventembed_model(input_ids, char_ids, mask)
                    token_emb = emb["token_embeddings"].squeeze(0)  # [seq_len, 256]
                
                # Pad to max_len
                if seq_len < max_len:
                    pad = torch.zeros(max_len - seq_len, 256, device=DEVICE)
                    token_emb = torch.cat([token_emb, pad], dim=0)
                    attention = [1] * seq_len + [0] * (max_len - seq_len)
                else:
                    token_emb = token_emb[:max_len]
                    attention = [1] * max_len
                
                # Token labels: mark first token as B-EVENT, rest as O
                # This is a simplification since GDELT doesn't have token-level annotations
                t_labels = [1] + [0] * (max_len - 1)  # B-EVENT at position 0
                
                # Event type label
                event_code = r.get("event_root_code", "")
                event_label = event_type_to_id.get(event_code, 0)
                
                batch_embeddings.append(token_emb)
                batch_token_labels.append(t_labels)
                batch_event_labels.append(event_label)
                batch_masks.append(attention)
            
            if batch_embeddings:
                batches.append({
                    "embeddings": torch.stack(batch_embeddings),
                    "token_labels": torch.tensor(batch_token_labels, dtype=torch.long, device=DEVICE),
                    "event_labels": torch.tensor(batch_event_labels, dtype=torch.long, device=DEVICE),
                    "attention_mask": torch.tensor(batch_masks, dtype=torch.long, device=DEVICE),
                })
        return batches
    
    # Use a subset for efficiency
    train_subset = train_records[:5000] if len(train_records) > 5000 else train_records
    val_subset = val_records[:1000] if len(val_records) > 1000 else val_records
    
    print(f"  Training on {len(train_subset)} records")
    train_batches = prepare_eventnet_batch(train_subset, batch_size=64)
    
    # Training loop
    epochs = 10
    history = {"train_loss": []}
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        
        for batch in train_batches:
            optimizer.zero_grad()
            outputs = model(batch["embeddings"], batch["attention_mask"])
            
            loss_dict = loss_fn(
                outputs["token_logits"], batch["token_labels"],
                outputs["event_logits"], batch["event_labels"]
            )
            loss = loss_dict["loss"]
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / max(len(train_batches), 1)
        history["train_loss"].append(avg_loss)
        
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
    
    # Evaluation on validation set
    print("  Evaluating on validation set...")
    val_batches = prepare_eventnet_batch(val_subset, batch_size=64)
    
    model.eval()
    all_token_preds, all_token_labels = [], []
    all_event_preds, all_event_labels = [], []
    
    with torch.no_grad():
        for batch in val_batches:
            outputs = model(batch["embeddings"], batch["attention_mask"])
            
            # Token predictions
            token_preds = outputs["token_logits"].argmax(dim=-1)
            mask = batch["attention_mask"].bool()
            for i in range(token_preds.size(0)):
                m = mask[i]
                all_token_preds.extend(token_preds[i][m].cpu().tolist())
                all_token_labels.extend(batch["token_labels"][i][m].cpu().tolist())
            
            # Event predictions
            event_preds = outputs["event_logits"].argmax(dim=-1)
            all_event_preds.extend(event_preds.cpu().tolist())
            all_event_labels.extend(batch["event_labels"].cpu().tolist())
    
    # Compute metrics
    from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score
    
    token_f1 = f1_score(all_token_labels, all_token_preds, average="macro", zero_division=0)
    event_macro_f1 = f1_score(all_event_labels, all_event_preds, average="macro", zero_division=0)
    event_accuracy = accuracy_score(all_event_labels, all_event_preds)
    
    metrics = {
        "span_f1": token_f1,
        "event_type_macro_f1": event_macro_f1,
        "event_type_accuracy": event_accuracy,
    }
    
    print(f"  Span F1: {token_f1:.4f}")
    print(f"  Event-type Macro-F1: {event_macro_f1:.4f}")
    print(f"  Event-type Accuracy: {event_accuracy:.4f}")
    
    # Save checkpoint
    checkpoint_dir = MODELS_DIR / "eventnet"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    checkpoint_path = checkpoint_dir / "model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": config.model_dump(),
        "event_type_to_id": event_type_to_id,
        "num_token_labels": num_token_labels,
        "training_history": history,
        "val_metrics": metrics,
        "seed": SEED,
    }, str(checkpoint_path))
    
    metadata = {
        "model_version": "v2.0",
        "architecture": "BiLSTM+SelfAttention",
        "num_event_types": num_event_types,
        "num_token_labels": num_token_labels,
        "training_epochs": epochs,
        "final_loss": history["train_loss"][-1],
        "training_information_end_time": TRAIN_CUTOFF,
        "dataset_version": "v2.0",
        "val_metrics": metrics,
        "parameter_count": params,
    }
    
    with open(checkpoint_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    if mlflow_instance:
        with mlflow_instance.start_run(run_name="eventnet_training", nested=True):
            mlflow_instance.log_param("epochs", epochs)
            mlflow_instance.log_param("num_event_types", num_event_types)
            mlflow_instance.log_param("training_cutoff", TRAIN_CUTOFF)
            for k, v in metrics.items():
                mlflow_instance.log_metric(k, v)
    
    print(f"  EventNet checkpoint saved: {checkpoint_path}")
    return model, event_type_to_id, metrics


# ============================================================================
# Step 5: Real CredNet Training
# ============================================================================
def train_crednet(train_records, val_records, mlflow_instance=None):
    """Train CredNet on real GDELT source features."""
    print("\n" + "=" * 60)
    print("Step 5: Training Real CredNet")
    print("=" * 60)
    
    def extract_credibility_features(record):
        """Extract 12 credibility features from GDELT record."""
        domain = record.get("source_domain", "")
        url = record.get("source_url", "")
        
        # 1. author_identifiable (GDELT doesn't have author, use actor presence)
        author_id = 1.0 if record.get("actor1_name") else 0.0
        
        # 2. article_length (proxy: number of mentions)
        num_mentions = float(record.get("num_mentions", "1"))
        article_length = min(num_mentions / 50.0, 1.0)
        
        # 3. citation_density (proxy: number of sources)
        num_sources = float(record.get("num_sources", "1"))
        citation_density = min(num_sources / 20.0, 1.0)
        
        # 4. title_sensationalism (proxy: abs goldstein scale)
        try:
            gs = abs(float(record.get("goldstein_scale", "0")))
            sensationalism = min(gs / 10.0, 1.0)
        except ValueError:
            sensationalism = 0.5
        
        # 5. historical_source_reliability (proxy: based on avg_tone moderation)
        try:
            tone = abs(float(record.get("avg_tone", "0")))
            reliability = max(1.0 - tone / 20.0, 0.0)
        except ValueError:
            reliability = 0.5
        
        # 6. corroboration (proxy: num_articles)
        num_articles = float(record.get("num_articles", "1"))
        corroboration = min(num_articles / 20.0, 1.0)
        
        # 7. correction_history (deterministic from domain hash)
        correction = (hash(domain) % 100) / 100.0
        
        # 8. publication_consistency (deterministic from domain)
        consistency = 1.0 / (1.0 + (hash(domain + "cons") % 10))
        
        # 9. primary_source_presence (quad_class 1 = verbal cooperation ~ official)
        quad = record.get("quad_class", "0")
        primary = 1.0 if quad in ("1", "3") else 0.0
        
        # 10. attribution_completeness (has both actors)
        attr = 1.0 if record.get("actor1_code") and record.get("actor2_code") else 0.0
        
        # 11. author_history (has country attribution)
        auth_hist = 1.0 if record.get("actor1_country") else 0.0
        
        # 12. source_longevity (proxy from domain hash, deterministic)
        longevity = (hash(domain + "longevity") % 3650) / 3650.0
        
        return [author_id, article_length, citation_density, sensationalism, reliability,
                corroboration, correction, consistency, primary, attr, auth_hist, longevity]
    
    def get_credibility_label(record):
        """Derive credibility label from GDELT structural signals."""
        score = 0.0
        # Multiple sources = more credible
        try:
            ns = int(record.get("num_sources", "1"))
            if ns >= 3:
                score += 0.3
        except ValueError:
            pass
        # Multiple articles = more credible
        try:
            na = int(record.get("num_articles", "1"))
            if na >= 3:
                score += 0.2
        except ValueError:
            pass
        # Known actors = more credible
        if record.get("actor1_code"):
            score += 0.15
        if record.get("actor2_code"):
            score += 0.15
        # Root event = more structured
        if record.get("is_root_event") == "1":
            score += 0.2
        
        return 1.0 if score >= 0.5 else 0.0
    
    # Build datasets
    train_features = [extract_credibility_features(r) for r in train_records]
    train_labels = [get_credibility_label(r) for r in train_records]
    val_features = [extract_credibility_features(r) for r in val_records]
    val_labels = [get_credibility_label(r) for r in val_records]
    
    print(f"  Train: {len(train_features)} samples, positive rate: {sum(train_labels)/max(len(train_labels),1):.3f}")
    print(f"  Val: {len(val_features)} samples, positive rate: {sum(val_labels)/max(len(val_labels),1):.3f}")
    
    # Create tensors
    X_train = torch.tensor(train_features, dtype=torch.float32)
    y_train = torch.tensor(train_labels, dtype=torch.float32).unsqueeze(1)
    X_val = torch.tensor(val_features, dtype=torch.float32)
    y_val = torch.tensor(val_labels, dtype=torch.float32).unsqueeze(1)
    
    # Balance positive weight
    pos_count = sum(train_labels)
    neg_count = len(train_labels) - pos_count
    pos_weight = torch.tensor([neg_count / max(pos_count, 1)], dtype=torch.float32)
    
    # Model
    model = CredNet(input_dim=12).to(DEVICE)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight.to(DEVICE))
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    # Train
    epochs = 20
    batch_size = 256
    history = {"train_loss": [], "val_loss": []}
    best_val_loss = float("inf")
    best_state = None
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        n_batches = 0
        
        indices = list(range(len(X_train)))
        random.shuffle(indices)
        
        for i in range(0, len(indices), batch_size):
            batch_idx = indices[i:i+batch_size]
            X_batch = X_train[batch_idx].to(DEVICE)
            y_batch = y_train[batch_idx].to(DEVICE)
            
            optimizer.zero_grad()
            logits = model(X_batch)
            loss = criterion(logits, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            n_batches += 1
        
        avg_train_loss = total_loss / max(n_batches, 1)
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_logits = model(X_val.to(DEVICE))
            val_loss = criterion(val_logits, y_val.to(DEVICE)).item()
        
        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(val_loss)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
        
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1}/{epochs} - Train Loss: {avg_train_loss:.4f}, Val Loss: {val_loss:.4f}")
    
    # Restore best model
    if best_state:
        model.load_state_dict(best_state)
        model.to(DEVICE)
    
    # Final evaluation
    model.eval()
    with torch.no_grad():
        val_logits = model(X_val.to(DEVICE)).cpu().view(-1).numpy()
        val_probs = 1.0 / (1.0 + np.exp(-val_logits))
    
    metrics = crednet_metrics(val_labels, val_probs.tolist())
    
    print(f"  Macro-F1: {metrics.get('macro_f1', 'N/A')}")
    print(f"  ROC-AUC: {metrics.get('roc_auc', 'N/A')}")
    print(f"  Brier: {metrics.get('brier', 'N/A')}")
    print(f"  ECE: {metrics.get('ece', 'N/A')}")
    
    # Save checkpoint
    checkpoint_dir = MODELS_DIR / "crednet"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    checkpoint_path = checkpoint_dir / "model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "training_history": history,
        "val_metrics": metrics,
        "seed": SEED,
    }, str(checkpoint_path))
    
    metadata = {
        "model_version": "v2.0",
        "architecture": "MLP(12,32,16,1)",
        "training_epochs": epochs,
        "best_val_loss": best_val_loss,
        "training_information_end_time": TRAIN_CUTOFF,
        "dataset_version": "v2.0",
        "val_metrics": metrics,
    }
    
    with open(checkpoint_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    if mlflow_instance:
        with mlflow_instance.start_run(run_name="crednet_training", nested=True):
            mlflow_instance.log_param("epochs", epochs)
            mlflow_instance.log_param("training_cutoff", TRAIN_CUTOFF)
            for k, v in metrics.items():
                try:
                    mlflow_instance.log_metric(k, float(v))
                except (ValueError, TypeError):
                    pass
    
    print(f"  CredNet checkpoint saved: {checkpoint_path}")
    return model, metrics


# ============================================================================
# Step 6: Build Real FAISS Index
# ============================================================================
def build_faiss_index(eventembed_model, vocab, train_records, mlflow_instance=None):
    """Build FAISS index from real EventEmbed on training data."""
    print("\n" + "=" * 60)
    print("Step 6: Building Real FAISS Index")
    print("=" * 60)
    
    index = FaissHistoricalIndex(dimension=256)
    
    events = []
    batch_size = 128
    
    eventembed_model.eval()
    
    for i in range(0, len(train_records), batch_size):
        batch = train_records[i:i+batch_size]
        
        for r in batch:
            text = build_text_from_record(r)
            tokens = vocab.encode(normalize(text, {}).split())
            if not tokens:
                tokens = [1]  # UNK
            
            input_ids = torch.tensor([tokens], dtype=torch.long, device=DEVICE)
            char_ids = torch.zeros(1, len(tokens), 5, dtype=torch.long, device=DEVICE)
            mask = torch.ones(1, len(tokens), dtype=torch.long, device=DEVICE)
            
            with torch.no_grad():
                emb = eventembed_model(input_ids, char_ids, mask)
                seq_emb = emb["sequence_embedding"].squeeze(0).cpu().numpy().tolist()
            
            event = HistoricalEventDocument(
                event_id=r.get("global_event_id", f"E_{i}"),
                event_date=r.get("event_date", ""),
                timestamp=r.get("event_date", ""),
                event_type=r.get("event_root_code", ""),
                action=r.get("event_code", ""),
                actor_ids=[r.get("actor1_code", "")] if r.get("actor1_code") else [],
                target_ids=[r.get("actor2_code", "")] if r.get("actor2_code") else [],
                domain=r.get("source_domain", ""),
                text=text,
                event_embedding=seq_emb,
                source_id=r.get("source_domain", ""),
                embedding_version="v2.0",
                eventnet_version="v2.0",
                dataset_split="train",
                prediction_information_cutoff=TRAIN_CUTOFF,
            )
            events.append(event)
        
        if (i + batch_size) % 1000 == 0 or i + batch_size >= len(train_records):
            print(f"  Encoded {min(i + batch_size, len(train_records))}/{len(train_records)} events")
    
    # Build and save index
    os.makedirs(str(INDEXES_DIR), exist_ok=True)
    
    builder = HistoricalIndexBuilder(dimension=256)
    manifest = builder.build(events, str(INDEXES_DIR), {
        "index_version": "v2.0",
        "eventembed_version": "v2.0",
        "tokenizer_version": "v2.0",
        "dataset_version": "v2.0",
        "environment": "training",
    })
    
    print(f"  FAISS index built: {manifest['record_count']} vectors")
    print(f"  Saved to: {INDEXES_DIR}")
    
    if mlflow_instance:
        with mlflow_instance.start_run(run_name="faiss_index_build", nested=True):
            mlflow_instance.log_param("vector_count", manifest["record_count"])
            mlflow_instance.log_param("dimension", 256)
    
    return manifest


# ============================================================================
# Step 7: Real CausalSeq Training
# ============================================================================
def train_causalseq(eventembed_model, vocab, train_records, val_records, event_type_to_id, mlflow_instance=None):
    """Train CausalSeq from random initialization on real event trajectories."""
    print("\n" + "=" * 60)
    print("Step 7: Training Real CausalSeq")
    print("=" * 60)
    
    num_event_types = len(event_type_to_id)
    
    # Build actor/target/domain vocabularies from training data
    actor_vocab = sorted(set(r.get("actor1_code", "") for r in train_records if r.get("actor1_code")))
    target_vocab = sorted(set(r.get("actor2_code", "") for r in train_records if r.get("actor2_code")))
    domain_vocab = sorted(set(r.get("source_domain", "") for r in train_records if r.get("source_domain")))
    
    actor_to_id = {a: i for i, a in enumerate(actor_vocab)}
    target_to_id = {t: i for i, t in enumerate(target_vocab)}
    domain_to_id = {d: i for i, d in enumerate(domain_vocab)}
    
    num_actors = max(len(actor_to_id), 2)
    num_targets = max(len(target_to_id), 2)
    num_domains = max(len(domain_to_id), 2)
    
    config = CausalSeqConfig(
        input_dim=256,
        hidden_dim=256,
        encoder_layers=1,
        decoder_layers=1,
        num_event_types=num_event_types,
        num_actors=num_actors,
        num_targets=num_targets,
        num_time_bins=9,
        num_domains=num_domains,
        max_context_length=10,
        max_forecast_length=5,
        checkpoint_training_end_time=TRAIN_CUTOFF,
    )
    
    model = CausalSeq(config).to(DEVICE)
    loss_fn = CausalSeqLoss(config)
    optimizer = optim.Adam(model.parameters(), lr=config.learning_rate)
    
    print(f"  Actors: {num_actors}, Targets: {num_targets}, Domains: {num_domains}")
    print(f"  Event types: {num_event_types}")
    
    # Build chronological event trajectories
    # Sort by date, then group into sequences of consecutive events
    sorted_records = sorted(train_records, key=lambda r: r.get("event_date", ""))
    
    # Create sequences of length context+forecast
    context_len = config.max_context_length
    forecast_len = config.max_forecast_length
    total_len = context_len + forecast_len
    
    sequences = []
    for i in range(0, len(sorted_records) - total_len, forecast_len):
        seq = sorted_records[i:i+total_len]
        # Verify temporal ordering
        dates = [r.get("event_date", "") for r in seq]
        if dates == sorted(dates):  # Strictly ordered
            context = seq[:context_len]
            target = seq[context_len:]
            
            # Verify temporal split: target must be after context
            ctx_max_date = max(r.get("event_date", "") for r in context)
            tgt_min_date = min(r.get("event_date", "") for r in target)
            if ctx_max_date <= tgt_min_date or ctx_max_date == tgt_min_date:
                sequences.append((context, target))
    
    print(f"  Trajectories: {len(sequences)}")
    
    if not sequences:
        print("  WARNING: No valid trajectories found. Skipping CausalSeq training.")
        return None, {}
    
    # Prepare batches
    def encode_trajectory_batch(seqs, batch_size=32):
        """Encode a batch of (context, target) trajectory pairs."""
        batches = []
        for bi in range(0, len(seqs), batch_size):
            batch_seqs = seqs[bi:bi+batch_size]
            B = len(batch_seqs)
            
            # Encode context with EventEmbed
            ctx_embeddings = []
            ctx_masks = []
            tgt_event_types = []
            tgt_time_bins = []
            tgt_actors = []
            tgt_targets = []
            tgt_domains = []
            
            for context, target in batch_seqs:
                # Encode context events
                ctx_emb = []
                for r in context:
                    text = build_text_from_record(r)
                    tokens = vocab.encode(normalize(text, {}).split())
                    if not tokens:
                        tokens = [1]
                    t_ids = torch.tensor([tokens], dtype=torch.long, device=DEVICE)
                    c_ids = torch.zeros(1, len(tokens), 5, dtype=torch.long, device=DEVICE)
                    m = torch.ones(1, len(tokens), dtype=torch.long, device=DEVICE)
                    with torch.no_grad():
                        emb = eventembed_model(t_ids, c_ids, m)
                        ctx_emb.append(emb["sequence_embedding"].squeeze(0))
                
                ctx_emb_tensor = torch.stack(ctx_emb)  # [context_len, 256]
                ctx_embeddings.append(ctx_emb_tensor)
                ctx_masks.append(torch.ones(context_len, dtype=torch.bool, device=DEVICE))
                
                # Encode target sequence
                evt_types = [config.num_event_types + 1]  # BOS
                time_bins = [config.num_time_bins + 1]  # BOS
                actors_seq = [0]  # BOS placeholder
                targets_seq = [0]  # BOS placeholder
                domains_seq = [0]  # BOS placeholder
                
                for r in target:
                    et = event_type_to_id.get(r.get("event_root_code", ""), 0)
                    evt_types.append(et)
                    time_bins.append(0)  # Simplified: all events in bin 0
                    actors_seq.append(actor_to_id.get(r.get("actor1_code", ""), 0))
                    targets_seq.append(target_to_id.get(r.get("actor2_code", ""), 0))
                    domains_seq.append(domain_to_id.get(r.get("source_domain", ""), 0))
                
                tgt_event_types.append(evt_types)
                tgt_time_bins.append(time_bins)
                tgt_actors.append(actors_seq)
                tgt_targets.append(targets_seq)
                tgt_domains.append(domains_seq)
            
            # Pad all target sequences to same max length
            max_tgt = max(len(t) for t in tgt_event_types)
            for j in range(B):
                pad_len = max_tgt - len(tgt_event_types[j])
                tgt_event_types[j].extend([config.num_event_types] * pad_len)
                tgt_time_bins[j].extend([config.num_time_bins] * pad_len)
                tgt_actors[j].extend([0] * pad_len)
                tgt_targets[j].extend([0] * pad_len)
                tgt_domains[j].extend([0] * pad_len)
            
            batches.append({
                "src": torch.stack(ctx_embeddings),
                "src_mask": torch.stack(ctx_masks),
                "tgt_event_type": torch.tensor(tgt_event_types, dtype=torch.long, device=DEVICE),
                "tgt_time_bin": torch.tensor(tgt_time_bins, dtype=torch.long, device=DEVICE),
                "tgt_actor": torch.tensor(tgt_actors, dtype=torch.long, device=DEVICE),
                "tgt_target": torch.tensor(tgt_targets, dtype=torch.long, device=DEVICE),
                "tgt_domain": torch.tensor(tgt_domains, dtype=torch.long, device=DEVICE),
            })
        return batches
    
    # Use subset for efficiency
    train_seqs = sequences[:2000] if len(sequences) > 2000 else sequences
    
    print(f"  Training on {len(train_seqs)} trajectories")
    train_batches = encode_trajectory_batch(train_seqs, batch_size=32)
    
    # Training loop
    epochs = 10
    history = {"train_loss": []}
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        
        for batch in train_batches:
            optimizer.zero_grad()
            outputs = model(
                batch["src"], batch["src_mask"],
                batch["tgt_event_type"], batch["tgt_time_bin"],
                teacher_forcing_ratio=max(0.5 - epoch * 0.05, 0.1)
            )
            
            # CausalSeqLoss expects (preds_dict, targets_dict, mask)
            targets_dict = {
                "event_type": batch["tgt_event_type"],
                "time_bin": batch["tgt_time_bin"],
                "actor": batch["tgt_actor"],
                "target": batch["tgt_target"],
                "domain": batch["tgt_domain"],
            }
            loss, _ = loss_fn(outputs, targets_dict, batch["src_mask"])
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.gradient_clipping)
            optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / max(len(train_batches), 1)
        history["train_loss"].append(avg_loss)
        
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
    
    # Simple evaluation: check event type prediction accuracy
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in train_batches[:5]:
            outputs = model(
                batch["src"], batch["src_mask"],
                batch["tgt_event_type"], batch["tgt_time_bin"],
                teacher_forcing_ratio=0.0
            )
            preds = outputs["event_type"].argmax(dim=-1)
            targets = batch["tgt_event_type"][:, 1:]  # Skip BOS
            preds = preds[:, 1:]  # Skip BOS position
            
            min_len = min(preds.size(1), targets.size(1))
            correct += (preds[:, :min_len] == targets[:, :min_len]).sum().item()
            total += min_len * preds.size(0)
    
    recall_at_1 = correct / max(total, 1)
    
    metrics = {
        "event_recall_at_1": recall_at_1,
        "final_loss": history["train_loss"][-1],
    }
    
    print(f"  Event Recall@1: {recall_at_1:.4f}")
    
    # Save checkpoint
    checkpoint_dir = MODELS_DIR / "causalseq"
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    checkpoint_path = checkpoint_dir / "model.pt"
    torch.save({
        "model_state_dict": model.state_dict(),
        "config": config.to_dict(),
        "actor_to_id": actor_to_id,
        "target_to_id": target_to_id,
        "domain_to_id": domain_to_id,
        "event_type_to_id": event_type_to_id,
        "training_history": history,
        "metrics": metrics,
        "seed": SEED,
    }, str(checkpoint_path))
    
    metadata = {
        "model_version": "v2.0",
        "architecture": "EncoderDecoder-LSTM-BahdanauAttention",
        "training_epochs": epochs,
        "final_loss": history["train_loss"][-1],
        "training_information_end_time": TRAIN_CUTOFF,
        "dataset_version": "v2.0",
        "metrics": metrics,
    }
    
    with open(checkpoint_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    if mlflow_instance:
        with mlflow_instance.start_run(run_name="causalseq_training", nested=True):
            mlflow_instance.log_param("epochs", epochs)
            mlflow_instance.log_param("training_cutoff", TRAIN_CUTOFF)
            for k, v in metrics.items():
                mlflow_instance.log_metric(k, v)
    
    print(f"  CausalSeq checkpoint saved: {checkpoint_path}")
    return model, config, metrics


# ============================================================================
# Main Pipeline
# ============================================================================
def main():
    set_seed(SEED)
    
    print("=" * 70)
    print("  DELPHI Phase 13 — Real Model Training Pipeline")
    print("=" * 70)
    print(f"  Device: {DEVICE}")
    print(f"  Seed: {SEED}")
    print(f"  Train cutoff: {TRAIN_CUTOFF}")
    print(f"  Val cutoff: {VAL_CUTOFF}")
    
    mlflow = setup_mlflow()
    
    # Step 1: Load data
    print("\n" + "=" * 60)
    print("Step 1: Loading Real Data Corpus")
    print("=" * 60)
    records = load_gdelt_corpus()
    train_records, val_records, test_records = temporal_split(records, TRAIN_CUTOFF, VAL_CUTOFF)
    
    if mlflow:
        parent_run = mlflow.start_run(run_name="Phase13_FullPipeline")
    
    try:
        # Step 2: Tokenizer
        tokenizer, vocab, tokenized_corpus, tok_stats = train_tokenizer(train_records, mlflow)
        
        # Step 3: EventEmbed
        eventembed_model, ee_metadata = train_eventembed(tokenizer, vocab, tokenized_corpus, train_records, val_records, mlflow)
        
        if eventembed_model is None:
            print("FATAL: EventEmbed training failed. Aborting pipeline.")
            return
        
        # Step 4: EventNet
        eventnet_model, event_type_to_id, en_metrics = train_eventnet(
            eventembed_model, vocab, train_records, val_records, mlflow
        )
        
        # Step 5: CredNet
        crednet_model, cn_metrics = train_crednet(train_records, val_records, mlflow)
        
        # Step 6: FAISS Index
        index_manifest = build_faiss_index(eventembed_model, vocab, train_records, mlflow)
        
        # Step 7: CausalSeq
        causalseq_model, cs_config, cs_metrics = train_causalseq(
            eventembed_model, vocab, train_records, val_records, event_type_to_id, mlflow
        )
        
        # Save calibration artifact (UNCALIBRATED - temperature 1.0)
        cal_dir = MODELS_DIR / "calibration"
        os.makedirs(cal_dir, exist_ok=True)
        cal_artifact = {
            "state": "UNCALIBRATED",
            "temperature": 1.0,
            "method": "temperature_scaling",
            "fitted": False,
            "reason": "Insufficient independent validation data for calibration fitting",
            "dataset_version": "v2.0",
        }
        with open(cal_dir / "scenario_temperature.json", "w") as f:
            json.dump(cal_artifact, f, indent=2)
        
        # Summary
        print("\n" + "=" * 70)
        print("  TRAINING PIPELINE COMPLETE")
        print("=" * 70)
        print(f"  Tokenizer: vocab_size={vocab.size()}")
        print(f"  EventEmbed: loss={ee_metadata.get('final_loss', 'N/A'):.4f}")
        print(f"  EventNet: Macro-F1={en_metrics.get('event_type_macro_f1', 'N/A'):.4f}")
        print(f"  CredNet: Macro-F1={cn_metrics.get('macro_f1', 'N/A')}")
        print(f"  FAISS: {index_manifest.get('record_count', 0)} vectors")
        print(f"  CausalSeq: Recall@1={cs_metrics.get('event_recall_at_1', 'N/A')}")
        print(f"  Calibration: UNCALIBRATED")
        print(f"\n  All artifacts saved to: {MODELS_DIR}")
        print(f"  FAISS index saved to: {INDEXES_DIR}")
        
    finally:
        if mlflow:
            mlflow.end_run()
    
    print("\nDone.")


if __name__ == "__main__":
    main()
