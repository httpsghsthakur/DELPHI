import re

class ContentExtractor:
    """
    Deterministic HTML cleaner and content extractor.
    Extracts readable text without an LLM.
    """
    
    def extract_text(self, html: str) -> str:
        """Strip tags and scripts/styles, return clean text."""
        # Remove script and style elements
        text = re.sub(r'<(script|style).*?>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Unescape common HTML entities (simple version)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_claims(self, text: str) -> list[str]:
        """
        Extract sentences that look like claims.
        Very simplistic heuristic based on keywords or structure.
        """
        claims = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        keywords = ['said', 'stated', 'announced', 'reported', 'found', 'showed', 'will', 'expected', 'ordered', 'signed']
        
        for s in sentences:
            s_lower = s.lower()
            if any(k in s_lower for k in keywords) and len(s) > 20 and len(s) < 300:
                claims.append(s.strip())
                
        return claims
