# DELPHI Dataset Documentation

## Layer 1 Implementation
We have established the DELPHI Data Foundation, which consists of:
- **Canonical Schemas**: Standardized Pydantic models for News, Events, EventRelations, Sources, Economics, and Trade.
- **Ingestion Adapters**: Interfaces and stubs for ingesting GDELT, ICEWS, MAVEN, NELA-GT, Comtrade, World Bank, and IMF datasets.
- **Data Preprocessing**: Modules for exact deduplication (`Deduplicator`), text and URL normalization.
- **Temporal Splitting**: Strong temporal leakage guards and deterministic train/validation/test split logic.
- **Manifest Generation**: Automatic dataset metadata and checksum generation.
- **CLI**: A command-line interface for data operations (`python -m delphi.datasets`).

### Next Steps (Layer 2)
Layer 2 will implement the Custom Tokenizer which processes the text fields defined in these schemas into integer arrays.
