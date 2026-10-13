import requests
import uuid
from typing import List, Optional
from datetime import datetime, timezone
from .base import SearchProvider
from ..schemas import SearchResult

class WikipediaProvider(SearchProvider):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DELPHI_Forecast_Engine/1.0 (https://github.com/delphi-project/delphi; admin@delphi.local)"
        })
        
    def search(
        self,
        query: str,
        *,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        domain: Optional[str] = None,
        max_results: int = 5,
    ) -> List[SearchResult]:
        
        # Wikipedia search API
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "utf8": "",
            "format": "json",
            "srlimit": max_results
        }
        
        try:
            response = self.session.get("https://en.wikipedia.org/w/api.php", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"Wikipedia provider failed: {e}")
            return []
            
        results = []
        now_str = datetime.now(timezone.utc).isoformat()
        
        search_hits = data.get("query", {}).get("search", [])
        for idx, item in enumerate(search_hits):
            if idx >= max_results:
                break
                
            title = item.get("title", "")
            page_id = item.get("pageid", "")
            snippet = item.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', '')
            timestamp = item.get("timestamp", "PUBLICATION_TIME_UNKNOWN")
            
            url = f"https://en.wikipedia.org/?curid={page_id}"
            
            results.append(SearchResult(
                result_id=str(uuid.uuid4()),
                query=query,
                title=title,
                url=url,
                snippet=snippet,
                source_domain="wikipedia.org",
                source_name="Wikipedia",
                published_at=timestamp,
                retrieved_at=now_str,
                provider="wikipedia",
                rank=idx + 1,
                raw_metadata=item
            ))
            
        return results
