from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/historical/{event_id}")
def get_historical_matches(event_id: str):
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
