import os
from typing import Dict
from .base import SearchProvider
from .serpapi_provider import SerpApiProvider
from .gdelt_provider import GdeltProvider
from .wikipedia_provider import WikipediaProvider

class ProviderRegistry:
    def __init__(self):
        self.providers: Dict[str, SearchProvider] = {}
        
    def register(self, name: str, provider: SearchProvider):
        self.providers[name] = provider
        
    def get_provider(self, name: str) -> SearchProvider:
        return self.providers.get(name)
        
    def get_default_fallback_chain(self):
        chain = []
        
        # Load from config
        primary = os.environ.get("SEARCH_PROVIDER", "serpapi")
        if primary in self.providers:
            chain.append(self.providers[primary])
            
        if "wikipedia" in self.providers and primary != "wikipedia":
            chain.append(self.providers["wikipedia"])
            
        if "gdelt" in self.providers and primary != "gdelt":
            chain.append(self.providers["gdelt"])
            
        return chain

registry = ProviderRegistry()

# Initialize default providers
serpapi_key = os.environ.get("SERPAPI_API_KEY")
if serpapi_key:
    registry.register("serpapi", SerpApiProvider(api_key=serpapi_key))
else:
    # Register anyway so fallback logic handles the failure gracefully
    registry.register("serpapi", SerpApiProvider())
    
gdelt_enabled = os.environ.get("GDELT_ENABLED", "true").lower() == "true"
registry.register("gdelt", GdeltProvider(enabled=gdelt_enabled))
registry.register("wikipedia", WikipediaProvider())
