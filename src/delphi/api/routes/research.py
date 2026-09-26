from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from delphi.api.schemas.requests import AnalysisRequest
from delphi.api.dependencies import get_orchestrator
from delphi.api.services.persistence import get_db, ResearchRunRecord, ResearchDocumentRecord
from delphi.research.schemas import ResearchReport
from datetime import datetime, timezone
import json

research_router = APIRouter()

@research_router.post("", response_model=ResearchReport)
def run_standalone_research(
    request: AnalysisRequest,
    req: Request,
    orchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db)
):
    """
    Run the Live Research Engine standalone without the full forecast pipeline.
    """
    current_event = orchestrator.event_extractor.extract(request)
    
    report = orchestrator.research_engine.run_research(
        current_event, 
        request.prediction_information_cutoff
    )
    
    # Save ResearchRun
    run_rec = ResearchRunRecord(
        run_id=report.run_id,
        started_at=datetime.now(timezone.utc).isoformat(),
        completed_at=datetime.now(timezone.utc).isoformat(),
        cutoff=request.prediction_information_cutoff,
        status=report.status,
        provider_metadata={"providers_used": report.providers_used}
    )
    db.add(run_rec)
    db.commit()
    
    return report
