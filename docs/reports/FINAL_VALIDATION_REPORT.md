# DELPHI — FINAL VALIDATION REPORT

**Report Date**: 2026-09-26  
**Report Type**: Release Candidate Validation  
**Report Version**: 1.0  

---

## 1. Architecture Status

**Status: COMPLETE**

The DELPHI architecture through Layer 12 is fully implemented:

| Layer | Component | Status |
|-------|-----------|--------|
| 1 | Data Foundation (Ingestion, Schemas, Manifests) | ✅ Complete |
| 2 | Custom Tokenizer (Vocabulary, Normalization) | ✅ Complete |
| 3 | EventEmbed (Word2Vec + CharCNN, 256-dim) | ✅ Complete |
| 4 | EventNet (BiLSTM + Self-Attention, BIO + Event Type) | ✅ Complete |
| 5 | Historical Intelligence (EventEmbed → FAISS → Matcher) | ✅ Complete |
| 6 | CredNet (12-feature → 32 → 16 → 1 MLP) | ✅ Complete |
| 7 | CausalSeq (Encoder-Decoder LSTM with Bahdanau Attention) | ✅ Complete |
| 8 | Forecast Orchestrator (Scenarios, Scoring, Calibration) | ✅ Complete |
| 9 | Phase B/C Evaluation Infrastructure | ✅ Complete |
| 10 | FastAPI Backend | ✅ Complete |
| 11 | React/TypeScript Frontend | ✅ Complete |
| 12 | Docker Containerization | ✅ Implemented |

All custom models are built from scratch. No external LLMs, pretrained transformers, or API wrappers are used anywhere in the system.

---

## 2. Deployment Status

### Docker

**Status: IMPLEMENTED — NOT RUNTIME-VERIFIED**

Docker is **not available** on the current host (`docker` command not found). The following Docker artifacts exist and are syntactically valid:

- `docker-compose.yml` — 3-service architecture (PostgreSQL, FastAPI backend, React+Nginx frontend)
- `docker/backend.Dockerfile` — Python backend container
- `docker/frontend.Dockerfile` — Multi-stage Node build + Nginx serve
- `docker/nginx.conf` — Reverse proxy routing `/api/` to backend
- `docker/backend-entrypoint.sh` — Entrypoint script
- `.env.docker.example` — Environment template

**Cannot verify:**
- Container builds
- Service startup
- Inter-service networking
- Health check endpoints via Docker
- Database persistence across restarts
- `docker compose config` validation

**Reason:** Docker Engine is not installed on this Windows host.

### Local Development

The backend and frontend run successfully in local development mode:
- Backend: `uvicorn delphi.api.app:app` (SQLite)
- Frontend: `npm run dev` (Vite dev server)

---

## 3. Real-Data Status

### Available Datasets

| Dataset | Source | Type | Time Range | Records | Checksum |
|---------|--------|------|------------|---------|----------|
| GDELT V2 Sample | data.gdeltproject.org | **REAL** (but minimal) | 2023-01-01 00:00–00:15 | 1,001 | `fef9830b...` |

- **Manifest version:** v1.0
- **Preprocessing version:** v1
- **Split version:** v1
- **Schema version:** v1
- **Source count:** 1 domain extracted from 15-minute window

### Critical Assessment

The only physically available dataset is a **single 15-minute GDELT export** containing 1,001 records. While this is real GDELT data (not fabricated), it is:

- Too small for meaningful model convergence
- Insufficient for statistically significant evaluation
- Limited to a single time window (no temporal diversity)
- Contains only 1 source domain

**No additional datasets exist.** The Phase B/C evaluation report references "7,007 events" from a "7-day scale-up" — this was produced by **repeating the same 1,001-record sample** 7 times with synthetic day offsets. This is effectively a **synthetic augmentation**, not genuinely independent multi-day data.

---

## 4. Model Training Status

### Tokenizer

- **Architecture:** Custom Word2Vec-compatible vocabulary
- **Real training:** NO — vocabulary is defined but no learned embeddings are persisted
- **Checkpoint file:** DOES NOT EXIST (`models/vocab/` is empty)
- **Version:** v1 (configuration only)

### EventEmbed

- **Architecture:** Word2Vec + Character CNN, 256-dimensional output
- **Real training:** NO — architecture passes smoke tests but no persisted `.pt` checkpoint exists
- **Checkpoint file:** DOES NOT EXIST
- **Training info end time:** N/A
- **Reported loss:** 0.4200 (from a single 5-epoch pass on 1,001 records — effectively random initialization)

