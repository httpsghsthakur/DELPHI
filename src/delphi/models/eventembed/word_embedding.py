import torch
import torch.nn as nn

class WordEmbedding(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, pad_idx: int = 0):
        super().__init__()
        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dim,
            padding_idx=pad_idx
        )
        
        # Initialize randomly
        nn.init.xavier_uniform_(self.embedding.weight)
        with torch.no_grad():
            self.embedding.weight[pad_idx].fill_(0.0)
            
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        Args:
            input_ids: [batch_size, seq_len]
        Returns:
            [batch_size, seq_len, embedding_dim]
        """
        return self.embedding(input_ids)
