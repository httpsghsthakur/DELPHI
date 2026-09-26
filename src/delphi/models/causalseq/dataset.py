import torch
from torch.utils.data import Dataset
from typing import List, Dict, Tuple
from datetime import datetime
from .schemas import FutureEventPrediction

class SequenceExample:
    def __init__(self, context_events: List[torch.Tensor], context_mask: List[bool], target_events: List[Dict[str, int]], target_mask: List[bool], cutoff_timestamp: str):
        self.context_events = context_events # list of (256,)
        self.context_mask = context_mask
        self.target_events = target_events
        self.target_mask = target_mask
        self.cutoff_timestamp = cutoff_timestamp

class CausalSeqDataset(Dataset):
    def __init__(self, examples: List[SequenceExample]):
        self.examples = examples
        
    def __len__(self):
        return len(self.examples)
        
    def __getitem__(self, idx):
        ex = self.examples[idx]
        
        src = torch.stack(ex.context_events) # (max_ctx, 256)
        src_mask = torch.tensor(ex.context_mask, dtype=torch.bool)
        
        # targets
        tgt_len = len(ex.target_events)
        tgt_evt = torch.zeros(tgt_len, dtype=torch.long)
        tgt_time = torch.zeros(tgt_len, dtype=torch.long)
        tgt_actor = torch.zeros(tgt_len, dtype=torch.long)
        tgt_target = torch.zeros(tgt_len, dtype=torch.long)
        tgt_domain = torch.zeros(tgt_len, dtype=torch.long)
        tgt_mask = torch.tensor(ex.target_mask, dtype=torch.bool)
        
        for i, ev in enumerate(ex.target_events):
            tgt_evt[i] = ev.get("event_type", 0)
            tgt_time[i] = ev.get("time_bin", 0)
            tgt_actor[i] = ev.get("actor", 0)
            tgt_target[i] = ev.get("target", 0)
            tgt_domain[i] = ev.get("domain", 0)
            
        return src, src_mask, tgt_evt, tgt_time, tgt_actor, tgt_target, tgt_domain, tgt_mask

def construct_sequences_with_temporal_guard(raw_events: List[Dict], max_context: int, max_forecast: int, pad_idx: int, time_pad_idx: int = 9) -> List[SequenceExample]:
    """
    Constructs train examples strictly forbidding temporal leakage.
    raw_events: List of dicts representing events, must have 'timestamp'.
    """
    # Deterministic chronological sort with ID tie-breaker
    raw_events.sort(key=lambda x: (x["timestamp"], x.get("event_id", "")))
    
    examples = []
    
    # Simple sliding window for demonstration
    for i in range(len(raw_events) - 1):
        cutoff_time = raw_events[i]["timestamp"]
        
        context = []
        c_mask = []
        for j in range(max(0, i - max_context + 1), i + 1):
            if raw_events[j]["timestamp"] > cutoff_time:
                raise ValueError("Temporal Leakage detected during sequence construction")
            context.append(raw_events[j]["embedding"])
            c_mask.append(True)
            
        # Pad context
        while len(context) < max_context:
            context.insert(0, torch.zeros(256)) # Pre-pad
            c_mask.insert(0, False)
            
        targets = []
        t_mask = []
        # BOS
        targets.append({"event_type": pad_idx+1, "time_bin": time_pad_idx+1, "actor": 0, "target": 0, "domain": 0})
        t_mask.append(True)
        
        # Collect strictly future events (up to max_forecast - 2 to leave room for BOS and EOS)
        for j in range(i + 1, min(i + 1 + max_forecast - 2, len(raw_events))):
            if raw_events[j]["timestamp"] <= cutoff_time:
                raise ValueError("Temporal Leakage: Target event is before or at cutoff")
            targets.append(raw_events[j])
            t_mask.append(True)
            
        # EOS
        targets.append({"event_type": pad_idx+2, "time_bin": time_pad_idx+2, "actor": 0, "target": 0, "domain": 0})
        t_mask.append(True)
        
        # Pad targets
        while len(targets) < max_forecast:
            targets.append({"event_type": pad_idx, "time_bin": time_pad_idx, "actor": 0, "target": 0, "domain": 0})
            t_mask.append(False)
            
        examples.append(SequenceExample(context, c_mask, targets, t_mask, cutoff_time))
        
    return examples

def create_causal_temporal_split(examples: List[SequenceExample], val_ratio: float = 0.1, test_ratio: float = 0.1):
    # Sort strictly by cutoff timestamp
    examples.sort(key=lambda x: x.cutoff_timestamp)
    
    total = len(examples)
    train_end = int(total * (1.0 - val_ratio - test_ratio))
    val_end = int(total * (1.0 - test_ratio))
    
    train_ex = examples[:train_end]
    val_ex = examples[train_end:val_end]
    test_ex = examples[val_end:]
    
    if train_ex and val_ex:
        assert train_ex[-1].cutoff_timestamp <= val_ex[0].cutoff_timestamp, "Temporal leak"
    if val_ex and test_ex:
        assert val_ex[-1].cutoff_timestamp <= test_ex[0].cutoff_timestamp, "Temporal leak"
        
    return CausalSeqDataset(train_ex), CausalSeqDataset(val_ex), CausalSeqDataset(test_ex)
