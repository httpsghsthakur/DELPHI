from fastapi import APIRouter
from delphi.api.routes.analysis import analyze

forecasts_router = APIRouter()

from delphi.api.schemas.responses import APIForecastReport

# Alias to the analysis endpoint
@forecasts_router.post("", response_model=APIForecastReport)
def create_forecast(*args, **kwargs):
    return analyze(*args, **kwargs)
