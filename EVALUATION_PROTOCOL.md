# EVALUATION PROTOCOL

## 1. Zero Leakage Rule
Strict temporal evaluation framework must be used for forecasting models. For any target event at time T0, models must only receive inputs derived from information available strictly before or at T0.
The DELPHI `TemporalLeakageGuard` and `TemporalSplitter` ensure that dataset generation respects these strict chronological limits.

## 2. Evaluation Metrics by Component
- **EventNet**: Precision, Recall, F1, Span F1.
- **EventEmbed**: Similarity scores, intrinsic evaluation metrics.
- **CredNet**: Macro F1, ROC-AUC, Calibration, Brier score.
- **Historical Intelligence**: Recall@K, Precision@K, Temporal consistency.

## 3. Backtesting
Backtesting will be the core evaluation mechanism.
- Model produces a forecast at T0.
- System records the forecast.
- System compares actual occurrences after T0 to the generated scenarios.
- Scenarios must be scored probabilistically.
