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

### Decoder
- **Type**: Autoregressive LSTM
- **Input per step**: Embedded previous `event_type` + embedded previous `time_bin` + Context Vector.
- Multi-head outputs for structured prediction:
  - `event_type`
  - `time_bin` (0=hours, 1=1d, 2=3d, 3=7d, 4=14d, 5=30d, 6=90d, 7=180d, 8=365+d)
  - `actor`
  - `target`
  - `domain`

## Temporal Leakage Protections
- `construct_sequences_with_temporal_guard` guarantees no future information enters the encoder.
- A strict cutoff timestamp $T_0$ is enforced. Any target event must have timestamp $> T_0$. Any context event must have timestamp $\leq T_0$.
- `create_causal_temporal_split` sequentially sorts cutoffs before splitting into Train/Val/Test.

## Generation & Decoding
The model supports:
- **Greedy Decoding**: Deterministic top-1 generation.
- **Beam Search**: Deterministic beam search with length-normalized `sequence_score` tracking.

## Training & Loss
- Uses Teacher Forcing (configurable ratio).
- Loss is a weighted sum of CrossEntropy across all output heads (`lambda_event_type`, `lambda_time`, etc.).
- Missing labels (e.g. absent `actor`) are masked out (`ignore_index=-1`) and do not penalize the model or create false negatives.

## Backtesting
The `CausalSeqBacktester` provides a chronological sweeping evaluation where the model context is frozen at specific historical cutoffs and predictions are evaluated against actual future trajectories.

## Real Data Status
**CAUSALSEQ ARCHITECTURE VALIDATED — REAL HISTORICAL TRAINING/BACKTESTING PENDING**
(The current state implements the full architectural contract but weights are randomly initialized. No pretrained weights have been injected.)
