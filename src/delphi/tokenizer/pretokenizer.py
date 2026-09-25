import re
from typing import List

class PreTokenizer:
    def __init__(self):
        # Regex to split on whitespace but keep punctuation separate, EXCEPT for hyphenated words, 
        # percentages, dates, currencies, and specific domain terms.
        # This is a basic deterministic split.
        self.pattern = re.compile(
            r'('
            r'<[^>]+>|'                         # Special tokens like <BOS>
            r'\d{4}-\d{2}-\d{2}|'               # Dates (YYYY-MM-DD)
            r'[A-Za-z0-9]+-[A-Za-z0-9]+|'       # Hyphenated words (US-China)
            r'\$\d+(?:\.\d+)?[MBKmbk]?|'        # Currencies ($5.2B)
            r'€\d+(?:\.\d+)?[MBKmbk]?|'         # Currencies (€2.3M)
            r'₹\d+(?:,\d+)*(?:\.\d+)?(?:\s*crore|\s*lakh)?|' # Rupees
            r'\d+(?:,\d+)*(?:\.\d+)?%|'         # Percentages
            r'\d+(?:,\d+)*(?:\.\d+)?|'          # Numbers
            r'\w+|'                             # Words
            r'[^\w\s]'                          # Punctuation
            r')', re.UNICODE | re.IGNORECASE
        )

    def pre_tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        
        # We find all matches. The regex captures the tokens.
        tokens = []
        for match in self.pattern.finditer(text):
            token = match.group(1).strip()
            if token:
                tokens.append(token)
        return tokens
