from pydantic import BaseModel
from typing import List

class FilterConfig(BaseModel):
    kernel_size: int
    channels: int

class CharacterConfig(BaseModel):
    embedding_dim: int = 32
    max_length: int = 32
    filters: List[FilterConfig] = [
        FilterConfig(kernel_size=3, channels=32),
        FilterConfig(kernel_size=4, channels=32),
        FilterConfig(kernel_size=5, channels=32),
    ]
    output_dim: int = 64

class FusionConfig(BaseModel):
    strategy: str = "concat_projection"

class EventEmbedConfig(BaseModel):
    vocab_size: int
    word_embedding_dim: int = 192
    output_dim: int = 256
    context_window: int = 5
    negative_samples: int = 5
    min_frequency: int = 2
    character: CharacterConfig = CharacterConfig()
    fusion: FusionConfig = FusionConfig()
