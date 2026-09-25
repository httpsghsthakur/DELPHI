import hashlib
from typing import Dict, Any

class Deduplicator:
    def __init__(self):
        self.seen_urls = set()
        self.seen_hashes = set()

    def is_duplicate(self, url: str, content_hash: str) -> bool:
        if url and url in self.seen_urls:
            return True
        if content_hash and content_hash in self.seen_hashes:
            return True
        
        if url:
            self.seen_urls.add(url)
        if content_hash:
            self.seen_hashes.add(content_hash)
            
        return False

    @staticmethod
    def compute_content_hash(text: str) -> str:
        """
        Compute deterministic hash for normalized text content.
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
