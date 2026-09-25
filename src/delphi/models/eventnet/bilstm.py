import torch
import torch.nn as nn
from .config import BiLSTMConfig

class BiLSTM(nn.Module):
    def __init__(self, input_dim: int, config: BiLSTMConfig):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=config.hidden_size,
            num_layers=config.num_layers,
            bidirectional=config.bidirectional,
            batch_first=True,
            dropout=config.dropout if config.num_layers > 1 else 0.0
        )
        self.output_dim = config.hidden_size * 2 if config.bidirectional else config.hidden_size
        
        # Init weights appropriately
        for name, param in self.lstm.named_parameters():
            if 'weight_ih' in name:
                nn.init.xavier_uniform_(param.data)
            elif 'weight_hh' in name:
                nn.init.orthogonal_(param.data)
            elif 'bias' in name:
                nn.init.zeros_(param.data)
                # LSTM forget gate bias usually initialized to 1
                n = param.size(0)
                param.data[n//4:n//2].fill_(1.0)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            x: [B, T, input_dim]
            mask: [B, T] of 1s (valid) and 0s (padding)
        """
        # Pack padded sequence if mask is provided to save computation (optional)
        # For simplicity and given self-attention handles masks later, we can just run LSTM
        # over the whole sequence, but we can also use pack_padded_sequence.
        
        if mask is not None:
            lengths = mask.sum(dim=1).cpu()
            # Enforce lengths > 0 to avoid crash
            lengths = torch.clamp(lengths, min=1).int()
            
            packed = nn.utils.rnn.pack_padded_sequence(
                x, lengths, batch_first=True, enforce_sorted=False
            )
            out_packed, _ = self.lstm(packed)
            out, _ = nn.utils.rnn.pad_packed_sequence(
                out_packed, batch_first=True, total_length=x.size(1)
            )
            return out
        else:
            out, _ = self.lstm(x)
            return out
