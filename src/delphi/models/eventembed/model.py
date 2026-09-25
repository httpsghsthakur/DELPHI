import torch
import torch.nn as nn
from typing import Dict, Any

from .word_embedding import WordEmbedding
from .char_encoder import CharacterCNN
from .fusion import FusionLayer
from .config import EventEmbedConfig

class EventEmbed(nn.Module):
    def __init__(self, config: EventEmbedConfig, char_vocab_size: int, pad_idx: int = 0, char_pad_idx: int = 0):
        super().__init__()
        self.config = config
        self.pad_idx = pad_idx
        
        self.word_embedding = WordEmbedding(
            vocab_size=config.vocab_size,
            embedding_dim=config.word_embedding_dim,
            pad_idx=pad_idx
        )
        
        filters = [{"kernel_size": f.kernel_size, "channels": f.channels} for f in config.character.filters]
        
        self.char_encoder = CharacterCNN(
            vocab_size=char_vocab_size,
            embedding_dim=config.character.embedding_dim,
            filters=filters,
            output_dim=config.character.output_dim,
            pad_idx=char_pad_idx
        )
        
        self.fusion = FusionLayer(
            word_dim=config.word_embedding_dim,
            char_dim=config.character.output_dim,
            output_dim=config.output_dim,
            strategy=config.fusion.strategy
        )

    def forward(self, input_ids: torch.Tensor, char_ids: torch.Tensor, attention_mask: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Args:
            input_ids: [batch_size, seq_len]
            char_ids: [batch_size, seq_len, max_char_len]
            attention_mask: [batch_size, seq_len] (optional, 1 for real, 0 for pad)
        Returns:
            dict with 'token_embeddings' [batch_size, seq_len, output_dim] and 
            'sequence_embedding' [batch_size, output_dim]
        """
        word_repr = self.word_embedding(input_ids)
        char_repr = self.char_encoder(char_ids)
        
        token_embeddings = self.fusion(word_repr, char_repr)
        
        # Sequence representation via masked mean pooling
        if attention_mask is not None:
            # [batch_size, seq_len, 1]
            mask_expanded = attention_mask.unsqueeze(-1).float()
            # [batch_size, output_dim]
            sum_embeddings = torch.sum(token_embeddings * mask_expanded, dim=1)
            sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
            sequence_embedding = sum_embeddings / sum_mask
        else:
            sequence_embedding = torch.mean(token_embeddings, dim=1)
            
        return {
            "token_embeddings": token_embeddings,
            "sequence_embedding": sequence_embedding
        }
        
    def count_parameters(self) -> dict:
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        return {"total": total, "trainable": trainable}
