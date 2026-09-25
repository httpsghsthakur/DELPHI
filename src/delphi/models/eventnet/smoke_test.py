import torch
import tempfile
from torch.utils.data import DataLoader

from delphi.models.eventembed import EventEmbed, EventEmbedConfig
from delphi.models.eventnet import EventNet, EventNetConfig, BIO_TO_ID
from delphi.models.eventnet.dataset import EventNetDataset, collate_eventnet
from delphi.training.eventnet_trainer import EventNetTrainer
from delphi.models.eventnet.decoding import decode_predictions

def run_smoke_test():
    print("Running EventNet Smoke Test...")
    torch.manual_seed(42)
    
    # 1. Setup Models
    embed_config = EventEmbedConfig(
        vocab_size=100,
        word_embedding_dim=192,
        output_dim=256
    )
    eventembed = EventEmbed(embed_config, char_vocab_size=50)
    
    net_config = EventNetConfig(
        input_dim=256,
        num_token_labels=15, # BIO tags
        num_event_types=16 # Event Types
    )
    eventnet = EventNet(net_config)
    
    params = eventnet.count_parameters()
    print(f"EventNet Total Parameters: {params['total']}")
    print(f"EventNet Trainable Parameters: {params['trainable']}")
    
    # 2. Fake Data
    data = [
        {
            "input_ids": [2, 10, 20, 30, 40, 3],
            "char_ids": [[1], [1, 2], [3], [4], [5], [1]],
            "attention_mask": [1, 1, 1, 1, 1, 1],
            "token_labels": [0, BIO_TO_ID["B-ACTOR"], BIO_TO_ID["B-ACTION"], BIO_TO_ID["B-TARGET"], 0, 0],
            "event_label": 2 # CONFLICT
        },
        {
            "input_ids": [2, 10, 20, 3],
            "char_ids": [[1], [1, 2], [3], [1]],
            "attention_mask": [1, 1, 1, 1],
            "token_labels": [0, BIO_TO_ID["B-ACTOR"], BIO_TO_ID["B-ACTION"], 0],
            "event_label": 0 # TRADE
        }
    ]
    
    dataset = EventNetDataset(data)
    dataloader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=collate_eventnet)
    
    # 3. Trainer (Frozen mode)
    trainer_config = {"learning_rate": 0.01}
    trainer = EventNetTrainer(eventnet, eventembed, trainer_config, device="cpu")
    
    # Check frozen gradients
    assert eventnet.config.eventembed.mode == "frozen"
    assert next(eventembed.parameters()).requires_grad == False
    
    initial_loss = trainer.train_epoch(dataloader)
    print(f"Epoch 1 Loss: {initial_loss['loss']:.4f}")
    
    second_loss = trainer.train_epoch(dataloader)
    print(f"Epoch 2 Loss: {second_loss['loss']:.4f}")
    
    # Verify gradients on EventNet
    has_lstm_grad = eventnet.bilstm.lstm.weight_ih_l0.grad is not None
    has_attn_grad = eventnet.attention.q_proj.weight.grad is not None
    has_token_head_grad = eventnet.token_head.classifier.weight.grad is not None
    has_event_head_grad = eventnet.event_head.classifier.weight.grad is not None
    
    assert has_lstm_grad, "No grad on BiLSTM"
    assert has_attn_grad, "No grad on Attention"
    assert has_token_head_grad, "No grad on token head"
    assert has_event_head_grad, "No grad on event head"
    print("Gradients verified successfully.")
    
    # 4. Decoding test
    eventnet.eval()
    with torch.no_grad():
        batch = next(iter(dataloader))
        embed_out = eventembed(batch["input_ids"], batch["char_ids"], batch["attention_mask"])
        net_out = eventnet(embed_out["token_embeddings"], batch["attention_mask"])
        
        token_logits = net_out["token_logits"][0].tolist()
        event_logits = net_out["event_logits"][0].tolist()
        tokens = ["<BOS>", "India", "banned", "rice", ".", "<EOS>"]
        
        pred = decode_predictions(token_logits, event_logits, tokens)
        print(f"Decoded Predictions: {pred['event_type']}")
    
    # 5. Checkpoint
    with tempfile.TemporaryDirectory() as tmpdir:
        trainer.save_checkpoint(tmpdir)
        print("Checkpoint saved.")
        trainer.load_checkpoint(tmpdir)
        print("Checkpoint loaded.")
        
    print("EventNet Smoke Test: COMPLETE")

if __name__ == "__main__":
    run_smoke_test()
