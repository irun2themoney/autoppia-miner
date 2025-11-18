"""Advanced Semantic Caching - Semantic similarity matching for 50%+ cache hit rate"""
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import time
from collections import OrderedDict
import re
import logging

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Advanced semantic caching with similarity matching
    Uses text similarity to find similar tasks (not just exact matches)
    Target: 50%+ cache hit rate
    """
    
    def __init__(self, max_size: int = 200, ttl: int = 600, similarity_threshold: float = 0.98):
        self.max_size = max_size
        self.ttl = ttl
        self.similarity_threshold = similarity_threshold  # Increased to 0.98 to prevent false matches (almost exact only)
        self.cache: OrderedDict[str, Tuple[List[Dict[str, Any]], float, str]] = OrderedDict()
        self.access_times: Dict[str, float] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        if not text:
            return ""
        
        # Lowercase
        normalized = text.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # For login tasks, be more strict - include username/password placeholders in the key
        # This prevents matching incomplete login patterns
        if 'login' in normalized or 'sign in' in normalized:
            # Keep the structure but normalize values
            normalized = re.sub(r'username[:\s]+[^\s]+', 'username:PLACEHOLDER', normalized)
            normalized = re.sub(r'password[:\s]+[^\s]+', 'password:PLACEHOLDER', normalized)
        else:
            # For other tasks, remove specific values
            normalized = re.sub(r'username[:\s]+[^\s]+', 'username:XXX', normalized)
            normalized = re.sub(r'password[:\s]+[^\s]+', 'password:XXX', normalized)
        
        # Remove email and URLs
        normalized = re.sub(r'email[:\s]+[^\s@]+@[^\s@]+\.[^\s@]+', 'email:XXX@XXX.XXX', normalized)
        normalized = re.sub(r'https?://[^\s]+', 'URL:XXX', normalized)
        
        # Remove common filler words
        filler_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        words = normalized.split()
        words = [w for w in words if w not in filler_words]
        normalized = ' '.join(words)
        
        return normalized.strip()
    
    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text"""
        normalized = self._normalize_text(text)
        # Split into words and filter out very short words
        words = [w for w in normalized.split() if len(w) > 2]
        return set(words)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts
        Uses Jaccard similarity on keywords
        """
        keywords1 = self._extract_keywords(text1)
        keywords2 = self._extract_keywords(text2)
        
        if not keywords1 and not keywords2:
            return 1.0  # Both empty
        
        if not keywords1 or not keywords2:
            return 0.0  # One empty
        
        # Jaccard similarity
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        if union == 0:
            return 0.0
        
        similarity = intersection / union
        
        # Boost similarity if key action words match
        action_words = {'login', 'click', 'type', 'submit', 'search', 'fill', 'select', 'navigate'}
        action_match1 = keywords1 & action_words
        action_match2 = keywords2 & action_words
        
        if action_match1 and action_match2 and action_match1 == action_match2:
            similarity += 0.1  # Boost for matching action words
        
        return min(1.0, similarity)
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain.lower()
        except:
            return ""
    
    def _create_cache_key(self, prompt: str, url: str) -> str:
        """Create cache key from prompt and URL"""
        normalized_prompt = self._normalize_text(prompt)
        domain = self._get_domain(url)
        
        # Create key from normalized prompt and domain
        key_str = f"{normalized_prompt}|{domain}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(
        self,
        prompt: str,
        url: str
    ) -> Optional[Tuple[List[Dict[str, Any]], float]]:
        """
        Get cached result with semantic similarity matching
        DYNAMIC ZERO: Includes anti-overfitting protection
        
        Returns:
            (cached_actions, similarity_score) or None
        """
        # DYNAMIC ZERO: Import anti-overfitting (lazy import to avoid circular deps)
        try:
            from .anti_overfitting import anti_overfitting
            has_anti_overfitting = True
        except ImportError:
            has_anti_overfitting = False
        
        # First try exact match
        exact_key = self._create_cache_key(prompt, url)
        if exact_key in self.cache:
            actions, timestamp, original_prompt = self.cache[exact_key]
            
            # Check TTL
            if time.time() - timestamp < self.ttl:
                # DYNAMIC ZERO: Check for overfitting before using exact match
                if has_anti_overfitting:
                    similarity = 1.0  # Exact match
                    should_use, adjusted_confidence = anti_overfitting.should_use_pattern(
                        similarity, exact_key, prompt, url
                    )
                    if not should_use or adjusted_confidence < 0.6:
                        # Overfitting detected, skip cache
                        logger.info(f"Semantic cache: Overfitting detected, skipping exact match")
                        self.cache_misses += 1
                        return None
                    similarity = adjusted_confidence
                else:
                    similarity = 1.0
                
                self.access_times[exact_key] = time.time()
                self.cache.move_to_end(exact_key)
                self.cache_hits += 1
                logger.info(f"Semantic cache: Exact match found")
                return (actions, similarity)
            else:
                # Expired, remove
                del self.cache[exact_key]
                del self.access_times[exact_key]
        
        # Try semantic similarity matching
        normalized_prompt = self._normalize_text(prompt)
        best_match = None
        best_similarity = 0.0
        
        current_time = time.time()
        for key, (actions, timestamp, cached_prompt) in self.cache.items():
            # Check TTL
            if current_time - timestamp >= self.ttl:
                continue
            
            # Calculate similarity
            similarity = self._calculate_similarity(normalized_prompt, cached_prompt)
            
            # Also check domain match
            domain = self._get_domain(url)
            cached_domain = self._get_domain(cached_prompt)  # Try to extract from cached prompt
            if domain and cached_domain and domain == cached_domain:
                similarity += 0.05  # Small boost for same domain
            
            # DYNAMIC ZERO: Check for overfitting
            if has_anti_overfitting and similarity >= self.similarity_threshold:
                should_use, adjusted_confidence = anti_overfitting.should_use_pattern(
                    similarity, key, prompt, url
                )
                if should_use and adjusted_confidence >= 0.5:
                    similarity = adjusted_confidence
                else:
                    # Overfitting detected, skip this match
                    continue
            
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = (key, actions)
        
        if best_match:
            key, actions = best_match
            self.access_times[key] = time.time()
            self.cache.move_to_end(key)
            self.cache_hits += 1
            logger.info(f"Semantic cache: Similar match found (similarity: {best_similarity:.2f})")
            return (actions, best_similarity)
        
        self.cache_misses += 1
        return None
    
    def set(
        self,
        prompt: str,
        url: str,
        actions: List[Dict[str, Any]]
    ):
        """Cache result"""
        key = self._create_cache_key(prompt, url)
        normalized_prompt = self._normalize_text(prompt)
        
        # Remove oldest if at max size
        if len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        # Add new entry
        self.cache[key] = (actions, time.time(), normalized_prompt)
        self.access_times[key] = time.time()
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.access_times.clear()
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": round(hit_rate, 2),
            "similarity_threshold": self.similarity_threshold
        }


# Global instance
semantic_cache = SemanticCache()

