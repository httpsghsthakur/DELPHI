import torch
import os
import joblib
import json
from typing import Dict, Any, List
from delphi.datasets.schemas import CredibilityFeatures
from .model import CredNet

class CredibilityResult:
    def __init__(self, source_id: str, article_id: str, raw_logit: float, uncalibrated_score: float, calibrated_score: float, explanation: dict):
        self.source_id = source_id
        self.article_id = article_id
        self.raw_logit = raw_logit
        self.uncalibrated_score = uncalibrated_score # Sigmoid
        self.calibrated_score = calibrated_score
        self.explanation = explanation

class CredNetInference:
    def __init__(self, checkpoint_dir: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CredNet(input_dim=12).to(self.device)
        self.model.load_state_dict(torch.load(os.path.join(checkpoint_dir, "model.pt"), map_location=self.device))
        self.model.eval()
        
        self.scaler = joblib.load(os.path.join(checkpoint_dir, "scaler.pkl"))
        
        with open(os.path.join(checkpoint_dir, "metadata.json"), "r") as f:
            self.metadata = json.load(f)
            
    def predict(self, feature_list: List[CredibilityFeatures]) -> List[CredibilityResult]:
        if not feature_list:
            return []
            
        vectors = []
        for feat in feature_list:
            v = [
                feat.author_identifiable,
                feat.article_length_normalized,
                feat.citation_density,
                feat.title_sensationalism,
                feat.historical_source_reliability,
                feat.corroboration_count_normalized,
                feat.correction_history_signal,
                feat.publication_consistency,
                feat.primary_source_presence,
                feat.attribution_completeness,
                feat.author_history_availability,
                feat.source_longevity_normalized
            ]
            vectors.append(v)
            
        X = torch.tensor(vectors, dtype=torch.float32).to(self.device)
        
        with torch.no_grad():
            logits = self.model(X).cpu().view(-1).numpy().tolist()
            
        calibrated_probs = self.scaler.calibrate(logits)
        
        results = []
        for i, feat in enumerate(feature_list):
            # Simple explanation: weight magnitude proxy (requires inspection in real system, here we just attach inputs)
            explanation = {
                "inputs_used": vectors[i]
            }
            # Sigmoid for raw probability
            raw_prob = 1.0 / (1.0 + torch.exp(torch.tensor(-logits[i]))).item()
            
            res = CredibilityResult(
                source_id=feat.source_id,
                article_id=feat.article_id,
                raw_logit=logits[i],
                uncalibrated_score=raw_prob,
                calibrated_score=calibrated_probs[i],
                explanation=explanation
            )
            results.append(res)
            
        return results
