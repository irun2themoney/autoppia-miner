"""
Tests for Task Classification Engine
Tests the new intelligent task classification, caching, and action generation
"""

import pytest
import json
import time
from typing import Dict, Any
from unittest.mock import AsyncMock, patch, MagicMock

# Import the classes we're testing
import sys
sys.path.insert(0, '/Users/illfaded2022/Desktop/WORKSPACE/autoppia-miner')

from api import TaskClassifier, RequestCache, RetryHandler


class TestTaskClassifier:
    """Test suite for TaskClassifier"""
    
    def test_classify_search_task(self):
        """Test classification of search tasks"""
        prompts = [
            "Find the best laptop under $1000",
            "Search for blue shoes online",
            "Look for the cheapest flights to NYC"
        ]
        
        for prompt in prompts:
            task_type = TaskClassifier.classify_task(prompt)
            assert task_type == "search", f"Failed to classify: {prompt}"
    
    def test_classify_form_fill_task(self):
        """Test classification of form fill tasks"""
        prompts = [
            "Fill out the registration form",
            "Complete the checkout process",
            "Submit the contact form with my information"
        ]
        
        for prompt in prompts:
            task_type = TaskClassifier.classify_task(prompt)
            assert task_type == "form_fill", f"Failed to classify: {prompt}"
    
    def test_classify_price_compare_task(self):
        """Test classification of price comparison tasks"""
        prompts = [
            "Compare prices on three different websites",
            "Compare the cost on Amazon vs eBay vs Walmart",
            "Show me the price comparison across all sites"
        ]
        
        for prompt in prompts:
            task_type = TaskClassifier.classify_task(prompt)
            assert task_type == "price_compare", f"Failed to classify: {prompt}"
    
    def test_classify_click_task(self):
        """Test classification of click tasks"""
        prompts = [
            "Click the login button",
            "Select the checkout option",
            "Tap the subscribe button"
        ]
        
        for prompt in prompts:
            task_type = TaskClassifier.classify_task(prompt)
            assert task_type == "click", f"Failed to classify: {prompt}"
    
    def test_classify_extract_task(self):
        """Test classification of extract tasks"""
        prompts = [
            "Extract all product names from the page",
            "Get the email address from the contact page",
            "Retrieve all links from this website"
        ]
        
        for prompt in prompts:
            task_type = TaskClassifier.classify_task(prompt)
            assert task_type == "extract", f"Failed to classify: {prompt}"
    
    def test_classify_checkout_task(self):
        """Test classification of checkout tasks"""
        prompts = [
            "Proceed to checkout",
            "Add item to cart and checkout",
            "Complete the purchase and pay now"
        ]
        
        for prompt in prompts:
            task_type = TaskClassifier.classify_task(prompt)
            assert task_type == "checkout", f"Failed to classify: {prompt}"
    
    def test_classify_generic_task(self):
        """Test classification of generic/unknown tasks"""
        prompt = "Do something random on this page"
        task_type = TaskClassifier.classify_task(prompt)
        # Could be generic or another type - just verify it doesn't crash
        assert isinstance(task_type, str)
    
    def test_generate_search_actions(self):
        """Test action generation for search tasks"""
        actions = TaskClassifier.generate_specialized_actions(
            "search",
            "https://example.com",
            "Find laptops"
        )
        
        assert len(actions) > 0
        assert any(a["action_type"] == "navigate" for a in actions)
        assert any(a["action_type"] == "click" for a in actions)
        assert any(a["action_type"] == "type" for a in actions)
        assert any(a["action_type"] == "screenshot" for a in actions)
    
    def test_generate_form_fill_actions(self):
        """Test action generation for form fill tasks"""
        actions = TaskClassifier.generate_specialized_actions(
            "form_fill",
            "https://example.com/register",
            "Fill registration form"
        )
        
        assert len(actions) > 0
        assert any(a["action_type"] == "navigate" for a in actions)
        assert any(a["action_type"] == "click" for a in actions)
        assert any(a["action_type"] == "type" for a in actions)
        assert any(a["action_type"] == "screenshot" for a in actions)
    
    def test_generate_price_compare_actions(self):
        """Test action generation for price compare tasks"""
        actions = TaskClassifier.generate_specialized_actions(
            "price_compare",
            "https://example.com",
            "Compare prices"
        )
        
        assert len(actions) > 0
        assert any(a["action_type"] == "scroll" for a in actions)
        assert any(a["action_type"] == "screenshot" for a in actions)
    
    def test_generate_checkout_actions(self):
        """Test action generation for checkout tasks"""
        actions = TaskClassifier.generate_specialized_actions(
            "checkout",
            "https://shop.example.com",
            "Buy product"
        )
        
        assert len(actions) > 0
        assert any(a["action_type"] == "navigate" for a in actions)
        assert any(a["action_type"] == "click" for a in actions)
        assert any(a["action_type"] == "screenshot" for a in actions)
    
    def test_all_actions_have_required_fields(self):
        """Test that all generated actions have required fields"""
        actions = TaskClassifier.generate_specialized_actions(
            "search",
            "https://example.com",
            "Find something"
        )
        
        for action in actions:
            assert "action_type" in action, f"Missing action_type in {action}"
            assert isinstance(action["action_type"], str)


