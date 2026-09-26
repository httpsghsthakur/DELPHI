import sys
import os
import json

sys.path.insert(0, 'c:/Users/gt643/Downloads/DELPHI/src')
sys.path.insert(0, 'c:/Users/gt643/Downloads/DELPHI')

os.environ['DELPHI_EXECUTION_MODE'] = 'REAL'
os.environ['DELPHI_MODELS_DIR'] = 'models'
os.environ['DELPHI_INDEXES_DIR'] = 'indexes'

from delphi.api.dependencies import get_orchestrator
from delphi.forecast.schemas import ForecastRequest

def run_backtest():
    print("Initializing REAL ForecastOrchestrator...")
    orchestrator = get_orchestrator()
    print("Initialization complete.")
    
    events = [
        {
            "text": "Tensions mount as border disputes continue between the neighboring nations.",
            "pub_date": "2023-05-10T12:00:00Z",
            "domain": "geopolitics"
        },
        {
            "text": "A new trade agreement was signed today boosting economic cooperation.",
            "pub_date": "2023-06-15T09:30:00Z",
            "domain": "economics"
        }
    ]
    
    for i, evt in enumerate(events):
        print(f"\n--- Backtest Step {i+1} ---")
        req = ForecastRequest(
            article_text=evt["text"],
            domain=evt["domain"],
            publication_timestamp=evt["pub_date"],
            prediction_information_cutoff='2027-01-01T00:00:00Z', # After training end time
            requested_forecast_horizon='30d'
        )
        
        report = orchestrator.generate_forecast(req)
        print(f"Status: {report.forecast_status}")
        print(f"Scenarios Generated: {len(report.candidate_scenarios)}")
        for idx, s in enumerate(report.candidate_scenarios):
            event_type = s.trajectory[0]["event_type"] if s.trajectory else "UNKNOWN"
            prob = report.scenario_probabilities.get(s.scenario_id, 0.0)
            print(f"  [{idx+1}] Scenario ID: {s.scenario_id}, Event Type: {event_type}, Probability: {prob:.4f}")
        print(f"Provenance prediction cutoff: {report.provenance.prediction_cutoff}")

if __name__ == '__main__':
    run_backtest()
