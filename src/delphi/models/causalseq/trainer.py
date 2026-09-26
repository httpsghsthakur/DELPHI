import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional
import os
import json

from .model import CausalSeq
from .config import CausalSeqConfig
from .losses import CausalSeqLoss
from .metrics import compute_sequence_metrics

class CausalSeqTrainer:
    def __init__(self, config: CausalSeqConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CausalSeq(config).to(self.device)
        self.criterion = CausalSeqLoss(config).to(self.device)
        self.optimizer = optim.AdamW(self.model.parameters(), lr=config.learning_rate)
        
    def train(self, train_loader: DataLoader, val_loader: DataLoader, epochs: int = 10) -> Dict[str, Any]:
        best_val_loss = float('inf')
        best_model_state = None
        
        history = {"train_loss": [], "val_loss": []}
        
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0.0
            
            for src, src_mask, tgt_evt, tgt_time, tgt_actor, tgt_tgt, tgt_dom, tgt_mask in train_loader:
                src = src.to(self.device)
                src_mask = src_mask.to(self.device)
                tgt_evt = tgt_evt.to(self.device)
                tgt_time = tgt_time.to(self.device)
                tgt_actor = tgt_actor.to(self.device)
                tgt_tgt = tgt_tgt.to(self.device)
                tgt_dom = tgt_dom.to(self.device)
                tgt_mask = tgt_mask.to(self.device)
                
                self.optimizer.zero_grad()
                
                preds = self.model(src, src_mask, tgt_evt, tgt_time, self.config.teacher_forcing_ratio)
                
                targets = {
                    "event_type": tgt_evt[:, 1:], # offset for prediction
                    "time_bin": tgt_time[:, 1:],
                    "actor": tgt_actor[:, 1:],
                    "target": tgt_tgt[:, 1:],
                    "domain": tgt_dom[:, 1:]
                }
                
                preds_sliced = {k: v[:, 1:] for k, v in preds.items()}
                
                loss, _ = self.criterion(preds_sliced, targets, tgt_mask[:, 1:])
                loss.backward()
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.gradient_clipping)
                self.optimizer.step()
                
                total_loss += loss.item()
                
            avg_train_loss = total_loss / max(len(train_loader), 1)
            history["train_loss"].append(avg_train_loss)
            
            # Validation
            val_loss, val_metrics = self._evaluate(val_loader)
            history["val_loss"].append(val_loss)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                
        # Restore best model
        if best_model_state:
            self.model.load_state_dict(best_model_state)
            
        _, final_metrics = self._evaluate(val_loader)
        final_metrics["best_val_loss"] = best_val_loss
        
        return {
            "history": history,
            "metrics": final_metrics,
            "params_count": sum(p.numel() for p in self.model.parameters())
        }
        
    def _evaluate(self, loader: DataLoader):
        self.model.eval()
        total_loss = 0.0
        
        all_preds = {"event_type": [], "time_bin": []}
        all_targets = {"event_type": [], "time_bin": []}
        all_masks = []
        
        with torch.no_grad():
            for src, src_mask, tgt_evt, tgt_time, tgt_actor, tgt_tgt, tgt_dom, tgt_mask in loader:
                src = src.to(self.device)
                src_mask = src_mask.to(self.device)
                tgt_evt = tgt_evt.to(self.device)
                tgt_time = tgt_time.to(self.device)
                tgt_actor = tgt_actor.to(self.device)
                tgt_tgt = tgt_tgt.to(self.device)
                tgt_dom = tgt_dom.to(self.device)
                tgt_mask = tgt_mask.to(self.device)
                
                # Teacher forcing = 0.0 for pure evaluation
                preds = self.model(src, src_mask, tgt_evt, tgt_time, 0.0)
                
                targets = {
                    "event_type": tgt_evt[:, 1:],
                    "time_bin": tgt_time[:, 1:],
                    "actor": tgt_actor[:, 1:],
                    "target": tgt_tgt[:, 1:],
                    "domain": tgt_dom[:, 1:]
                }
                
                preds_sliced = {k: v[:, 1:] for k, v in preds.items()}
                
                mask = tgt_mask[:, 1:]
                loss, _ = self.criterion(preds_sliced, targets, mask)
                total_loss += loss.item()
                
                all_preds["event_type"].append(preds_sliced["event_type"])
                all_preds["time_bin"].append(preds_sliced["time_bin"])
                all_targets["event_type"].append(targets["event_type"])
                all_targets["time_bin"].append(targets["time_bin"])
                all_masks.append(mask)
                
        avg_loss = total_loss / max(len(loader), 1)
        
        if all_masks:
            cat_preds = {k: torch.cat(v, dim=0) for k, v in all_preds.items()}
            cat_targets = {k: torch.cat(v, dim=0) for k, v in all_targets.items()}
            cat_mask = torch.cat(all_masks, dim=0)
            metrics = compute_sequence_metrics(cat_preds, cat_targets, cat_mask, self.model.PAD_IDX)
        else:
            metrics = {}
            
        return avg_loss, metrics
        
    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(path, "model.pt"))
        self.config.save(os.path.join(path, "config.json"))
        
        meta = {
            "model_version": "v1.0.0",
            "architecture": "CausalSeq(EncoderLSTM-Bahdanau-DecoderLSTM)",
            "params_count": sum(p.numel() for p in self.model.parameters())
        }
            
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(meta, f, indent=2)
