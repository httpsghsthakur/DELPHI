import torch
import pytest

from delphi.models.eventnet import EventNet, EventNetConfig, BiLSTMConfig, AttentionConfig

def test_eventnet_shapes():
    batch_size = 4
    seq_len = 10
    input_dim = 256
    
    config = EventNetConfig(
        input_dim=input_dim,
        num_token_labels=15,
        num_event_types=16
    )
    
    model = EventNet(config)
    
    embeddings = torch.randn(batch_size, seq_len, input_dim)
    mask = torch.ones(batch_size, seq_len)
    
    out = model(embeddings, attention_mask=mask)
    
    assert out["token_logits"].shape == (batch_size, seq_len, 15)
    assert out["event_logits"].shape == (batch_size, 16)
    
def test_bilstm_output_dim():
    config = EventNetConfig(
        input_dim=256,
        num_token_labels=15,
        num_event_types=16,
        bilstm=BiLSTMConfig(hidden_size=128, bidirectional=True)
    )
    model = EventNet(config)
    assert model.bilstm.output_dim == 256
    
    config = EventNetConfig(
        input_dim=256,
        num_token_labels=15,
        num_event_types=16,
        bilstm=BiLSTMConfig(hidden_size=128, bidirectional=False)
    )
    model = EventNet(config)
    assert model.bilstm.output_dim == 128
