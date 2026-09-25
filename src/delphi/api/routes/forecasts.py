from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/forecasts/{forecast_id}")
def get_forecast(forecast_id: str):
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
