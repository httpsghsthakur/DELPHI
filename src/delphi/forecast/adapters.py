from typing import Dict, Any, List
from delphi.forecast.schemas import ForecastRequest

# Placeholder mock models representing actual frozen Layer 1-7 imports
class MockActualEventNet:
    def __init__(self):
        self.version = "v1"
        self.training_information_end_time = "2026-01-01T00:00Z"
    def predict(self, text: str):
        return {"event_type": 1, "actor": 2, "target": 3, "domain": 1}

class MockActualCredNet:
    def __init__(self):
        self.version = "v1"
        self.training_information_end_time = "2026-01-01T00:00Z"
    def predict(self, features: dict):
        return {"credibility_score": 0.82, "raw_logit": 1.5}

class MockActualHistoricalMatcher:
    def __init__(self):
        self.version = "v1"
    def retrieve(self, event, cutoff):
        return [{"event_id": "H_REAL", "match_score": 0.88, "timestamp": "2020-01-01T00:00"}]

class MockActualCausalSeq:
    def __init__(self):
        self.version = "v1"
        self.training_information_end_time = "2026-01-01T00:00Z"
    def generate(self, context, cutoff):
        return [
            {"trajectory": [{"event_type": 2, "time_bin": 1, "actor": 1, "target": 2, "domain": 1}], "sequence_score": -0.5},
            {"trajectory": [{"event_type": 3, "time_bin": 2, "actor": 1, "target": 3, "domain": 1}], "sequence_score": -1.2}
        ]

CAMEO_EVENT_CODES = {
    0: "Unspecified Event",
    1: "Make Public Statement",
    2: "Appeal",
    3: "Express Intent to Cooperate",
    4: "Consult",
    5: "Engage in Diplomatic Cooperation",
    6: "Engage in Material Cooperation",
    7: "Provide Aid",
    8: "Yield",
    9: "Investigate",
    10: "Demand / Political Action",
    11: "Disapprove",
    12: "Reject",
    13: "Threaten",
    14: "Protest",
    15: "Exhibit Military Posture",
    16: "Reduce Relations",
    17: "Coerce",
    18: "Assault",
    19: "Fight / Military Conflict",
    20: "Mass Violence"
}

class EventExtractionAdapter:
    def __init__(self, model):
        self.model = model
        
    def extract(self, request: ForecastRequest) -> Dict[str, Any]:
        result = self.model.predict(request.article_text)
        evt_type = result["event_type"]
        
        # Check text context for protest or demonstration keywords if code is 10 or 14
        text_lower = request.article_text.lower()
        if "protest" in text_lower or "demonstrat" in text_lower or "crackdown" in text_lower:
            code_label = "Protest / Public Demonstration" if evt_type in [10, 14] else CAMEO_EVENT_CODES.get(evt_type, f"Event Type {evt_type}")
        else:
            code_label = CAMEO_EVENT_CODES.get(evt_type, result.get("event_type_code", f"Event Type {evt_type}"))
            
        return {
            "event_id": request.article_id or "E_NEW",
            "event_type": evt_type,
            "event_type_code": code_label,
            "timestamp": request.publication_timestamp,
            "actors": [result.get("actor")],
            "targets": [result.get("target")],
            "domain": result.get("domain"),
            "embedding": result.get("embedding"),
            "source_text": request.article_text,
            "model_version": self.model.version
        }

class CredibilityAdapter:
    def __init__(self, model):
        self.model = model
        self.temperature = None
        import os, json
        cal_path = "models/calibration/calibration.json"
        if os.path.exists(cal_path):
            try:
                with open(cal_path) as f:
                    meta = json.load(f)
                    self.temperature = meta.get("temperature", 1.0)
            except Exception:
                pass
        
    def assess(self, event: Dict[str, Any]) -> Dict[str, Any]:
        features = {"domain": event.get("domain")}
        result = self.model.predict(features)
        raw_logit = result["raw_logit"]
        
        calibrated_score = None
        if self.temperature and self.temperature > 0:
            import math
            calibrated_score = 1.0 / (1.0 + math.exp(-raw_logit / self.temperature))
            
        return {
            "credibility_score": result["credibility_score"],
            "raw_logit": raw_logit,
            "calibrated_score": calibrated_score,
            "calibrated": calibrated_score is not None,
            "model_version": self.model.version
        }

class HistoricalRetrievalAdapter:
    def __init__(self, model):
        self.model = model
        
    def retrieve(self, event: Dict[str, Any], cutoff: str) -> List[Dict[str, Any]]:
        return self.model.retrieve(event, cutoff)

class CausalForecastAdapter:
    def __init__(self, model):
        self.model = model
        
    def forecast(self, event: Dict[str, Any], analogues: List[Dict[str, Any]], cutoff: str) -> List[Dict[str, Any]]:
        return self.model.generate(event, cutoff)
