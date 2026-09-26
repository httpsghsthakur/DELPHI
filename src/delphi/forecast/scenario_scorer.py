from typing import List
from .schemas import ScenarioCandidate
from .config import ForecastConfig

class ScenarioScorer:
    def __init__(self, config: ForecastConfig):
        self.config = config
        
    def score_scenarios(self, scenarios: List[ScenarioCandidate]) -> List[ScenarioCandidate]:
        """
        Calculates the raw_scenario_score using a deterministic weighted combination
        of available evidence scores.
        """
        for scen in scenarios:
            # Simple linear combination for orchestration purposes
            raw_score = (
                self.config.weight_sequence_score * scen.sequence_score +
                self.config.weight_historical_support * scen.historical_support_score +
                self.config.weight_credibility * scen.evidence_score +
                self.config.weight_model_confidence * scen.model_support_score
            )
            scen.raw_scenario_score = raw_score
            
        return scenarios
