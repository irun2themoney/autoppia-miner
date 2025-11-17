"""Smart caching strategies for improved performance"""
from typing import Dict, Any, List, Optional
import hashlib
import time
from collections import OrderedDict


class SmartCache:
    """Intelligent caching with similarity matching"""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict[str, tuple] = OrderedDict()
        self.access_times: Dict[str, float] = {}
    
    def _normalize_key(self, prompt: str, url: str) -> str:
        """Normalize prompt for better cache hits"""
        # Lowercase
        normalized = prompt.lower()
        
        # Remove specific values (usernames, passwords, emails)
        import re
        normalized = re.sub(r'username[:\s]+[^\s]+', 'username:XXX', normalized)
        normalized = re.sub(r'password[:\s]+[^\s]+', 'password:XXX', normalized)
        normalized = re.sub(r'email[:\s]+[^\s@]+@[^\s@]+\.[^\s@]+', 'email:XXX@XXX.XXX', normalized)
        
        # Extract domain from URL
        domain = ""
        if url:
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc
            except:
                pass
        
        # Create hash
        key_str = f"{normalized}|{domain}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, prompt: str, url: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached result"""
        key = self._normalize_key(prompt, url)
        
        if key in self.cache:
            actions, timestamp = self.cache[key]
            
            # Check TTL
            if time.time() - timestamp < self.ttl:
                # Update access time (LRU)
                self.access_times[key] = time.time()
                self.cache.move_to_end(key)
                return actions
            else:
                # Expired, remove
                del self.cache[key]
                del self.access_times[key]
        
        return None
    
    def set(self, prompt: str, url: str, actions: List[Dict[str, Any]]):
        """Cache result"""
        key = self._normalize_key(prompt, url)
        
        # Remove oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        # Add new entry
        self.cache[key] = (actions, time.time())
        self.access_times[key] = time.time()
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
        }

