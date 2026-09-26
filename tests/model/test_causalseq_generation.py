import torch
from delphi.models.causalseq import CausalSeqConfig, CausalSeq, generate_greedy, generate_beam_search

def test_deterministic_generation():
    config = CausalSeqConfig(
        input_dim=16,
        hidden_dim=32,
        num_event_types=10,
        num_time_bins=5,
        num_actors=10,
        num_targets=10,
        num_domains=10
    )
    
    # Fix seed for reproducibility
    torch.manual_seed(42)
    model = CausalSeq(config)
    
    src = torch.randn(1, 5, 16)
    mask = torch.ones(1, 5, dtype=torch.bool)
    
    # Greedy
    greedy_out1 = generate_greedy(model, src, mask, max_len=4)
    greedy_out2 = generate_greedy(model, src, mask, max_len=4)
    
    assert torch.equal(greedy_out1["event_type"], greedy_out2["event_type"])
    
    # Beam Search
    beam_out1 = generate_beam_search(model, src, mask, max_len=4, beam_width=3)
    beam_out2 = generate_beam_search(model, src, mask, max_len=4, beam_width=3)
    
    assert torch.equal(beam_out1["event_type"], beam_out2["event_type"])
    assert torch.equal(beam_out1["time_bin"], beam_out2["time_bin"])
    assert beam_out1["sequence_score"] == beam_out2["sequence_score"]
    
    # Ensure they actually generated something
    assert len(beam_out1["event_type"]) > 0
    assert len(greedy_out1["event_type"]) > 0
