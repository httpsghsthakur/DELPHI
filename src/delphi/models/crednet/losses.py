import torch
import torch.nn as nn

class CredibilityLoss(nn.Module):
    def __init__(self, pos_weight: float = None):
        super().__init__()
        # Binary Cross Entropy with Logits for numerical stability
        pos_weight_tensor = torch.tensor([pos_weight]) if pos_weight is not None else None
        self.criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)
        
    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return self.criterion(logits, targets)
