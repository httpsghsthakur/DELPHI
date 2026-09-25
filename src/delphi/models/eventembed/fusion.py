import torch
import torch.nn as nn

class FusionLayer(nn.Module):
    def __init__(self, word_dim: int, char_dim: int, output_dim: int, strategy: str = "concat_projection"):
        super().__init__()
        self.strategy = strategy
        
        if self.strategy == "concat_projection":
            self.net = nn.Sequential(
                nn.Linear(word_dim + char_dim, output_dim),
                nn.GELU(),
                nn.LayerNorm(output_dim)
            )
            for m in self.net.modules():
                if isinstance(m, nn.Linear):
                    nn.init.xavier_uniform_(m.weight)
                    if m.bias is not None:
                        nn.init.zeros_(m.bias)
        else:
            raise ValueError(f"Unknown fusion strategy: {strategy}")

    def forward(self, word_repr: torch.Tensor, char_repr: torch.Tensor) -> torch.Tensor:
        """
        Args:
            word_repr: [batch_size, seq_len, word_dim]
            char_repr: [batch_size, seq_len, char_dim]
        Returns:
            [batch_size, seq_len, output_dim]
        """
        if self.strategy == "concat_projection":
            combined = torch.cat([word_repr, char_repr], dim=-1)
            return self.net(combined)
