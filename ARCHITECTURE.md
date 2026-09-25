# DELPHI Architecture

DELPHI is a research-grade system designed to extract structured events, model their causal relationships, and forecast probability-weighted scenarios without relying on external LLM APIs.

## System Architecture

DELPHI follows a layered pipeline approach:
1.  **Ingestion & Tokenization**: Raw data from various sources (news, ICEWS, GDELT) is ingested and tokenized using a custom-built tokenizer.
2.  **Event Embeddings (EventEmbed)**: Tokens are processed into dense representations using a custom Word2Vec-style embedding system combined with character-level CNNs.
3.  **Event Extraction (EventNet)**: A BiLSTM and Self-Attention model processes token embeddings to extract structured events.
4.  **Historical Matching**: FAISS index stores historical event embeddings to match current events with historical analogues.
5.  **Source Credibility (CredNet)**: An MLP evaluates source credibility based on specific features.
6.  **Causal Reasoning (CausalSeq)**: An Encoder-Decoder LSTM generates future scenarios by modeling event chains and causal relationships.
7.  **Forecasting & API**: The output of models is synthesized into structured forecasts exposed via FastAPI to a React frontend.

## Module Boundaries
-   `src/delphi/ingestion`: Handles loading raw data from various sources.
-   `src/delphi/tokenizer`: Houses custom tokenization logic.
-   `src/delphi/datasets`: Provides standardized datasets for the models.
-   `src/delphi/models`: Contains the definition of each custom PyTorch model (EventEmbed, EventNet, CausalSeq, CredNet).
-   `src/delphi/retrieval`: Handles interaction with FAISS for historical matching.
-   `src/delphi/api`: The FastAPI layer serving inferences.

## Model Boundaries
Models are decoupled and communicate via defined contracts (e.g., EventNet outputs structured extractions that CausalSeq expects). Models NEVER use external API calls.

## Dependencies
- PyTorch (Core ML framework)
- FastAPI (Backend API)
- DuckDB / Polars (Data processing)
- FAISS (Similarity search)
- NetworkX (Causal graph structures)
