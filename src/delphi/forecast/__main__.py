import argparse
import sys
from delphi.forecast import ForecastConfig, ForecastOrchestrator, ForecastRequest, ReportGenerator

def main():
    parser = argparse.ArgumentParser(description="DELPHI Forecast CLI")
    parser.add_argument("command", choices=["analyze", "backtest", "validate", "inspect"])
    parser.add_argument("--article", type=str, default="Sample headline for testing.")
    parser.add_argument("--cutoff", type=str, default="2026-09-01T00:00Z")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        config = ForecastConfig()
        orchestrator = ForecastOrchestrator(config)
        
        req = ForecastRequest(
            article_text=args.article,
            publication_timestamp="2026-08-30T00:00Z",
            prediction_information_cutoff=args.cutoff,
            domain="geopolitics",
            requested_forecast_horizon="30 days"
        )
        
        report = orchestrator.generate_forecast(req)
        md = ReportGenerator.generate_markdown(report)
        print(md)
        print("\nDELPHI END-TO-END ARCHITECTURE VALIDATED — REAL TEMPORAL BACKTESTING AND CALIBRATED FORECASTING PENDING")
        
    elif args.command == "validate":
        print("SYNTHETIC END-TO-END VALIDATION")
        config = ForecastConfig()
        orchestrator = ForecastOrchestrator(config)
        
        req = ForecastRequest(
            article_text=args.article,
            publication_timestamp="2026-08-30T00:00Z",
            prediction_information_cutoff=args.cutoff,
            domain="geopolitics",
            requested_forecast_horizon="30 days"
        )
        report = orchestrator.generate_forecast(req)
        print(f"Validation successful. {len(report.candidate_scenarios)} scenarios generated.")
        
    elif args.command in ["backtest", "inspect"]:
        print(f"Command {args.command} is stubbed for end-to-end integration.")

if __name__ == "__main__":
    main()
