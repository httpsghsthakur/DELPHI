import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any

class EventNetDataset(Dataset):
    def __init__(self, tokenized_data: List[Dict[str, Any]], pad_token_id: int = 0, pad_label_id: int = -100):
        """
        tokenized_data should be a list of dicts with:
        - input_ids: List[int]
        - char_ids: List[List[int]]
        - attention_mask: List[int]
        - token_labels: List[int]
        - event_label: int
        """
        self.data = tokenized_data
        self.pad_token_id = pad_token_id
        self.pad_label_id = pad_label_id

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

def collate_eventnet(batch, pad_token_id=0, pad_label_id=-100):
    # Padding sequences for input_ids, char_ids, attention_mask, token_labels
    
    max_seq_len = max(len(x["input_ids"]) for x in batch)
    
    # Calculate global max_char_len
    max_char_len = 0
    for x in batch:
        if x["char_ids"]:
            curr_max = max(len(chars) for chars in x["char_ids"])
            if curr_max > max_char_len:
                max_char_len = curr_max
                
    # Ensure max_char_len is at least 5 to prevent CNN kernel crashes on very short batches
    max_char_len = max(max_char_len, 5)
                
    batch_input_ids = []
    batch_char_ids = []
    batch_attention_mask = []
    batch_token_labels = []
    batch_event_labels = []
    
    for item in batch:
        seq_len = len(item["input_ids"])
        pad_len = max_seq_len - seq_len
        
        batch_input_ids.append(item["input_ids"] + [pad_token_id] * pad_len)
        batch_attention_mask.append(item["attention_mask"] + [0] * pad_len)
        batch_token_labels.append(item["token_labels"] + [pad_label_id] * pad_len)
        batch_event_labels.append(item["event_label"])
        
        # Char IDs
        char_seq = []
        for chars in item["char_ids"]:
            char_pad = max_char_len - len(chars)
            char_seq.append(chars + [0] * char_pad)
        # padding for sequence length
        for _ in range(pad_len):
            char_seq.append([0] * max_char_len)
        batch_char_ids.append(char_seq)
        
    return {
        "input_ids": torch.tensor(batch_input_ids, dtype=torch.long),
        "char_ids": torch.tensor(batch_char_ids, dtype=torch.long),
        "attention_mask": torch.tensor(batch_attention_mask, dtype=torch.long),
        "token_labels": torch.tensor(batch_token_labels, dtype=torch.long),
        "event_labels": torch.tensor(batch_event_labels, dtype=torch.long)
    }
