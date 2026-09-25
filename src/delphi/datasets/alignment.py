class AlignmentError(Exception):
    pass

def align_labels_to_tokens(raw_tokens: list, raw_labels: list, tokenizer_tokens: list) -> list:
    """
    Aligns BIO labels to tokenizer output tokens.
    DELPHI uses a custom word-level tokenizer, so in most cases, 
    one raw token corresponds to one tokenizer token.
    However, if normalization stripped or split tokens, we must track and align.
    """
    if len(raw_tokens) != len(raw_labels):
        raise AlignmentError("Raw tokens and raw labels length mismatch")
        
    aligned_labels = []
    
    # Very basic alignment for demonstration purposes
    # A real world dataset would map offsets precisely
    
    raw_idx = 0
    for t_token in tokenizer_tokens:
        if t_token in ["<BOS>", "<EOS>", "<PAD>"]:
            aligned_labels.append("O")
            continue
            
        if raw_idx < len(raw_tokens):
            aligned_labels.append(raw_labels[raw_idx])
            raw_idx += 1
        else:
            aligned_labels.append("O")
            
    return aligned_labels