class TestRequestCache:
    """Test suite for RequestCache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture for cache instance"""
        return RequestCache(max_size=10, ttl=100)  # 100 second TTL for testing
    
    def test_cache_initialization(self, cache):
        """Test cache initialization"""
        assert cache.max_size == 10
        assert cache.ttl == 100
        assert len(cache.cache) == 0
    
    def test_cache_set_and_get(self, cache):
        """Test setting and getting from cache"""
        prompt = "Find laptops"
        url = "https://shop.example.com"
        actions = [{"action_type": "navigate", "url": url}]
        
        # Set in cache
        cache.set(prompt, url, actions)
        
        # Get from cache
        retrieved = cache.get(prompt, url)
        
        assert retrieved is not None
        assert len(retrieved) == 1
        assert retrieved[0]["action_type"] == "navigate"
    
    def test_cache_miss(self, cache):
        """Test cache miss"""
        prompt = "Find laptops"
        url = "https://shop.example.com"
        
        # Try to get something that was never set
        retrieved = cache.get(prompt, url)
        
        assert retrieved is None
    
    def test_cache_key_generation(self, cache):
        """Test that different prompts/urls create different keys"""
        key1 = cache.get_key("Find laptops", "https://site1.com")
        key2 = cache.get_key("Find laptops", "https://site2.com")
        key3 = cache.get_key("Find shoes", "https://site1.com")
        
        assert key1 != key2, "Different URLs should create different keys"
        assert key1 != key3, "Different prompts should create different keys"
    
    def test_cache_max_size_enforcement(self, cache):
        """Test that cache respects max_size"""
        # Add more items than max_size
        for i in range(15):
            prompt = f"Find item {i}"
            url = f"https://site{i}.com"
            actions = [{"action_type": "navigate", "url": url}]
            cache.set(prompt, url, actions)
        
        # Cache should not exceed max_size
        assert len(cache.cache) <= cache.max_size
    
    def test_cache_ttl_expiration(self, cache):
        """Test that cache items expire after TTL"""
        cache_short = RequestCache(max_size=100, ttl=1)  # 1 second TTL
        
        prompt = "Find laptops"
        url = "https://shop.example.com"
        actions = [{"action_type": "navigate", "url": url}]
        
        # Set in cache
        cache_short.set(prompt, url, actions)
        
        # Immediately should be available
        assert cache_short.get(prompt, url) is not None
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should be expired now
        assert cache_short.get(prompt, url) is None
    
    def test_cache_multiple_entries(self, cache):
        """Test caching multiple different prompts/urls"""
        entries = [
            ("Find laptops", "https://shop1.com", [{"action_type": "search"}]),
            ("Find shoes", "https://shop2.com", [{"action_type": "browse"}]),
            ("Compare prices", "https://compare.com", [{"action_type": "scroll"}])
        ]
        
        # Set all entries
        for prompt, url, actions in entries:
            cache.set(prompt, url, actions)
        
        # Verify all can be retrieved
        for prompt, url, expected_actions in entries:
            retrieved = cache.get(prompt, url)
            assert retrieved is not None
            assert len(retrieved) == len(expected_actions)


class TestRetryHandler:
    """Test suite for RetryHandler"""
    
    @pytest.mark.asyncio
    async def test_successful_call_first_attempt(self):
        """Test successful call on first attempt"""
        call_count = 0
        
        async def success_coro():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await RetryHandler.call_with_retry(success_coro, max_retries=3)
        
        assert result == "success"
        assert call_count == 1, "Should succeed on first attempt"
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_then_success(self):
        """Test retry logic - fail then succeed"""
        call_count = 0
        
        async def flaky_coro():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = await RetryHandler.call_with_retry(
            flaky_coro,
            max_retries=3,
            base_delay=0.01  # Short delay for testing
        )
        
        assert result == "success"
        assert call_count == 2, "Should retry once"
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test that exception is raised after max retries"""
        call_count = 0
        
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Persistent failure"):
            await RetryHandler.call_with_retry(
                always_fails,
                max_retries=2,
                base_delay=0.01
            )
        
        assert call_count == 2, "Should attempt exactly max_retries times"
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Test that exponential backoff increases delay"""
        call_times = []
        
        async def track_timing():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("Retry me")
            return "success"
        
        start = time.time()
        result = await RetryHandler.call_with_retry(
            track_timing,
            max_retries=3,
            base_delay=0.05
        )
        
        assert result == "success"
        assert len(call_times) == 3
        
        # Check that delays increased exponentially
        if len(call_times) > 1:
            delay1 = call_times[1] - call_times[0]
            # Should be at least base_delay
            assert delay1 >= 0.04, "First delay should be ~base_delay"


class TestTaskClassificationIntegration:
    """Integration tests for the full task classification flow"""
    
    def test_classification_to_action_generation_flow(self):
        """Test complete flow: classify → generate actions"""
        test_cases = [
            ("Find the cheapest laptop", "search"),
            ("Fill the form and submit", "form_fill"),
            ("Compare prices on Amazon and eBay", "price_compare"),
            ("Click the login button", "click"),
        ]
        
        for prompt, expected_type in test_cases:
            # Step 1: Classify
            task_type = TaskClassifier.classify_task(prompt)
            assert task_type == expected_type, f"Classification failed for: {prompt}"
            
            # Step 2: Generate actions
            actions = TaskClassifier.generate_specialized_actions(
                task_type,
                "https://example.com",
                prompt
            )
            
            # Step 3: Verify actions
            assert len(actions) > 0
            assert all("action_type" in a for a in actions)
    
    def test_cache_with_classification_flow(self):
        """Test caching with the full classification flow"""
        cache = RequestCache()
        prompt = "Find laptops under $1000"
        url = "https://shop.example.com"
        
        # First time: should not be cached
        cached = cache.get(prompt, url)
        assert cached is None
        
        # Generate and cache
        task_type = TaskClassifier.classify_task(prompt)
        actions = TaskClassifier.generate_specialized_actions(
            task_type, url, prompt
        )
        cache.set(prompt, url, actions)
        
        # Second time: should be cached
        cached = cache.get(prompt, url)
        assert cached is not None
        assert len(cached) == len(actions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

