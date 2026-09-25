import numpy as np

def normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """
    Validates and L2 normalizes embeddings for FAISS inner product search.
    
    Args:
        embeddings: np.ndarray of shape [N, D]
        
    Returns:
        np.ndarray of L2 normalized embeddings
    """
    if embeddings.ndim != 2:
        raise ValueError(f"Embeddings must be 2D, got shape {embeddings.shape}")
        
    if np.isnan(embeddings).any():
        raise ValueError("NaN detected in embeddings")
        
    if np.isinf(embeddings).any():
        raise ValueError("Inf detected in embeddings")
        
    # L2 normalize
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    # Prevent division by zero
    norms[norms == 0] = 1.0
    
    normalized = embeddings / norms
    
    # Verify norms are 1.0 (with small numerical tolerance)
    new_norms = np.linalg.norm(normalized, axis=1)
    if not np.allclose(new_norms, 1.0, atol=1e-5):
        # Allow zero-vectors to stay zero vectors, otherwise raise
        sq = np.atleast_1d(norms.squeeze())
        non_zeros = np.where(sq != 1.0)[0] # we forced 0 norm to 1.0 above
        if len(non_zeros) > 0 and not np.allclose(new_norms[non_zeros], 1.0, atol=1e-5):
             raise ValueError("L2 normalization failed to produce unit norms")
        
    return normalized
