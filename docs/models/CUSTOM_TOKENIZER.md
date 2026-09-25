# CUSTOM TOKENIZER

## Why a Custom Tokenizer?
DELPHI requires precise control over tokenization to preserve information critical for geopolitical, economic, and trade forecasting. Pre-trained subword tokenizers (like WordPiece or BPE from BERT/LLMs) frequently shred important entities like "US-China", specific dates (e.g. "2026-09-25"), or numerical thresholds (e.g. "40%", "$5.2B") into meaningless fragments, reducing the efficacy of temporal reasoning.

## Design
The DELPHI tokenizer is a deterministic word-oriented tokenizer coupled with fixed special token IDs.
- **Normalization**: Handles Unicode standardizing, whitespace squashing, URL mapping, and Email mapping.
- **Pre-tokenization**: Employs an intelligent regex to preserve dates, hyphenated words, percentages, currencies, and HTML-like tags (`<ACTOR>`).
- **Vocabulary**: Frequency-based with a deterministic lexicographical tie-breaker. Unknown words map to `<UNK>`.

## Numerical and Date Handling
Rather than immediately mapping all numbers to `<NUM>`, the tokenizer attempts to preserve percentages, currencies, and dates intact. Future revisions will allow mapping these into specific metadata channels.

## Special Tokens
```text
<PAD>, <UNK>, <BOS>, <EOS>, <SEP>, <MASK>, <NUM>, <DATE>, <URL>, <EMAIL>, <PERCENT>, <CURRENCY>, <ACTOR>, </ACTOR>, <ACTION>, </ACTION>, <TARGET>, </TARGET>, <LOCATION>, </LOCATION>, <TIME>, </TIME>, <CAUSE>, </CAUSE>, <EVENT>, </EVENT>, <CAUSE_EVENT>, </CAUSE_EVENT>, <OUTCOME_EVENT>, </OUTCOME_EVENT>, <SCENARIO>, </SCENARIO>
```

## Serialization and Versioning
Tokenizers are serialized to JSON with a `vocabulary.json`, `config.json`, and `metadata.json` containing SHA-256 checksums to guarantee artifact equivalence across distributed training runs.

## Limitations
- A purely word-based vocabulary can suffer from high OOV (out-of-vocabulary) rates on morphologically rich or highly noisy text. We rely on the future EventEmbed character-level CNN to learn robust representations for `<UNK>` tokens.
