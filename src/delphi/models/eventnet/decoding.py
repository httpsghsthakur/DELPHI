from typing import List, Dict, Any
from .labels import ID_TO_BIO, ID_TO_EVENT_TYPE

def extract_spans(token_ids: List[int], tokens: List[str], offsets: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Extracts continuous spans from BIO predicted token IDs.
    """
    spans = []
    current_span = None
    
    for i, tag_id in enumerate(token_ids):
        tag = ID_TO_BIO.get(tag_id, "O")
        
        if tag.startswith("B-"):
            if current_span:
                spans.append(current_span)
            span_type = tag[2:]
            current_span = {
                "type": span_type,
                "start_token": i,
                "end_token": i,
                "text": tokens[i] if i < len(tokens) else ""
            }
            if offsets and i < len(offsets):
                current_span["start_char"] = offsets[i].get("start", 0)
                current_span["end_char"] = offsets[i].get("end", 0)
                
        elif tag.startswith("I-"):
            span_type = tag[2:]
            if current_span and current_span["type"] == span_type:
                current_span["end_token"] = i
                current_span["text"] += " " + (tokens[i] if i < len(tokens) else "")
                if offsets and i < len(offsets):
                    current_span["end_char"] = offsets[i].get("end", 0)
            else:
                # Invalid I- tag without a B- tag, sometimes we treat as B- or ignore. Let's ignore for strictness.
                pass
        else:
            if current_span:
                spans.append(current_span)
                current_span = None
                
    if current_span:
        spans.append(current_span)
        
    return spans

def decode_predictions(
    token_logits: List[List[float]], 
    event_logits: List[float],
    tokens: List[str],
    offsets: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    
    import torch
    
    # Argmax
    token_preds = torch.tensor(token_logits).argmax(dim=-1).tolist()
    event_pred = torch.tensor(event_logits).argmax(dim=-1).item()
    
    event_type = ID_TO_EVENT_TYPE.get(event_pred, "UNKNOWN")
    spans = extract_spans(token_preds, tokens, offsets)
    
    actors = [s for s in spans if s["type"] == "ACTOR"]
    actions = [s for s in spans if s["type"] == "ACTION"]
    targets = [s for s in spans if s["type"] == "TARGET"]
    locations = [s for s in spans if s["type"] == "LOCATION"]
    times = [s for s in spans if s["type"] == "TIME"]
    causes = [s for s in spans if s["type"] == "CAUSE"]
    triggers = [s for s in spans if s["type"] == "EVENT_TRIGGER"]
    
    return {
        "event_type": event_type,
        "trigger": triggers[0] if triggers else {},
        "actors": actors,
        "actions": actions,
        "targets": targets,
        "locations": locations,
        "times": times,
        "causes": causes,
        "spans": spans
    }
