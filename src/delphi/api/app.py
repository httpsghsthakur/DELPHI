from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from delphi.api.config import settings
from delphi.api.routes.health import health_router, models_router
from delphi.api.routes.analysis import analysis_router
from delphi.api.routes.forecasts import forecasts_router
from delphi.api.routes.historical import historical_router
from delphi.api.routes.backtests import backtests_router
from delphi.api.routes.research import research_router
from delphi.api.middleware.request_id import RequestIDMiddleware
from delphi.api.middleware.error_handler import custom_exception_handler
from delphi.api.schemas.errors import TemporalLeakageError, CheckpointIncompatibleError

from contextlib import asynccontextmanager
from delphi.api.services.persistence import init_db, create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(settings.database_url)
    # For local sqlite dev, auto-create tables. 
    # Production should use proper migrations.
    if settings.database_url.startswith("sqlite"):
        create_tables()
    yield

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="DELPHI Forecast API - Machine-Readable Intelligence",
        lifespan=lifespan,
    )

    # Middlewares
    app.add_middleware(RequestIDMiddleware)
    
    @app.middleware("http")
    async def limit_payload_size(request: Request, call_next):
        if request.headers.get("content-length"):
            if int(request.headers.get("content-length")) > settings.max_payload_length:
                return JSONResponse(status_code=413, content={"detail": "Payload too large"})
        return await call_next(request)
        
    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    if "*" in origins and not settings.debug:
        origins = ["http://localhost:3000"]
        
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Error handlers
    app.add_exception_handler(TemporalLeakageError, custom_exception_handler)
    app.add_exception_handler(CheckpointIncompatibleError, custom_exception_handler)
    app.add_exception_handler(Exception, custom_exception_handler)

    # Routes
    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(models_router, prefix="/models", tags=["models"])
    app.include_router(analysis_router, prefix="/analysis", tags=["analysis"])
    app.include_router(forecasts_router, prefix="/forecasts", tags=["forecasts"])
    app.include_router(historical_router, prefix="/historical", tags=["historical"])
    app.include_router(backtests_router, prefix="/backtests", tags=["backtests"])
    app.include_router(research_router, prefix="/research", tags=["research"])

    return app

app = create_app()
