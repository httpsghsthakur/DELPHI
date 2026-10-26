import os
from typing import Dict, List
from .base import SearchProvider
from .serpapi_provider import SerpApiProvider
from .gdelt_provider import GdeltProvider
from .wikipedia_provider import WikipediaProvider
from .duckduckgo_provider import DuckDuckGoProvider
from .local_provider import LocalHistoricalSearchProvider

class ProviderRegistry:
    def __init__(self):
        self.providers: Dict[str, SearchProvider] = {}
        
    def register(self, name: str, provider: SearchProvider):
        self.providers[name] = provider
        
    def get_provider(self, name: str) -> SearchProvider:
        return self.providers.get(name)
        
    def get_default_fallback_chain(self) -> List[SearchProvider]:
        chain = []
        
        primary = os.environ.get("SEARCH_PROVIDER", "wikipedia")
        if primary in self.providers:
            chain.append(self.providers[primary])
            
        # Add wikipedia if not primary
        if "wikipedia" in self.providers and primary != "wikipedia":
            chain.append(self.providers["wikipedia"])

        # Add duckduckgo if not primary
        if "duckduckgo" in self.providers and primary != "duckduckgo":
            chain.append(self.providers["duckduckgo"])

        # Add local historical corpus
        if "local_historical" in self.providers and primary != "local_historical":
            chain.append(self.providers["local_historical"])
            
        # Add gdelt if enabled and not primary
        if "gdelt" in self.providers and primary != "gdelt":
            chain.append(self.providers["gdelt"])
            
        # Add serpapi if key exists and not primary
        if "serpapi" in self.providers and primary != "serpapi" and os.environ.get("SERPAPI_API_KEY"):
            chain.append(self.providers["serpapi"])
            
        return chain

registry = ProviderRegistry()

# Initialize providers
serpapi_key = os.environ.get("SERPAPI_API_KEY")
if serpapi_key:
    registry.register("serpapi", SerpApiProvider(api_key=serpapi_key))
else:
    registry.register("serpapi", SerpApiProvider())
    
gdelt_enabled = os.environ.get("GDELT_ENABLED", "true").lower() == "true"
registry.register("gdelt", GdeltProvider(enabled=gdelt_enabled))
registry.register("wikipedia", WikipediaProvider())
registry.register("duckduckgo", DuckDuckGoProvider())
registry.register("local_historical", LocalHistoricalSearchProvider())
