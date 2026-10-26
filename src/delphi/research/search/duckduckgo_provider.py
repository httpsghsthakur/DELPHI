import requests
import re
import uuid
import urllib.parse
from typing import List, Optional
from urllib.parse import urlparse
from datetime import datetime, timezone
from .base import SearchProvider
from ..schemas import SearchResult

class DuckDuckGoProvider(SearchProvider):
    """
    Public web search provider querying DuckDuckGo HTML interface.
    Extracts genuine organic web search results with actual publisher domains and URLs.
    No API key required; respects standard rate limits and timeouts.
    """
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        
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
            
        search_query = query
        if domain:
            search_query += f" site:{domain}"
            
        html = ""
        try:
            response = self.session.post(
                "https://html.duckduckgo.com/html/",
                data={"q": search_query},
                timeout=6
            )
            if response.status_code == 200:
                html = response.text
        except Exception:
            html = ""
            
        results: List[SearchResult] = []
        now_str = datetime.now(timezone.utc).isoformat()
        seen_urls = set()
        
        # 1. If HTML returned search results, parse them
        if html:
            raw_links = re.findall(r'<a[^>]+href="([^"]*uddg=[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            for href, text in raw_links:
                if len(results) >= max_results:
                    break
                m = re.search(r'uddg=([^&]+)', href)
                if not m:
                    continue
                actual_url = urllib.parse.unquote(m.group(1))
                if not actual_url.startswith("http") or "duckduckgo.com" in actual_url or actual_url in seen_urls:
                    continue
                seen_urls.add(actual_url)
                
                clean_title = re.sub(r'<[^>]+>', ' ', text)
                clean_title = re.sub(r'\s+', ' ', clean_title).strip() or actual_url
                parsed = urlparse(actual_url)
                domain_name = parsed.netloc.lower()
                if domain_name.startswith("www."):
                    domain_name = domain_name[4:]
                source_name = domain_name.split(".")[0].capitalize() if domain_name else "Web"
                
                results.append(SearchResult(
                    result_id=str(uuid.uuid4()),
                    query=query,
                    title=clean_title,
                    url=actual_url,
                    snippet=clean_title,
                    source_domain=domain_name,
                    source_name=source_name,
                    published_at="PUBLICATION_TIME_UNKNOWN",
                    retrieved_at=now_str,
                    provider="duckduckgo",
                    rank=len(results) + 1
                ))
                
        # 2. Fallback to DuckDuckGo Instant Answer API if results are empty
        if not results:
            try:
                api_resp = self.session.get(
                    "https://api.duckduckgo.com/",
                    params={"q": search_query, "format": "json", "no_html": 1, "skip_disambig": 1},
                    timeout=6
                )
                if api_resp.content:
                    api_data = api_resp.json()
                    abstract_url = api_data.get("AbstractURL")
                    abstract_text = api_data.get("AbstractText")
                    if abstract_url and abstract_url not in seen_urls:
                        seen_urls.add(abstract_url)
                        parsed = urlparse(abstract_url)
                        domain_name = parsed.netloc.lower()
                        results.append(SearchResult(
                            result_id=str(uuid.uuid4()),
                            query=query,
                            title=api_data.get("Heading") or query,
                            url=abstract_url,
                            snippet=abstract_text or query,
                            source_domain=domain_name,
                            source_name=domain_name.split(".")[0].capitalize() if domain_name else "DuckDuckGo",
                            published_at="PUBLICATION_TIME_UNKNOWN",
                            retrieved_at=now_str,
                            provider="duckduckgo_api",
                            rank=1
                        ))
                    for item in api_data.get("RelatedTopics", []):
                        if len(results) >= max_results:
                            break
                        first_url = item.get("FirstURL")
                        text_val = item.get("Text")
                        if first_url and first_url not in seen_urls:
                            seen_urls.add(first_url)
                            parsed = urlparse(first_url)
                            domain_name = parsed.netloc.lower()
                            results.append(SearchResult(
                                result_id=str(uuid.uuid4()),
                                query=query,
                                title=text_val[:80] if text_val else first_url,
                                url=first_url,
                                snippet=text_val or "",
                                source_domain=domain_name,
                                source_name=domain_name.split(".")[0].capitalize() if domain_name else "Web",
                                published_at="PUBLICATION_TIME_UNKNOWN",
                                retrieved_at=now_str,
                                provider="duckduckgo_api",
                                rank=len(results) + 1
                            ))
            except Exception:
                pass
                
        return results
        
        for href, text in raw_links:
            if len(results) >= max_results:
                break
                
            m = re.search(r'uddg=([^&]+)', href)
            if not m:
                continue
            actual_url = urllib.parse.unquote(m.group(1))
            
            # Filter internal/tracking urls
            if not actual_url.startswith("http") or "duckduckgo.com" in actual_url:
                continue
            if actual_url in seen_urls:
                continue
            seen_urls.add(actual_url)
            
            clean_title = re.sub(r'<[^>]+>', ' ', text)
            clean_title = re.sub(r'\s+', ' ', clean_title).strip()
            if not clean_title or len(clean_title) < 3:
                clean_title = actual_url
                
            parsed = urlparse(actual_url)
            domain_name = parsed.netloc.lower()
            if domain_name.startswith("www."):
                domain_name = domain_name[4:]
                
            source_name = domain_name.split(".")[0].capitalize() if domain_name else "Web"
            
            # Find snippet nearby if possible
            snippet = clean_title
            
            results.append(SearchResult(
                result_id=str(uuid.uuid4()),
                query=query,
                title=clean_title,
                url=actual_url,
                snippet=snippet,
                source_domain=domain_name,
                source_name=source_name,
                published_at="PUBLICATION_TIME_UNKNOWN",
                retrieved_at=now_str,
                provider="duckduckgo",
                rank=rank,
                raw_metadata={"raw_url": actual_url}
            ))
            rank += 1
            
        return results
