import torch
from torch.utils.data import DataLoader
from typing import Dict, List, Any
import copy
from .trainer import CredNetTrainer
from .dataset import CredNetDataset
from .metrics import compute_metrics

class AblationEvaluator:
    def __init__(self, trainer: CredNetTrainer, val_loader: DataLoader, feature_names: List[str]):
        self.trainer = trainer
        self.val_loader = val_loader
        self.feature_names = feature_names
        
        # Mapping semantic groups
        self.feature_groups = {
            "source_history": [
                "historical_source_reliability",
                "correction_history_signal",
                "publication_consistency",
                "author_history_availability",
                "source_longevity_normalized"
            ],
            "article_content": [
                "article_length_normalized",
                "citation_density",
                "title_sensationalism",
                "primary_source_presence",
                "attribution_completeness"
            ],
            "metadata": [
                "author_identifiable",
                "corroboration_count_normalized"
            ]
        }
        
    def evaluate_ablation(self) -> Dict[str, Dict[str, float]]:
        results = {}
        
        # Baseline (Full 12 features)
        baseline_loss, baseline_logits, baseline_labels = self.trainer._evaluate(self.val_loader)
        baseline_probs = self.trainer.scaler.calibrate(baseline_logits)
        results["baseline_full"] = compute_metrics(baseline_labels, baseline_probs)
        
        # Ablate individual features
        for i, feat in enumerate(self.feature_names):
            ablated_loader = self._create_ablated_loader([i])
            _, logits, labels = self.trainer._evaluate(ablated_loader)
            probs = self.trainer.scaler.calibrate(logits)
            results[f"ablated_feature_{feat}"] = compute_metrics(labels, probs)
            
        # Ablate groups
        for group_name, feats in self.feature_groups.items():
            indices = [self.feature_names.index(f) for f in feats if f in self.feature_names]
            ablated_loader = self._create_ablated_loader(indices)
            _, logits, labels = self.trainer._evaluate(ablated_loader)
            probs = self.trainer.scaler.calibrate(logits)
            results[f"ablated_group_{group_name}"] = compute_metrics(labels, probs)
            
        return results

    def _create_ablated_loader(self, indices_to_zero: List[int]) -> DataLoader:
        # We wrap the original dataset but zero out specific indices
        original_ds = self.val_loader.dataset
        
        class AblatedDataset(torch.utils.data.Dataset):
            def __init__(self, ds, indices):
                self.ds = ds
                self.indices = indices
            def __len__(self): return len(self.ds)
            def __getitem__(self, idx):
                X, y, meta = self.ds[idx]
                X_ablated = X.clone()
                for i in self.indices:
                    X_ablated[i] = 0.0 # Neutral ablation
                return X_ablated, y, meta
                
        return DataLoader(
            AblatedDataset(original_ds, indices_to_zero),
            batch_size=self.val_loader.batch_size,
            shuffle=False
        )
