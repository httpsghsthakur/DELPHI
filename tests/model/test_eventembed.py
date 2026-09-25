import torch
import pytest
from delphi.models.eventembed import EventEmbed, EventEmbedConfig

def test_eventembed_shapes():
    vocab_size = 100
    char_vocab_size = 50
    batch_size = 4
    seq_len = 10
    max_char_len = 15
    
    config = EventEmbedConfig(
        vocab_size=vocab_size,
        word_embedding_dim=192,
        output_dim=256
    )
    
    model = EventEmbed(config, char_vocab_size=char_vocab_size)
    
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))
    char_ids = torch.randint(0, char_vocab_size, (batch_size, seq_len, max_char_len))
    
    outputs = model(input_ids, char_ids)
    
    assert outputs["token_embeddings"].shape == (batch_size, seq_len, 256)
    assert outputs["sequence_embedding"].shape == (batch_size, 256)

def test_padding_invariance():
    vocab_size = 100
    char_vocab_size = 50
    
    config = EventEmbedConfig(
        vocab_size=vocab_size,
        word_embedding_dim=192,
        output_dim=256
    )
    model = EventEmbed(config, char_vocab_size=char_vocab_size)
    model.eval()
    
    # Input A (length 2)
    input_ids_A = torch.tensor([[10, 20]])
    char_ids_A = torch.ones((1, 2, 5), dtype=torch.long)
    mask_A = torch.tensor([[1, 1]])
    
    # Input B (length 5, with 3 pads)
    input_ids_B = torch.tensor([[10, 20, 0, 0, 0]])
    char_ids_B = torch.ones((1, 5, 5), dtype=torch.long)
    # the pads should have 0s for chars but for this test we rely on mask
    mask_B = torch.tensor([[1, 1, 0, 0, 0]])
    
    with torch.no_grad():
        out_A = model(input_ids_A, char_ids_A, mask_A)
        out_B = model(input_ids_B, char_ids_B, mask_B)
        
    seq_A = out_A["sequence_embedding"]
    seq_B = out_B["sequence_embedding"]
    
    assert torch.allclose(seq_A, seq_B, atol=1e-6), "Masked sequence pooling should be invariant to padding"
    
def test_oov_handling():
    config = EventEmbedConfig(
        vocab_size=100,
        word_embedding_dim=192,
        output_dim=256
    )
    model = EventEmbed(config, char_vocab_size=50)
    
    # Known word (ID 10) vs UNK (ID 1)
    input_ids = torch.tensor([[10, 1]])
    
    # Provide DIFFERENT char inputs for UNK
    char_ids_1 = torch.randint(1, 50, (1, 2, 10))
    char_ids_2 = torch.randint(1, 50, (1, 2, 10))
    # Make sure char_ids for index 1 are different
    
    with torch.no_grad():
        out1 = model(input_ids, char_ids_1)["token_embeddings"]
        out2 = model(input_ids, char_ids_2)["token_embeddings"]
        
    # The embeddings for the UNK token (index 1) should be DIFFERENT because their character sequences are different!
    assert not torch.allclose(out1[0, 1], out2[0, 1]), "Character encoder must differentiate UNK tokens based on character input"
