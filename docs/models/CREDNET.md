# DELPHI CredNet Model

CredNet is the source credibility prediction layer of DELPHI. It estimates the historical credibility of an article based on 12 explicit, deterministic features.

## Purpose
> "Given measurable evidence available at the relevant point in time, how credible has this source/article historically appeared?"

It does **not** predict absolute truth. It assigns a calibrated credibility score based on structural and historical features.

## Architecture
The model is a deterministic PyTorch MLP:
- **Input**: 12 deterministic features
- **Hidden 1**: Linear(12, 32) + GELU
- **Hidden 2**: Linear(32, 16) + GELU
- **Output**: Linear(16, 1) raw logit

**Total Parameters**: 961

## Features
1. `author_identifiable`: (Binary) `1.0` if a named author exists (excluding "unknown"), else `0.0`. Higher = better trackability.
2. `article_length_normalized`: (Float) Total words / 2000. Capped at `1.0`. Available at $T_0$.
3. `citation_density`: (Float) Density of quotes `"` per 100 words. Capped at `1.0`. Higher = more source attribution.
4. `title_sensationalism`: (Float) Ratio of capitalized letters + (exclamation marks * 5) to title length. Capped at `1.0`. Higher = less credible.
5. `historical_source_reliability`: (Float) Running historical average of source credibility. Strict constraint: Computed *only* on events $< T_0$.
6. `corroboration_count_normalized`: (Float) $\log(1 + \text{corroborators}) / \log(51)$. Number of independent sources reporting the same event *before* $T_0$.
7. `correction_history_signal`: (Float) $1.0 - \text{correction\_rate}$. Rate computed strictly prior to $T_0$.
8. `publication_consistency`: (Float) $1.0 / (1.0 + \text{variance})$. Variance of publication frequency prior to $T_0$.
9. `primary_source_presence`: (Binary) `1.0` if text explicitly quotes primary sources (e.g. "official statement").
10. `attribution_completeness`: (Float) Ratio of capitalized words (entity proxies) to total words. Capped at `1.0`.
11. `author_history_availability`: (Binary) `1.0` if author was observed in dataset prior to $T_0$.
12. `source_longevity_normalized`: (Float) Days since source was first observed in dataset / 3650. Capped at `1.0` (10 years). Strictly $< T_0$.

Missing data is handled using neutral proxies (e.g. `0.0` or `0.5`) to avoid implicit penalization.

## Temporal Rules
CredNet features are extracted strictly using information available at or before the `prediction_cutoff` ($T_0$). 
- Future retractions or subsequent corroborations are explicitly forbidden.
- The `CredibilityFeatureExtractor` explicitly asserts that the `historical_source_data` object itself was calculated before $T_0$.

## Splitting Rules
- **Temporal Split**: `create_temporal_split` strictly sorts all records by `timestamp` and splits them sequentially, mathematically guaranteeing $T_{train} \leq T_{val} \leq T_{test}$.
- **Source-Disjoint Split**: `create_source_disjoint_split` groups by `source_id` before distribution. Ensures $Train\_Sources \cap Val\_Sources = \emptyset$.

## Calibration
The model uses `BCEWithLogitsLoss`. After training, validation logits are scaled using Platt Scaling (`LogisticRegression`) to convert raw logits into bounded, calibrated credibility probabilities between 0 and 1. The test set never interacts with the scaler fitting.

## Label Semantics
`1.0`: The article was historically designated as credible by the specific dataset (e.g., NELA-GT) based on journalistic standards at $T_0$.
`0.0`: The article was historically designated as low-credibility (e.g., propaganda, hyper-partisan, fake news).
*Note: This is NOT an absolute truth measure. It reflects structural/historical publisher signals.*

## Inference
The `CredNetInference` pipeline returns a `CredibilityResult` containing:
- `raw_logit`: Raw MLP float output.
- `uncalibrated_score`: Sigmoid of the logit.
- `calibrated_score`: Bounded Platt-scaled probability.

## Ablation
The module includes an `AblationEvaluator` that deterministically evaluates the model by zeroing out specific features or feature groups (e.g., `source_history`, `article_content`) on the validation set, allowing us to quantify exact feature importance.
