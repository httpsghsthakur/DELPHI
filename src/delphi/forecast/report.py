from typing import List
from .schemas import ForecastReport

class ReportGenerator:
    @staticmethod
    def generate_markdown(report: ForecastReport) -> str:
        md = []
        md.append("# DELPHI FORECAST\n")
        
        md.append("## Current Event")
        md.append(f"Event ID: {report.current_event.get('event_id')}")
        md.append(f"Type: {report.current_event.get('event_type')}\n")
        
        md.append("## Credibility Assessment")
        md.append(f"Score: {report.credibility_assessment.get('credibility_score', 'N/A')}\n")
        
        md.append("## Historical Evidence")
        for i, h in enumerate(report.historical_analogues):
            md.append(f"### Analogue {i+1}")
            md.append(f"ID: {h.get('event_id')}")
            md.append(f"Match Score: {h.get('match_score')}")
        md.append("")
        
        md.append("## Scenarios")
        for s in report.candidate_scenarios:
            md.append(f"### {s.title}")
            md.append(f"ID: {s.scenario_id}")
            prob = report.scenario_probabilities.get(s.scenario_id, 0.0)
            md.append(f"Probability: {prob:.4f}")
            md.append(f"Trajectory Length: {len(s.trajectory)}")
        md.append("")
        
        md.append("## Probability Status")
        md.append(f"{report.forecast_status}\n")
        
        md.append("## Indicators to Watch")
        for ind in report.indicators_to_watch:
            md.append(f"- [{ind.scenario_linkage}] {ind.description} ({ind.time_window})")
        md.append("")
        
        md.append("## Supporting Evidence")
        for e in report.supporting_evidence:
            md.append(f"- {e.source_id} ({e.timestamp})")
        md.append("")
            
        md.append("## Contradictory Evidence")
        for e in report.contradictory_evidence:
            md.append(f"- {e.source_id} ({e.timestamp})")
        md.append("")
        
        md.append("## Model / Dataset Provenance")
        md.append(f"Prediction Cutoff: {report.provenance.prediction_cutoff}")
        md.append(f"Checkpoint End Time: {report.provenance.checkpoint_training_end_time}\n")
        
        md.append("## Temporal Safety")
        md.append(f"{report.temporal_safety_status}\n")
        
        md.append("## Known Limitations")
        for lim in report.limitations:
            md.append(f"- {lim}")
            
        return "\n".join(md)
