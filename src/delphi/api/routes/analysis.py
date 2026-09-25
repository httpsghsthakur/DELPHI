from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/analysis")
def create_analysis():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@router.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")
