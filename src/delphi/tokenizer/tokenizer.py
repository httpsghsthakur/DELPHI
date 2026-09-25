from typing import List, Dict, Optional, Union, Any
from .vocabulary import Vocabulary
from .normalization import normalize
from .pretokenizer import PreTokenizer
from .special_tokens import PAD_ID, BOS_ID, EOS_ID
from .types import TokenizerOutput, TokenizedBatch
from .serialization import serialize_tokenizer, deserialize_tokenizer

class CustomTokenizer:
    def __init__(self, vocab: Vocabulary, config: dict):
        self.vocab = vocab
        self.config = config
        self.pretokenizer = PreTokenizer()
        
    def normalize(self, text: str) -> str:
        norm_config = self.config.get("normalization", {})
        return normalize(text, norm_config)
        
    def tokenize(self, text: str) -> List[str]:
        norm_text = self.normalize(text)
        return self.pretokenizer.pre_tokenize(norm_text)
        
    def encode(self, text: str, **kwargs) -> TokenizerOutput:
        norm_text = self.normalize(text)
        tokens = self.pretokenizer.pre_tokenize(norm_text)
        
        seq_config = self.config.get("sequence", {})
        max_length = kwargs.get("max_length", seq_config.get("max_length", 256))
        add_bos = kwargs.get("add_bos", seq_config.get("add_bos", True))
        add_eos = kwargs.get("add_eos", seq_config.get("add_eos", True))
        truncation = kwargs.get("truncation", seq_config.get("truncation", True))
        padding = kwargs.get("padding", seq_config.get("padding", "longest"))
        
        input_ids = self.vocab.encode(tokens)
        
        if add_bos:
            input_ids = [BOS_ID] + input_ids
        if add_eos:
            input_ids = input_ids + [EOS_ID]
            
        truncated = False
        if truncation and len(input_ids) > max_length:
            input_ids = input_ids[:max_length]
            if add_eos:
                input_ids[-1] = EOS_ID
            truncated = True
            
        attention_mask = [1] * len(input_ids)
        
        if padding == "max_length" and len(input_ids) < max_length:
            pad_len = max_length - len(input_ids)
            input_ids.extend([PAD_ID] * pad_len)
            attention_mask.extend([0] * pad_len)
            
        return TokenizerOutput(
            input_ids=input_ids,
            attention_mask=attention_mask,
            tokens=tokens,
            original_text=text,
            normalized_text=norm_text,
            length=len(input_ids),
            truncated=truncated
        )

    def decode(self, ids: List[int], skip_special_tokens: bool = True) -> str:
        tokens = self.vocab.decode(ids)
        if skip_special_tokens:
            from .special_tokens import SPECIAL_TOKENS_MAP
            special_ids = set(SPECIAL_TOKENS_MAP.values())
            tokens = [t for i, t in zip(ids, tokens) if i not in special_ids]
        return " ".join(tokens)
        
    def batch_encode(self, texts: List[str], **kwargs) -> TokenizedBatch:
        seq_config = self.config.get("sequence", {})
        padding = kwargs.get("padding", seq_config.get("padding", "longest"))
        
        outputs = [self.encode(text, **kwargs) for text in texts]
        
        input_ids = [out.input_ids for out in outputs]
        attention_mask = [out.attention_mask for out in outputs]
        lengths = [out.length for out in outputs]
        
        if padding == "longest":
            max_len = max(lengths) if lengths else 0
            for i in range(len(input_ids)):
                pad_len = max_len - len(input_ids[i])
                if pad_len > 0:
                    input_ids[i].extend([PAD_ID] * pad_len)
                    attention_mask[i].extend([0] * pad_len)
                    
        return TokenizedBatch(
            input_ids=input_ids,
            attention_mask=attention_mask,
            lengths=lengths
        )
        
    def save(self, path: str, version: str = "1.0.0"):
        serialize_tokenizer(self.vocab.token_map, self.config, version, path)
        
    @classmethod
    def load(cls, path: str):
        vocab_map, config, metadata = deserialize_tokenizer(path)
        vocab = Vocabulary(vocab_map)
        return cls(vocab, config)
