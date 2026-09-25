import unicodedata
import re

def normalize_text(text: str) -> str:
    """
    Deterministically normalizes text:
    - Unicode normalization (NFKC)
    - Removes control characters
    - Normalizes whitespace
    - Strips leading/trailing space
    """
    if not text:
        return ""
    
    # Unicode normalize
    text = unicodedata.normalize("NFKC", text)
    
    # Remove control characters (but keep newlines/tabs for now, then replace them)
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ["\n", "\t"])
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def normalize_url(url: str) -> str:
    """
    Basic URL normalization.
    """
    if not url:
        return ""
    return url.strip().lower()
