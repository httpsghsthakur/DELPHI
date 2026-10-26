import re
from typing import List, Dict, Any

class ContentExtractor:
    """
    Deterministic HTML cleaner and content extractor.
    Extracts readable text, structured claims, numerical metrics,
    and conflicting/unverified signals without external LLMs.
    """
    
    def extract_text(self, html: str) -> str:
        """Strip tags, navigation, scripts/styles, return clean substantive text."""
        # Remove script, style, nav, footer, header tags
        text = re.sub(r'<(script|style|nav|footer|header|aside|noscript).*?>.*?</\1>', ' ', html, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Unescape common HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&mdash;', ' — ')
        text = text.replace('&ndash;', ' – ')
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_claims(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract sentences that constitute factual claims, official positions,
        analytical judgments, or counter-claims.
        """
        claims = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        official_verbs = ['announced', 'signed', 'ordered', 'confirmed', 'declared', 'issued', 'introduced', 'passed']
        reporting_verbs = ['reported', 'stated', 'noted', 'documented', 'revealed', 'showed', 'indicated']
        assessment_verbs = ['projected', 'estimated', 'warned', 'forecast', 'anticipated', 'assessed', 'expected']
        conflict_verbs = ['denied', 'rejected', 'refuted', 'disputed', 'dismissed', 'contradicted', 'claimed otherwise']
        
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) < 30 or len(s_clean) > 350:
                continue
                
            s_lower = s_clean.lower()
            
            # Determine claim type and direction
            claim_type = "reported_fact"
            direction = "supporting"
            
            if any(k in s_lower for k in conflict_verbs) or "not " in s_lower or "untrue" in s_lower:
                claim_type = "competing_account"
                direction = "conflicting"
            elif any(k in s_lower for k in official_verbs):
                claim_type = "official_statement"
                direction = "supporting"
            elif any(k in s_lower for k in assessment_verbs):
                claim_type = "expert_analysis"
                direction = "neutral"
            elif any(k in s_lower for k in reporting_verbs):
                claim_type = "reported_fact"
                direction = "supporting"
            else:
                # If sentence contains important entity actions or metrics
                if any(m in s_lower for m in ['percent', '%', 'billion', 'million', 'treaty', 'accord', 'sanction', 'crisis']):
                    claim_type = "reported_fact"
                    direction = "supporting"
                else:
                    continue
                    
            claims.append({
                "claim_text": s_clean,
                "claim_type": claim_type,
                "direction": direction
            })
            
        return claims

    def extract_quantitative_data(self, text: str) -> List[str]:
        """Extract explicit numbers, statistics, percentages, and currencies with context."""
        matches = []
        pattern = r'([^.!?]*\b(?:\$[\d,.]+(?:\s*(?:billion|million|trillion))?|\b\d+(?:\.\d+)?%|\b\d{1,3}(?:,\d{3})+\b)[^.!?]*[.!?])'
        for m in re.finditer(pattern, text, re.IGNORECASE):
            snippet = m.group(1).strip()
            if 15 < len(snippet) < 180 and snippet not in matches:
                matches.append(snippet)
                if len(matches) >= 5:
                    break
        return matches

    def extract_unresolved_questions(self, text: str) -> List[str]:
        """Extract statements indicating unverified claims, investigation ongoing, or conflicting facts."""
        uncertainties = []
        indicators = ['remains unclear', 'not independently verified', 'investigation ongoing', 'conflicting reports', 'dispute whether', 'unconfirmed', 'sources disagree']
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences:
            s_clean = s.strip()
            if any(ind in s_clean.lower() for ind in indicators) and 20 < len(s_clean) < 250:
                uncertainties.append(s_clean)
                if len(uncertainties) >= 4:
                    break
        return uncertainties
