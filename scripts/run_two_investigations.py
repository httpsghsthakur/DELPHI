import os
import sys
import json
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.abspath("src"))

from delphi.forecast.orchestrator import ForecastOrchestrator
from delphi.forecast.config import ForecastConfig
from delphi.forecast.schemas import ForecastRequest

def test_investigation(name: str, question: str, domain: str):
    print("=" * 80)
    print(f"RUNNING INVESTIGATION: {name}")
    print(f"Question: {question}")
    print("=" * 80)
    
    cfg = ForecastConfig()
    cfg.models_dir = "models"
    cfg.indexes_dir = "indexes"
    cfg.strict_temporal_mode = True
    
    orchestrator = ForecastOrchestrator(cfg)
    
    req = ForecastRequest(
        article_text=question,
        publication_timestamp="2026-09-20T00:00:00Z",
        prediction_information_cutoff="2026-12-31T00:00:00Z",
        domain=domain,
        requested_forecast_horizon="30d",
        live_research=True
    )
    
    start_time = datetime.now()
    report = orchestrator.generate_forecast(req)
    duration = (datetime.now() - start_time).total_seconds()
    
    print(f"\n[1] Analysis Completed in {duration:.2f} seconds")
    print(f"EventNet Extracted Event: {report.current_event.get('event_type_code', 'unknown')}")
    print(f"CredNet Credibility Score: {report.credibility_assessment.get('credibility_score', 'N/A')}")
    
    # Historical Analogues
    print(f"\n[2] FAISS Historical Analogues ({len(report.historical_analogues)} retrieved):")
    for idx, h in enumerate(report.historical_analogues[:3], 1):
        h_dict = h if isinstance(h, dict) else h.model_dump()
        print(f"  {idx}. Event {h_dict.get('event_id')} | Similarity: {h_dict.get('similarity_score', 0):.3f} | Code: {h_dict.get('event_type')}")
        
    # Research Dossier
    res = report.live_research_report
    if res:
        print(f"\n[3] Deep Research Audit:")
        print(f"  Executed Queries ({len(res.get('queries_executed', []))}): {res.get('queries_executed', [])[:3]}")
        print(f"  Providers Used: {res.get('providers_used', [])}")
        print(f"  Provider Statuses: {res.get('provider_statuses', {})}")
        print(f"  Documents Discovered: {res.get('documents_discovered', 0)} | Fetched: {res.get('documents_fetched', 0)}")
        print(f"  Independent Clusters: {res.get('source_clusters', 0)}")
        print(f"  Supporting Evidence Items: {len(report.supporting_evidence)}")
        print(f"  Contradictory Evidence Items: {len(report.contradictory_evidence)}")
        
    # CausalSeq Scenarios
    print(f"\n[4] CausalSeq Scenarios ({len(report.candidate_scenarios)} generated):")
    for s in report.candidate_scenarios:
        prob = report.scenario_probabilities.get(s.scenario_id, 0.0)
        traj_len = len(s.trajectory)
        print(f"  - {s.scenario_id}: Prob={prob:.2%} | RawScore={s.raw_scenario_score:.3f} | TrajectorySteps={traj_len}")
        
    # Intelligence Briefing
    intel = report.intelligence_report
    if intel:
        print(f"\n[5] Grounded Intelligence Briefing:")
        print(f"  Title: {intel.get('title')}")
        sections = [
            'executive_summary', 'background_and_context', 'current_developments',
            'evidence_and_sources', 'historical_comparisons', 'causal_analysis',
            'future_scenarios', 'risks_and_uncertainties', 'conclusion'
        ]
        total_words = 0
        for sec in sections:
            txt = intel.get(sec, "")
            wc = len(txt.split())
            total_words += wc
            print(f"  - Section '{sec}': {wc} words")
        print(f"  -> TOTAL BRIEFING WORDS: {total_words}")
        print(f"  -> Inline Sources Listed: {len(intel.get('sources_and_reading', []))}")
        
        print("\n--- SAMPLE EXTRACT (Executive Summary) ---")
        print(intel.get('executive_summary', '')[:500] + "...\n")
        print("--- SAMPLE EXTRACT (Current Developments) ---")
        print(intel.get('current_developments', '')[:500] + "...\n")
    else:
        print("\n[!] No intelligence report attached!")

if __name__ == "__main__":
    test_investigation(
        "A: Semiconductor Export Restriction",
        "A major country announces new restrictions on advanced semiconductor exports and lithography equipment",
        "economy"
    )
    print("\n\n")
    test_investigation(
        "B: Central Bank Unexpected Rate Hike",
        "A central bank unexpectedly raises its benchmark interest rate by 50 basis points to counter persistent inflation",
        "economy"
    )
