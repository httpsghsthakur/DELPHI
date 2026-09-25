import torch
from torch.utils.data import Dataset
from typing import List, Dict
import numpy as np

class SkipGramDataset(Dataset):
    def __init__(self, tokenized_sequences: List[List[int]], context_window: int, pad_idx: int = 0):
        self.pairs = []
        self.context_window = context_window
        
        # Generate skip-gram pairs
        for seq in tokenized_sequences:
            seq_len = len(seq)
            for i in range(seq_len):
                target = seq[i]
                if target == pad_idx:
                    continue
                    
                # Context window boundaries
                start = max(0, i - context_window)
                end = min(seq_len, i + context_window + 1)
                
                for j in range(start, end):
                    if i != j and seq[j] != pad_idx:
                        self.pairs.append((target, seq[j]))
                        
    def __len__(self):
        return len(self.pairs)
        
    def __getitem__(self, idx):
        target, context = self.pairs[idx]
        return target, context

def collate_skipgram(batch):
    targets = torch.tensor([item[0] for item in batch], dtype=torch.long)
    contexts = torch.tensor([item[1] for item in batch], dtype=torch.long)
    return targets, contexts
