import pytest
from delphi.models.crednet.calibration import PlattScaler
from delphi.models.crednet.metrics import compute_metrics, expected_calibration_error
import numpy as np

def test_platt_scaler():
    scaler = PlattScaler()
    
    # Perfect logits
    logits = [-5.0, -2.0, 0.0, 2.0, 5.0]
    labels = [0.0, 0.0, 0.0, 1.0, 1.0]
    
    scaler.fit(logits, labels)
    probs = scaler.calibrate(logits)
    
    assert len(probs) == 5
    assert all(0.0 <= p <= 1.0 for p in probs)
    assert probs[0] < probs[-1]

def test_metrics():
    labels = [1.0, 0.0, 1.0, 0.0]
    probs = [0.9, 0.1, 0.8, 0.2]
    
    metrics = compute_metrics(labels, probs)
    
    assert metrics["accuracy"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["roc_auc"] == 1.0
    assert metrics["brier"] > 0.0
    assert metrics["ece"] >= 0.0
    
def test_ece_calculation():
    y_true = np.array([1.0, 1.0, 0.0, 0.0])
    # Perfectly calibrated
    y_prob = np.array([0.9, 0.9, 0.1, 0.1])
    
    # ECE should be small but not 0 due to bins, wait, 0.9 mean is close to 1.0 true mean
    # in bin [0.8, 0.9): prob=0.9, true=1.0 -> diff=0.1
    ece = expected_calibration_error(y_true, y_prob, n_bins=10)
    assert ece > 0.0
