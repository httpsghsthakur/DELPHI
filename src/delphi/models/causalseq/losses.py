import torch
import torch.nn as nn
from .config import CausalSeqConfig

class CausalSeqLoss(nn.Module):
    def __init__(self, config: CausalSeqConfig):
        super().__init__()
        self.config = config
        
        self.ce_event = nn.CrossEntropyLoss(ignore_index=config.num_event_types) # PAD_IDX
        self.ce_time = nn.CrossEntropyLoss(ignore_index=config.num_time_bins) # TIME_PAD_IDX
        
        # for actor, target, domain, missing labels might exist. We'll use cross entropy and ignore -1
        self.ce_generic = nn.CrossEntropyLoss(ignore_index=-1)
        
    def forward(self, preds, targets, mask):
        """
        preds: dict of (batch, seq_len, vocab_size)
        targets: dict of (batch, seq_len)
        mask: (batch, seq_len)
        """
        # We only compute loss on valid mask positions, but ignore_index in CrossEntropyLoss handles padding too
        # preds['event_type'] is (batch, seq, vocab) -> needs (batch*seq, vocab)
        
        def compute_ce(pred, target, ce_fn):
            l = ce_fn(pred.reshape(-1, pred.size(-1)), target.reshape(-1))
            if torch.isnan(l):
                return torch.tensor(0.0, device=pred.device, requires_grad=True)
            return l
            
        loss_evt = compute_ce(preds["event_type"], targets["event_type"], self.ce_event)
        loss_time = compute_ce(preds["time_bin"], targets["time_bin"], self.ce_time)
        
        # Replace 0 with -1 where target is missing if 0 means 'unknown' or just ignore if it's not present
        loss_actor = compute_ce(preds["actor"], targets["actor"], self.ce_generic)
        loss_target = compute_ce(preds["target"], targets["target"], self.ce_generic)
        loss_domain = compute_ce(preds["domain"], targets["domain"], self.ce_generic)
        
        total = (
            self.config.lambda_event_type * loss_evt +
            self.config.lambda_time * loss_time +
            self.config.lambda_actor * loss_actor +
            self.config.lambda_target * loss_target +
            self.config.lambda_domain * loss_domain
        )
        
        return total, {
            "event": loss_evt.item(),
            "time": loss_time.item(),
            "actor": loss_actor.item(),
            "target": loss_target.item(),
            "domain": loss_domain.item()
        }
