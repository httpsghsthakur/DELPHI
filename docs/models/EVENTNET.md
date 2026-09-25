# EVENTNET

## Purpose
EventNet is the primary contextual sequence-tagging and event classification model for DELPHI. It consumes the rich domain-aware dense representations from EventEmbed and predicts structured geopolitical events consisting of triggers, actors, actions, targets, times, locations, and causes.

## Architecture
EventNet consists of:
- **Input**: `[B, T, 256]` dense representations from EventEmbed.
- **BiLSTM**: A bidirectional LSTM layer allowing context to propagate forward and backward across the time steps. (Default: 128 hidden units × 2 = 256 output units).
- **Self-Attention**: A Multi-Head Self-Attention layer allowing global context integration across the entire sequence.
- **Token Classification Head**: A linear projection mapping contextual tokens to BIO space for argument extraction.
- **Event Classification Head**: A masked mean-pooling followed by a linear projection mapping the entire sequence to an Event Type space.

The expected parameter count for the EventNet architecture is around **~2 million** parameters.

## Loss and Optimization
- **Multi-task Loss**: Total loss is a combination of token classification cross-entropy and event classification cross-entropy, weighted by a `lambda_event` scalar.
- **Masking**: Padded token inputs (`<PAD>`) are aggressively ignored both via the Self-Attention mask (set to `-inf` prior to softmax) and during Event Classification pooling, guaranteeing temporal stability. Padding is also ignored in the token cross-entropy loss via `ignore_index`.

## Evaluation
Due to class imbalance resulting from excessive `O` tags, EventNet relies on Macro F1, Micro F1, and Span-level F1 rather than raw classification accuracy for its performance metrics. Event-level accuracy and Macro F1 evaluate the `Event Classification Head`.

## Training Modes
1. **Frozen Mode (Default)**: EventEmbed's gradients are disabled. EventNet trains in isolation using deterministic, pre-computed input features.
2. **Trainable Mode (Joint Fine-Tuning)**: EventEmbed gradients are enabled, fine-tuning word embeddings and morphological filters jointly against the supervised event labels.

## Data Alignment
Token alignments strictly follow the boundaries defined by the CustomTokenizer. Event span offsets outputted by `decode_predictions` map exactly back to the source text strings.