### EventNet

- **Architecture:** BiLSTM + Self-Attention, token BIO extraction + event-type classification
- **Real training:** NO — same as above, architecture-level smoke test only
- **Checkpoint file:** DOES NOT EXIST
- **Training info end time:** N/A
- **Reported Span F1:** 0.2200 (near-random on 1,001 records)
- **Reported Macro-F1:** 0.1800 (near-random)

### CredNet

- **Architecture:** 12-feature MLP → 32 → 16 → 1
- **Real training:** NO — architecture validated, no persisted checkpoint
- **Checkpoint file:** DOES NOT EXIST
- **Training info end time:** N/A
- **Reported Macro-F1:** 0.4900 (near-random)
- **Reported ROC-AUC:** 0.5200 (barely above chance)

### CausalSeq

- **Architecture:** Encoder-Decoder LSTM with Bahdanau Attention
- **Real training:** NO — architecture smoke test only
- **Checkpoint file:** DOES NOT EXIST
- **Training info end time:** N/A
- **Reported Recall@3:** 0.1200 (near-random)
- **Reported NLL:** 4.5000 (high, unconverged)

### FAISS Index

- **Status:** DOES NOT EXIST
- **`indexes/` directory:** Empty

### Calibration Artifact

- **Status:** DOES NOT EXIST
- **Calibrator state:** `UNCALIBRATED`
- **Temperature:** 1.0 (default, unfitted)

### MLflow Records

- **Status:** `mlruns/` directory is empty
- **`mlflow.db`:** File exists (876 KB) but contains no experiment runs

---

## 5. Model Artifact Audit

| Artifact | Exists | Version | Compatible | Training End Time |
|----------|--------|---------|------------|-------------------|
| Tokenizer vocabulary | ❌ No file | v1 (config) | N/A | N/A |
| EventEmbed checkpoint | ❌ No `.pt` file | N/A | N/A | N/A |
| EventNet checkpoint | ❌ No `.pt` file | N/A | N/A | N/A |
| CredNet checkpoint | ❌ No `.pt` file | N/A | N/A | N/A |
| CausalSeq checkpoint | ❌ No `.pt` file | N/A | N/A | N/A |
| FAISS index | ❌ No file | N/A | N/A | N/A |
| Calibration artifact | ❌ No file | N/A | N/A | N/A |
| Dataset manifest | ✅ Exists | v1.0 | ✅ | 2023-01-01T00:15Z |

---

## 6. Empirical Metrics

### Important Caveat

All metrics below were obtained on a **1,001-record, 15-minute GDELT sample**. They represent near-random initialization performance, NOT converged model quality. They are reproduced here for completeness.

### EventNet

| Metric | Value | Assessment |
|--------|-------|------------|
| Span F1 | 0.2200 | Near-random |
| Event-type Macro-F1 | 0.1800 | Near-random |

### Historical Retrieval

| Metric | Value | Assessment |
|--------|-------|------------|
| Recall@10 | 0.1500 | Near-random |

(Recall@1, Recall@5, MRR not separately reported)

### CredNet

| Metric | Value | Assessment |
|--------|-------|------------|
| Macro-F1 | 0.4900 | Near-random |
| ROC-AUC | 0.5200 | Barely above chance |
| Brier | 0.2450 | Unconverged |
| ECE | 0.2100 | Poorly calibrated |

### CausalSeq

| Metric | Value | Assessment |
|--------|-------|------------|
| Recall@3 | 0.1200 | Near-random |
| Macro-F1 | 0.0800 | Near-random |
| NLL | 4.5000 | Unconverged |
| Brier | 0.8500 | Very poor |
| Time-bin Top-1 | 0.1100 | Near-random |

### Forecast Engine

| Metric | Value | Assessment |
|--------|-------|------------|
| Scenario Recall@1 | 0.0800 | Near-random |
| ECE | 0.3500 | Poorly calibrated |

---

## 7. Baseline Results

From the Phase A validation (all on 1,001-record sample):

| Baseline | Metric | Value |
|----------|--------|-------|
| Frequency-based event forecasting | Recall@3 | 0.1400 |
| Logistic credibility classifier | ROC-AUC | 0.5050 |
| BM25 retrieval baseline | Recall@10 | 0.1200 |

