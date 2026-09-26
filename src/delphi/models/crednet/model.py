import torch
import torch.nn as nn

class CredNet(nn.Module):
    """
    CredNet: A 12-dimensional source credibility MLP model.
    Architecture:
    Linear(12, 32) -> GELU -> Linear(32, 16) -> GELU -> Linear(16, 1)
    Outputs raw logits.
    """
    def __init__(self, input_dim: int = 12):
        super(CredNet, self).__init__()
        
        if input_dim != 12:
            raise ValueError("CredNet strictly requires exactly 12 input features.")
            
        self.fc1 = nn.Linear(input_dim, 32)
        self.act1 = nn.GELU()
        self.fc2 = nn.Linear(32, 16)
        self.act2 = nn.GELU()
        self.out = nn.Linear(16, 1)
        
        # Initialize weights deterministically if seeds are set
        self._init_weights()
        
    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
                    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        x: (batch_size, 12)
        returns: (batch_size, 1) raw logits
        """
        x = self.fc1(x)
        x = self.act1(x)
        x = self.fc2(x)
        x = self.act2(x)
        logits = self.out(x)
        return logits
