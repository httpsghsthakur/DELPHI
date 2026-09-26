# DELPHI Forecast Orchestration (Layer 8)

## Architecture Overview
The Forecast Orchestration layer is the deterministically constructed pipeline that connects DELPHI's neural layers into a unified intelligence engine. It extracts current events, gathers historical analogies, predicts future trajectories, and synthesizes them into structured, scenario-weighted forecast reports.

### Pipeline Stages
1. **Forecast Request Formulation**: Accepts structured metadata and text, strictly enforcing the `prediction_information_cutoff`.
2. **Current Event Extraction (EventNet)**: Converts text into structured current events.
3. **Credibility Assessment (CredNet)**: Evaluates the source material for historical reliability without automatically altering probability.
4. **Historical Intelligence (Layer 5)**: Retrieves analogue historical outcomes.
5. **CausalSeq Generation (Layer 7)**: Generates structured candidate future event trajectories autoregressively.
6. **Scenario Construction & Deduplication**: Condenses multiple trajectories into a manageable set (default max 3) of unique structural pathways.
7. **Scenario Scoring**: Evaluates scenarios using a configurable weighting of `sequence_score`, `historical_support_score`, `evidence_score` and `model_support_score`.
8. **Probability Calibration**: Converts raw scores into normalized weights summing to 1. In `UNCALIBRATED / RESEARCH MODE` these are softmax-normalized scores, not calibrated probabilities. Becomes calibrated only when a temperature-scaling model has been fitted and independently validated.
9. **Indicator Detection**: Extracts measurable downstream real-world conditions to monitor for each scenario.
10. **Evidence Aggregation**: Formalizes supporting and contradictory evidence.
11. **Confidence Assessment**: Derives a confidence category based on calibration, historical agreement, and evidence spread.
12. **Forecast Validation**: Fails loudly if temporal rules, math rules (sum to 1), or structural metadata are violated.
13. **Report Generation**: Emits a deterministic, machine-readable report (markdown supported).

## Strict From-Scratch Rule
This layer relies solely on DELPHI's internal deterministic logic and PyTorch models. No external LLMs, AI APIs, or pretrained embedding representations are used anywhere in the pipeline. Explanations derive structurally from model traces, avoiding hallucination.

## Real Component Integration
The Forecast Orchestrator operates using explicit `Adapter` classes (e.g. `EventExtractionAdapter`, `CredibilityAdapter`, `HistoricalRetrievalAdapter`, `CausalForecastAdapter`) that invoke the real underlying DELPHI components (Layers 1-7).
The distinction between production model execution and synthetic tests is strictly maintained:
- **Production Execution**: Adapters wrap the real PyTorch models and FAISS indices.
- **Synthetic Test**: Adapters wrap mock representations of the PyTorch models that yield deterministic synthetic output. At no point are arbitrary dictionaries fabricated directly within the orchestrator.

## Scenario Scoring and Probability
- **Scoring Traceability**: Every scenario includes an `explain_scenario_score()` method returning the exact mathematical components (`sequence_component`, `historical_component`, `credibility_component`, `model_component`).
- **Probability Guarantee**: Always sum to 1 within a tolerance limit. Handled by `ProbabilityCalibrator`.
- **Calibration States**: The calibrator transitions explicitly between:
  - `UNINITIALIZED`
  - `UNCALIBRATED / RESEARCH MODE` (Normalization only)
  - `FITTED_VALIDATION` (Temperature scaling optimized via NLL on validation set)
  - `HELDOUT_VALIDATED` (Calibration confirmed against test data)

## Temporal Checkpoint Rules
Strict chronological enforcement exists across the entire pipeline.
- Future evidence is explicitly barred.
- The temporal bounds of all individual component weights (`eventembed_training_end`, `eventnet_training_end`, `crednet_training_end`, `causalseq_training_end`, `calibration_training_end`) are checked against the `prediction_information_cutoff`.
- The CLI command `python -m delphi.forecast backtest` runs in strict mode and explicitly rejects any cutoff violating the checkpoint provenance boundary, rather than silently substituting future data.

## Evidence
Evidence is explicitly categorized as supporting, contradictory, or neutral. It traces back to known datasets and features, avoiding "black box" decisions. `evidence_score` relies strictly on the structured output of `CredNet`.

## Real Data Status
**MODEL EXECUTION**: REAL DELPHI COMPONENTS (via Adapters)  
**DATA**: SYNTHETIC FIXTURE  
**CALIBRATION**: UNCALIBRATED  
**TEMPORAL SAFETY**: ARCHITECTURALLY VERIFIED  

*(DELPHI END-TO-END ARCHITECTURE VALIDATED — REAL TEMPORAL BACKTESTING AND CALIBRATED FORECASTING PENDING)*
