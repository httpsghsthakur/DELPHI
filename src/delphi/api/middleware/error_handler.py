from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from delphi.api.schemas.errors import APIError, TemporalLeakageError, CheckpointIncompatibleError

async def custom_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown")
    
    if isinstance(exc, TemporalLeakageError):
        error = APIError(
            error_code="TEMPORAL_LEAKAGE",
            message=str(exc),
            request_id=req_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        return JSONResponse(status_code=400, content=error.model_dump())
        
    if isinstance(exc, CheckpointIncompatibleError):
        error = APIError(
            error_code="CHECKPOINT_INCOMPATIBLE",
            message=str(exc),
            request_id=req_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        return JSONResponse(status_code=500, content=error.model_dump())
        
    import traceback
    traceback.print_exc()
    
    # Generic error
    error = APIError(
        error_code="INTERNAL_PIPELINE_ERROR",
        message=f"An unexpected error occurred in the DELPHI pipeline: {str(exc)}",
        request_id=req_id,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    return JSONResponse(status_code=500, content=error.model_dump())
