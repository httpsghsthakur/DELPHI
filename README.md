# DELPHI — Predictive Intelligence & Deep Research System

DELPHI is a custom-engineered, end-to-end predictive intelligence platform designed to conduct multi-source web research, extract structured events, model causal trajectories, retrieve historical precedents, and compose comprehensive, paragraph-based intelligence briefings with full citation traceability.

**All models are custom-built from scratch — 0% external LLM APIs, 0% pretrained transformers, 0% hallucinated results.**

---

## Current Operational Status

| Subsystem / Layer | Operational Status | Reality & Architecture Verification |
|---|---|---|
| **Core Models (Layers 1–8)** | **100% Operational** | Custom PyTorch models (`EventNet`, `CredNet`, `CausalSeq`, `EventEmbed` totaling 3,935,725 parameters) load from local `.pt` checkpoints without external dependencies. |
| **Deterministic Tokenizer** | **100% Operational** | Custom BPE tokenizer with 16,384 vocabulary (`models/vocab/vocabulary.json`). |
| **Historical FAISS Retrieval** | **100% Operational** | FAISS cosine vector search querying 10,000 real historical GDELT records with temporal leakage safeguards. |
| **Backend REST API (FastAPI)** | **100% Operational** | All endpoints active (`/analysis`, `/events`, `/historical/search`, `/historical/{id}`, `/backtests`, `/research`, `/models`, `/health/ready`). Stubs replaced with real neural and database logic. |
| **Live Research Engine (Layer 13)** | **100% Operational** | Domain-adaptive QueryPlanner querying DuckDuckGo, Wikipedia, GDELT, and Local Historical Parquet with wire deduplication and source clustering. |
| **Grounded Intelligence Briefings** | **100% Operational** | GroundedReportComposer synthesizes research dossiers and custom neural outputs into ~3,000 words across 9 paragraph sections with clickable inline citations. |
| **Offline Temporal Backtesting** | **100% Operational** | `/backtests` executes real walk-forward sequence evaluation using custom `CausalSeq` on `data/processed/causal_seqs.json`. |
| **Frontend UI (React/TypeScript)** | **100% Operational** | 13/13 Vitest tests passing; production bundle compiles in 10s; features intelligence briefing reading view, metrics strip, quick scenario presets, and SQLite analysis reopening. |
| **Render Cloud Deployment** | **Configured & Verified** | Native `render.yaml` and `.python-version` (3.12.8) with all dependencies (`pydantic-settings`, `requests`, `scikit-learn`, `python-multipart`). |
| **Docker Deployment** | **Configured** | Multi-container setup (`docker-compose.yml`, `backend.Dockerfile`, `frontend.Dockerfile`). |
| **Empirical Checkpoint Quality** | **Research Prototype** | Models operate deterministically, but trained on small GDELT samples (1,001–7,000 records). Predictive accuracy is near baseline pending cluster scale-up. |

---

## What DELPHI Is

An explainable, backtestable predictive intelligence platform that:

- **Performs Topic-Adaptive Deep Research:** Formulates multi-angle queries for trade restrictions, monetary policy, and geopolitical events; fetches accessible web documents; normalizes timestamps; and clusters syndicated wire reports.
- **Extracts Structured Events (EventNet):** Translates raw text into CAMEO-style structured events using custom BiLSTM + Multi-Head Attention neural architecture.
- **Embeds Events into Semantic Space (EventEmbed):** Maps structured events into dense 64-dimensional vectors.
- **Retrieves Historical Analogues (FAISS):** Searches 10,000 historical records using cosine similarity with strict temporal cutoffs to prevent future data leakage.
- **Scores Source Credibility (CredNet):** Estimates source reliability based on domain provenance and reporting rigor.
- **Projects Multi-Step Trajectories (CausalSeq):** Custom GRU sequence model modeling future event steps via beam search.
- **Composes Grounded Intelligence Briefings:** Produces a 2,800–3,100 word analytical intelligence briefing organized in 9 connected paragraph sections with inline citations `[[1]](<url>)`.
- **Enforces Strict Temporal Validation:** Actively rejects any document, checkpoint, or evidence that postdates the forecast information cutoff.

---

## What DELPHI Is NOT

- A chatbot or generic LLM wrapper (0% OpenAI, Gemini, Claude, or Anthropic APIs).
- A pretrained transformer consumer (no BERT, RoBERTa, GPT-2, Llama, or Mistral weights).
- A superficial summary card generator (outputs deep, reasoned paragraphs, not disconnected bullet points).
- An oracle claiming certainty (uncalibrated probability distributions and evidentiary gaps are explicitly disclosed).

---

## Quick Start & Local Execution

### 1. Launch FastAPI Backend
```powershell
# From repository root:
.venv\Scripts\python.exe -m uvicorn delphi.api.app:app --host 127.0.0.1 --port 8000 --reload
```
*Health Check*: Visit `http://127.0.0.1:8000/health/ready` (returns `"status": "ok"` with all 7 dependencies green).

### 2. Launch React Frontend
```powershell
cd frontend
npm run dev
```
*Workspace*: Visit `http://localhost:5173`. Use the quick scenario presets (`⚡ Semiconductor Restrictions`, `🏛️ 50bps Rate Hike`, `🚢 Maritime Disruption`) to launch a complete investigation in one click.

### 3. Run Automated Tests
```powershell
# Backend (Python):
.venv\Scripts\python.exe -m pytest -q
# Expected: 72 passed, 1 skipped in ~35s (100% runnable pass rate)

# Frontend (TypeScript / Vitest):
cd frontend
npm test -- --run
# Expected: 13 passed in ~10s (100% pass rate)
```

### 4. Run Real-World Dual Investigation Script
```powershell
.venv\Scripts\python.exe scripts\run_two_investigations.py
```
*Executes end-to-end investigations for Semiconductor Export Controls and Central Bank Rate Hikes, producing ~3,000-word paragraph-based briefings.*

---

## Deployment on Render

DELPHI includes native Render Blueprint configuration:

- **Runtime**: Python 3.12 (specified via `.python-version`)
- **Build Command**:
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt && pip install -e .
  ```
- **Start Command**:
  ```bash
  uvicorn delphi.api.app:app --host 0.0.0.0 --port $PORT
  ```
- **Environment Variables**:
  - `PYTHON_VERSION`: `3.12.8`
  - `DELPHI_EXECUTION_MODE`: `REAL`
  - `STRICT_TEMPORAL_MODE`: `true`
  - `DATABASE_URL`: `sqlite:///delphi.db`
  - `CORS_ORIGINS`: `*`

---

## Repository Documentation

- [DELPHI_DEEP_REPORT.md](DELPHI_DEEP_REPORT.md) — Comprehensive technical architecture, defect repair log, and operational verification audit.
- [ARCHITECTURE.md](ARCHITECTURE.md) — Layer boundaries, schemas, and model contracts.
- [MODEL_SPECIFICATION.md](MODEL_SPECIFICATION.md) — Formal mathematical specs of custom neural models.
- [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md) — Scientific evaluation criteria and temporal split rules.
- [DATA_DICTIONARY.md](DATA_DICTIONARY.md) — Canonical event, trade, and news schemas.
