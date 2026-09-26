from typing import List
from .schemas import ConfidenceAssessment, ScenarioCandidate
from .config import ForecastConfig

class ConfidenceEvaluator:
    def __init__(self, config: ForecastConfig):
        self.config = config
        
    def assess_confidence(self, scenarios: List[ScenarioCandidate], calibration_status: str) -> ConfidenceAssessment:
        if not scenarios:
            return ConfidenceAssessment(
                confidence_status="insufficient_evidence",
                calibration_status=calibration_status,
                historical_evaluation_quality=0.0,
                evidence_coverage=0.0,
                model_agreement=0.0,
                scenario_separation=0.0
            )
            
        # Example metrics representing data completeness and separation
        # In a fully implemented system, these would pull from backtest results
        
        # Calculate separation (difference between top 2 scenario scores if multiple exist)
        separation = 0.0
        if len(scenarios) > 1:
            separation = scenarios[0].raw_scenario_score - scenarios[1].raw_scenario_score
            
        evidence_coverage = min(1.0, len(scenarios[0].supporting_evidence) / 5.0)
        
        status = "sufficient" if evidence_coverage > 0.2 else "insufficient_evidence"
        
        return ConfidenceAssessment(
            confidence_status=status,
            calibration_status=calibration_status,
            historical_evaluation_quality=0.5, # Placeholder for architecture valid
            evidence_coverage=evidence_coverage,
            model_agreement=0.8,
            scenario_separation=separation
        )
