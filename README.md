# DELPHI — Deterministic Predictive Intelligence & Deep Research System

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C.svg)](https://pytorch.org)
[![Neural Parameters](https://img.shields.io/badge/Parameters-3.935M-success.svg)](#neural-parameters-breakdown-3935725-total)
[![External LLMs](https://img.shields.io/badge/External%20LLMs-0%25-brightgreen.svg)](#core-architectural-philosophy)
[![Pretrained Weights](https://img.shields.io/badge/Pretrained%20Weights-0%25-brightgreen.svg)](#core-architectural-philosophy)
[![Test Suite](https://img.shields.io/badge/Tests-73%20Passed-brightgreen.svg)](#running-automated-tests)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**DELPHI** is a custom-engineered, end-to-end predictive intelligence research platform designed to extract structured events from raw text, retrieve historically analogous crises, project causal future trajectories, evaluate source credibility, and synthesize probability-weighted scenario forecasts with zero reliance on commercial LLM APIs or pretrained transformer checkpoints.

---

## Table of Contents
- [Executive Summary](#executive-summary)
- [Core Architectural Philosophy](#core-architectural-philosophy)
- [System Architecture & Dataflow](#system-architecture--dataflow)
- [Neural Parameters Breakdown (3,935,725 Total)](#neural-parameters-breakdown-3935725-total)
- [Layer-by-Layer Technical Specification (Layers 0 to 13)](#layer-by-layer-technical-specification)
  - [Layer 0: Contracts, Schemas & Configuration](#layer-0-contracts-schemas--configuration)
  - [Layer 1: Data Ingestion & Temporal Splitting](#layer-1-data-ingestion--temporal-splitting)
  - [Layer 2: Deterministic Custom Tokenizer](#layer-2-deterministic-custom-tokenizer)
  - [Layer 3: EventEmbed (Word2Vec + Char-CNN)](#layer-3-eventembed-word2vec--char-cnn)
  - [Layer 4: EventNet (BiLSTM + Self-Attention Extractor)](#layer-4-eventnet-bilstm--self-attention-extractor)
  - [Layer 5: Historical Intelligence & FAISS Vector Matching](#layer-5-historical-intelligence--faiss-vector-matching)
  - [Layer 6: CredNet (Source Credibility Scorer)](#layer-6-crednet-source-credibility-scorer)
  - [Layer 7: CausalSeq (Seq2Seq Trajectory Engine)](#layer-7-causalseq-seq2seq-trajectory-engine)
  - [Layer 8: Forecast Orchestration & Scenario Synthesis](#layer-8-forecast-orchestration--scenario-synthesis)
  - [Layer 9: Strict Temporal Leakage Guard & Calibration](#layer-9-strict-temporal-leakage-guard--calibration)
  - [Layer 10: High-Performance FastAPI Backend](#layer-10-high-performance-fastapi-backend)
  - [Layer 11: React 18 & D3.js Visualization Frontend](#layer-11-react-18--d3js-visualization-frontend)
  - [Layer 12: Automated Walk-Forward Backtesting](#layer-12-automated-walk-forward-backtesting)
  - [Layer 13: Grounded Live Research Engine](#layer-13-grounded-live-research-engine)
- [Current Subsystem Status & Operational Matrix](#current-subsystem-status--operational-matrix)
- [Repository File & Directory Structure](#repository-file--directory-structure)
- [Quick Start & Local Execution](#quick-start--local-execution)
- [REST API Reference & Example Payloads](#rest-api-reference--example-payloads)
- [Containerization & Cloud Deployment (Docker / Render)](#containerization--cloud-deployment)
- [Associated Project Documentation](#associated-project-documentation)

---

## Executive Summary

Contemporary predictive analytics often rely on black-box Large Language Models (LLMs) that hallucinate facts, violate temporal boundaries by leaking future information, and cannot be systematically audited or backtested. 

**DELPHI takes the opposite approach**:
- **Fully Custom Neural Network Suite**: Built with 4 domain-specific neural architectures (`CausalSeq`, `EventNet`, `EventEmbed`, `CredNet`) totaling **3,935,725 parameters**.
- **100% Local Inference**: Runs deterministically in milliseconds on standard CPU hardware or consumer GPUs without network dependencies or third-party cloud credits.
- **Strict Information Cutoffs ($T_{cutoff}$)**: Enforces temporal isolation. A prediction for March 2023 cannot access news, vector embeddings, or weights from April 2023.
- **Explainable Probabilistic Forecasts**: Calibrated scenarios, tripwire indicator checklists, and provenance ledgers accompanying every generated output.

---

## Core Architectural Philosophy

Governed strictly by [`AGENTS.md`](AGENTS.md):

1. **0% External LLM APIs**: No OpenAI, Anthropic, Gemini, or Claude API calls anywhere in the inference path.
2. **0% Pretrained Weights**: No BERT, RoBERTa, GPT-2, Llama, or Mistral foundation models. All neural representations are trained from scratch.
3. **Strict Temporal Integrity**: Built-in cryptographic and metadata temporal guards prevent future data leakage during inference and backtesting.
4. **Deterministic Foundations**: Tokenization, candidate reranking, query planning, and evidence deduplication use deterministic mathematical logic.
5. **Calibrated Confidence**: Raw neural logits are scaled via empirical temperature calibration to minimize Expected Calibration Error (ECE).

---

## System Architecture & Dataflow

```mermaid
flowchart TD
    subgraph Data & Tokenization [Phase 1: Ingestion & Normalization]
        Raw[Raw Global News / GDELT / Live Feeds] --> L1[Layer 1: Ingestion & Deduplication]
        L1 --> L2[Layer 2: Deterministic Custom Tokenizer]
    end

    subgraph Neural Representation [Phase 2: Custom Models]
        L2 -->|Token IDs & Char Tensors| L3[Layer 3: EventEmbed<br/>Word2Vec + Char-CNN (281k params)]
        L3 -->|256d Embeddings| L4[Layer 4: EventNet<br/>BiLSTM + Multi-Head Attention (725k params)]
    end

    subgraph Memory & Verification [Phase 3: Precedents & Trust]
        L3 -->|256d Vectors| L5[Layer 5: Historical Intelligence<br/>FAISS Search + Parquet Filter]
        Raw -->|12 Metadata Features| L6[Layer 6: CredNet<br/>Source Credibility MLP (961 params)]
    end

    subgraph Causal Reasoning [Phase 4: Trajectory Projection]
        L4 & L5 -->|Structured Event Chains| L7[Layer 7: CausalSeq<br/>Seq2Seq LSTM + Bahdanau Attention (2.93M params)]
    end

    subgraph Synthesis & Safety [Phase 5: Orchestration & Calibration]
        L4 & L5 & L6 & L7 --> L8[Layer 8: Forecast Orchestrator<br/>Scenario Clustering & Synthesis]
        L8 --> L9{Layer 9: Strict Temporal<br/>Leakage Guard & Calibration}
    end

    subgraph User Delivery [Phase 6: Full Stack Interfaces]
        L9 -->|Verified & Calibrated Payload| L10[Layer 10: FastAPI Backend Engine]
        L10 --> L11[Layer 11: React 18 + D3.js Visualization UI]
        L10 --> L12[Layer 12: Walk-Forward Backtester]
        L10 --> L13[Layer 13: Live Research Dossier Engine]
    end
```

---

## Neural Parameters Breakdown (3,935,725 Total)

DELPHI's intelligence is distributed across 4 lightweight, specialized neural networks:

| Model Component | Architecture / Purpose | Location | Exact Parameters | Share % |
| :--- | :--- | :--- | :--- | :--- |
| **CausalSeq** | Seq2Seq BiLSTM + Bahdanau Attention + Multi-Head Forecast Projections | [`models/causalseq/model.pt`](models/causalseq/model.pt) | **2,928,649** | **74.4%** |
| **EventNet** | BiLSTM Context Encoder + Multi-Head Self-Attention + Multi-Task Heads | [`models/eventnet/model.pt`](models/eventnet/model.pt) | **724,995** | **18.4%** |
| **EventEmbed** | Custom Vocab Table + Multi-Filter Char-CNN + Fusion Projection MLP | [`models/eventembed/model.pt`](models/eventembed/model.pt) | **281,120** | **7.1%** |
| **CredNet** | 3-Layer Deep Multi-Layer Perceptron Source Credibility Scorer | [`models/crednet/model.pt`](models/crednet/model.pt) | **961** | **<0.1%** |
| **TOTAL** | **Full DELPHI Neural Pipeline** | — | **3,935,725 (~3.935M)** | **100.0%** |

### Internal Weight Distribution

```
1. CausalSeq (2,928,649 params)
   ├── BiLSTM Encoder (Input: 256, Hidden: 256 bidirectional) -> 1,052,672 params
   ├── Hidden & Cell State Projection Mappings                 ->   262,656 params
   ├── Bahdanau Additive Attention Engine (Wa, Ua, Va)        ->   197,377 params
   ├── Autoregressive Decoder LSTM (Input: 768, Hidden: 256)   -> 1,050,624 params
   └── Prediction Heads (Event, Time, Actor, Target, Domain)   ->   365,320 params

2. EventNet (724,995 params)
   ├── BiLSTM Sequence Backbone (Input: 256, Hidden: 128 x 2) ->   395,264 params
   ├── Multi-Head Self-Attention (4 Heads, Query/Key/Val/Out)  ->   263,168 params
   ├── Token-Level IOB Entity Head                             ->     2,313 params
   └── Sequence-Level CAMEO Event Head (250 classes)           ->    64,250 params

3. EventEmbed (281,120 params)
   ├── Word Embedding Table (1,000 vocab x 192 dim)            ->   192,000 params
   ├── Character Embedding Table (128 ASCII x 32 dim)          ->     4,096 params
   ├── Character Conv1D Filter Banks (Kernels: 3, 4, 5)        ->    12,288 params
   ├── Character Subword Projection MLP (96 -> 64 dim)         ->     6,272 params
   └── Dimension Fusion MLP (Concatenated 256 -> 256 dim)      ->    66,464 params

4. CredNet (961 params)
   ├── Input Layer: Linear(12 -> 32) + BatchNorm + ReLU        ->       416 params
   ├── Hidden Layer: Linear(32 -> 16) + ReLU                   ->       528 params
   └── Output Layer: Linear(16 -> 1) + Sigmoid                 ->        17 params
```

---

## Layer-by-Layer Technical Specification

### Layer 0: Contracts, Schemas & Configuration
- **Purpose**: Defines immutable Pydantic V2 schemas, base interfaces, and YAML configurations.
- **Key Modules**: [`src/delphi/datasets/schemas.py`](src/delphi/datasets/schemas.py), [`config/config.yaml`](config/config.yaml), [`config/model_config.yaml`](config/model_config.yaml).
- **Core Entities**: `NewsArticle`, `StructuredEvent`, `ScenarioRecord`, `ActorRecord`, `Indicator`.

### Layer 1: Data Ingestion & Temporal Splitting
- **Purpose**: Ingests multi-source geopolitical data (GDELT V2, ICEWS, UN Comtrade) and enforces chronological boundary splits.
- **Key Modules**: [`src/delphi/ingestion/`](src/delphi/ingestion/), [`src/delphi/preprocessing/temporal.py`](src/delphi/preprocessing/temporal.py), [`src/delphi/preprocessing/deduplication.py`](src/delphi/preprocessing/deduplication.py).
- **Leakage Prevention**: Guaranteed chronological ordering ($T_{train} < T_{val} < T_{test}$). MinHash deduplication eliminates syndicated wire duplicates.

### Layer 2: Deterministic Custom Tokenizer
- **Purpose**: Splits natural language into token and character tensors without external tokenizer dependencies.
- **Key Modules**: [`src/delphi/tokenizer/tokenizer.py`](src/delphi/tokenizer/tokenizer.py), [`src/delphi/tokenizer/vocabulary.py`](src/delphi/tokenizer/vocabulary.py), [`models/vocab/vocabulary.json`](models/vocab/vocabulary.json).
- **Mechanics**: Unicode NFKC normalization, geopolitical acronym preservation ("NATO", "UN"), frequency thresholding, and deterministic special tokens (`<PAD>=0`, `<UNK>=1`, `<BOS>=2`, `<EOS>=3`, `<EVENT>=4`, `<ACTOR>=5`).

### Layer 3: EventEmbed (Word2Vec + Char-CNN)
- **Purpose**: Maps token sequences and subword characters into a continuous 256-dimensional vector space.
- **Key Modules**: [`src/delphi/models/eventembed/model.py`](src/delphi/models/eventembed/model.py), [`src/delphi/models/eventembed/char_cnn.py`](src/delphi/models/eventembed/char_cnn.py).
- **Mechanics**: Ingests word IDs (192d) and character IDs passed through parallel Conv1D filters (kernels 3, 4, 5 with max-pooling, 64d) fused via MLP into a unified 256d vector. Resilient to misspellings, transliterations, and unseen names.

### Layer 4: EventNet (BiLSTM + Self-Attention Extractor)
- **Purpose**: Translates dense token sequences into structured event definitions (Who did What to Whom, Where, and When).
- **Key Modules**: [`src/delphi/models/eventnet/model.py`](src/delphi/models/eventnet/model.py), [`src/delphi/models/eventnet/attention.py`](src/delphi/models/eventnet/attention.py).
- **Mechanics**: BiLSTM contextual sequence encoder + 4-head self-attention. Outputs token-level entity spans (Actor, Target, Location) and sequence-level CAMEO event classes across 250 taxonomy codes.

### Layer 5: Historical Intelligence & FAISS Vector Matching
- **Purpose**: Ground forward-looking projections in verifiable historical precedents.
- **Key Modules**: [`src/delphi/retrieval/faiss_index.py`](src/delphi/retrieval/faiss_index.py), [`src/delphi/retrieval/historical_matcher.py`](src/delphi/retrieval/historical_matcher.py).
- **Mechanics**: 10,000+ historical crises (1990–2024) embedded into 256d L2-normalized vectors in [`indexes/historical/index.faiss`](indexes/historical/index.faiss). Filtered with microsecond latency using Parquet metadata to exclude any historical events occurring after $T_{cutoff}$.

### Layer 6: CredNet (Source Credibility Scorer)
- **Purpose**: Scores source trustworthiness to prevent disinformation from corrupting scenario weights.
- **Key Modules**: [`src/delphi/models/crednet/model.py`](src/delphi/models/crednet/model.py).
- **Mechanics**: 12 engineered features (domain age, author presence, citation density, sentiment skew, retraction rate) mapped through a 3-layer MLP to output a credibility score $C \in [0.0, 1.0]$.

### Layer 7: CausalSeq (Seq2Seq Trajectory Engine)
- **Purpose**: Projects causal event rollout trees across multiple future time horizons ($t+1, t+7, t+30$ days).
- **Key Modules**: [`src/delphi/models/causalseq/model.py`](src/delphi/models/causalseq/model.py), [`src/delphi/models/causalseq/attention.py`](src/delphi/models/causalseq/attention.py).
- **Mechanics**: BiLSTM trajectory encoder + Bahdanau additive attention + autoregressive LSTM decoder with multi-task projection heads predicting event codes, target actors, and temporal deltas.

### Layer 8: Forecast Orchestration & Scenario Synthesis
- **Purpose**: Synthesizes inputs from Layers 4, 5, 6, and 7 into structured, narrative forecast scenarios.
- **Key Modules**: [`src/delphi/forecast/orchestrator.py`](src/delphi/forecast/orchestrator.py), [`src/delphi/forecast/scenario_builder.py`](src/delphi/forecast/scenario_builder.py).
- **Mechanics**: Generates 50 stochastic CausalSeq rollout paths, clusters them via DBSCAN in trajectory embedding space into discrete scenarios (Base Case, Escalation, De-escalation), weights them by credibility and historical analogue density, and derives actionable tripwire watchlists.

### Layer 9: Strict Temporal Leakage Guard & Calibration
- **Purpose**: Prevents temporal contamination and ensures forecast probabilities match empirical reality.
- **Key Modules**: [`src/delphi/forecast/validation.py`](src/delphi/forecast/validation.py), [`src/delphi/forecast/calibration.py`](src/delphi/forecast/calibration.py), [`models/calibration/calibration.json`](models/calibration/calibration.json).
- **Mechanics**: Rejects any request if an input document, model checkpoint, or citation postdates $T_{cutoff}$. Applies temperature scaling ($T = 1.3612$) to raw softmax logits, reducing Expected Calibration Error (ECE) from 0.24 to 0.099.

### Layer 10: High-Performance FastAPI Backend
- **Purpose**: Exposes the entire pipeline via asynchronous, documented REST endpoints.
- **Key Modules**: [`src/delphi/api/app.py`](src/delphi/api/app.py), [`src/delphi/api/routes/`](src/delphi/api/routes/), [`src/delphi/api/registry/`](src/delphi/api/registry/).
- **Mechanics**: In-memory model caching, request tracing via UUIDs, async route execution, and dual persistence (SQLite `delphi.db` and PostgreSQL 15).

### Layer 11: React 18 & D3.js Visualization Frontend
- **Purpose**: Delivers an intelligence-grade, high-density analytical dashboard.
- **Key Modules**: [`frontend/src/App.tsx`](frontend/src/App.tsx), [`frontend/src/pages/`](frontend/src/pages/), [`frontend/src/components/charts/`](frontend/src/components/charts/).
- **Mechanics**: Interactive D3.js force-directed causal graphs, calibrated probability distribution bars, scenario preset launchers, and detailed provenance audit badges.

### Layer 12: Automated Walk-Forward Backtesting
- **Purpose**: Continuously validates forecasting accuracy using historical walk-forward stepping.
- **Key Modules**: [`scripts/temporal_backtest.py`](scripts/temporal_backtest.py), [`src/delphi/api/routes/backtests.py`](src/delphi/api/routes/backtests.py).
- **Mechanics**: Freezes knowledge at historical dates, forecasts outcomes, compares against reality, and computes Brier scores and Top-K accuracy.

### Layer 13: Grounded Live Research Engine
- **Purpose**: Dynamically searches the public web for real-time grounding evidence without commercial LLMs.
- **Key Modules**: [`src/delphi/research/engine.py`](src/delphi/research/engine.py), [`src/delphi/research/query_planner.py`](src/delphi/research/query_planner.py), [`src/delphi/research/composer.py`](src/delphi/research/composer.py).
- **Mechanics**: Deterministic query expansion across DuckDuckGo, Wikipedia, and GDELT; async HTML scraping; boilerpipe-style extraction; and citation compilation.

---

## Current Subsystem Status & Operational Matrix

| Subsystem / Layer | Operational Status | Reality & Architecture Verification |
| :--- | :--- | :--- |
| **Custom PyTorch Models** | **100% Operational** | Checkpoints (`EventNet`, `CredNet`, `CausalSeq`, `EventEmbed`) load and infer deterministically. |
| **Deterministic Tokenizer** | **100% Operational** | Vocabulary (1,000 words + 128 characters) tokenizes without external dependencies. |
| **Historical FAISS Retrieval** | **100% Operational** | Cosine similarity search over 10,000 real GDELT vectors in < 2ms with Parquet filtering. |
| **Backend REST API (FastAPI)** | **100% Operational** | All endpoints active (`/forecast/analyze`, `/research/dossier`, `/historical/match`, `/backtests/run`, `/health`). |
| **Live Research Engine (Layer 13)**| **100% Operational** | Domain-adaptive query planning querying live providers with URL and content deduplication. |
| **Frontend UI (React/TypeScript)** | **100% Operational** | Vitest tests passing; D3.js causal graph, scenario breakdown, and indicator lists rendering. |
| **Temporal Leakage Guard** | **100% Operational** | Strict runtime validator rejecting timestamps exceeding user information cutoffs. |
| **Probability Calibration** | **100% Operational** | Empirical temperature calibration ($T=1.3612$) loaded from `calibration.json`. |
| **Cloud & Docker Deployment** | **Configured & Verified** | Docker Compose (`docker-compose.yml`) and Render Blueprint (`render.yaml`) verified. |

---

## Repository File & Directory Structure

```
DELPHI/
├── DELPHI_LAYER_BY_LAYER_EXPLANATION.txt  # Plain-text operational & architectural manual
├── DELPHI_DEEP_REPORT.md                 # Full-stack audit report and verification findings
├── AGENTS.md                             # Mandatory DELPHI architectural laws & constraints
├── ARCHITECTURE.md                       # High-level layer boundaries and model contracts
├── MODEL_SPECIFICATION.md                # Formal mathematical specs of custom neural models
├── EVALUATION_PROTOCOL.md                # Scientific evaluation criteria & metric definitions
├── DATA_DICTIONARY.md                    # Canonical schemas for events, news, trade, and actors
├── ROADMAP.md                            # Complete Layer 0 to Layer 13 development status
├── Makefile                              # Automation commands (setup, test, lint, format)
├── docker-compose.yml                    # Multi-container production orchestration
├── pyproject.toml                        # Python package configuration
├── requirements.txt                      # Production backend dependencies
│
├── config/                               # System Configuration
│   ├── config.yaml                       # Global system configuration
│   ├── model_config.yaml                 # Neural hyperparameters (dims, heads, layers)
│   └── training_config.yaml              # Learning rates, batch sizes, optimizers
│
├── models/                               # Serialized Model Weights & Checkpoints
│   ├── vocab/vocabulary.json             # Custom tokenizer vocabulary
│   ├── eventembed/model.pt               # 1.13 MB checkpoint (281,120 parameters)
│   ├── eventnet/model.pt                 # 2.91 MB checkpoint (724,995 parameters)
│   ├── causalseq/model.pt                # 11.72 MB checkpoint (2,928,649 parameters)
│   ├── crednet/model.pt                  # 6.5 KB checkpoint (961 parameters)
│   └── calibration/calibration.json      # Fitted temperature scaling parameters
│
├── indexes/                              # Vector Retrieval Indexes
│   └── historical/
│       ├── index.faiss                   # 10.2 MB FAISS vector index (10,000 events)
│       ├── metadata.parquet              # 47.7 MB Parquet metadata table
│       └── manifest.json                 # Index date boundaries & verification hash
│
├── src/delphi/                           # Primary DELPHI Source Package
│   ├── api/                              # FastAPI endpoints, routers, schemas, services
│   ├── forecast/                         # Orchestrator, scenario builder, leakage guards
│   ├── models/                           # PyTorch definitions for all 4 neural models
│   ├── retrieval/                        # FAISS vector wrapper, historical matcher, reranker
│   ├── research/                         # Live web research engine, query planner, fetcher
│   ├── tokenizer/                        # Deterministic custom tokenizer & normalizer
│   ├── ingestion/                        # Dataset adapters for GDELT, ICEWS, Comtrade
│   └── preprocessing/                    # Temporal splitters, deduplicators, cleaners
│
├── frontend/                             # React 18 + TypeScript + Vite Dashboard
│   ├── src/
│   │   ├── components/charts/            # D3.js causal force graphs & timeline views
│   │   ├── pages/                        # Dashboard, Analysis, Research, Backtests, Historical
│   │   └── api/                          # Typed API client interfacing with FastAPI
│   └── package.json
│
├── scripts/                              # Operational & Diagnostic Scripts
│   ├── verify_all.py                     # Validates all models, weights, indexes & database
│   ├── train_pipeline.py                 # Monolithic pipeline training models sequentially
│   ├── temporal_backtest.py              # Walk-forward backtest driver
│   └── run_two_investigations.py         # End-to-end multi-domain test runner
│
└── tests/                                # Automated Test Suite (73 Tests)
    ├── api/                              # FastAPI route tests
    ├── model/                            # PyTorch forward-pass and contract tests
    ├── forecast/                         # Scenario building and leakage guard tests
    └── tokenizer/                        # Deterministic tokenization tests
```

---

## Quick Start & Local Execution

### Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ and npm
- (Optional) Git & Docker

### 1. Environment Setup
```powershell
# Clone the repository
git clone https://github.com/your-username/DELPHI.git
cd DELPHI

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install backend dependencies in editable mode
pip install -r requirements.txt
pip install -e .
```

### 2. Verify System Health & Weights
Run the diagnostic script to verify that all 4 neural checkpoints load and all 3,935,725 parameters are active:
```powershell
python scripts/verify_all.py
```

### 3. Launch the Backend API
```powershell
python -m uvicorn delphi.api.app:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/health/ready](http://127.0.0.1:8000/health/ready)

### 4. Launch the React Dashboard
In a separate terminal window:
```powershell
cd frontend
npm install
npm run dev
```
Visit [http://localhost:5173](http://localhost:5173) in your browser.

---

## Running Automated Tests

The repository maintains an automated test suite verifying model shapes, gradient computations, tokenizer determinism, and temporal leakage prevention:

```powershell
# Run backend test suite (Pytest):
pytest tests/ -v

# Run frontend tests (Vitest):
cd frontend
npm test -- --run
```

---

## REST API Reference & Example Payloads

### 1. Generate Predictive Forecast
**Endpoint**: `POST /api/v1/forecast/analyze`

**Request Body**:
```json
{
  "text": "Country A imposes export restrictions on critical mineral shipments to Country B after maritime skirmish.",
  "information_cutoff": "2026-10-26T12:00:00Z",
  "horizon_days": 30,
  "num_scenarios": 3
}
```

**Response Payload**:
```json
{
  "request_id": "9f3c7b2a-14d2-4e9a-8c56-f281e09581c3",
  "extracted_event": {
    "actor": "Country A",
    "target": "Country B",
    "event_code": "0163",
    "event_type": "Impose Economic Sanctions",
    "confidence": 0.942
  },
  "source_credibility": 0.885,
  "scenarios": [
    {
      "scenario_id": "scen-01",
      "title": "Reciprocal Trade Restrictions (Base Case)",
      "probability": 0.54,
      "calibrated": true,
      "timeline": [
        {"day": 3, "event": "Diplomatic protest filed with WTO"},
        {"day": 8, "event": "Target country enacts retaliatory tariff on agricultural goods"}
      ],
      "tripwires": [
        "Watch for formal retaliatory announcement by Ministry of Commerce within 10 days"
      ]
    },
    {
      "scenario_id": "scen-02",
      "title": "Maritime Escalation & Blockade Probing",
      "probability": 0.31,
      "calibrated": true,
      "timeline": [
        {"day": 5, "event": "Naval patrol deployments in contested corridor"}
      ],
      "tripwires": [
        "Notice to Mariners issued for naval live-fire exercises"
      ]
    },
    {
      "scenario_id": "scen-03",
      "title": "Third-Party Diplomatic Mediation",
      "probability": 0.15,
      "calibrated": true,
      "timeline": [
        {"day": 12, "event": "Regional bloc convenes emergency security summit"}
      ],
      "tripwires": [
        "Joint communique calling for bilateral ceasefire"
      ]
    }
  ],
  "historical_analogues": [
    {
      "event_id": "HIST-2018-0912",
      "title": "2018 Rare Earth Export Suspension",
      "similarity_score": 0.891,
      "date": "2018-04-14",
      "outcome_summary": "Tariff dispute escalated for 4 months before bilateral quota agreement"
    }
  ],
  "provenance": {
    "model_checkpoint_hash": "a1f9e2...",
    "cutoff_enforced": "2026-10-26T12:00:00Z",
    "temporal_leakage_detected": false,
    "temperature_scale_factor": 1.3612
  }
}
```

---

## Containerization & Cloud Deployment

### Docker Compose
DELPHI includes production multi-stage Dockerfiles:
```powershell
docker compose up --build -d
```
- Backend runs on `http://localhost:8000`
- Frontend serves via Nginx on `http://localhost:3000`

### Render Cloud Deployment
Native [`render.yaml`](render.yaml) specification:
- **Environment**: Python 3.12 (specified via `.python-version`)
- **Build Command**: `pip install -r requirements.txt && pip install -e .`
- **Start Command**: `uvicorn delphi.api.app:app --host 0.0.0.0 --port $PORT`

---

## Associated Project Documentation

For deeper architectural, mathematical, and operational information:
- 📖 [DELPHI_LAYER_BY_LAYER_EXPLANATION.txt](DELPHI_LAYER_BY_LAYER_EXPLANATION.txt) — Exhaustive plain-text layer-by-layer technical reference manual.
- 📋 [DELPHI_DEEP_REPORT.md](DELPHI_DEEP_REPORT.md) — Comprehensive system verification, defect remediation, and full-stack operational audit.
- 📐 [MODEL_SPECIFICATION.md](MODEL_SPECIFICATION.md) — Exact mathematical equations, loss functions, and tensor shapes.
- ⚖️ [AGENTS.md](AGENTS.md) — Mandatory DELPHI development laws and architectural invariants.
- 🧪 [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md) — Temporal backtesting rules, calibration standards, and scientific baselines.
- 🗂️ [DATA_DICTIONARY.md](DATA_DICTIONARY.md) — Canonical schemas for articles, structured events, and actors.

---

## License

DELPHI is open-source research software licensed under the [MIT License](LICENSE).
