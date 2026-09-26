from typing import List, Dict, Any
from urllib.parse import urlparse, urlunparse
import re

class Deduplicator:
    
    @staticmethod
    def normalize_url(url: str) -> str:
        parsed = urlparse(url)
        # Strip scheme (http/https), www., and trailing slash
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        path = parsed.path
        if path.endswith("/"):
            path = path[:-1]
        
        return f"{netloc}{path}"

    @staticmethod
    def deduplicate_results(results: List[Any]) -> List[Any]:
        """Deduplicate search results based on normalized URL."""
        seen_urls = set()
        unique = []
        for r in results:
            n_url = Deduplicator.normalize_url(r.url)
            if n_url not in seen_urls:
                seen_urls.add(n_url)
                unique.append(r)
        return unique
        
    @staticmethod
    def deduplicate_documents(docs: List[Any]) -> List[Any]:
        """Deduplicate fetched documents based on checksum and normalized URL."""
        seen_urls = set()
        seen_checksums = set()
        unique = []
        
        for d in docs:
            n_url = Deduplicator.normalize_url(d.url)
            if n_url in seen_urls or d.checksum in seen_checksums:
                continue
            seen_urls.add(n_url)
            seen_checksums.add(d.checksum)
            unique.append(d)
            
        return unique

class SourceClusterer:
    """Group documents that appear to derive from the same underlying source."""
    
    @staticmethod
    def cluster(docs: List[Any]) -> List[List[Any]]:
        clusters = []
        for d in docs:
            placed = False
            for cluster in clusters:
                # Simple clustering based on identical domain or high title overlap
                c_leader = cluster[0]
                if c_leader.source_domain == d.source_domain:
                    cluster.append(d)
                    placed = True
                    break
                # Or title similarity (very simplistic jaccard)
                t1 = set(re.findall(r'\w+', c_leader.title.lower()))
                t2 = set(re.findall(r'\w+', d.title.lower()))
                if t1 and t2:
                    overlap = len(t1.intersection(t2)) / len(t1.union(t2))
                    if overlap > 0.6:
                        cluster.append(d)
                        placed = True
                        break
            if not placed:
                clusters.append([d])
        return clusters
