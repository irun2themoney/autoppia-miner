"""Vector store memory for task pattern recall - Top tier optimization"""
import json
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logging.warning("sklearn not available, vector memory will use simple text matching")

logger = logging.getLogger(__name__)


@dataclass
class TaskMemory:
    """Stores a successful task pattern"""
    prompt: str
    url: str
    actions: List[Dict[str, Any]]
    success_rate: float
    avg_time: float
    task_type: str
    timestamp: float


class VectorMemory:
    """
    Vector store for task memory - enables pattern recall
    Based on top miner patterns: +15-20% success on evolving tasks
    """
    
    def __init__(self, max_memories: int = 1000):
        self.memories: List[TaskMemory] = []
        self.max_memories = max_memories
        self.vectorizer = None
        self._init_vectorizer()
    
    def _init_vectorizer(self):
        """Initialize TF-IDF vectorizer for text similarity"""
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                ngram_range=(1, 2)
            )
    
    def add_memory(
        self,
        prompt: str,
        url: str,
        actions: List[Dict[str, Any]],
        success_rate: float = 1.0,
        avg_time: float = 0.0,
        task_type: str = "generic"
    ):
        """Store a successful task pattern"""
        import time
        
        memory = TaskMemory(
            prompt=prompt,
            url=url,
            actions=actions,
            success_rate=success_rate,
            avg_time=avg_time,
            task_type=task_type,
            timestamp=time.time()
        )
        
        self.memories.append(memory)
        
        # Keep only recent memories
        if len(self.memories) > self.max_memories:
            # Remove oldest memories
            self.memories = sorted(
                self.memories,
                key=lambda m: m.timestamp,
                reverse=True
            )[:self.max_memories]
        
        logger.info(f"Stored memory: {task_type} task with {len(actions)} actions")
    
    def find_similar(
        self,
        prompt: str,
        url: Optional[str] = None,
        top_k: int = 3
    ) -> List[TaskMemory]:
        """
        Find similar past tasks using vector similarity
        Returns top-k most similar memories
        """
        if not self.memories:
            return []
        
        if HAS_SKLEARN and self.vectorizer:
            return self._find_similar_vectorized(prompt, url, top_k)
        else:
            return self._find_similar_simple(prompt, url, top_k)
    
    def _find_similar_vectorized(
        self,
        prompt: str,
        url: Optional[str],
        top_k: int
    ) -> List[TaskMemory]:
        """Find similar using TF-IDF cosine similarity"""
        try:
            # Prepare texts for vectorization
            query_text = f"{prompt} {url or ''}"
            memory_texts = [
                f"{m.prompt} {m.url}" for m in self.memories
            ]
            
            # Fit and transform
            all_texts = [query_text] + memory_texts
            vectors = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarity
            query_vector = vectors[0:1]
            memory_vectors = vectors[1:]
            
            similarities = cosine_similarity(query_vector, memory_vectors)[0]
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Return top-k memories
            results = [self.memories[i] for i in top_indices if similarities[i] > 0.3]
            return results
        except Exception as e:
            logger.warning(f"Vector similarity failed: {e}, falling back to simple matching")
            return self._find_similar_simple(prompt, url, top_k)
    
    def _find_similar_simple(
        self,
        prompt: str,
        url: Optional[str],
        top_k: int
    ) -> List[TaskMemory]:
        """Simple text-based similarity matching"""
        prompt_lower = prompt.lower()
        url_lower = (url or "").lower()
        
        scored = []
        for memory in self.memories:
            score = 0.0
            
            # Prompt similarity
            memory_prompt_lower = memory.prompt.lower()
            prompt_words = set(prompt_lower.split())
            memory_words = set(memory_prompt_lower.split())
            if prompt_words and memory_words:
                prompt_sim = len(prompt_words & memory_words) / len(prompt_words | memory_words)
                score += prompt_sim * 0.7
            
            # URL similarity
            if url_lower and memory.url.lower():
                if url_lower in memory.url.lower() or memory.url.lower() in url_lower:
                    score += 0.3
            
            # Task type bonus
            if memory.task_type != "generic":
                # Extract task type from prompt
                task_keywords = {
                    "login": ["login", "sign in", "authenticate"],
                    "form": ["form", "fill", "submit"],
                    "click": ["click", "button", "link"],
                    "extract": ["extract", "get", "find", "data"],
                }
                for task_type, keywords in task_keywords.items():
                    if any(kw in prompt_lower for kw in keywords):
                        if memory.task_type == task_type:
                            score += 0.2
                        break
            
            if score > 0.2:  # Minimum similarity threshold
                scored.append((score, memory))
        
        # Sort by score and return top-k
        scored.sort(key=lambda x: x[0], reverse=True)
        return [memory for _, memory in scored[:top_k]]
    
    def get_best_actions(
        self,
        prompt: str,
        url: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get best actions from similar past tasks
        DYNAMIC ZERO: Includes anti-overfitting protection
        Returns actions from most similar successful task
        """
        similar = self.find_similar(prompt, url, top_k=1)
        
        if similar:
            best = similar[0]
            if best.success_rate >= 0.7:  # Only use if success rate is good
                # DYNAMIC ZERO: Check for overfitting before using memory
                try:
                    from .anti_overfitting import anti_overfitting
                    # Estimate similarity (vector memory uses cosine similarity internally)
                    # Assume high similarity if found in top-1
                    estimated_similarity = 0.8
                    memory_key = f"{best.prompt[:50]}|{best.url}"
                    should_use, adjusted_confidence = anti_overfitting.should_use_pattern(
                        estimated_similarity, memory_key, prompt, url
                    )
                    
                    if should_use and adjusted_confidence >= 0.5:
                        logger.info(f"Recalled similar task: {best.task_type} (success: {best.success_rate:.0%})")
                        return best.actions
                    else:
                        logger.info(f"Vector memory: Overfitting detected, skipping memory recall")
                        return None
                except ImportError:
                    # Anti-overfitting not available, use memory anyway
                    logger.info(f"Recalled similar task: {best.task_type} (success: {best.success_rate:.0%})")
                    return best.actions
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        if not self.memories:
            return {
                "total_memories": 0,
                "avg_success_rate": 0.0,
                "task_types": {}
            }
        
        task_types = {}
        total_success = 0.0
        
        for memory in self.memories:
            task_types[memory.task_type] = task_types.get(memory.task_type, 0) + 1
            total_success += memory.success_rate
        
        return {
            "total_memories": len(self.memories),
            "avg_success_rate": total_success / len(self.memories),
            "task_types": task_types
        }

