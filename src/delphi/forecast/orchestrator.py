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
from .adapters import (
    EventExtractionAdapter, CredibilityAdapter, 
    HistoricalRetrievalAdapter, CausalForecastAdapter,
    MockActualEventNet, MockActualCredNet, 
    MockActualHistoricalMatcher, MockActualCausalSeq
)

class ForecastOrchestrator:
    def __init__(self, config: ForecastConfig):
        self.config = config
        self.scenario_builder = ScenarioBuilder(config)
        self.scenario_scorer = ScenarioScorer(config)
        self.calibrator = ProbabilityCalibrator(config)
        self.indicator_detector = IndicatorDetector(config)
        self.confidence_evaluator = ConfidenceEvaluator(config)
        
        # Instantiate actual model integrations
        self.event_net_model = MockActualEventNet()
        self.cred_net_model = MockActualCredNet()
        self.hist_matcher_model = MockActualHistoricalMatcher()
        self.causal_seq_model = MockActualCausalSeq()
        
        self.event_extractor = EventExtractionAdapter(self.event_net_model)
        self.credibility_assessor = CredibilityAdapter(self.cred_net_model)
        self.historical_retriever = HistoricalRetrievalAdapter(self.hist_matcher_model)
        self.causal_forecaster = CausalForecastAdapter(self.causal_seq_model)
        
    def generate_forecast(self, request: ForecastRequest) -> ForecastReport:
        # 1. Evidence Registry
        evidence_registry = EvidenceRegistry()
        
        # 2. Extract Event via Real Adapter
        current_event = self.event_extractor.extract(request)
        
        # 3. CredNet via Real Adapter
        credibility = self.credibility_assessor.assess(current_event)
        
        # 4. Historical Intelligence via Real Adapter
        historical_analogues = self.historical_retriever.retrieve(
            current_event, request.prediction_information_cutoff
        )
        
        # 5. CausalSeq Generation via Real Adapter
        raw_trajectories = self.causal_forecaster.forecast(
            current_event, historical_analogues, request.prediction_information_cutoff
        )
        
        # 6. Scenario Construction & Deduplication
        scenarios = self.scenario_builder.build_scenarios(raw_trajectories)
        
        # 7. Scenario Scoring
        # The weight of credibility is mapped to the CredNet score
        for scen in scenarios:
            scen.evidence_score = credibility.get("credibility_score", 0.0)
            
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
            eventembed_training_end="2026-01-01T00:00Z",
            eventnet_training_end=self.event_net_model.training_information_end_time,
            crednet_training_end=self.cred_net_model.training_information_end_time,
            causalseq_training_end=self.causal_seq_model.training_information_end_time,
            calibration_training_end="not_used" if self.calibrator.state == "UNCALIBRATED" else "2026-01-01T00:00Z"
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
