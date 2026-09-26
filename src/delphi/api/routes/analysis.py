from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from delphi.api.schemas.requests import AnalysisRequest
from delphi.api.schemas.responses import APIForecastReport, APIScenario, APIProvenance
from delphi.api.dependencies import get_orchestrator, get_registry
from delphi.api.schemas.errors import TemporalLeakageError
from delphi.forecast.orchestrator import ForecastOrchestrator
from delphi.forecast import ForecastRequest
from delphi.api.services.persistence import (
    get_db, AnalysisRun, ForecastRecord, ScenarioRecord, EvidenceRecord
)
import json
from datetime import datetime

analysis_router = APIRouter()

@analysis_router.post("", response_model=APIForecastReport)
def analyze(
    request: AnalysisRequest,
    req: Request,
    idempotency_key: str | None = Header(alias="Idempotency-Key", default=None),
    orchestrator: ForecastOrchestrator = Depends(get_orchestrator),
    registry = Depends(get_registry),
    db: Session = Depends(get_db)
):
    try:
        req_id = getattr(req.state, "request_id", "unknown")
        
        # Idempotency Check
        if idempotency_key:
            existing_run = db.query(AnalysisRun).filter(AnalysisRun.idempotency_key == idempotency_key).first()
            if existing_run and existing_run.status == "SUCCESS":
                existing_record = db.query(ForecastRecord).filter(ForecastRecord.analysis_run_id == existing_run.id).first()
                if existing_record and existing_record.forecast_payload:
                    return APIForecastReport(**existing_record.forecast_payload)
                    
        # Validate temporal constraints
        pub_time = datetime.fromisoformat(request.publication_timestamp.replace("Z", "+00:00"))
        cutoff_time = datetime.fromisoformat(request.prediction_information_cutoff.replace("Z", "+00:00"))
        
        if pub_time > cutoff_time:
            raise TemporalLeakageError("Publication timestamp cannot be after prediction cutoff.")
            
        forecast_req = ForecastRequest(
            article_text=request.text,
            publication_timestamp=request.publication_timestamp,
            prediction_information_cutoff=request.prediction_information_cutoff,
            domain=request.domain,
            requested_forecast_horizon=f"{request.forecast_horizon} days"
        )
        
        report = orchestrator.generate_forecast(forecast_req)
        
        # Map scenarios
        scenarios = []
        for s in report.candidate_scenarios:
            scenarios.append(APIScenario(
                scenario_id=s.scenario_id,
                trajectory=[ev if isinstance(ev, dict) else ev.model_dump() for ev in s.trajectory],
                raw_score=s.raw_scenario_score,
                normalized_weight=report.scenario_probabilities.get(s.scenario_id, 0.0),
                probability=report.scenario_probabilities.get(s.scenario_id, 0.0)
            ))
            
        prov = APIProvenance(
            prediction_cutoff=report.provenance.prediction_cutoff,
            tokenizer_version=report.provenance.tokenizer_version,
            eventembed_version=report.provenance.eventembed_version,
            eventnet_version=report.provenance.eventnet_version,
            crednet_version=report.provenance.crednet_version,
            causalseq_version=report.provenance.causalseq_version,
            retrieval_index_version=report.provenance.retrieval_index_version,
            calibration_version=report.provenance.calibration_version,
            dataset_version=report.provenance.dataset_manifest_version,
            checkpoint_training_bounds={"eventnet": report.provenance.eventnet_training_end},
            temporal_validation_status=report.temporal_safety_status
        )
            
        api_report = APIForecastReport(
            current_event=report.current_event if isinstance(report.current_event, dict) else report.current_event.model_dump(),
            credibility_assessment=report.credibility_assessment if isinstance(report.credibility_assessment, dict) else report.credibility_assessment.model_dump(),
            historical_analogues=[h if isinstance(h, dict) else h.model_dump() for h in report.historical_analogues],
            scenarios=scenarios,
            indicators=[i.indicator_id for i in report.indicators_to_watch],
            evidence=[e if isinstance(e, dict) else e.model_dump() for e in report.supporting_evidence + report.contradictory_evidence],
            calibration_status=report.confidence_metadata.calibration_status,
            provenance=prov,
            limitations=report.limitations
        )
        
        # Transaction Persistence
        run_record = AnalysisRun(
            request_id=req_id,
            idempotency_key=idempotency_key,
            prediction_cutoff=request.prediction_information_cutoff,
            publication_timestamp=request.publication_timestamp,
            domain=request.domain,
            status="SUCCESS",
            model_versions=prov.model_dump(),
            temporal_status=report.temporal_safety_status
        )
        db.add(run_record)
        db.flush() # Get run_record.id
        
        forecast_rec = ForecastRecord(
            analysis_run_id=run_record.id,
            forecast_payload=api_report.model_dump(mode='json'),
            calibration_status=report.confidence_metadata.calibration_status,
            temporal_status=report.temporal_safety_status,
            provenance=prov.model_dump()
        )
        db.add(forecast_rec)
        
        for s in report.candidate_scenarios:
            db.add(ScenarioRecord(
                analysis_run_id=run_record.id,
                scenario_id=s.scenario_id,
                raw_score=s.raw_scenario_score,
                normalized_weight=report.scenario_probabilities.get(s.scenario_id, 0.0),
                probability=report.scenario_probabilities.get(s.scenario_id, 0.0),
                trajectory_payload=[ev if isinstance(ev, dict) else ev.model_dump() for ev in s.trajectory]
            ))
            
        for ev in (report.supporting_evidence + report.contradictory_evidence):
            ev_dict = ev if isinstance(ev, dict) else ev.model_dump()
            db.add(EvidenceRecord(
                analysis_run_id=run_record.id,
                evidence_id=ev_dict.get('source_id', 'unknown'),
                direction=ev_dict.get('direction', 'unknown'),
                source_id=ev_dict.get('source_id', 'unknown'),
                timestamp=ev_dict.get('timestamp', 'unknown'),
                evidence_payload=ev_dict
            ))
            
        db.commit()
        return api_report
        
    except ValueError as e:
        db.rollback()
        if "future" in str(e).lower() or "temporal" in str(e).lower():
            raise TemporalLeakageError(str(e))
        raise e
    except Exception as e:
        db.rollback()
        raise e
