# DELPHI — Predictive Intelligence Research System

DELPHI is a custom-built, end-to-end research system for structured event analysis and scenario generation. It extracts events from text, retrieves historical analogues, assesses source credibility, models causal trajectories, and produces scenario-weighted forecasts.

**All models are custom-built from scratch — no external LLMs, no pretrained transformers, no API wrappers.**

## Current Status

| Component | Status |
|---|---|
| Architecture (Layers 1–8) | **Complete** |
| Backend (FastAPI) | **Implemented** |
| Frontend (React/TypeScript) | **Implemented** |
| Docker Deployment | **Implemented** (not yet runtime-verified) |
| Model Training | **Architecture-validated** (not trained to convergence on large-scale data) |
| Calibration | **Uncalibrated / Research Mode** |
| Empirical Forecast Performance | **Not established** on independent held-out data |
| Temporal Backtesting | **Framework implemented** (pending real-scale execution) |

## What DELPHI Is

A research-grade predictive intelligence system that:

- Extracts structured events from raw text (EventNet)
- Embeds events into a custom vector space (EventEmbed)
- Retrieves historical analogues via FAISS similarity search
- Assesses source credibility with a learned model (CredNet)
- Generates future event trajectories (CausalSeq encoder-decoder)
- Produces scenario-weighted forecasts with explicit provenance
- Enforces strict temporal validation to prevent data leakage

## What DELPHI Is NOT

- A chatbot or language model wrapper
- An OpenAI/Gemini/Claude API consumer
- A generic news summarizer
- A pretrained-model demo
- An oracle that claims to know the future
- A production-ready forecasting service (it is a research system)

## Important Disclaimers

- **Scenario weights are uncalibrated** unless a fitted calibration artifact is present. The frontend labels these as "Uncalibrated / Research Mode."
- **Historical similarity scores are not probabilities.** They measure embedding distance, not likelihood.
- **Credibility scores are model estimates**, not ground-truth assertions about factual accuracy.
- **All current metrics** were obtained on a very small GDELT sample (1,001 records from a 15-minute window) and reflect near-random initialization, not converged model performance.

## Deployment

- See [DOCKER.md](docs/deployment/DOCKER.md) for Docker Compose deployment.
- See [LOCAL_SETUP.md](docs/deployment/LOCAL_SETUP.md) for local development setup.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system architecture.

## Evaluation

See [docs/reports/](docs/reports/) for validation reports and empirical results.
