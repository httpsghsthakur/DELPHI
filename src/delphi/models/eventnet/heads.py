import torch
import torch.nn as nn

class TokenClassificationHead(nn.Module):
    def __init__(self, input_dim: int, num_labels: int):
        super().__init__()
        self.classifier = nn.Linear(input_dim, num_labels)
        nn.init.xavier_uniform_(self.classifier.weight)
        if self.classifier.bias is not None:
            nn.init.zeros_(self.classifier.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: [B, T, input_dim]
        Returns:
            logits: [B, T, num_labels]
        """
        return self.classifier(x)

class EventClassificationHead(nn.Module):
    def __init__(self, input_dim: int, num_event_types: int):
        super().__init__()
        self.classifier = nn.Linear(input_dim, num_event_types)
        nn.init.xavier_uniform_(self.classifier.weight)
        if self.classifier.bias is not None:
            nn.init.zeros_(self.classifier.bias)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        """
        Args:
            x: [B, T, input_dim]
            mask: [B, T]
        Returns:
            logits: [B, num_event_types]
        """
        if mask is not None:
            # Masked mean pooling
            mask_expanded = mask.unsqueeze(-1).float()
            sum_x = torch.sum(x * mask_expanded, dim=1)
            sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
            pooled = sum_x / sum_mask
        else:
            pooled = torch.mean(x, dim=1)
            
        return self.classifier(pooled)
