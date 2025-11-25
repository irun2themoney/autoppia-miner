#!/usr/bin/env python3
"""
Test performance optimizations - browser caching and response times
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import time
from api.utils.browser_analyzer import _get_browser, get_browser_analyzer, close_browser

async def test_browser_caching():
    """Test that browser instance is cached and reused"""
    print("=" * 70)
    print("🧪 Testing Browser Instance Caching")
    print("=" * 70)
    print()
    
    # Test 1: First browser creation (should be slow)
    print("Test 1: First browser creation...")
    start_time = time.time()
    browser1 = await _get_browser()
    first_time = time.time() - start_time
    print(f"   ✅ Browser created in {first_time:.2f} seconds")
    print(f"   Browser ID: {id(browser1)}")
    print()
    
    # Test 2: Second call (should be instant - cached)
    print("Test 2: Second call (should use cached instance)...")
    start_time = time.time()
    browser2 = await _get_browser()
    second_time = time.time() - start_time
    print(f"   ✅ Browser retrieved in {second_time:.2f} seconds")
    print(f"   Browser ID: {id(browser2)}")
    print()
    
    # Verify same instance
    if browser1 is browser2:
        print("   ✅ SUCCESS: Same browser instance reused (cached)")
    else:
        print("   ❌ FAILED: Different browser instances (not cached)")
    print()
    
    # Test 3: Multiple rapid calls (all should be instant)
    print("Test 3: Multiple rapid calls (testing cache performance)...")
    start_time = time.time()
    browsers = []
    for i in range(10):
        browser = await _get_browser()
        browsers.append(browser)
    rapid_time = time.time() - start_time
    avg_time = rapid_time / 10
    print(f"   ✅ 10 calls completed in {rapid_time:.2f} seconds")
    print(f"   Average: {avg_time:.4f} seconds per call")
    print()
    
    # Verify all same instance
    all_same = all(b is browser1 for b in browsers)
    if all_same:
        print("   ✅ SUCCESS: All calls returned same cached instance")
    else:
        print("   ❌ FAILED: Different instances returned")
    print()
    
    # Test 4: Browser analyzer (should also use cached browser)
    print("Test 4: Browser analyzer (should use cached browser)...")
    start_time = time.time()
    analyzer1 = await get_browser_analyzer()
    analyzer_time = time.time() - start_time
    print(f"   ✅ Analyzer created in {analyzer_time:.2f} seconds")
    if analyzer1 and analyzer1.browser is browser1:
        print("   ✅ SUCCESS: Analyzer uses cached browser instance")
    else:
        print("   ❌ FAILED: Analyzer created new browser")
    print()
    
    # Summary
    print("=" * 70)
    print("📊 Performance Summary")
    print("=" * 70)
    print(f"First creation: {first_time:.2f}s (expected: 1-3s)")
    print(f"Second call: {second_time:.4f}s (expected: < 0.01s)")
    print(f"Average (10 calls): {avg_time:.4f}s (expected: < 0.01s)")
    print()
    
    if second_time < 0.01 and avg_time < 0.01:
        print("✅ SUCCESS: Browser caching working correctly!")
        print("   Response times should be < 1.5s now (down from 3-6s)")
    else:
        print("⚠️  WARNING: Browser may not be cached properly")
    print()
    
    # Cleanup
    await close_browser()
    print("✅ Browser closed (cleanup)")

async def test_page_loading():
    """Test page loading performance"""
    print("=" * 70)
    print("🧪 Testing Page Loading Performance")
    print("=" * 70)
    print()
    
    analyzer = await get_browser_analyzer()
    if not analyzer:
        print("❌ Failed to get browser analyzer")
        return
    
    # Test page loading
    test_url = "https://example.com"
    print(f"Test: Loading {test_url}...")
    
    start_time = time.time()
    result = await analyzer.fetch_page(test_url, timeout=5.0)
    load_time = time.time() - start_time
    
    if result:
        print(f"   ✅ Page loaded in {load_time:.2f} seconds")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Elements found: {len(result.get('elements', []))}")
        print()
        
        if load_time < 1.5:
            print("   ✅ SUCCESS: Page loading < 1.5s target!")
        elif load_time < 3.0:
            print("   ⚠️  WARNING: Page loading > 1.5s but < 3s")
        else:
            print("   ❌ FAILED: Page loading > 3s (too slow)")
    else:
        print("   ❌ Failed to load page")
    
    print()
    
    # Cleanup
    await close_browser()

async def main():
    """Run all tests"""
    print()
    print("🚀 Performance Optimization Tests")
    print()
    
    try:
        await test_browser_caching()
        print()
        await test_page_loading()
        print()
        print("=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

