import torch
import torch.nn as nn
from typing import Dict, Optional

from .config import EventNetConfig
from .bilstm import BiLSTM
from .attention import SelfAttention
from .heads import TokenClassificationHead, EventClassificationHead

class EventNet(nn.Module):
    def __init__(self, config: EventNetConfig):
        super().__init__()
        self.config = config
        
        # 1. BiLSTM Layer
        self.bilstm = BiLSTM(config.input_dim, config.bilstm)
        lstm_out_dim = self.bilstm.output_dim
        
        # 2. Self-Attention Layer
        self.attention = SelfAttention(
            embed_dim=lstm_out_dim,
            num_heads=config.attention.num_heads,
            dropout=config.attention.dropout
        )
        
        # 3. Heads
        self.token_head = TokenClassificationHead(lstm_out_dim, config.num_token_labels)
        self.event_head = EventClassificationHead(lstm_out_dim, config.num_event_types)
        
    def forward(self, embeddings: torch.Tensor, attention_mask: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Args:
            embeddings: [B, T, input_dim] from EventEmbed
            attention_mask: [B, T] 1 for valid, 0 for pad
        Returns:
            Dict containing token_logits and event_logits
        """
        # [B, T, lstm_out_dim]
        lstm_out = self.bilstm(embeddings, mask=attention_mask)
        
        # [B, T, lstm_out_dim]
        attn_out = self.attention(
            query=lstm_out,
            key=lstm_out,
            value=lstm_out,
            attention_mask=attention_mask
        )
        
        # Add residual connection
        context_out = lstm_out + attn_out
        
        # [B, T, num_token_labels]
        token_logits = self.token_head(context_out)
        
        # [B, num_event_types]
        event_logits = self.event_head(context_out, mask=attention_mask)
        
        return {
            "token_logits": token_logits,
            "event_logits": event_logits
        }
        
    def count_parameters(self) -> dict:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total": total, "trainable": trainable}
