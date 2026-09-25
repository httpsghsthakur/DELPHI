from typing import List, Dict, Any, Optional
from datetime import datetime
from .schemas import HistoricalEventDocument

class TemporalHistoricalFilter:
    @staticmethod
    def filter(candidates: List[HistoricalEventDocument], prediction_time: str) -> List[HistoricalEventDocument]:
        """
        Removes candidates that occurred after the prediction_time.
        Expected date format: YYYY-MM-DD
        """
        pred_date = datetime.strptime(prediction_time[:10], "%Y-%m-%d").date()
        valid = []
        for cand in candidates:
            if not cand.event_date:
                continue
            cand_date = datetime.strptime(cand.event_date[:10], "%Y-%m-%d").date()
            if cand_date <= pred_date:
                valid.append(cand)
        return valid

class MetadataFilter:
    def __init__(self, domain: Optional[str] = None, event_type: Optional[str] = None, query_event_id: Optional[str] = None):
        self.domain = domain
        self.event_type = event_type
        self.query_event_id = query_event_id

    def filter(self, candidates: List[HistoricalEventDocument]) -> List[HistoricalEventDocument]:
        valid = []
        for cand in candidates:
            # Self-match prevention
            if self.query_event_id and cand.event_id == self.query_event_id:
                continue
                
            if self.domain and cand.domain and cand.domain != self.domain:
                continue
                
            if self.event_type and cand.event_type and cand.event_type != self.event_type:
                continue
                
            valid.append(cand)
        return valid