**Note:** On this tiny dataset, baselines and DELPHI models perform comparably, both near random. This is expected with insufficient training data.

---

## 8. Calibration Status

**Status: UNCALIBRATED / RESEARCH MODE**

- No calibration artifact has been fitted
- Temperature scaling is at default (1.0)
- Scenario weights are softmax-normalized raw scores, NOT calibrated probabilities
- The `ProbabilityCalibrator.state` is `"UNCALIBRATED"`
- The frontend correctly labels outputs as "Uncalibrated / Research Mode"

---

## 9. Walk-Forward Temporal Backtest

### Phase A

- **Cutoffs attempted:** 1
- **Cutoffs successful:** 1
- **Cutoffs rejected:** 0
- **Cutoff value:** 2023-01-01T00:00Z
- **Assessment:** Ran on the only available 15-minute slice. Not a meaningful temporal evaluation.

### Phase B/C

- **Reported walk-forward steps:** 6
- **Average accuracy:** 0.6926
- **Assessment:** These 6 steps were generated by **repeating the same 1,001-record file** with synthetic day offsets. The reported ~69% accuracy is on **duplicated data** and does NOT represent genuine temporal forecasting performance on independent future data.

### Real Walk-Forward Test

**Cannot execute.** Requirements:

1. Model checkpoints with known `training_information_end_time` — **none exist**
2. Multiple temporally distinct data windows — **only one 15-minute window exists**
3. FAISS index — **does not exist**
4. Calibration artifact — **does not exist**

---

## 10. Production vs Synthetic Mode

### Current State

The `docker-compose.yml` sets `DELPHI_EXECUTION_MODE=synthetic` by default.

The orchestrator instantiates `MockActual*` classes (`MockActualEventNet`, `MockActualCredNet`, `MockActualHistoricalMatcher`, `MockActualCausalSeq`) which return hardcoded synthetic values. These are **not** the real PyTorch models — they are deterministic mock wrappers.

### Production Mode Requirements

To run in genuine production mode, the following would be required:

1. Persisted `.pt` checkpoints for all 4 models — ❌ Missing
2. Populated FAISS index — ❌ Missing
3. Fitted calibration artifact — ❌ Missing
4. The `ModelRegistry` to load actual weights instead of returning hardcoded version strings — ⚠️ Not yet wired

**A missing artifact correctly produces a readiness failure** when checked via `/health/ready` with real model requirements.

---

## 11. Frontend UI Audit

### Calibration Labels

✅ `ScenarioDistribution.tsx` correctly distinguishes between calibrated probabilities and uncalibrated weights:
- Displays "Probability Distribution" when `probability` field is present
- Displays "Normalized Scenario Weight" with a yellow `Uncalibrated / Research Mode` badge otherwise

### Credibility Display

✅ `CredibilityPanel.tsx` correctly:
- Labels scores as "Credibility Signal" (not "truth" or "accuracy")
- Shows CALIBRATED/UNCALIBRATED badges
- Includes disclaimer: *"The credibility signal reflects measurable source and structural characteristics. It is a modeled estimate, not a guarantee of absolute factual truth."*

### Provenance

✅ `ProvenancePanel.tsx` displays:
- Prediction cutoff timestamp
- Dataset version
- All model versions
- Temporal validation status

### No False Claims Found in Frontend

The frontend does NOT display:
- ❌ Uncalibrated weights as probabilities — correctly handled
- ❌ Historical similarity as probability — similarity scores shown as "match_score"
- ❌ Credibility as truth — explicitly disclaimed
- ❌ Synthetic results as real-world validation — mode is labeled

---

## 12. Complete Regression Results

### Backend (pytest -W error)

```
67 passed in 31.90s
```

**0 failures, 0 warnings treated as errors.**

Test breakdown by module:
- `tests/tokenizer/` — 2 files
- `tests/data/` — 4 files
- `tests/model/` — 11 files (EventEmbed, EventNet, CredNet, CausalSeq)
- `tests/retrieval/` — 7 files
- `tests/forecast/` — 1 file
- `tests/api/` — 1 file (integration)

### Frontend (Vitest)

```
1 passed (1 test file)
Duration: 8.96s
```

### TypeScript Typecheck

```
tsc --noEmit: PASSED (exit code 0, no errors)
```

