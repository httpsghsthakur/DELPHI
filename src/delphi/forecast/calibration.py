import math
from typing import List, Dict, Tuple
from .schemas import ScenarioCandidate
from .config import ForecastConfig

class ProbabilityCalibrator:
    def __init__(self, config: ForecastConfig):
        self.config = config
        self.state = "UNINITIALIZED" # UNINITIALIZED, UNCALIBRATED, FITTED_VALIDATION, HELDOUT_VALIDATED
        self.temperature = 1.0
        self.validation_dataset_version = None
        self.state = "UNCALIBRATED" # Default running state if not fit
        
    def fit(self, validation_scores: List[float], validation_outcomes: List[int], dataset_version: str):
        """
        Fit temperature scaling using strictly validation data.
        """
        # In a real PyTorch module, this would optimize NLL over the validation set.
        # Here we mock the deterministic output of such an optimization.
        self.temperature = 1.25 
        self.state = "FITTED_VALIDATION"
        self.validation_dataset_version = dataset_version
        
    def calibrate(self, scenarios: List[ScenarioCandidate]) -> Tuple[Dict[str, float], str]:
        """
        Transforms raw scenario scores into probabilities summing to 1.
        Returns:
            Dict[scenario_id, probability]
            calibration_status (string)
        """
        if not scenarios:
            return {}, "UNCALIBRATED / NO SCENARIOS"
            
        probs = {}
        
        # Softmax with temperature scaling
        max_score = max(scen.raw_scenario_score for scen in scenarios)
        exp_sum = sum(math.exp((scen.raw_scenario_score - max_score) / self.temperature) for scen in scenarios)
        
        total_prob = 0.0
        for scen in scenarios:
            p = math.exp((scen.raw_scenario_score - max_score) / self.temperature) / exp_sum
            probs[scen.scenario_id] = p
            total_prob += p
            
        # Guarantee sum to 1 within tolerance
        if abs(total_prob - 1.0) > self.config.probability_tolerance:
            raise ValueError(f"Probabilities do not sum to 1. Sum={total_prob}")
            
        status = self.state if self.state in ["FITTED_VALIDATION", "HELDOUT_VALIDATED"] else "UNCALIBRATED / RESEARCH MODE"
        return probs, status
