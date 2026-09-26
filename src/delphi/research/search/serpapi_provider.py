import os
import requests
import time
import uuid
from typing import List, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone
from .base import SearchProvider
from ..schemas import SearchResult

class SerpApiProvider(SearchProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("SERPAPI_API_KEY")
        
    def search(
        self,
        query: str,
        *,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        domain: Optional[str] = None,
        max_results: int = 10,
    ) -> List[SearchResult]:
        if not self.api_key:
            # Return empty or raise? Returning empty allows fallback.
            return []
            
        params = {
            "q": query,
            "engine": "google",
            "api_key": self.api_key,
            "num": max_results,
            "tbm": "nws" # Search news
        }
        
        # We could add temporal filters via Google search operators (e.g. tbs=cdr:1,cd_min:...,cd_max:...)
        
        try:
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"SerpApi provider failed: {e}")
            return []
            
        results = []
        now_str = datetime.now(timezone.utc).isoformat()
        
        for idx, item in enumerate(data.get("news_results", [])):
            if idx >= max_results:
                break
                
            url = item.get("link", "")
            domain_name = urlparse(url).netloc
            published_at = item.get("date", "PUBLICATION_TIME_UNKNOWN")
            
            # Simple conversion of relative dates (e.g., "2 hours ago") would normally happen here.
            # For strictness, if we can't parse it exactly, we leave as is, and temporal filter might reject it.
            
            results.append(SearchResult(
                result_id=str(uuid.uuid4()),
                query=query,
                title=item.get("title", ""),
                url=url,
                snippet=item.get("snippet", ""),
                source_domain=domain_name,
                source_name=item.get("source", ""),
                published_at=published_at,
                retrieved_at=now_str,
                provider="serpapi",
                rank=idx + 1,
                raw_metadata=item
            ))
            
        return results
