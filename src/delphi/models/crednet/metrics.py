from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, brier_score_loss
import numpy as np
from typing import Dict, List

def compute_metrics(labels: List[float], probs: List[float], threshold: float = 0.5) -> Dict[str, float]:
    """
    Computes rigorous credibility metrics.
    labels: true labels (0.0 or 1.0)
    probs: calibrated probabilities (or sigmoid of logits)
    """
    y_true = np.array(labels)
    y_prob = np.array(probs)
    y_pred = (y_prob >= threshold).astype(float)
    
    metrics = {}
    
    # Classification
    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["precision"] = precision_score(y_true, y_pred, zero_division=0)
    metrics["recall"] = recall_score(y_true, y_pred, zero_division=0)
    metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)
    metrics["macro_f1"] = f1_score(y_true, y_pred, average="macro", zero_division=0)
    
    # Ranking
    try:
        metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
    except ValueError:
        metrics["roc_auc"] = 0.5 # Default if only one class exists in batch
        
    # Calibration
    metrics["brier"] = brier_score_loss(y_true, y_prob)
    metrics["ece"] = expected_calibration_error(y_true, y_prob)
    
    return metrics

def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    binids = np.digitize(y_prob, bins) - 1
    
    ece = 0.0
    total_samples = len(y_prob)
    
    for i in range(n_bins):
        in_bin = (binids == i)
        if np.any(in_bin):
            bin_prob = y_prob[in_bin].mean()
            bin_true = y_true[in_bin].mean()
            bin_count = np.sum(in_bin)
            ece += (bin_count / total_samples) * np.abs(bin_prob - bin_true)
            
    return ece
