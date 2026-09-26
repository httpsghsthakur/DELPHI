import torch
from .model import CausalSeq
from typing import List, Dict

class BeamState:
    def __init__(self, seq_event_type, seq_time_bin, log_prob, hidden, is_finished=False):
        self.seq_event_type = seq_event_type # list
        self.seq_time_bin = seq_time_bin # list
        self.log_prob = log_prob # float
        self.hidden = hidden # Tuple[tensor, tensor]
        self.is_finished = is_finished
        
def generate_greedy(model: CausalSeq, src: torch.Tensor, src_mask: torch.Tensor, max_len: int) -> Dict[str, torch.Tensor]:
    """
    Deterministic greedy decoding.
    """
    model.eval()
    batch_size = src.size(0)
    device = src.device
    
    with torch.no_grad():
        encoder_outputs, hidden = model.encoder(src, src_mask)
        
        prev_evt = torch.full((batch_size,), model.BOS_IDX, dtype=torch.long, device=device)
        prev_time = torch.full((batch_size,), model.TIME_BOS_IDX, dtype=torch.long, device=device)
        
        generated_evts = []
        generated_times = []
        
        for _ in range(max_len):
            preds, hidden, _ = model.decoder(prev_evt, prev_time, hidden, encoder_outputs, src_mask)
            
            prev_evt = preds["event_type"].argmax(dim=-1)
            prev_time = preds["time_bin"].argmax(dim=-1)
            
            generated_evts.append(prev_evt)
            generated_times.append(prev_time)
            
            # Stop if all EOS
            if (prev_evt == model.EOS_IDX).all():
                break
                
        return {
            "event_type": torch.stack(generated_evts, dim=1),
            "time_bin": torch.stack(generated_times, dim=1)
        }

def generate_beam_search(model: CausalSeq, src: torch.Tensor, src_mask: torch.Tensor, max_len: int, beam_width: int = 3):
    """
    Deterministic beam search for batch_size=1
    """
    model.eval()
    assert src.size(0) == 1, "Beam search currently supports batch_size=1"
    device = src.device
    
    with torch.no_grad():
        encoder_outputs, init_hidden = model.encoder(src, src_mask)
        
        initial_state = BeamState(
            seq_event_type=[model.BOS_IDX],
            seq_time_bin=[model.TIME_BOS_IDX],
            log_prob=0.0,
            hidden=init_hidden
        )
        
        beams = [initial_state]
        
        for step in range(max_len):
            new_beams = []
            for b in beams:
                if b.is_finished:
                    new_beams.append(b)
                    continue
                    
                prev_evt = torch.tensor([b.seq_event_type[-1]], dtype=torch.long, device=device)
                prev_time = torch.tensor([b.seq_time_bin[-1]], dtype=torch.long, device=device)
                
                preds, new_hidden, _ = model.decoder(prev_evt, prev_time, b.hidden, encoder_outputs, src_mask)
                
                # Top-K for event_type
                log_probs_evt = torch.log_softmax(preds["event_type"], dim=-1)[0]
                topk_probs_evt, topk_idx_evt = log_probs_evt.topk(beam_width)
                
                # Greedy for time_bin based on this state
                best_time = preds["time_bin"].argmax(dim=-1)[0].item()
                
                for k in range(beam_width):
                    evt_idx = topk_idx_evt[k].item()
                    prob = topk_probs_evt[k].item()
                    
                    is_finished = (evt_idx == model.EOS_IDX)
                    
                    new_state = BeamState(
                        seq_event_type=b.seq_event_type + [evt_idx],
                        seq_time_bin=b.seq_time_bin + [best_time],
                        log_prob=b.log_prob + prob,
                        hidden=new_hidden,
                        is_finished=is_finished
                    )
                    new_beams.append(new_state)
                    
            # Length normalization rule: log_prob / length
            # Deterministic tie-breaking by sorting sequence arrays if log_probs are equal
            new_beams.sort(key=lambda x: (x.log_prob / len(x.seq_event_type), x.seq_event_type), reverse=True)
            beams = new_beams[:beam_width]
            
            if all(b.is_finished for b in beams):
                break
                
        best_beam = beams[0]
        return {
            "event_type": torch.tensor(best_beam.seq_event_type[1:]), # skip BOS
            "time_bin": torch.tensor(best_beam.seq_time_bin[1:]),
            "sequence_score": best_beam.log_prob / len(best_beam.seq_event_type)
        }
