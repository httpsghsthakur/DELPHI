from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import time
from datetime import datetime, timezone
from delphi.api.services.persistence import get_db, BacktestRun
from delphi.api.config import settings

backtests_router = APIRouter()

class BacktestRequest(BaseModel):
    domain: str = "geopolitics"
    window_days: int = 7

class BacktestResponse(BaseModel):
    run_id: str
    status: str
    configuration: Dict[str, Any]
    created_at: str

class BacktestStatusResponse(BaseModel):
    run_id: str
    status: str
    metrics: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    completed_at: Optional[str] = None

def run_backtest_task(run_id: str, db_url: str):
    # This must run in a background thread and use its own DB session
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(db_url, connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        run = db.query(BacktestRun).filter(BacktestRun.run_id == run_id).first()
        if not run:
            return
            
        run.status = "RUNNING"
        db.commit()
        
        # Simulate backtest workload execution
        time.sleep(2)
        
        run.status = "COMPLETED"
        run.completed_at = datetime.now(timezone.utc)
        run.metrics = {"accuracy": 0.85}
        run.provenance = {"tokenizer_version": "v1"}
        db.commit()
    except Exception as e:
        db.rollback()
        run = db.query(BacktestRun).filter(BacktestRun.run_id == run_id).first()
        if run:
            run.status = "FAILED"
            run.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()

@backtests_router.post("", response_model=BacktestResponse)
def start_backtest(
    req: BacktestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    run_id = str(uuid.uuid4())
    config = req.model_dump()
    
    # Init queued state
    run = BacktestRun(
        run_id=run_id,
        status="QUEUED",
        configuration=config
    )
    db.add(run)
    db.commit()
    
    background_tasks.add_task(run_backtest_task, run_id, settings.database_url)
    
    return BacktestResponse(
        run_id=run_id,
        status="QUEUED",
        configuration=config,
        created_at=run.created_at.isoformat()
    )

@backtests_router.get("/{run_id}", response_model=BacktestStatusResponse)
def get_backtest(run_id: str, db: Session = Depends(get_db)):
    run = db.query(BacktestRun).filter(BacktestRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Backtest not found")
        
    return BacktestStatusResponse(
        run_id=run.run_id,
        status=run.status,
        metrics=run.metrics,
        provenance=run.provenance,
        completed_at=run.completed_at.isoformat() if run.completed_at else None
    )
