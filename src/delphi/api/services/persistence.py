from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String, index=True)
    idempotency_key = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    prediction_cutoff = Column(String)
    publication_timestamp = Column(String)
    domain = Column(String)
    status = Column(String)
    model_versions = Column(JSON)
    temporal_status = Column(String)

class ForecastRecord(Base):
    __tablename__ = "forecast_records"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_run_id = Column(Integer, index=True)
    forecast_payload = Column(JSON)
    calibration_status = Column(String)
    temporal_status = Column(String)
    provenance = Column(JSON)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ScenarioRecord(Base):
    __tablename__ = "scenario_records"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_run_id = Column(Integer, index=True)
    scenario_id = Column(String)
    raw_score = Column(Float)
    normalized_weight = Column(Float)
    probability = Column(Float, nullable=True)
    trajectory_payload = Column(JSON)

class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_run_id = Column(Integer, index=True)
    evidence_id = Column(String)
    direction = Column(String)
    source_id = Column(String)
    timestamp = Column(String)
    evidence_payload = Column(JSON)

class BacktestRun(Base):
    __tablename__ = "backtest_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    status = Column(String)
    configuration = Column(JSON)
    result_payload = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    provenance = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

class ResearchRunRecord(Base):
    __tablename__ = "research_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    analysis_id = Column(String, index=True, nullable=True)
    started_at = Column(String)
    completed_at = Column(String)
    cutoff = Column(String)
    status = Column(String)
    provider_metadata = Column(JSON)

class ResearchDocumentRecord(Base):
    __tablename__ = "research_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True)
    research_run_id = Column(String, index=True)
    url = Column(String)
    source = Column(String)
    published_at = Column(String)
    retrieved_at = Column(String)
    checksum = Column(String)
    metadata_payload = Column(JSON) # To avoid storing raw text if not needed


# Engine and Session configuration
_engine = None
_SessionLocal = None

def init_db(database_url: str):
    global _engine, _SessionLocal
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    _engine = create_engine(database_url, connect_args=connect_args)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
def create_tables():
    if _engine is not None:
        Base.metadata.create_all(bind=_engine)

def get_db():
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized.")
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
