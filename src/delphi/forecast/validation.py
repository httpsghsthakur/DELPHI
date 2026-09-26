from typing import List, Dict, Any
from .schemas import ForecastReport

class ForecastValidator:
    @staticmethod
    def validate(report: ForecastReport):
        # 1. Probabilities sum to 1
        total_prob = sum(report.scenario_probabilities.values())
        if report.scenario_probabilities and abs(total_prob - 1.0) > 1e-4:
            raise ValueError(f"Scenario probabilities do not sum to 1.0: {total_prob}")
            
        # 2. Scenario IDs unique
        ids = [s.scenario_id for s in report.candidate_scenarios]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate scenario IDs found")
            
        # 3. Provenance exists
        if not report.provenance.prediction_cutoff:
            raise ValueError("Prediction cutoff missing from provenance")
            
        # 4. Strict temporal mode: check checkpoint and evidence
        cutoff = report.provenance.prediction_cutoff
        prov_time = report.provenance.checkpoint_training_end_time
        if prov_time and prov_time > cutoff:
            raise ValueError(f"Temporal Leakage: checkpoint {prov_time} > cutoff {cutoff}")
            
        for ev in report.supporting_evidence + report.contradictory_evidence:
            if ev.timestamp > cutoff:
                raise ValueError(f"Temporal Leakage: evidence timestamp {ev.timestamp} > cutoff {cutoff}")
                
        # 5. Indicators map to scenarios
        for ind in report.indicators_to_watch:
            if ind.scenario_linkage not in ids:
                raise ValueError(f"Indicator {ind.indicator_id} links to unknown scenario {ind.scenario_linkage}")
                
        return True
