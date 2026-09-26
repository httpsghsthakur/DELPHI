import torch
from typing import Dict
from sklearn.metrics import accuracy_score, f1_score

def compute_sequence_metrics(preds: Dict[str, torch.Tensor], targets: Dict[str, torch.Tensor], mask: torch.Tensor, pad_idx: int) -> Dict[str, float]:
    """
    Computes top-1 metrics on valid positions.
    preds: dict of (batch, seq, vocab)
    targets: dict of (batch, seq)
    """
    metrics = {}
    
    # Flatten and mask
    valid_mask = mask.view(-1).cpu().numpy()
    
    def get_valid(pred_tensor, target_tensor):
        p = pred_tensor.argmax(dim=-1).view(-1).cpu().numpy()
        t = target_tensor.view(-1).cpu().numpy()
        # Also ignore BOS/EOS/PAD tokens for pure accuracy
        valid = valid_mask & (t < pad_idx)
        return p[valid], t[valid]
        
    p_evt, t_evt = get_valid(preds["event_type"], targets["event_type"])
    if len(t_evt) > 0:
        metrics["event_acc_top1"] = accuracy_score(t_evt, p_evt)
        metrics["event_macro_f1"] = f1_score(t_evt, p_evt, average="macro", zero_division=0)
    else:
        metrics["event_acc_top1"] = 0.0
        metrics["event_macro_f1"] = 0.0
        
    p_time, t_time = get_valid(preds["time_bin"], targets["time_bin"])
    if len(t_time) > 0:
        metrics["time_acc_top1"] = accuracy_score(t_time, p_time)
    else:
        metrics["time_acc_top1"] = 0.0
        
    # Recall@3 for events
    if len(t_evt) > 0:
        # Get top 3
        probs = torch.softmax(preds["event_type"], dim=-1)
        top3_preds = probs.topk(3, dim=-1)[1].view(-1, 3).cpu().numpy()
        t_evt_full = targets["event_type"].view(-1).cpu().numpy()
        valid = valid_mask & (t_evt_full < pad_idx)
        
        top3_preds = top3_preds[valid]
        t_evt_full = t_evt_full[valid]
        
        correct = 0
        for i in range(len(t_evt_full)):
            if t_evt_full[i] in top3_preds[i]:
                correct += 1
        metrics["event_recall_at_3"] = correct / max(len(t_evt_full), 1)
    else:
        metrics["event_recall_at_3"] = 0.0

    # Probabilistic metrics
    if len(t_evt) > 0:
        probs = torch.softmax(preds["event_type"], dim=-1)
        valid_probs = probs.view(-1, probs.size(-1))[valid]
        
        # NLL
        log_probs = torch.log(valid_probs + 1e-9)
        # Gather the log prob of the actual target
        nll = -log_probs.gather(1, t_evt_full[valid].unsqueeze(1)).mean().item()
        if torch.isnan(torch.tensor(nll)):
            metrics["event_nll"] = "undefined"
        else:
            metrics["event_nll"] = nll
            
        # Brier (multiclass equivalent)
        # (prob - 1)^2 for correct class + sum(prob^2) for incorrect classes
        one_hot = torch.zeros_like(valid_probs).scatter_(1, t_evt_full[valid].unsqueeze(1), 1.0)
        brier = torch.mean(torch.sum((valid_probs - one_hot) ** 2, dim=1)).item()
        metrics["event_brier"] = brier
    else:
        metrics["event_nll"] = "undefined"
        metrics["event_brier"] = "undefined"

    return metrics
