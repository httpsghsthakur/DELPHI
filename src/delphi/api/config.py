import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "DELPHI Forecast API"
    version: str = "1.0.0"
    debug: bool = False
    
    # Temporal mode
    strict_temporal_mode: bool = True
    
    # CORS
    cors_origins: str = os.getenv("DELPHI_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    
    # Payload
    max_payload_length: int = 50000
    
    # Paths
    database_url: str = os.getenv("DELPHI_DB_URL", "sqlite:///delphi.db")
    model_registry_path: str = os.getenv("DELPHI_REGISTRY_PATH", "models/registry")
    
    model_config = {"env_prefix": "DELPHI_", "protected_namespaces": ()}

settings = Settings()
