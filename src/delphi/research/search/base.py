from abc import ABC, abstractmethod
from typing import List, Optional
from ..schemas import SearchResult

class SearchProvider(ABC):
    @abstractmethod
    def search(
        self,
        query: str,
        *,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
        domain: Optional[str] = None,
        max_results: int = 10,
    ) -> List[SearchResult]:
        """
        Execute a search and return normalized DELPHI search results.
        """
        pass
