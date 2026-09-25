import torch
import torch.nn as nn
import torch.nn.functional as F

class SkipGramNegativeSamplingLoss(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, pad_idx: int = 0):
        super().__init__()
        # Target embeddings for the objective (the "context" vectors in word2vec)
        self.context_embeddings = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dim,
            padding_idx=pad_idx
        )
        nn.init.xavier_uniform_(self.context_embeddings.weight)
        with torch.no_grad():
            self.context_embeddings.weight[pad_idx].fill_(0.0)

    def forward(self, target_vectors: torch.Tensor, positive_ids: torch.Tensor, negative_ids: torch.Tensor) -> torch.Tensor:
        """
        Args:
            target_vectors: [batch_size, embedding_dim] - The representations coming from EventEmbed
            positive_ids: [batch_size] - The positive context token IDs
            negative_ids: [batch_size, num_negatives] - The negative context token IDs
            
        Returns:
            Scalar loss
        """
        # Positive loss part
        # [batch_size, embedding_dim]
        pos_embeddings = self.context_embeddings(positive_ids)
        # dot product: [batch_size]
        pos_scores = torch.sum(target_vectors * pos_embeddings, dim=-1)
        # log_sigmoid(x) = log(1 / (1 + exp(-x)))
        pos_loss = -F.logsigmoid(pos_scores)
        
        # Negative loss part
        # [batch_size, num_negatives, embedding_dim]
        neg_embeddings = self.context_embeddings(negative_ids)
        # dot product: target_vectors [batch_size, 1, embedding_dim] * neg_embeddings [batch_size, num_neg, embedding_dim] -> [batch_size, num_neg]
        neg_scores = torch.bmm(neg_embeddings, target_vectors.unsqueeze(-1)).squeeze(-1)
        # We want target * negative to be large negative, so log_sigmoid(-score)
        neg_loss = -F.logsigmoid(-neg_scores).sum(dim=-1)
        
        # Mean over batch
        return (pos_loss + neg_loss).mean()
