# HISTORICAL INTELLIGENCE

## Purpose
Layer 5 of DELPHI provides historical intelligence by retrieving structurally and contextually similar historical events. It is designed to answer: *“What historical events are analogous to the current event, and what happened afterward?”*

## Architecture
- **Input**: A `query_event` containing an EventEmbed vector (`[256]`) and structured metadata (from EventNet).
- **Index**: A `FAISS IndexFlatIP` engine optimized for Inner Product search (which mathematically equates to Cosine Similarity because all embeddings are strictly L2 normalized prior to index insertion).
- **Metadata**: FAISS indices map to a highly structured `metadata.parquet` storing canonical data (actors, domain, event_type, date).
- **Filtering**:
  - *Strict Temporal Leakage Guard*: Completely drops any candidate occurring after the prediction boundary.
  - *Self-Match Prevention*: Ensures an event cannot retrieve itself.
- **Reranker**: A deterministic, configurable reranker that weights semantic FAISS similarity against exact matches on `event_type`, `domain`, and Jaccard-overlap of `actors` and `targets`.
- **Output**: Returns `HistoricalAnalogue` schemas containing the historical event, overlap metrics, specific computed similarities/differences, and temporal outcome horizons.

## Important Distinctions
- **Not a Probability**: A high cosine similarity in retrieval does *not* equate to a high probability of a future event occurring. Probability generation is the exclusive domain of the downstream Forecast Engine.
- **Not a LLM Reasoner**: Similarities and differences are determined via deterministic subset logic, not through prone-to-hallucinate LLM inference.
- **Not a Causal Engine**: This layer purely *retrieves* historical outcomes. It does not infer causation for the *current* event.

## Usage
Indices must be rebuilt entirely if the upstream `EventEmbed` neural parameters change. 
Version constraints are strictly enforced via `manifest.json`.

```bash
python -m delphi.retrieval.smoke_test
```
