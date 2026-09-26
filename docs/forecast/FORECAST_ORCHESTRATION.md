# DELPHI Forecast Orchestration (Layer 8)

## Architecture Overview
The Forecast Orchestration layer is the deterministically constructed pipeline that connects DELPHI's neural layers into a unified intelligence engine. It extracts current events, gathers historical analogies, predicts future trajectories, and synthesizes them into actionable, calibrated forecast reports.

### Pipeline Stages
1. **Forecast Request Formulation**: Accepts structured metadata and text, strictly enforcing the `prediction_information_cutoff`.
2. **Current Event Extraction (EventNet)**: Converts text into structured current events.
3. **Credibility Assessment (CredNet)**: Evaluates the source material for historical reliability without automatically altering probability.
4. **Historical Intelligence (Layer 5)**: Retrieves analogue historical outcomes.
5. **CausalSeq Generation (Layer 7)**: Generates structured candidate future event trajectories autoregressively.
6. **Scenario Construction & Deduplication**: Condenses multiple trajectories into a manageable set (default max 3) of unique structural pathways.
7. **Scenario Scoring**: Evaluates scenarios using a configurable weighting of `sequence_score`, `historical_support_score`, `evidence_score` and `model_support_score`.
8. **Probability Calibration**: Converts raw scores into calibrated probabilities summing to 1. Tracks whether the model is in `UNCALIBRATED / RESEARCH MODE` or fully calibrated.
9. **Indicator Detection**: Extracts measurable downstream real-world conditions to monitor for each scenario.
10. **Evidence Aggregation**: Formalizes supporting and contradictory evidence.
11. **Confidence Assessment**: Derives a confidence category based on calibration, historical agreement, and evidence spread.
12. **Forecast Validation**: Fails loudly if temporal rules, math rules (sum to 1), or structural metadata are violated.
13. **Report Generation**: Emits a deterministic, machine-readable report (markdown supported).

## Strict From-Scratch Rule
This layer relies solely on DELPHI's internal deterministic logic and PyTorch models. No external LLMs, AI APIs, or pretrained embedding representations are used anywhere in the pipeline. Explanations derive structurally from model traces, avoiding hallucination.

## Scenario Scoring and Probability
- **Scoring**: A weighted sum of evidence components.
- **Probability Guarantee**: Always sum to 1 within a tolerance limit. Handled by `ProbabilityCalibrator`.
- **Status**: The pipeline tracks whether the calibration functions have been validated on real ground-truth outcomes. Currently, it emits `UNCALIBRATED / RESEARCH MODE`.

## Temporal Checkpoint Rules
Strict chronological enforcement exists across the entire pipeline.
- Future evidence is explicitly barred.
- The temporal bound `checkpoint_training_end_time` of the model weights is strictly checked against the `prediction_information_cutoff`. If violated, the run is flagged as `STRICT_TEMPORAL_BACKTEST_UNAVAILABLE` or failed.

## Evidence
Evidence is explicitly categorized as supporting, contradictory, or neutral. It traces back to known datasets and features, avoiding "black box" decisions.

## Real Data Status
**DELPHI END-TO-END ARCHITECTURE VALIDATED — REAL TEMPORAL BACKTESTING AND CALIBRATED FORECASTING PENDING**
