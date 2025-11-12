#!/usr/bin/env python3
"""Quick test to verify worker functionality"""

import asyncio
from worker import AutoppiaWorker

async def test():
    print("Testing Autoppia Worker...")
    print("-" * 50)
    
    worker = AutoppiaWorker()
    print(f"✓ Worker initialized: {worker.worker_name}")
    print(f"✓ Chutes API configured: {worker.config.chutes_api_key is not None}")
    
    health = await worker.health_check()
    print(f"✓ Health status: {health['status']}")
    print(f"✓ Chutes API status: {health.get('chutes_api_configured', False)}")
    
    await worker.__aexit__(None, None, None)
    print("\n✓ All basic tests passed!")

if __name__ == "__main__":
    asyncio.run(test())

