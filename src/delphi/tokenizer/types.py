from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class TokenizerOutput:
    input_ids: List[int]
    attention_mask: List[int]
    tokens: List[str]
    original_text: str
    normalized_text: str
    length: int
    truncated: bool
    offsets: Optional[List[Dict[str, Any]]] = None

@dataclass
class TokenizedBatch:
    input_ids: List[List[int]]
    attention_mask: List[List[int]]
    lengths: List[int]
