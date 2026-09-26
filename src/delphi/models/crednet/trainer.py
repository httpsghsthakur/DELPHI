import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional
import os
import json
import uuid

from .model import CredNet
from .losses import CredibilityLoss
from .calibration import PlattScaler
from .metrics import compute_metrics

class CredNetTrainer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CredNet(input_dim=12).to(self.device)
        self.criterion = CredibilityLoss(pos_weight=config.get("pos_weight", None)).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=config.get("learning_rate", 1e-3))
        self.scaler = PlattScaler()
        
    def train(self, train_loader: DataLoader, val_loader: DataLoader) -> Dict[str, Any]:
        epochs = self.config.get("epochs", 10)
        best_val_loss = float('inf')
        best_model_state = None
        
        history = {"train_loss": [], "val_loss": []}
        
        for epoch in range(epochs):
            self.model.train()
            total_loss = 0.0
            
            for X, y, _ in train_loader:
                X, y = X.to(self.device), y.to(self.device)
                
                self.optimizer.zero_grad()
                logits = self.model(X)
                loss = self.criterion(logits, y)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                
            avg_train_loss = total_loss / max(len(train_loader), 1)
            history["train_loss"].append(avg_train_loss)
            
            # Validation
            val_loss, val_logits, val_labels = self._evaluate(val_loader)
            history["val_loss"].append(val_loss)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                
        # Restore best model
        if best_model_state:
            self.model.load_state_dict(best_model_state)
            
        # Calibrate using best model and validation set
        _, val_logits, val_labels = self._evaluate(val_loader)
        self.scaler.fit(val_logits, val_labels)
        val_probs = self.scaler.calibrate(val_logits)
        
        final_metrics = compute_metrics(val_labels, val_probs)
        final_metrics["best_val_loss"] = best_val_loss
        
        # In a real environment, log to MLflow here
        
        return {
            "history": history,
            "metrics": final_metrics
        }
        
    def _evaluate(self, loader: DataLoader):
        self.model.eval()
        total_loss = 0.0
        all_logits = []
        all_labels = []
        
        with torch.no_grad():
            for X, y, _ in loader:
                X, y = X.to(self.device), y.to(self.device)
                logits = self.model(X)
                loss = self.criterion(logits, y)
                
                total_loss += loss.item()
                all_logits.extend(logits.cpu().view(-1).numpy().tolist())
                all_labels.extend(y.cpu().view(-1).numpy().tolist())
                
        avg_loss = total_loss / max(len(loader), 1)
        return avg_loss, all_logits, all_labels
        
    def save(self, path: str, extra_meta: dict = None):
        os.makedirs(path, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(path, "model.pt"))
        
        import joblib
        joblib.dump(self.scaler, os.path.join(path, "scaler.pkl"))
        
        meta = {
            "model_version": "v1.0.0",
            "architecture": "MLP(12, 32, 16, 1)",
            "feature_version": "v1.0",
            "dataset_version": self.config.get("dataset_version", "unknown"),
            "training_config": self.config
        }
        if extra_meta:
            meta.update(extra_meta)
            
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(meta, f, indent=2)
