import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import os
import json
from datetime import datetime

from delphi.models.eventembed import EventEmbed, EventEmbedConfig, SkipGramNegativeSamplingLoss, NegativeSampler, SkipGramDataset, collate_skipgram

class EventEmbedTrainer:
    def __init__(
        self, 
        model: EventEmbed, 
        config: dict, 
        token_frequencies: dict, 
        vocab_size: int, 
        pad_idx: int = 0,
        device: str = "cpu"
    ):
        self.model = model.to(device)
        self.device = device
        self.config = config
        self.pad_idx = pad_idx
        
        # Loss and Sampler
        self.loss_fn = SkipGramNegativeSamplingLoss(
            vocab_size=vocab_size,
            embedding_dim=model.config.output_dim,
            pad_idx=pad_idx
        ).to(device)
        
        self.sampler = NegativeSampler(
            token_frequencies=token_frequencies,
            vocab_size=vocab_size,
            pad_idx=pad_idx
        )
        
        self.optimizer = optim.Adam(
            list(self.model.parameters()) + list(self.loss_fn.parameters()),
            lr=config.get("learning_rate", 0.001)
        )
        
        self.epoch = 0
        self.global_step = 0
        
    def train_epoch(self, dataloader: DataLoader) -> float:
        self.model.train()
        self.loss_fn.train()
        
        total_loss = 0.0
        
        num_negatives = self.model.config.negative_samples
        
        for batch_idx, (targets, contexts) in enumerate(dataloader):
            targets = targets.to(self.device)
            contexts = contexts.to(self.device)
            batch_size = targets.size(0)
            
            # Forward EventEmbed (targets act as input sequences of length 1)
            # targets: [batch_size] -> [batch_size, 1]
            input_ids = targets.unsqueeze(1)
            
            # Dummy char ids for now, we will assume an external process maps tokens to chars.
            # In a real pipeline, the dataset would provide char_ids.
            # For simplicity, we create dummy char_ids [batch_size, 1, max_char_len]
            max_char_len = self.model.config.character.max_length
            char_ids = torch.zeros((batch_size, 1, max_char_len), dtype=torch.long, device=self.device)
            
            self.optimizer.zero_grad()
            
            # target_vectors: [batch_size, 1, output_dim]
            outputs = self.model(input_ids, char_ids)
            target_vectors = outputs["token_embeddings"].squeeze(1) # [batch_size, output_dim]
            
            # Sample negatives
            negatives = self.sampler.sample(batch_size, num_negatives).to(self.device)
            
            # Compute loss
            loss = self.loss_fn(target_vectors, contexts, negatives)
            
            # Backward
            loss.backward()
            
            # Check for NaNs
            found_nan = False
            for p in self.model.parameters():
                if p.grad is not None and torch.isnan(p.grad).any():
                    found_nan = True
                    break
            if found_nan:
                raise ValueError("NaN gradient detected during training!")
                
            self.optimizer.step()
            
            total_loss += loss.item()
            self.global_step += 1
            
        return total_loss / len(dataloader)
        
    def save_checkpoint(self, path: str):
        os.makedirs(path, exist_ok=True)
        checkpoint = {
            "model_state_dict": self.model.state_dict(),
            "loss_state_dict": self.loss_fn.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "epoch": self.epoch,
            "global_step": self.global_step,
            "config": self.config
        }
        torch.save(checkpoint, os.path.join(path, "checkpoint.pt"))
        
        # Save metadata
        metadata = {
            "model": "EventEmbed",
            "timestamp": datetime.now().isoformat(),
            "epoch": self.epoch,
            "global_step": self.global_step
        }
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
            
    def load_checkpoint(self, path: str):
        checkpoint = torch.load(os.path.join(path, "checkpoint.pt"), map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.loss_fn.load_state_dict(checkpoint["loss_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.epoch = checkpoint["epoch"]
        self.global_step = checkpoint["global_step"]
