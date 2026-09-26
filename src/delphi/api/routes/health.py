from fastapi import APIRouter, Depends
from datetime import datetime
from delphi.api.schemas.responses import APIHealthResponse, APIModelStatus
from delphi.api.dependencies import get_registry
from delphi.api.config import settings

health_router = APIRouter()
models_router = APIRouter()

@health_router.get("/live", response_model=APIHealthResponse)
def health_live():
    return APIHealthResponse(
        status="ok",
        api_version=settings.version,
        models_loaded=False,
        temporal_mode="strict" if settings.strict_temporal_mode else "relaxed",
        execution_mode="UNKNOWN",
        dependencies={}
    )

@health_router.get("/ready", response_model=APIHealthResponse)
def health_ready(registry = Depends(get_registry)):
    try:
        from delphi.api.services.persistence import get_db
        db_gen = get_db()
        db = next(db_gen)
        db_status = "ok"
    except Exception:
        db_status = "error"
        
    status_data = registry.get_status()
    execution_mode = "SYNTHETIC" if "dummy" in status_data.get("eventembed_version", "").lower() or status_data.get("eventembed_version") == "v1" else "REAL"
    
    deps = {
        "tokenizer": "ok" if status_data.get("tokenizer_version") else "missing",
        "eventembed": "ok" if status_data.get("eventembed_version") else "missing",
        "eventnet": "ok" if status_data.get("eventnet_version") else "missing",
        "crednet": "ok" if status_data.get("crednet_version") else "missing",
        "causalseq": "ok" if status_data.get("causalseq_version") else "missing",
        "retrieval_index": "ok" if status_data.get("retrieval_index_version") else "missing",
        "calibration": "ok" if status_data.get("calibration_version") else "missing",
        "database": db_status
    }
    
    is_ready = all(v == "ok" for v in deps.values())
    
    return APIHealthResponse(
        status="ok" if is_ready else "error",
        api_version=settings.version,
        models_loaded=registry.is_loaded,
        temporal_mode="strict" if settings.strict_temporal_mode else "relaxed",
        execution_mode=execution_mode,
        dependencies=deps
    )

@health_router.get("", response_model=APIHealthResponse)
def health(registry = Depends(get_registry)):
    return health_ready(registry)

@models_router.get("", response_model=APIModelStatus)
def get_models_status(registry = Depends(get_registry)):
    return APIModelStatus(**registry.get_status())
