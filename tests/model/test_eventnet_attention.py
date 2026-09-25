import torch
import pytest
from delphi.models.eventnet.attention import SelfAttention

def test_self_attention_shapes():
    B, T, D = 4, 10, 256
    num_heads = 4
    
    attn = SelfAttention(embed_dim=D, num_heads=num_heads)
    
    q = torch.randn(B, T, D)
    k = torch.randn(B, T, D)
    v = torch.randn(B, T, D)
    
    out = attn(q, k, v)
    assert out.shape == (B, T, D)
    
def test_self_attention_masking():
    B, T, D = 1, 5, 256
    attn = SelfAttention(embed_dim=D, num_heads=4)
    attn.eval() # disable dropout for deterministic comparison
    
    # Input A (length 2)
    q_A = torch.randn(B, 2, D)
    k_A = q_A
    v_A = q_A
    out_A = attn(q_A, k_A, v_A)
    
    # Input B (length 5, first 2 are same as A, rest are padded)
    q_B = torch.cat([q_A, torch.randn(B, 3, D)], dim=1)
    k_B = q_B
    v_B = q_B
    
    mask_B = torch.tensor([[1, 1, 0, 0, 0]])
    
    out_B = attn(q_B, k_B, v_B, attention_mask=mask_B)
    
    # The output for the first two tokens should be identical because the padding tokens are masked out
    assert torch.allclose(out_A[0, 0], out_B[0, 0], atol=1e-5)
    assert torch.allclose(out_A[0, 1], out_B[0, 1], atol=1e-5)
