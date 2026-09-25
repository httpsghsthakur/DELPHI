import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import os
import json
from datetime import datetime
from typing import Optional

from delphi.models.eventnet import EventNet, EventNetConfig, EventNetLoss
from delphi.models.eventembed import EventEmbed

class EventNetTrainer:
    def __init__(
        self,
        eventnet: EventNet,
        eventembed: EventEmbed,
        config: dict,
        device: str = "cpu"
    ):
        self.eventnet = eventnet.to(device)
        self.eventembed = eventembed.to(device)
        self.config = config
        self.device = device
        
        self.mode = eventnet.config.eventembed.mode
        if self.mode == "frozen":
            for param in self.eventembed.parameters():
                param.requires_grad = False
            self.eventembed.eval()
        
        # Loss
        self.loss_fn = EventNetLoss(
            num_token_labels=eventnet.config.num_token_labels,
            lambda_event=eventnet.config.loss.lambda_event
        ).to(device)
        
        trainable_params = list(self.eventnet.parameters())
        if self.mode == "trainable":
            trainable_params += list(self.eventembed.parameters())
            
        self.optimizer = optim.Adam(
            trainable_params,
            lr=config.get("learning_rate", 0.001)
        )
        
        self.epoch = 0
        self.global_step = 0

    def train_epoch(self, dataloader: DataLoader) -> dict:
        self.eventnet.train()
        if self.mode == "trainable":
            self.eventembed.train()
            
        total_loss = 0.0
        total_token_loss = 0.0
        total_event_loss = 0.0
        
        for batch in dataloader:
            input_ids = batch["input_ids"].to(self.device)
            char_ids = batch["char_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            token_labels = batch["token_labels"].to(self.device)
            event_labels = batch["event_labels"].to(self.device)
            
            self.optimizer.zero_grad()
            
            if self.mode == "frozen":
                with torch.no_grad():
                    embed_outputs = self.eventembed(input_ids, char_ids, attention_mask)
            else:
                embed_outputs = self.eventembed(input_ids, char_ids, attention_mask)
                
            token_embeddings = embed_outputs["token_embeddings"]
            
            # Forward EventNet
            net_outputs = self.eventnet(token_embeddings, attention_mask)
            
            # Loss
            loss_outputs = self.loss_fn(
                net_outputs["token_logits"],
                token_labels,
                net_outputs["event_logits"],
                event_labels
            )
            
            loss = loss_outputs["loss"]
            loss.backward()
            
            # Check for NaNs
            found_nan = False
            for name, p in self.eventnet.named_parameters():
                if p.grad is not None and torch.isnan(p.grad).any():
                    found_nan = True
                    break
            if found_nan:
                raise ValueError("NaN gradient detected during training!")
                
            self.optimizer.step()
            
            total_loss += loss.item()
            total_token_loss += loss_outputs["token_loss"].item()
            total_event_loss += loss_outputs["event_loss"].item()
            
            self.global_step += 1
            
        steps = len(dataloader)
        return {
            "loss": total_loss / steps,
            "token_loss": total_token_loss / steps,
            "event_loss": total_event_loss / steps
        }
        
    def save_checkpoint(self, path: str):
        os.makedirs(path, exist_ok=True)
        checkpoint = {
            "eventnet_state_dict": self.eventnet.state_dict(),
            "eventembed_state_dict": self.eventembed.state_dict() if self.mode == "trainable" else None,
            "optimizer_state_dict": self.optimizer.state_dict(),
            "epoch": self.epoch,
            "global_step": self.global_step,
            "config": self.config
        }
        torch.save(checkpoint, os.path.join(path, "checkpoint.pt"))
        
        # Save metadata
        metadata = {
            "model": "EventNet",
            "timestamp": datetime.now().isoformat(),
            "epoch": self.epoch,
            "global_step": self.global_step,
            "mode": self.mode
        }
        with open(os.path.join(path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

    def load_checkpoint(self, path: str):
        checkpoint = torch.load(os.path.join(path, "checkpoint.pt"), map_location=self.device)
        self.eventnet.load_state_dict(checkpoint["eventnet_state_dict"])
        if checkpoint["eventembed_state_dict"] is not None:
            self.eventembed.load_state_dict(checkpoint["eventembed_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.epoch = checkpoint["epoch"]
        self.global_step = checkpoint["global_step"]
