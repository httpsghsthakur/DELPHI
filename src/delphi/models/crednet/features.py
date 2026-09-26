from typing import Dict, Any, List
import math
from delphi.datasets.schemas import NewsArticle, CredibilityFeatures
from datetime import datetime

class CredibilityFeatureExtractor:
    """
    Extracts the 12 features deterministically, strictly obeying temporal boundaries.
    """
    def __init__(self):
        pass
        
    def extract(self, article: NewsArticle, prediction_cutoff: str, historical_source_data: Dict[str, Any] = None) -> CredibilityFeatures:
        """
        Extract features using ONLY information available <= prediction_cutoff.
        """
        cutoff_date = datetime.strptime(prediction_cutoff[:10], "%Y-%m-%d").date()
        if isinstance(article.publication_datetime, datetime):
            art_date = article.publication_datetime.date()
        else:
            art_date = datetime.strptime(str(article.publication_datetime)[:10], "%Y-%m-%d").date()
            
        if art_date > cutoff_date:
            raise ValueError(f"Temporal Leakage! Article date {art_date} is after cutoff {cutoff_date}")
            
        historical_source_data = historical_source_data or {}
        
        # 1. author_identifiable
        author_identifiable = 1.0 if (article.author and article.author.strip() and article.author.lower() != "unknown") else 0.0
        
        # 2. article_length_normalized
        words = len(article.body.split())
        article_length_normalized = min(float(words) / 2000.0, 1.0)
        
        # 3. citation_density
        # Proxy: count "http" or "href" if HTML, or just quotes if plaintext. Here we assume naive quote count proxy.
        quotes = article.body.count('"')
        citation_density = min(float(quotes) / max(words, 1) * 10.0, 1.0)
        
        # 4. title_sensationalism
        caps = sum(1 for c in article.title if c.isupper())
        exclaims = article.title.count('!')
        title_len = max(len(article.title), 1)
        sensationalism = min((caps + exclaims * 5) / float(title_len), 1.0)
        
        # 5. historical_source_reliability
        rel = historical_source_data.get("historical_reliability", 0.5)
        
        # 6. corroboration_count_normalized
        # Number of articles from DIFFERENT sources covering the same event *before* cutoff
        corr_count = historical_source_data.get("corroboration_count", 0)
        corroboration_count_normalized = math.log1p(corr_count) / math.log1p(50)
        corroboration_count_normalized = min(corroboration_count_normalized, 1.0)
        
        # 7. correction_history_signal
        correction_rate = historical_source_data.get("correction_rate", 0.5)
        correction_history_signal = 1.0 - correction_rate
        
        # 8. publication_consistency
        variance = historical_source_data.get("publication_variance", 1.0)
        publication_consistency = 1.0 / (1.0 + variance)
        
        # 9. primary_source_presence
        primary = 1.0 if any(k in article.body.lower() for k in ["according to a report", "official statement", "said in a statement"]) else 0.0
        
        # 10. attribution_completeness
        # Placeholder proxy: ratio of capitalized words (potential entities) to total words
        cap_words = sum(1 for w in article.body.split() if w and w[0].isupper())
        attribution_completeness = min(float(cap_words) / max(words, 1) * 5.0, 1.0)
        
        # 11. author_history_availability
        auth_hist = 1.0 if historical_source_data.get("author_known_historically", False) else 0.0
        
        # 12. domain_reputation
        domain = article.url.split("/")[2] if "//" in article.url else article.url
        if domain.endswith(".edu") or domain.endswith(".gov"):
            domain_rep = 1.0
        elif domain.endswith(".com") or domain.endswith(".org"):
            domain_rep = 0.5
        else:
            domain_rep = 0.3
            
        return CredibilityFeatures(
            source_id=article.source_id,
            article_id=article.article_id,
            timestamp=prediction_cutoff,
            author_identifiable=author_identifiable,
            article_length_normalized=article_length_normalized,
            citation_density=citation_density,
            title_sensationalism=sensationalism,
            historical_source_reliability=rel,
            corroboration_count_normalized=corroboration_count_normalized,
            correction_history_signal=correction_history_signal,
            publication_consistency=publication_consistency,
            primary_source_presence=primary,
            attribution_completeness=attribution_completeness,
            author_history_availability=auth_hist,
            domain_reputation=domain_rep,
            dataset_version="v1.0"
        )
