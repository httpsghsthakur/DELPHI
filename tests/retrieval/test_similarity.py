import pytest
import numpy as np
from delphi.retrieval.similarity import normalize_embeddings

def test_normalization():
    # Valid
    vec = np.array([[1.0, 1.0, 1.0]], dtype=np.float32)
    normed = normalize_embeddings(vec)
    assert np.allclose(np.linalg.norm(normed, axis=1), 1.0)
    
    # Zero vector
    vec_zero = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
    normed_zero = normalize_embeddings(vec_zero)
    assert np.allclose(normed_zero, 0.0)
    
    # NaN
    vec_nan = np.array([[1.0, np.nan, 1.0]], dtype=np.float32)
    with pytest.raises(ValueError):
        normalize_embeddings(vec_nan)
        
    # Dimension
    vec_1d = np.array([1.0, 1.0], dtype=np.float32)
    with pytest.raises(ValueError):
        normalize_embeddings(vec_1d)
