from typing import List, Dict, Any
from .schemas import EvidenceItem, ForecastRequest

class EvidenceRegistry:
    def __init__(self):
        self.evidence: List[EvidenceItem] = []
        
    def add_evidence(self, item: EvidenceItem):
        self.evidence.append(item)
        
    def get_supporting(self) -> List[EvidenceItem]:
        return [e for e in self.evidence if e.direction == "supporting"]
        
    def get_contradictory(self) -> List[EvidenceItem]:
        return [e for e in self.evidence if e.direction == "conflicting"]
        
    def validate_cutoff(self, cutoff_time: str) -> bool:
        """
        Ensure no evidence was gathered from after the cutoff.
        """
        for item in self.evidence:
            if item.timestamp > cutoff_time:
                return False
        return True
