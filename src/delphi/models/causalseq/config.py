import json
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class CausalSeqConfig:
    # Dimensions
    input_dim: int = 256 # EventEmbed dim
    hidden_dim: int = 256
    encoder_layers: int = 1
    decoder_layers: int = 1
    dropout: float = 0.1
    bidirectional_encoder: bool = True
    
    # Vocabularies
    num_event_types: int = 100
    num_actors: int = 500
    num_targets: int = 500
    num_time_bins: int = 9 # hours, 1d, 3d, 7d, 14d, 30d, 90d, 180d, 365+d
    num_domains: int = 20
    
    # Generation bounds
    max_context_length: int = 30
    max_forecast_length: int = 10
    
    # Training
    teacher_forcing_ratio: float = 0.5
    beam_width: int = 3
    learning_rate: float = 1e-3
    gradient_clipping: float = 1.0
    
    # Loss Weights
    lambda_event_type: float = 1.0
    lambda_time: float = 1.0
    lambda_actor: float = 0.5
    lambda_target: float = 0.5
    lambda_domain: float = 0.2
    
    # Versions and Provenance
    eventembed_version: str = "v1"
    schema_version: str = "v1"
    checkpoint_training_end_time: str = "" # Temporal provenance bound

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CausalSeqConfig":
        return cls(**data)
        
    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
            
    @classmethod
    def load(cls, path: str) -> "CausalSeqConfig":
        with open(path, "r") as f:
            return cls.from_dict(json.load(f))
