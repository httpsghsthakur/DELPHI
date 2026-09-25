# DELPHI Model Specification

## 1. EventEmbed
- **Purpose**: Provides dense vector representations of text sequences at the character and token level.
- **Inputs**: Tokenized document sequences.
- **Outputs**: 256-dimensional event/document representations.
- **Architecture**: Custom Word2Vec-style embedding + Character-level CNN.
- **Expected Parameters**: ~3M.
- **Training Data**: News corpus.
- **Evaluation Metrics**: Word analogy tasks, embedding similarity, intrinsic cluster evaluation.

## 2. EventNet
- **Purpose**: Extracts structured event information from text.
- **Inputs**: Token sequence (via EventEmbed).
- **Outputs**: Token classification, entities, event triggers, confidence.
- **Architecture**: BiLSTM + Self-Attention.
- **Expected Parameters**: ~2M.
- **Training Data**: MAVEN, MAVEN-ARG, DELPHI-specific annotations.
- **Evaluation Metrics**: Precision, recall, F1-score, span F1.

## 3. CausalSeq
- **Purpose**: Generates structured future-event/scenario predictions based on event histories.
- **Inputs**: Event histories/chains.
- **Outputs**: Structured scenarios (probability-weighted).
- **Architecture**: Encoder-Decoder LSTM + Bahdanau Attention.
- **Expected Parameters**: ~5M.
- **Training Data**: MAVEN-ERE, GDELT event sequences, ICEWS historical events.
- **Evaluation Metrics**: Scenario generation accuracy, historical analogue correctness.

## 4. CredNet
- **Purpose**: Estimates the source credibility of news and events.
- **Inputs**: 12 numerical source/article features.
- **Outputs**: Credibility score (0 to 1), confidence.
- **Architecture**: MLP (12 -> 32 -> 16 -> 1).
- **Training Data**: NELA-GT + DELPHI-specific source labels.
- **Evaluation Metrics**: Macro F1, ROC-AUC, Calibration, Brier Score.
