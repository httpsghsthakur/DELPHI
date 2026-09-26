import torch
from delphi.models.causalseq import CausalSeqConfig, CausalSeq, BahdanauAttention

def test_causalseq_architecture():
    config = CausalSeqConfig(
        input_dim=256,
        hidden_dim=128,
        encoder_layers=2,
        decoder_layers=2,
        num_event_types=50,
        num_time_bins=9,
        num_actors=100,
        num_targets=100,
        num_domains=10,
        bidirectional_encoder=True
    )
    
    model = CausalSeq(config)
    
    params = sum(p.numel() for p in model.parameters())
    assert params > 0
    # Expected approx parameter count for this config is around 1-2M
    
    # Forward pass test
    batch_size = 2
    seq_len = 10
    tgt_len = 5
    
    src = torch.randn(batch_size, seq_len, 256)
    src_mask = torch.ones(batch_size, seq_len, dtype=torch.bool)
    src_mask[0, -2:] = False # padding on first example
    
    tgt_evt = torch.randint(0, 50, (batch_size, tgt_len))
    tgt_time = torch.randint(0, 9, (batch_size, tgt_len))
    
    preds = model(src, src_mask, tgt_evt, tgt_time, teacher_forcing_ratio=1.0)
    
    assert preds["event_type"].shape == (batch_size, tgt_len, 53) # 50 + BOS/EOS/PAD
    assert preds["time_bin"].shape == (batch_size, tgt_len, 12)
    assert preds["actor"].shape == (batch_size, tgt_len, 100)

def test_bahdanau_attention():
    hidden_dim = 128
    encoder_dim = 256
    attention = BahdanauAttention(hidden_dim, encoder_dim)
    
    batch = 2
    seq_len = 5
    
    decoder_hidden = torch.randn(batch, hidden_dim)
    encoder_outputs = torch.randn(batch, seq_len, encoder_dim)
    
    mask = torch.ones(batch, seq_len, dtype=torch.bool)
    mask[0, 3:] = False # mask last 2 positions
    
    context, weights = attention(decoder_hidden, encoder_outputs, mask)
    
    assert context.shape == (batch, encoder_dim)
    assert weights.shape == (batch, seq_len)
    
    # Masked positions should have 0 attention
    assert torch.allclose(weights[0, 3:], torch.zeros(2))
    
    # Valid positions should sum to 1
    assert torch.allclose(weights[0].sum(), torch.tensor(1.0))
    assert torch.allclose(weights[1].sum(), torch.tensor(1.0))