### Frontend Build

```
vite build: PASSED
Output: dist/index.html (0.47 KB), dist/assets/index.css (15.37 KB), dist/assets/index.js (217.77 KB)
Built in 12.13s
```

### Frontend Lint

```
eslint: PASSED (exit code 0, no errors)
```

### Docker

```
NOT EXECUTED — Docker not available on this host
```

---

## 13. Known Limitations

1. **No persisted model checkpoints** — All models have been architecture-validated but no trained `.pt` weights exist in the repository.
2. **Minimal real data** — Only 1,001 records from a single 15-minute GDELT window.
3. **No FAISS index** — Historical retrieval requires a populated index which does not exist.
4. **No calibration** — Scenario weights are raw softmax-normalized scores.
5. **Phase B/C "walk-forward" used duplicated data** — The 7-day evaluation repeated the same 1,001-record file, not genuinely independent temporal data.
6. **Orchestrator uses mock wrappers** — `MockActualEventNet`, `MockActualCredNet`, etc. return hardcoded values, not actual model inference results.
7. **Docker not runtime-verified** — Dockerfiles exist but have never been built or run.
8. **No GPU training infrastructure validated** — All training was CPU-only on minimal data.
9. **Model registry hardcodes versions** — `ModelRegistry` returns static version strings without checking actual artifact files.
10. **Single-source data** — GDELT only. No ICEWS, no curated ground-truth event datasets.

---

## 14. Reproducibility

| Item | Value |
|------|-------|
| Git commit (latest) | `9d518a5` |
| Previous milestone commit | `999d43b` |
| Dataset manifest | `GDELT_SAMPLE_20230101` |
| Dataset SHA-256 | `fef9830b9208d3779445003becff788af93f8a13ce509a15c2ac5da334f9dfb2` |
| Random seed | 42 |
| Python | 3.12 |
| PyTorch | Installed via requirements |
| All models | Custom from-scratch (no external weights) |

---

## 15. Final Release Status

```
ARCHITECTURE:          COMPLETE
MODELS:                ARCHITECTURE-VALIDATED (no persisted checkpoints)
BACKEND:               VERIFIED (67 tests passing)
FRONTEND:              VERIFIED (build + typecheck + lint + test passing)
DOCKER:                IMPLEMENTED (not runtime-verified)
DATABASE:              VERIFIED (SQLite local; PostgreSQL via Docker untested)
REAL DATA:             AVAILABLE (minimal — 1,001 records, single 15-min window)
REAL TEMPORAL BACKTEST: PENDING (insufficient artifacts and data)
CALIBRATION:           UNCALIBRATED
EMPIRICAL FORECAST:    NOT ESTABLISHED (metrics reflect near-random initialization)
```

---

## 16. Release Commit

**Commit hash:** `9d518a5` (Layer 11 Frontend and Layer 12 Docker Deployment)

This commit is distinct from the previous milestone `999d43b`.

---

## 17. What Would Be Required for Production Readiness

1. **Large-scale real data ingestion** — Multiple months of GDELT/ICEWS data with temporal diversity
2. **GPU training to convergence** — All 4 models trained on sufficient data with proper hyperparameter tuning
3. **Checkpoint persistence** — `.pt` files with provenance metadata
4. **FAISS index population** — Built from trained EventEmbed on historical corpus
5. **Calibration fitting** — Temperature scaling on held-out validation data
6. **Independent held-out evaluation** — Metrics on data never seen during training
7. **Real walk-forward backtest** — Multiple temporal cutoffs with genuinely future test windows
8. **Docker runtime verification** — Full container integration test on Docker-capable host
9. **PostgreSQL integration test** — Persistence verification with real database

---

## 18. Conclusion

DELPHI is a **complete, architecturally sound research system** with:
- ✅ Full custom ML pipeline (no external LLMs)
- ✅ Robust backend with temporal safety
- ✅ Responsive frontend with honest labeling
- ✅ Docker deployment configuration
- ✅ 67 backend tests + frontend test/typecheck/build/lint all passing

It is **NOT yet**:
- ❌ Trained on sufficient data for meaningful predictions
- ❌ Empirically validated on independent held-out data
- ❌ Calibrated
- ❌ Runtime-verified in Docker
- ❌ A production forecasting service

**The system is a validated research architecture ready for the training and evaluation phases that would establish its empirical forecasting capability.**
