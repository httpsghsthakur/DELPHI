import pytest
from delphi.research.deduplication import Deduplicator
from delphi.research.schemas import SearchResult, ResearchDocument

def test_deduplicate_results():
    r1 = SearchResult(result_id="1", query="q", title="t", url="http://www.example.com/page", snippet="", source_domain="", source_name="", published_at="", retrieved_at="", provider="", rank=1)
    r2 = SearchResult(result_id="2", query="q", title="t", url="https://example.com/page/", snippet="", source_domain="", source_name="", published_at="", retrieved_at="", provider="", rank=2)
    
    unique = Deduplicator.deduplicate_results([r1, r2])
    assert len(unique) == 1
    
def test_deduplicate_documents():
    d1 = ResearchDocument(document_id="1", url="http://example.com/A", canonical_url="", title="", source="", source_domain="", published_at="", retrieved_at="", text="", language="", content_type="", word_count=0, checksum="abc")
    d2 = ResearchDocument(document_id="2", url="http://example.com/B", canonical_url="", title="", source="", source_domain="", published_at="", retrieved_at="", text="", language="", content_type="", word_count=0, checksum="abc")
    
    unique = Deduplicator.deduplicate_documents([d1, d2])
    assert len(unique) == 1
