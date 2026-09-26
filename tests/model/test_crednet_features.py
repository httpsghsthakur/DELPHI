import pytest
from delphi.models.crednet.features import CredibilityFeatureExtractor
from delphi.datasets.schemas import NewsArticle

def test_feature_extraction():
    extractor = CredibilityFeatureExtractor()
    
    article = NewsArticle(
        article_id="A1",
        source_id="S1",
        title="BREAKING!!! Huge news!",
        body="This is a test article. " * 50 + "According to a report, this is true. \"Quote\"",
        author="John Doe",
        url="http://example.edu/news",
        publication_datetime="2020-01-01T12:00:00Z",
        language="en",
        domain="example.edu",
        content_hash="abc",
        source_dataset="test",
        ingestion_timestamp="2020-01-01T12:00:00Z",
        dataset_version="v1"
    )
    
    historical = {
        "calculation_timestamp": "2020-12-30T12:00:00Z",
        "historical_reliability": 0.8,
        "corroboration_count": 5,
        "correction_rate": 0.1,
        "publication_variance": 0.2,
        "author_known_historically": True,
        "first_seen_date": "2015-12-31T00:00:00Z"
    }
    
    feats = extractor.extract(article, "2020-12-31T23:59:59Z", historical)
    
    assert feats.author_identifiable == 1.0
    assert feats.historical_source_reliability == 0.8
    assert feats.correction_history_signal == 0.9 # 1 - 0.1
    assert feats.author_history_availability == 1.0
    assert feats.source_longevity_normalized > 0.0 # 5 years
    assert feats.primary_source_presence == 1.0
    
    # Sensationalism: caps and exclamation marks
    # "BREAKING!!! Huge news!"
    assert feats.title_sensationalism > 0.0

def test_temporal_leakage_protection():
    extractor = CredibilityFeatureExtractor()
    article = NewsArticle(
        article_id="A1",
        source_id="S1",
        title="Test",
        body="Test",
        author="John Doe",
        url="http://example.com/news",
        publication_datetime="2022-01-01T12:00:00Z",
        language="en",
        domain="example.com",
        content_hash="abc",
        source_dataset="test",
        ingestion_timestamp="2022-01-01T12:00:00Z",
        dataset_version="v1"
    )
    
    # Cutoff is BEFORE article -> should raise ValueError
    with pytest.raises(ValueError, match="Temporal Leakage"):
        extractor.extract(article, "2021-01-01T00:00:00Z", {})
