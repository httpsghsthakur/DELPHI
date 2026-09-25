import unicodedata
import re

def normalize(text: str, config: dict) -> str:
    """
    Apply deterministic normalization to text based on configuration.
    """
    if not text:
        return ""
        
    if config.get("unicode", True):
        text = unicodedata.normalize("NFKC", text)
        
    if config.get("remove_control_chars", True):
        # Keep newlines and tabs, remove others
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ["\n", "\t"])
        
    if config.get("normalize_whitespace", True):
        text = re.sub(r'\s+', ' ', text)
        
    if config.get("lowercase", False):
        text = text.lower()
        
    # Basic URL replacement (only if true replacement is requested)
    if config.get("normalize_urls", False):
        text = re.sub(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', '<URL>', text)
        
    # Basic Email replacement
    if config.get("normalize_emails", False):
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '<EMAIL>', text)

    return text.strip()
