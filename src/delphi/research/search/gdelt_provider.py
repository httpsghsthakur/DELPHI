import requests
import uuid
from typing import List, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone
from .base import SearchProvider
from ..schemas import SearchResult

class GdeltProvider(SearchProvider):
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        
    def search(
        self,
        query: str,
        *,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        domain: Optional[str] = None,
        max_results: int = 10,
    ) -> List[SearchResult]:
        if not self.enabled:
            return []
            
        # GDELT DOC API (v2)
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_results,
            "format": "json"
        }
        
        try:
            response = requests.get("https://api.gdeltproject.org/api/v2/doc/doc", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"GDELT provider failed: {e}")
            return []
            
        results = []
        now_str = datetime.now(timezone.utc).isoformat()
        
        for idx, item in enumerate(data.get("articles", [])):
            if idx >= max_results:
                break
                
            url = item.get("url", "")
            domain_name = item.get("domain", urlparse(url).netloc)
            published_at = item.get("seendate", "PUBLICATION_TIME_UNKNOWN") # GDELT uses YYYYMMDDTHHMMSSZ format
            
            # Simple conversion
            if published_at != "PUBLICATION_TIME_UNKNOWN" and len(published_at) == 16:
                try:
                    dt = datetime.strptime(published_at, "%Y%m%dT%H%M%SZ")
                    published_at = dt.replace(tzinfo=timezone.utc).isoformat()
                except ValueError:
                    pass
            
            results.append(SearchResult(
                result_id=str(uuid.uuid4()),
                query=query,
                title=item.get("title", ""),
                url=url,
                snippet="", # GDELT DOC API doesn't always provide a good snippet in artlist
                source_domain=domain_name,
                source_name=domain_name,
                published_at=published_at,
                retrieved_at=now_str,
                provider="gdelt",
                rank=idx + 1,
                raw_metadata=item
            ))
            
        return results
