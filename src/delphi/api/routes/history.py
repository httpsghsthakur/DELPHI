from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from delphi.api.dependencies import get_orchestrator
from delphi.api.services.persistence import get_db, ForecastRecord
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import polars as pl
import os

history_router = APIRouter()

@history_router.get("/{event_id}")
def get_historical_matches(
    event_id: str,
    orchestrator = Depends(get_orchestrator),
    db: Session = Depends(get_db)
):
    """
    Get historical analogue matches for a specific event by querying the FAISS index.
    """
    # 1. Search in DB forecasts for this event
    matched_event = None
    forecasts = db.query(ForecastRecord).order_by(ForecastRecord.id.desc()).limit(100).all()
    for f in forecasts:
        payload = f.forecast_payload or {}
        curr_ev = payload.get("current_event") or {}
        if curr_ev.get("event_id") == event_id:
            matched_event = curr_ev
            break
            
    # 2. Search in historical parquet if not in active DB
    if not matched_event:
        parquet_path = "indexes/historical/metadata.parquet"
        if os.path.exists(parquet_path):
            try:
                df = pl.read_parquet(parquet_path)
                matched = df.filter(pl.col("event_id") == event_id)
                if len(matched) > 0:
                    row = matched.row(0, named=True)
                    text = str(row.get("text", ""))
                    from delphi.forecast.schemas import ForecastRequest
                    now_str = datetime.now(timezone.utc).isoformat()
                    fc_req = ForecastRequest(
                        article_text=text,
                        publication_timestamp=now_str,
                        prediction_information_cutoff=now_str,
                        domain="geopolitics",
                        requested_forecast_horizon="30d"
                    )
                    matched_event = orchestrator.event_extractor.extract(fc_req)
            except Exception:
                pass
                
    if not matched_event:
        raise HTTPException(status_code=404, detail=f"Event '{event_id}' not found")
        
    cutoff = matched_event.get("timestamp", datetime.now(timezone.utc).isoformat())
    analogues = orchestrator.historical_retriever.retrieve(matched_event, cutoff)
    
    return {
        "event_id": event_id,
        "cutoff": cutoff,
        "matches_count": len(analogues),
        "analogues": analogues
    }
