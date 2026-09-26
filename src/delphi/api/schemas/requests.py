from pydantic import BaseModel, Field
from typing import Optional

class AnalysisRequest(BaseModel):
    text: str = Field(..., description="The article or event text to analyze.")
    source_id: Optional[str] = None
    article_id: Optional[str] = None
    publication_timestamp: str = Field(..., description="ISO 8601 timestamp of publication.")
    prediction_information_cutoff: str = Field(..., description="ISO 8601 timestamp for temporal cutoff.")
    domain: str = Field(..., description="The domain of the event (e.g., geopolitics).")
    forecast_horizon: int = Field(30, description="Forecast horizon in days.")

class HistoricalSearchRequest(BaseModel):
    text: str = Field(..., description="The event text to find analogues for.")
    cutoff: str = Field(..., description="ISO 8601 temporal cutoff.")
    top_k: int = Field(5, description="Number of analogues to return.")
    domain: Optional[str] = None

class BacktestRequest(BaseModel):
    start_timestamp: str
    end_timestamp: str
    interval: str = "1d"
    strict_temporal_mode: bool = True
    dataset_version: str = "v1"
