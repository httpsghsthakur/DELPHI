import torch
import tempfile
from torch.utils.data import DataLoader
from delphi.models.eventembed import EventEmbed, EventEmbedConfig, SkipGramDataset, collate_skipgram
from delphi.training.eventembed_trainer import EventEmbedTrainer

def run_smoke_test():
    print("Running EventEmbed Smoke Test...")
    
    # 1. Setup deterministic tiny fixture (NOT TRAINING DATA)
    torch.manual_seed(42)
    vocab_size = 100
    char_vocab_size = 50
    pad_idx = 0
    
    # Fake tokenized sequences
    sequences = [
        [1, 5, 20, 35, 10, 2],
        [1, 15, 20, 42, 2],
        [1, 5, 80, 12, 2]
    ]
    
    # Fake token frequencies for negative sampling
    token_frequencies = {i: 10 for i in range(1, vocab_size)}
    
    dataset = SkipGramDataset(sequences, context_window=2, pad_idx=pad_idx)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True, collate_fn=collate_skipgram)
    
    # 2. Config & Model
    config_dict = {
        "learning_rate": 0.01
    }
    config = EventEmbedConfig(
        vocab_size=vocab_size,
        word_embedding_dim=192,
        output_dim=256,
        negative_samples=2
    )
    
    model = EventEmbed(config, char_vocab_size=char_vocab_size, pad_idx=pad_idx)
    
    # Print params
    params = model.count_parameters()
    print(f"Total parameters: {params['total']}")
    print(f"Trainable parameters: {params['trainable']}")
    
    trainer = EventEmbedTrainer(
        model=model,
        config=config_dict,
        token_frequencies=token_frequencies,
        vocab_size=vocab_size,
        pad_idx=pad_idx,
        device="cpu"
    )
    
    # 3. Verify forward & loss & backward
    initial_loss = trainer.train_epoch(dataloader)
    print(f"Epoch 1 Loss: {initial_loss}")
    
    # Train another epoch to see if loss changes
    second_loss = trainer.train_epoch(dataloader)
    print(f"Epoch 2 Loss: {second_loss}")
    
    # Verify gradients exist for components
    has_word_grad = model.word_embedding.embedding.weight.grad is not None
    has_char_grad = model.char_encoder.embedding.weight.grad is not None
    has_cnn_grad = model.char_encoder.convs[0].weight.grad is not None
    has_fusion_grad = model.fusion.net[0].weight.grad is not None
    
    assert has_word_grad, "No gradient on word embeddings"
    assert has_char_grad, "No gradient on char embeddings"
    assert has_cnn_grad, "No gradient on char CNN"
    assert has_fusion_grad, "No gradient on fusion layer"
    
    print("Gradients verified successfully.")
    
    # 4. Checkpointing
    with tempfile.TemporaryDirectory() as tmpdir:
        trainer.save_checkpoint(tmpdir)
        print(f"Saved checkpoint to {tmpdir}")
        
        # Load and verify
        new_model = EventEmbed(config, char_vocab_size=char_vocab_size, pad_idx=pad_idx)
        new_trainer = EventEmbedTrainer(
            model=new_model,
            config=config_dict,
            token_frequencies=token_frequencies,
            vocab_size=vocab_size,
            pad_idx=pad_idx,
            device="cpu"
        )
        new_trainer.load_checkpoint(tmpdir)
        print("Loaded checkpoint successfully.")
        
    print("EventEmbed Smoke Test: COMPLETE")
    
if __name__ == "__main__":
    run_smoke_test()
