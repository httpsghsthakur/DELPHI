# DELPHI CAUSALSEQ (Layer 7)

## Architecture Overview
CausalSeq is DELPHI's structured temporal event-sequence generation model. 
It takes an embedded context sequence (via EventEmbed) and autoregressively generates a structured future event sequence.

### Encoder
- **Type**: Bidirectional LSTM
- **Input**: 256-dim EventEmbed vectors
- **Hidden**: Configurable (default 256)

### Attention
- **Type**: Bahdanau Additive Attention
- Uses the decoder's top-layer hidden state to attend over the bidirectional encoder outputs.
- Fully masked to ignore padding.

### Decoder & Conditioning
- **Type**: Autoregressive LSTM
- **Input per step**: Embedded previous `event_type` + embedded previous `time_bin` + Context Vector.
- **Conditioning Semantics**: The autoregressive input is intentionally restricted to only the primary dimensions (`event_type` and `time_bin`). `actor`, `target`, and `domain` predictions are NOT fed back as autoregressive inputs. This choice is made to limit error compounding from sparser structured fields while maintaining a simpler architecture.
- Multi-head outputs for structured prediction:
  - `event_type`
  - `time_bin`
  - `actor`
  - `target`
  - `domain`

## Sequence Semantics & Ordering
- **Decoder Step Meaning**: Each decoder step represents exactly the **next chronological future event**. 
- **Timestamp Ordering**: Events are ordered primarily by `timestamp`. In the case of identical timestamps, a deterministic stable tie-breaker (`event_id`) is used.
- **Target Semantics**: For a context sequence `E1 → E2 → E3 → E4` with cutoff `T0 = time(E4)`, the target sequence is `E5 → E6 → E7`. The model strictly enforces that `time(E5) > T0` and `time(E5) <= time(E6) <= time(E7)`, subject to deterministic same-timestamp tie-breaking. Events with identical timestamps to `T0` are never targets.

## Temporal Leakage Protections & Checkpoint Provenance
- `construct_sequences_with_temporal_guard` guarantees no future information enters the encoder.
- **Checkpoint Provenance**: The configuration exposes `checkpoint_training_end_time`. Models trained must log this provenance boundary.

Two evaluation modes exist:
1. **Architecture Evaluation**: Used during synthetic tests or pure code validation (provenance unverified).
2. **Strict Historical Backtest**: Enforces `checkpoint_training_end_time <= prediction_cutoff`. If provenance is violated or missing, the backtester marks the status as `STRICT_TEMPORAL_BACKTEST_UNVERIFIED`.

## Generation & Decoding
The model supports:
- **Greedy Decoding**: Deterministic top-1 generation.
- **Beam Search**: Deterministic beam search with length-normalized `sequence_score` tracking. Rejects invalid ties deterministically.

## Training & Loss
- Uses Teacher Forcing (configurable ratio).
- Loss is a weighted sum of CrossEntropy across all output heads (`lambda_event_type`, `lambda_time`, etc.).
- **Missing Labels**: Missing labels (e.g., absent `actor`) are masked out using `ignore_index=-1`. They do not become false class labels, do not contribute invalid gradients, and do not distort evaluation metrics.

## Time-Bin Definitions
The exact mapping used during tokenization, encoding, and metrics generation is:
- 0: hours
- 1: 1 day
- 2: 3 days
- 3: 7 days
- 4: 14 days
- 5: 30 days
- 6: 90 days
- 7: 180 days
- 8: 365+ days
- 9: TIME_PAD_IDX

## Evaluation Metrics
- **Event Type**:
  - Top-1 accuracy (`event_acc_top1`)
  - Macro-F1 (`event_macro_f1`)
  - Recall@3 (`event_recall_at_3`)
- **Temporal**:
  - Time-bin Top-1 accuracy (`time_acc_top1`)
- **Probabilistic Safety**:
  - Negative Log-Likelihood (`event_nll`). Safe against NaN, outputs "undefined" on empty targets.
  - Brier Score multiclass equivalent (`event_brier`). Outputs "undefined" on empty targets.
- **Multiple Valid Future Events**: To handle cases where multiple historical events validly follow the context, structural match evaluations like Recall@3 are implemented using deterministic structured criteria (e.g., predicting an event type that matches any of the next valid target events), not natural language semantic similarity.

## Real Data Status
**CAUSALSEQ ARCHITECTURE VALIDATED — REAL HISTORICAL TRAINING/BACKTESTING PENDING**
(The current state implements the full architectural contract but weights are randomly initialized. No pretrained weights have been injected.)
