from typing import Dict, Any, List
from datetime import datetime

from .schemas import ForecastRequest, ForecastReport, Provenance
from .config import ForecastConfig
from .scenario_builder import ScenarioBuilder
from .scenario_scorer import ScenarioScorer
from .calibration import ProbabilityCalibrator
from .indicators import IndicatorDetector
from .evidence import EvidenceRegistry
from .confidence import ConfidenceEvaluator
from .validation import ForecastValidator

class ForecastOrchestrator:
    def __init__(self, config: ForecastConfig):
        self.config = config
        self.scenario_builder = ScenarioBuilder(config)
        self.scenario_scorer = ScenarioScorer(config)
        self.calibrator = ProbabilityCalibrator(config)
        self.indicator_detector = IndicatorDetector(config)
        self.confidence_evaluator = ConfidenceEvaluator(config)
        
        # Mock dependencies for architectural validation
        # In a full deployment, these would be injected implementations of Layers 1-7
        self.event_extractor = None
        self.crednet_model = None
        self.historical_retriever = None
        self.causalseq_model = None
        
    def generate_forecast(self, request: ForecastRequest) -> ForecastReport:
        # 1. Evidence Registry
        evidence_registry = EvidenceRegistry()
        
        # 2. Extract Event (Mock)
        current_event = {
            "event_id": request.article_id or "E_NEW",
            "event_type": 1,
            "timestamp": request.publication_timestamp
        }
        
        # 3. CredNet (Mock)
        credibility = {
            "credibility_score": 0.75,
            "calibrated_score": 0.72,
            "model_version": "v1"
        }
        
        # 4. Historical Intelligence (Mock)
        historical_analogues = [
            {"event_id": "H_1", "match_score": 0.85, "timestamp": "2020-01-01T00:00"}
        ]
        
        # 5. CausalSeq Generation (Mock)
        # Sequence of structural events
        raw_trajectories = [
            {"trajectory": [{"event_type": 2, "time_bin": 1, "actor": 1, "target": 2, "domain": 1}], "sequence_score": -0.5},
            {"trajectory": [{"event_type": 3, "time_bin": 2, "actor": 1, "target": 3, "domain": 1}], "sequence_score": -1.2}
        ]
        
        # 6. Scenario Construction & Deduplication
        scenarios = self.scenario_builder.build_scenarios(raw_trajectories)
        
        # 7. Scenario Scoring
        scenarios = self.scenario_scorer.score_scenarios(scenarios)
        
        # 8. Probability Calibration
        probs, cal_status = self.calibrator.calibrate(scenarios)
        
        # 9. Confidence
        confidence = self.confidence_evaluator.assess_confidence(scenarios, cal_status)
        
        # 10. Indicators
        indicators = self.indicator_detector.generate_indicators(scenarios)
        
        # 11. Provenance
        prov = Provenance(
            prediction_cutoff=request.prediction_information_cutoff,
            checkpoint_training_end_time="2025-01-01T00:00Z"
        )
        
        report = ForecastReport(
            request_metadata=request,
            current_event=current_event,
            credibility_assessment=credibility,
            historical_analogues=historical_analogues,
            observed_historical_outcomes=[],
            candidate_scenarios=scenarios,
            scenario_probabilities=probs,
            indicators_to_watch=indicators,
            supporting_evidence=evidence_registry.get_supporting(),
            contradictory_evidence=evidence_registry.get_contradictory(),
            confidence_metadata=confidence,
            provenance=prov,
            temporal_safety_status="VALID" if evidence_registry.validate_cutoff(request.prediction_information_cutoff) else "INVALID",
            limitations=["Discrete time bins", "Uncalibrated models in research mode"],
            forecast_status=cal_status
        )
        
        # 12. Validation
        if self.config.strict_temporal_mode:
            ForecastValidator.validate(report)
            
        return report
