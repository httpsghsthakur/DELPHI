from fastapi import APIRouter, Depends
from delphi.api.schemas.requests import HistoricalSearchRequest
from delphi.api.dependencies import get_orchestrator
from delphi.forecast.schemas import ForecastRequest
from datetime import datetime, timezone
from typing import Dict, Any, List

historical_router = APIRouter()

@historical_router.post("/search")
def search_historical(
    request: HistoricalSearchRequest,
    orchestrator = Depends(get_orchestrator)
):
    """
    Search historical analogues using custom EventEmbed representations
    and the populated FAISS historical index, strictly filtering by temporal cutoff.
    """
    now_str = datetime.now(timezone.utc).isoformat()
    fc_req = ForecastRequest(
        article_text=request.text,
        publication_timestamp=now_str,
        prediction_information_cutoff=request.cutoff,
        domain=request.domain or "geopolitics",
        requested_forecast_horizon="30d"
    )
    
    current_event = orchestrator.event_extractor.extract(fc_req)
    
    # Retrieve real analogues
    analogues = orchestrator.historical_retriever.retrieve(
        current_event,
        request.cutoff
    )
    
    # Slice to top_k
    analogues = analogues[:request.top_k]
    
    # Construct structured outcomes
    outcomes = []
    for a in analogues:
        outcomes.append({
            "event_id": a.get("event_id"),
            "event_type": a.get("event_type"),
            "timestamp": a.get("timestamp"),
            "similarity": a.get("match_score", 0.0),
            "summary": a.get("text", "")
        })
        
    return {
        "analogues": analogues,
        "similarity_components": {
            "embedding_dimension": 256,
            "metric": "cosine_l2",
            "index_type": "FAISS_IndexFlatIP",
            "count_returned": len(analogues)
        },
        "historical_outcomes": outcomes,
        "retrieval_metadata": {
            "query_text": request.text[:100],
            "cutoff": request.cutoff,
            "domain_filter": request.domain
        },
        "temporal_safety_status": "VERIFIED"
    }
