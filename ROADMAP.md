# DELPHI Roadmap

## Layer 0 — Foundation (Current)
Deliver:
- project structure
- config
- interfaces
- schemas
- documentation
- testing structure
- environment setup

## Layer 1 — Data Foundation (Completed)
Built:
- data ingestion adapters
- canonical schemas (News, Events, Trade, etc)
- dataset versioning and manifest generation
- temporal splitting and leakage guard
- text normalization and deduplication

## Layer 2 — Custom Tokenizer (Completed)
Built:
- vocabulary generation and token IDs
- deterministic normalization and pre-tokenization
- special tokens (events, entities, padding, etc)
- encode/decode, serialization, and deterministic tests
- PyTorch dataset/collator interfaces

## Layer 3 — EventEmbed (Completed)
Built and trained: Custom Word2Vec + Character CNN.
Input: token IDs & character IDs
Output: 256-dimensional representation.

## Layer 4 — EventNet (Completed)
Built and trained: BiLSTM + Self-Attention context encoder.
Input: EventEmbed vectors `[B,T,256]`
Outputs: Token-level BIO extraction, Sequence-level Event Type classification.

## Layer 5 — Historical Intelligence (Completed)
Built: EventEmbed -> FAISS -> Historical Event Matcher.
Includes: Temporal filtration, Deterministic metadata reranking, L2 Normalization.
Evaluate: Recall@K, Precision@K, similarity quality, temporal consistency

## Layer 6 — CredNet (Completed)
Build: 12 features -> 32 -> 16 -> 1.
Use source-level credibility data.
Evaluate: macro F1, ROC-AUC, calibration, Brier score

## Layer 7 — CausalSeq (Completed)
Build: Encoder -> Bahdanau Attention -> Decoder.
Train on structured event trajectories.

## Layer 8 — Forecast Orchestration & Scenario Intelligence (Completed)
Combine: EventNet + EventEmbed + Historical Matcher + CredNet + CausalSeq.
Output: deterministic scenarios, calibrated probabilities, evidence aggregation, indicators.

## Layer 9 — Final Backtesting & Calibration
Build a strict temporal evaluation framework (no future leakage).

## Layer 11 — Backend
Build FastAPI endpoints.

## Layer 12 — Frontend
Build React + D3 interface.

## Layer 13 — Deployment
Dockerize the complete system.
