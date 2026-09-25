import torch
import torch.nn as nn
from typing import List

class CharacterCNN(nn.Module):
    def __init__(self, vocab_size: int, embedding_dim: int, filters: List[dict], output_dim: int, pad_idx: int = 0):
        super().__init__()
        
        self.embedding = nn.Embedding(
            num_embeddings=vocab_size, 
            embedding_dim=embedding_dim, 
            padding_idx=pad_idx
        )
        nn.init.uniform_(self.embedding.weight, -0.1, 0.1)
        with torch.no_grad():
            self.embedding.weight[pad_idx].fill_(0.0)
        
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embedding_dim, out_channels=f["channels"], kernel_size=f["kernel_size"])
            for f in filters
        ])
        
        for conv in self.convs:
            nn.init.kaiming_uniform_(conv.weight, nonlinearity='relu')
            if conv.bias is not None:
                nn.init.zeros_(conv.bias)
                
        total_channels = sum([f["channels"] for f in filters])
        
        self.projection = nn.Sequential(
            nn.Linear(total_channels, output_dim),
            nn.GELU(),
            nn.LayerNorm(output_dim)
        )
        
        for m in self.projection.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, char_ids: torch.Tensor) -> torch.Tensor:
        """
        Args:
            char_ids: [batch_size, seq_len, max_char_len]
        Returns:
            [batch_size, seq_len, output_dim]
        """
        b, seq_len, max_char_len = char_ids.shape
        
        # Flatten to process characters for each token independently
        # [b * seq_len, max_char_len]
        flat_char_ids = char_ids.view(b * seq_len, max_char_len)
        
        # [b * seq_len, max_char_len, embedding_dim]
        embedded = self.embedding(flat_char_ids)
        
        # Conv1d expects [batch, channels, length], so we permute
        # [b * seq_len, embedding_dim, max_char_len]
        embedded = embedded.permute(0, 2, 1)
        
        conv_outputs = []
        for conv in self.convs:
            # [b * seq_len, channels, L_out]
            conv_out = torch.relu(conv(embedded))
            # Global max pool over the sequence length dimension
            # [b * seq_len, channels]
            pooled, _ = torch.max(conv_out, dim=2)
            conv_outputs.append(pooled)
            
        # [b * seq_len, total_channels]
        concatenated = torch.cat(conv_outputs, dim=1)
        
        # [b * seq_len, output_dim]
        projected = self.projection(concatenated)
        
        # [batch_size, seq_len, output_dim]
        return projected.view(b, seq_len, -1)
