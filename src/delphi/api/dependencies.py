from delphi.api.config import settings
from delphi.api.registry.model_registry import ModelRegistry
from delphi.forecast.orchestrator import ForecastOrchestrator
from delphi.forecast.config import ForecastConfig

# Singleton registry and orchestrator
_registry = None
_orchestrator = None

def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry

def get_orchestrator() -> ForecastOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        cfg = ForecastConfig(strict_temporal_mode=settings.strict_temporal_mode)
        _orchestrator = ForecastOrchestrator(cfg)
    return _orchestrator
