import pytest
from datetime import datetime
from pydantic import ValidationError
from delphi.datasets.schemas import NewsArticle

def test_news_article_schema_valid():
    article = NewsArticle(
        article_id="123",
        source_id="cnn",
        title="Test Article",
        body="This is a test body.",
        url="http://cnn.com/test",
        publication_datetime=datetime(2023, 1, 1),
        language="en",
        domain="cnn.com",
        content_hash="abc",
        source_dataset="gdelt",
        ingestion_timestamp=datetime(2023, 1, 2),
        dataset_version="1.0.0"
    )
    assert article.article_id == "123"

def test_news_article_schema_invalid():
    with pytest.raises(ValidationError):
        # Missing required fields
        NewsArticle(article_id="123")
