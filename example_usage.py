"""
Example usage of Autoppia Worker with Chutes API
"""

import asyncio
import os
from dotenv import load_dotenv
from worker import AutoppiaWorker, WorkerRequest

# Load environment variables
load_dotenv()


async def main():
    """Example usage of the Autoppia Worker"""
    
    # Initialize worker
    print("Initializing Autoppia Worker...")
    worker = AutoppiaWorker()
    
    # Check if Chutes API is configured
    if worker.config.chutes_api_key:
        print(f"✓ Chutes API configured: {worker.config.chutes_api_key[:20]}...")
    else:
        print("⚠ Chutes API not configured. Set CHUTES_API_KEY in .env file")
    
    # Example 1: Generate text with simple prompt
    print("\n" + "="*50)
    print("Example 1: Generate text with simple prompt")
    print("="*50)
    
    request1 = WorkerRequest(
        task="generate",
        input_data={
            "prompt": "Write a short summary about artificial intelligence",
            "model": "gpt-4",
            "max_tokens": 200,
            "temperature": 0.7
        }
    )
    
    response1 = await worker.process(request1)
    print(f"Success: {response1.success}")
    if response1.success:
        print(f"Generated text: {response1.result.get('generated_text', '')[:200]}...")
        print(f"Provider: {response1.result.get('provider', 'unknown')}")
        print(f"Tokens used: {response1.result.get('tokens_used', 0)}")
    else:
        print(f"Error: {response1.error}")
    
    # Example 2: Generate with chat messages format
    print("\n" + "="*50)
    print("Example 2: Generate with chat messages format")
    print("="*50)
    
    request2 = WorkerRequest(
        task="generate",
        input_data={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that explains complex topics simply."},
                {"role": "user", "content": "Explain quantum computing in 3 sentences."}
            ],
            "model": "gpt-4",
            "max_tokens": 150
        }
    )
    
    response2 = await worker.process(request2)
    print(f"Success: {response2.success}")
    if response2.success:
        print(f"Generated text: {response2.result.get('generated_text', '')}")
        print(f"Provider: {response2.result.get('provider', 'unknown')}")
    else:
        print(f"Error: {response2.error}")
    
    # Example 3: Process data
    print("\n" + "="*50)
    print("Example 3: Process data")
    print("="*50)
    
    request3 = WorkerRequest(
        task="process",
        input_data={
            "data": ["item1", "item2", "item3", "item4"]
        }
    )
    
    response3 = await worker.process(request3)
    print(f"Success: {response3.success}")
    if response3.success:
        print(f"Processed {response3.result.get('processed_count', 0)} items")
    
    # Example 4: Health check
    print("\n" + "="*50)
    print("Example 4: Health check")
    print("="*50)
    
    health = await worker.health_check()
    print(f"Status: {health.get('status')}")
    print(f"Chutes API configured: {health.get('chutes_api_configured', False)}")
    if 'chutes_api_status' in health:
        print(f"Chutes API status: {health.get('chutes_api_status')}")
    
    # Cleanup
    if worker.chutes_client:
        await worker.chutes_client.aclose()
    
    print("\n" + "="*50)
    print("Examples completed!")
    print("="*50)


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run examples
    asyncio.run(main())

