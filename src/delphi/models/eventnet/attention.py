import torch
import torch.nn as nn
import math

class SelfAttention(nn.Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)
        
        self.dropout = nn.Dropout(dropout)
        
        for m in [self.q_proj, self.k_proj, self.v_proj, self.out_proj]:
            nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor, attention_mask: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            query, key, value: [B, T, embed_dim]
            attention_mask: [B, T] with 1 for valid, 0 for padding.
        Returns:
            [B, T, embed_dim]
        """
        B, T, _ = query.size()
        
        q = self.q_proj(query).view(B, T, self.num_heads, self.head_dim).transpose(1, 2) # [B, num_heads, T, head_dim]
        k = self.k_proj(key).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(value).view(B, T, self.num_heads, self.head_dim).transpose(1, 2)
        
        # [B, num_heads, T, T]
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if attention_mask is not None:
            # attention_mask is [B, T]
            # Convert to [B, 1, 1, T] mask where 0 means valid, -inf means padding
            # Wait, attention_mask is 1 for valid, 0 for pad.
            extended_mask = attention_mask.unsqueeze(1).unsqueeze(2) # [B, 1, 1, T]
            extended_mask = (1.0 - extended_mask) * -10000.0
            scores = scores + extended_mask
            
        attn_probs = torch.softmax(scores, dim=-1)
        attn_probs = self.dropout(attn_probs)
        
        # [B, num_heads, T, head_dim] -> [B, T, embed_dim]
        context = torch.matmul(attn_probs, v)
        context = context.transpose(1, 2).contiguous().view(B, T, self.embed_dim)
        
        out = self.out_proj(context)
        return out
