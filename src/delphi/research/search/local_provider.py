import os
import uuid
from typing import List, Optional
from datetime import datetime, timezone
import polars as pl
from .base import SearchProvider
from ..schemas import SearchResult

class LocalHistoricalSearchProvider(SearchProvider):
    """
    Local historical corpus search provider querying DELPHI's indexed GDELT dataset.
    Provides fast, deterministic historical event grounding even in offline or rate-limited environments.
    """
    def __init__(self, metadata_path: str = "indexes/historical/metadata.parquet"):
        self.metadata_path = metadata_path
        self._df = None
        if os.path.exists(metadata_path):
            try:
                self._df = pl.read_parquet(metadata_path)
            except Exception:
                self._df = None

    def search(
        self,
        query: str,
        *,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        domain: Optional[str] = None,
        max_results: int = 5,
    ) -> List[SearchResult]:
        if self._df is None or len(self._df) == 0:
            return []

        tokens = [t.lower().strip() for t in query.split() if len(t.strip()) > 3]
        if not tokens:
            tokens = [t.lower().strip() for t in query.split()]

        # Filter rows containing any of the query terms in text column
        now_str = datetime.now(timezone.utc).isoformat()
        results: List[SearchResult] = []

        try:
            # Case-insensitive search on text column
            filtered = self._df
            for t in tokens[:2]: # match top tokens
                filtered = filtered.filter(pl.col("text").str.to_lowercase().str.contains(t))
                if len(filtered) < max_results:
                    break

            if len(filtered) == 0:
                # Fallback to single token
                if tokens:
                    filtered = self._df.filter(pl.col("text").str.to_lowercase().str.contains(tokens[0]))

            rows = filtered.head(max_results).to_dicts()
            for idx, r in enumerate(rows):
                ev_id = str(r.get("event_id", idx))
                ev_date = str(r.get("event_date", "2024-01-01T00:00:00Z"))
                text = str(r.get("text", "Historical event"))
                results.append(SearchResult(
                    result_id=str(uuid.uuid4()),
                    query=query,
                    title=f"Historical Event {ev_id}: {text[:70]}",
                    url=f"local://gdelt/event/{ev_id}",
                    snippet=text,
                    source_domain="gdeltproject.org",
                    source_name="GDELT Historical Archive",
                    published_at=ev_date,
                    retrieved_at=now_str,
                    provider="local_gdelt_archive",
                    rank=idx + 1,
                    raw_metadata=r
                ))
        except Exception:
            pass

        return results
