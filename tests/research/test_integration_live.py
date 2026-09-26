import pytest
import os
from delphi.research.search.serpapi_provider import SerpApiProvider

def test_live_web_integration():
    """LIVE WEB INTEGRATION TEST"""
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        pytest.skip("LIVE TEST NOT EXECUTED: SERPAPI_API_KEY not set")
        
    provider = SerpApiProvider(api_key=api_key)
    results = provider.search("global economy 2026", max_results=2)
    
    # If network/auth is good, we should get results or it shouldn't crash
    assert isinstance(results, list)
    if len(results) > 0:
        assert results[0].url.startswith("http")
