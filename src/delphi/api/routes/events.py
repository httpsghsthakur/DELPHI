from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/events")
def create_event():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@router.get("/events/{event_id}")
def get_event(event_id: str):
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
