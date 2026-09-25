import pytest
import os
import tempfile
from delphi.tokenizer.vocabulary import VocabularyBuilder
from delphi.tokenizer.tokenizer import CustomTokenizer
from delphi.tokenizer.special_tokens import BOS_ID, EOS_ID, PAD_ID, UNK_ID

@pytest.fixture
def sample_corpus():
    return [
        ["India", "bans", "rice", "exports", "."],
        ["The", "US-China", "trade", "deal", "failed", "."],
        ["Rice", "prices", "increased", "by", "40%", "."],
    ]

@pytest.fixture
def config():
    return {
        "normalization": {
            "unicode": True,
            "normalize_whitespace": True,
            "remove_control_chars": True,
            "lowercase": False
        },
        "sequence": {
            "max_length": 10,
            "add_bos": True,
            "add_eos": True,
            "truncation": True,
            "padding": "longest"
        }
    }

def test_vocabulary_builder_deterministic(sample_corpus):
    builder1 = VocabularyBuilder(min_frequency=1)
    vocab1 = builder1.build(sample_corpus)
    
    builder2 = VocabularyBuilder(min_frequency=1)
    vocab2 = builder2.build(sample_corpus)
    
    assert vocab1.token_map == vocab2.token_map

def test_tokenizer_encode_decode(sample_corpus, config):
    builder = VocabularyBuilder(min_frequency=1)
    vocab = builder.build(sample_corpus)
    tokenizer = CustomTokenizer(vocab, config)
    
    text = "India bans rice."
    output = tokenizer.encode(text)
    
    assert output.input_ids[0] == BOS_ID
    assert output.input_ids[-1] == EOS_ID
    
    decoded = tokenizer.decode(output.input_ids)
    assert decoded == "India bans rice ."

def test_tokenizer_padding(sample_corpus, config):
    builder = VocabularyBuilder(min_frequency=1)
    vocab = builder.build(sample_corpus)
    tokenizer = CustomTokenizer(vocab, config)
    
    batch = tokenizer.batch_encode(["India bans rice.", "The US-China trade deal failed."])
    assert len(batch.input_ids[0]) == len(batch.input_ids[1])
    assert batch.attention_mask[0][-1] == 0  # Should be padded
    assert batch.input_ids[0][-1] == PAD_ID

def test_tokenizer_save_load(sample_corpus, config):
    builder = VocabularyBuilder(min_frequency=1)
    vocab = builder.build(sample_corpus)
    tokenizer = CustomTokenizer(vocab, config)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tokenizer.save(tmpdir)
        loaded_tokenizer = CustomTokenizer.load(tmpdir)
        
        assert tokenizer.vocab.token_map == loaded_tokenizer.vocab.token_map
        assert tokenizer.config == loaded_tokenizer.config
        
        output1 = tokenizer.encode("India bans rice.")
        output2 = loaded_tokenizer.encode("India bans rice.")
        assert output1.input_ids == output2.input_ids
