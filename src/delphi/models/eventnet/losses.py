import torch
import torch.nn as nn
from typing import Dict, Optional

class EventNetLoss(nn.Module):
    def __init__(self, num_token_labels: int, lambda_event: float = 1.0, class_weights: Optional[torch.Tensor] = None):
        super().__init__()
        self.num_token_labels = num_token_labels
        self.lambda_event = lambda_event
        
        # ignore_index=-100 allows us to skip padded positions
        self.token_criterion = nn.CrossEntropyLoss(weight=class_weights, ignore_index=-100)
        self.event_criterion = nn.CrossEntropyLoss()

    def forward(
        self, 
        token_logits: torch.Tensor, 
        token_labels: torch.Tensor, 
        event_logits: torch.Tensor, 
        event_labels: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Args:
            token_logits: [B, T, num_token_labels]
            token_labels: [B, T] (padding should be -100)
            event_logits: [B, num_event_types]
            event_labels: [B]
        """
        # Reshape for cross entropy
        # token_logits: [B * T, num_token_labels]
        # token_labels: [B * T]
        token_loss = self.token_criterion(
            token_logits.view(-1, self.num_token_labels),
            token_labels.view(-1)
        )
        
        event_loss = self.event_criterion(event_logits, event_labels)
        
        total_loss = token_loss + self.lambda_event * event_loss
        
        return {
            "loss": total_loss,
            "token_loss": token_loss,
            "event_loss": event_loss
        }
