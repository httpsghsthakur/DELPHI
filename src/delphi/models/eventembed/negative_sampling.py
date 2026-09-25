import torch
import numpy as np
from typing import List, Dict

class NegativeSampler:
    def __init__(self, token_frequencies: Dict[int, int], vocab_size: int, pad_idx: int = 0, smoothing: float = 0.75):
        self.vocab_size = vocab_size
        self.pad_idx = pad_idx
        
        # Build probability distribution
        counts = np.zeros(vocab_size, dtype=np.float32)
        for token_id, count in token_frequencies.items():
            if token_id != pad_idx:
                counts[token_id] = count
                
        # Word2Vec paper suggests smoothing the distribution by raising to power 0.75
        counts = np.power(counts, smoothing)
        total = np.sum(counts)
        if total > 0:
            self.probs = counts / total
        else:
            # Fallback uniform
            self.probs = np.ones(vocab_size, dtype=np.float32) / (vocab_size - 1)
            self.probs[pad_idx] = 0.0
            
    def sample(self, batch_size: int, num_samples: int) -> torch.Tensor:
        """
        Samples negatives for a batch.
        Returns tensor of shape [batch_size, num_samples]
        """
        # We can use torch.multinomial or numpy choice
        # torch.multinomial on a large tensor is fast enough
        probs_tensor = torch.from_numpy(self.probs)
        # sample globally, then reshape
        negatives = torch.multinomial(probs_tensor, batch_size * num_samples, replacement=True)
        return negatives.view(batch_size, num_samples)
