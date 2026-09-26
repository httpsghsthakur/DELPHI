from typing import List, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression

class PlattScaler:
    def __init__(self):
        self.scaler = LogisticRegression(solver='lbfgs', max_iter=1000)
        self.is_fitted = False
        
    def fit(self, logits: List[float], labels: List[float]):
        """
        Fits Platt scaling on validation data.
        logits: unnormalized raw model output
        labels: 0.0 or 1.0 true labels
        """
        X = np.array(logits).reshape(-1, 1)
        y = np.array(labels)
        self.scaler.fit(X, y)
        self.is_fitted = True
        
    def calibrate(self, logits: List[float]) -> List[float]:
        """
        Calibrates logits into probabilities in [0, 1]
        """
        if not self.is_fitted:
            raise RuntimeError("Scaler is not fitted yet.")
        X = np.array(logits).reshape(-1, 1)
        # predict_proba returns [prob_class_0, prob_class_1]
        probs = self.scaler.predict_proba(X)[:, 1]
        return probs.tolist()
