from fastapi import FastAPI

from delphi.api.routes import health, analysis, events, forecasts, history

app = FastAPI(title="DELPHI - Predictive Intelligence Engine")

app.include_router(health.router)
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(forecasts.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")
