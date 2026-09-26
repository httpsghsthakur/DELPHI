from typing import List, Dict, Any
from .dataset import SequenceExample, construct_sequences_with_temporal_guard
from .model import CausalSeq
from .generation import generate_beam_search
import torch

class CausalSeqBacktester:
    def __init__(self, model: CausalSeq, raw_historical_events: List[Dict[str, Any]], max_context: int, max_forecast: int):
        """
        Backtesting infrastructure that explicitly prevents future leakage.
        """
        self.model = model
        self.raw_events = sorted(raw_historical_events, key=lambda x: (x["timestamp"], x.get("event_id", "")))
        self.max_context = max_context
        self.max_forecast = max_forecast
        
    def evaluate_cutoffs(self, cutoffs: List[str]) -> Dict[str, Any]:
        """
        Evaluates the model by pretending we are exactly at each cutoff in time.
        """
        results = {}
        
        for cutoff in cutoffs:
            # 0. Check checkpoint provenance
            prov = getattr(self.model.config, 'checkpoint_training_end_time', "")
            if prov and prov > cutoff:
                results[cutoff] = {
                    "matched_next_event": False,
                    "leakage_validation_status": "STRICT_TEMPORAL_BACKTEST_UNVERIFIED",
                    "error": f"Checkpoint end time {prov} is after cutoff {cutoff}"
                }
                continue
                
            # 1. Construct context strictly <= cutoff
            allowed_events = [e for e in self.raw_events if e["timestamp"] <= cutoff]
            if len(allowed_events) < 2:
                continue
                
            # 2. Get actual subsequent events
            future_events = [e for e in self.raw_events if e["timestamp"] > cutoff]
            if not future_events:
                continue
                
            # Take last max_context events
            context_events = allowed_events[-self.max_context:]
            
            src_list = [e["embedding"] for e in context_events]
            while len(src_list) < self.max_context:
                src_list.insert(0, torch.zeros(256))
                
            src = torch.stack(src_list).unsqueeze(0).to(self.model.encoder.lstm.weight_ih_l0.device)
            src_mask = torch.ones(1, self.max_context, dtype=torch.bool, device=src.device)
            # handle padding mask if we added zeros
            pad_count = self.max_context - len(context_events)
            if pad_count > 0:
                src_mask[0, :pad_count] = False
                
            # 3. Generate future candidates
            pred = generate_beam_search(self.model, src, src_mask, self.max_forecast, beam_width=3)
            
            # 4. Compare
            # Simplified evaluation: just check if first predicted event type matches actual next event type
            actual_next = future_events[0]
            pred_next_type = pred["event_type"][0].item() if len(pred["event_type"]) > 0 else -1
            
            match = (pred_next_type == actual_next.get("event_type", -2))
            
            results[cutoff] = {
                "matched_next_event": match,
                "predicted_sequence": pred["event_type"].tolist(),
                "actual_next_type": actual_next.get("event_type"),
                "sequence_score": pred["sequence_score"]
            }
            
        return results
