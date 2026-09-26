from pydantic import BaseModel

class ForecastConfig(BaseModel):
    max_scenarios: int = 3
    indicator_horizon_days: int = 30
    probability_tolerance: float = 1e-4
    strict_temporal_mode: bool = True
    provenance_required: bool = True
    
    # Weights for Scenario Scoring
    weight_sequence_score: float = 1.0
    weight_historical_support: float = 1.5
    weight_credibility: float = 0.5
    weight_model_confidence: float = 1.0
    
    # CausalSeq parameters
    beam_width: int = 3
    max_forecast_steps: int = 5
