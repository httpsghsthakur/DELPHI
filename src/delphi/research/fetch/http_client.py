import requests
import hashlib
from typing import Optional, Dict, Any

class HttpClient:
    def __init__(self, timeout: int = 10, max_size_bytes: int = 5 * 1024 * 1024):
        self.timeout = timeout
        self.max_size_bytes = max_size_bytes
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "DELPHI-Research-Bot/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        
    def fetch(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch URL respecting timeouts and size limits.
        Returns dict with text, status, etc., or None on failure.
        """
        try:
            # We could do a HEAD request to check size/type, but simple GET with stream is usually fine
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type and 'text/plain' not in content_type:
                return None
                
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.max_size_bytes:
                    # Too large, truncate or drop
                    break
                    
            text_content = content.decode('utf-8', errors='ignore')
            checksum = hashlib.sha256(content).hexdigest()
            
            return {
                "url": url,
                "canonical_url": response.url,
                "text": text_content,
                "content_type": content_type,
                "checksum": checksum,
                "status_code": response.status_code
            }
        except Exception as e:
            print(f"Fetch failed for {url}: {e}")
            return None
