from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from delphi.api.dependencies import get_orchestrator
from delphi.api.services.persistence import get_db, AnalysisRun, ForecastRecord
from sqlalchemy.orm import Session
import polars as pl
import os

events_router = APIRouter()

class EventCreateRequest(BaseModel):
    text: str = Field(..., description="Raw text describing the event")
    publication_timestamp: Optional[str] = None
    domain: Optional[str] = "geopolitics"
    source_id: Optional[str] = None

class EventResponse(BaseModel):
    event_id: str
    event_type: int
    event_type_code: str
    event_type_name: Optional[str] = None
    timestamp: str
    actors: List[Any] = Field(default_factory=list)
    targets: List[Any] = Field(default_factory=list)
    domain: int = 0
    embedding: List[float] = Field(default_factory=list)
    source_text: str = ""
    model_version: str = "v1"

@events_router.post("", response_model=Dict[str, Any])
def create_event(
    request: EventCreateRequest,
    orchestrator = Depends(get_orchestrator)
):
    """
    Extract structured event from raw text using custom EventNet and EventEmbed models.
    """
    from delphi.forecast.schemas import ForecastRequest
    from datetime import datetime, timezone

    now_str = datetime.now(timezone.utc).isoformat()
    pub_time = request.publication_timestamp or now_str

    fc_req = ForecastRequest(
        article_text=request.text,
        publication_timestamp=pub_time,
        prediction_information_cutoff=pub_time,
        domain=request.domain or "geopolitics",
        requested_forecast_horizon="30d",
        source_id=request.source_id
    )

    extracted = orchestrator.event_extractor.extract(fc_req)
    if isinstance(extracted, dict):
        return extracted
    return extracted.model_dump()

@events_router.get("/{event_id}", response_model=Dict[str, Any])
def get_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve structured event by ID from stored forecasts or historical index.
    """
    # 1. Check active database forecast records
    forecasts = db.query(ForecastRecord).order_by(ForecastRecord.id.desc()).limit(100).all()
    for f in forecasts:
        payload = f.forecast_payload or {}
        curr_ev = payload.get("current_event") or {}
        if curr_ev.get("event_id") == event_id:
            return curr_ev

    # 2. Check historical parquet index
    parquet_path = "indexes/historical/metadata.parquet"
    if os.path.exists(parquet_path):
        try:
            df = pl.read_parquet(parquet_path)
            matched = df.filter(pl.col("event_id") == event_id)
            if len(matched) > 0:
                row = matched.row(0, named=True)
                return {
                    "event_id": str(row.get("event_id")),
                    "event_type": int(row.get("event_type", 1)) if str(row.get("event_type", "")).isdigit() else 1,
                    "event_type_code": str(row.get("event_type", "CAMEO_010")),
                    "timestamp": str(row.get("event_date", "2024-01-01T00:00:00Z")),
                    "actors": [],
                    "targets": [],
                    "domain": 0,
                    "source_text": str(row.get("text", "")),
                    "model_version": "v1.0"
                }
        except Exception:
            pass

    raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found in active records or historical corpus")
