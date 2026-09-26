import pytest
import torch
from delphi.models.crednet.model import CredNet
from delphi.models.crednet.losses import CredibilityLoss
import tempfile
import os

def test_crednet_architecture():
    model = CredNet(input_dim=12)
    x = torch.randn(4, 12)
    logits = model(x)
    
    assert logits.shape == (4, 1)
    
    # Check parameters count
    # 12*32 + 32 = 416
    # 32*16 + 16 = 528
    # 16*1 + 1 = 17
    # Total = 416 + 528 + 17 = 961
    total_params = sum(p.numel() for p in model.parameters())
    assert total_params == 961
    
    # Test grads
    loss_fn = CredibilityLoss()
    y = torch.tensor([[1.0], [0.0], [1.0], [0.0]])
    loss = loss_fn(logits, y)
    loss.backward()
    
    for name, param in model.named_parameters():
        assert param.grad is not None
        assert not torch.isnan(param.grad).any()

def test_save_load():
    model = CredNet()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.pt")
        torch.save(model.state_dict(), path)
        
        model2 = CredNet()
        model2.load_state_dict(torch.load(path))
        
        for p1, p2 in zip(model.parameters(), model2.parameters()):
            assert torch.equal(p1, p2)
