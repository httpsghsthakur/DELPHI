# EVALUATION PROTOCOL

## 1. Zero Leakage Rule
Strict temporal evaluation framework must be used for forecasting models. For any target event at time T0, models must only receive inputs derived from information available strictly before or at T0.
The DELPHI `TemporalLeakageGuard` and `TemporalSplitter` ensure that dataset generation respects these strict chronological limits.

## 2. Evaluation Metrics by Component
- **EventNet**: Precision, Recall, F1, Span F1.
- **EventEmbed**: Similarity scores, intrinsic evaluation metrics.
- **CredNet**: Macro F1, ROC-AUC, Calibration, Brier score.
- **Historical Intelligence**: 
  - Metrics: Recall@1, Recall@5, Recall@10, Recall@20, MRR.
  - Evaluation infrastructure is implemented. Real benchmarks are pending real dataset preparation.
  - Absolute constraint: No future information leakage. All candidates must evaluate strictly against `prediction_time`.

## 3. Backtesting
Backtesting will be the core evaluation mechanism.
- Model produces a forecast at T0.
- System records the forecast.
- System compares actual occurrences after T0 to the generated scenarios.
- Scenarios must be scored probabilistically.
