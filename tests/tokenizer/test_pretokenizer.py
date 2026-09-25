import pytest
from delphi.tokenizer.pretokenizer import PreTokenizer

def test_pretokenizer_basic():
    pretok = PreTokenizer()
    text = "India announced a 40% restriction on rice exports on 25 September 2026."
    tokens = pretok.pre_tokenize(text)
    assert tokens == ["India", "announced", "a", "40%", "restriction", "on", "rice", "exports", "on", "25", "September", "2026", "."]

def test_pretokenizer_dates_and_currencies():
    pretok = PreTokenizer()
    text = "On 2024-07-15, the US-China trade deal involved $5.2B and €100M."
    tokens = pretok.pre_tokenize(text)
    assert "2024-07-15" in tokens
    assert "US-China" in tokens
    assert "$5.2B" in tokens
    assert "€100M" in tokens

def test_pretokenizer_organizations():
    pretok = PreTokenizer()
    text = "NVIDIA and TSMC partnered for F-35."
    tokens = pretok.pre_tokenize(text)
    assert "NVIDIA" in tokens
    assert "TSMC" in tokens
    assert "F-35" in tokens

def test_pretokenizer_special_tokens():
    pretok = PreTokenizer()
    text = "<ACTOR> India </ACTOR>"
    tokens = pretok.pre_tokenize(text)
    assert tokens == ["<ACTOR>", "India", "</ACTOR>"]
