# EVENTEMBED

## Purpose
EventEmbed is the first trainable neural component in DELPHI. It learns domain-specific numerical representations of text, focusing on geopolitical terminology, economics, trade, and actors.

## Architecture
EventEmbed implements a dual-branch architecture:
- **Word Branch**: A standard Word2Vec-style embedding lookup table (`vocab_size` × `word_embedding_dim`).
- **Character Branch**: A Character-level Convolutional Neural Network (CNN) that extracts morphological features from individual tokens, providing robustness for rare or out-of-vocabulary (OOV / `<UNK>`) words.
- **Fusion Layer**: The word and character representations are concatenated and projected through a Linear + GELU + LayerNorm block to produce a fixed 256-dimensional output.

### Skip-Gram with Negative Sampling
The model is trained using a standard Skip-Gram objective. For a given target token, it predicts the surrounding context window. Negative samples are drawn from the smoothed token frequency distribution.

### OOV Handling
By incorporating the Character CNN, EventEmbed ensures that any token mapped to `<UNK>` still receives a unique, contextually and morphologically meaningful representation based on its character sequence.

## Configuration
Example parameters:
- `word_embedding_dim`: 192
- `character.output_dim`: 64
- `output_dim`: 256
- `context_window`: 5
- `negative_samples`: 5

## Training Procedure
The model is trained directly from the parsed DELPHI corpus, without ANY pre-trained weights.
Use `python -m delphi.models.eventembed.smoke_test` to verify pipeline integrity using a tiny deterministic fixture.

## Future Integration
The outputs (`[B, T, 256]`) will be consumed by EventNet for sequence modeling and classification, and aggregated sequence representations (`[B, 256]`) will be indexed using FAISS for historical event retrieval.
