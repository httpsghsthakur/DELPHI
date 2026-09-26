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
1. `author_identifiable`: (Binary) Presence of a named, specific author.
2. `article_length_normalized`: (Float) Word count normalized (capped at 2000).
3. `citation_density`: (Float) Density of links or quotes per 100 words.
4. `title_sensationalism`: (Float) Ratio of capitalized words and exclamation marks to title length.
5. `historical_source_reliability`: (Float) Running historical average of the source's credibility.
6. `corroboration_count_normalized`: (Float) Log-normalized count of independent corroborating articles at $T_0$.
7. `correction_history_signal`: (Float) $1 - \text{correction\_rate}$.
8. `publication_consistency`: (Float) Inverse variance of publication frequency.
9. `primary_source_presence`: (Binary) Does the text quote official/primary statements.
10. `attribution_completeness`: (Float) Ratio of named entities to total words.
11. `author_history_availability`: (Binary) Has the author appeared previously in the dataset.
12. `domain_reputation`: (Float) Heuristic TLD scoring (.edu/.gov > .com/.org > other).

Missing data is handled using neutral proxies (e.g. 0.5) to avoid implicit penalization.

## Temporal Rules
CredNet features are extracted strictly using information available at or before the `prediction_cutoff`. Future retractions or subsequent corroborations are explicitly forbidden.

## Calibration
The model uses `BCEWithLogitsLoss`. After training, validation logits are scaled using Platt Scaling (`LogisticRegression`) to convert raw logits into bounded, calibrated credibility probabilities between 0 and 1.
