from typing import List, Dict
from collections import Counter
from .special_tokens import SPECIAL_TOKENS, SPECIAL_TOKENS_MAP

class Vocabulary:
    def __init__(self, token_to_id: Dict[str, int]):
        self._token_to_id = token_to_id
        self._id_to_token = {idx: token for token, idx in token_to_id.items()}

    def token_to_id(self, token: str) -> int:
        return self._token_to_id.get(token, SPECIAL_TOKENS_MAP["<UNK>"])

    def id_to_token(self, idx: int) -> str:
        return self._id_to_token.get(idx, "<UNK>")

    def encode(self, tokens: List[str]) -> List[int]:
        return [self.token_to_id(t) for t in tokens]

    def decode(self, ids: List[int]) -> List[str]:
        return [self.id_to_token(i) for i in ids]

    def contains(self, token: str) -> bool:
        return token in self._token_to_id

    def size(self) -> int:
        return len(self._token_to_id)
    
    @property
    def token_map(self) -> Dict[str, int]:
        return self._token_to_id

class VocabularyBuilder:
    def __init__(self, min_frequency: int = 2, max_size: int = 50000):
        self.min_frequency = min_frequency
        self.max_size = max_size

    def build(self, tokenized_corpus: List[List[str]]) -> Vocabulary:
        counter = Counter()
        for doc in tokenized_corpus:
            counter.update(doc)
            
        # Filter by min frequency
        valid_tokens = {token: count for token, count in counter.items() if count >= self.min_frequency}
        
        # Sort deterministicly: frequency descending, then lexical ascending
        sorted_tokens = sorted(valid_tokens.items(), key=lambda x: (-x[1], x[0]))
        
        # Reserve special tokens
        token_to_id = SPECIAL_TOKENS_MAP.copy()
        current_id = len(SPECIAL_TOKENS)
        
        for token, _ in sorted_tokens:
            if current_id >= self.max_size:
                break
            if token not in token_to_id:
                token_to_id[token] = current_id
                current_id += 1
                
        return Vocabulary(token_to_id)
