from pydantic import BaseModel
from typing import Optional

class BiLSTMConfig(BaseModel):
    hidden_size: int = 128
    num_layers: int = 1
    bidirectional: bool = True
    dropout: float = 0.1

class AttentionConfig(BaseModel):
    num_heads: int = 4
    dropout: float = 0.1

class LossConfig(BaseModel):
    use_class_weights: bool = True
    lambda_event: float = 1.0

class EventEmbedIntegrationConfig(BaseModel):
    mode: str = "frozen"  # "frozen" or "trainable"

class EventNetConfig(BaseModel):
    input_dim: int = 256  # Expected output dim of EventEmbed
    num_token_labels: int
    num_event_types: int
    bilstm: BiLSTMConfig = BiLSTMConfig()
    attention: AttentionConfig = AttentionConfig()
    loss: LossConfig = LossConfig()
    eventembed: EventEmbedIntegrationConfig = EventEmbedIntegrationConfig()
