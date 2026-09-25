import pytest
from delphi.preprocessing.deduplication import Deduplicator
from delphi.preprocessing.text import normalize_text

def test_deduplicator():
    dedup = Deduplicator()
    assert dedup.is_duplicate("http://test.com", "hash1") is False
    assert dedup.is_duplicate("http://test.com", "hash2") is True
    assert dedup.is_duplicate("http://test2.com", "hash1") is True
    assert dedup.is_duplicate("http://test3.com", "hash3") is False

def test_text_normalization():
    raw_text = "  This is   some\ntext \t with  weird\u200b spaces.  "
    normalized = normalize_text(raw_text)
    assert normalized == "This is some text with weird spaces."
