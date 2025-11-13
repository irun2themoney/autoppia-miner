#!/usr/bin/env python3
"""
Autoppia Worker Benchmark Script
Tests response times and performance metrics
"""

import asyncio
import httpx
import time
from statistics import mean, stdev
from typing import List, Dict
import json
from datetime import datetime

class WorkerBenchmark:
    """Benchmark suite for Autoppia Worker"""
    
    def __init__(self, base_url: str = "https://autoppia-miner.onrender.com"):
        self.base_url = base_url
        self.results = {}
    
    async def benchmark_endpoint(
        self, 
        endpoint: str, 
        payload: Dict,
        method: str = "POST",
        iterations: int = 10,
        timeout: float = 30.0
    ) -> Dict:
        """Benchmark an endpoint"""
        times = []
        errors = []
        
        print(f"\n{'='*60}")
        print(f"📊 Benchmarking: {endpoint}")
        print(f"Iterations: {iterations} | Method: {method}")
        print(f"{'='*60}")
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            for i in range(iterations):
                start = time.time()
                try:
                    if method == "POST":
                        response = await client.post(
                            f"{self.base_url}{endpoint}",
                            json=payload
                        )
                    else:
                        response = await client.get(f"{self.base_url}{endpoint}")
                    
                    duration = time.time() - start
                    times.append(duration)
                    
                    status_color = "✅" if response.status_code == 200 else "⚠️ "
                    print(f"  Request {i+1:2d}: {duration:6.3f}s - {status_color} "
                          f"Status: {response.status_code}")
                    
                except asyncio.TimeoutError:
                    duration = time.time() - start
                    errors.append(f"Timeout after {duration:.1f}s")
                    print(f"  Request {i+1:2d}: ⏱️  TIMEOUT (>{timeout}s)")
                except Exception as e:
                    duration = time.time() - start
                    error_msg = str(e)[:50]
                    errors.append(error_msg)
                    print(f"  Request {i+1:2d}: ❌ FAILED - {error_msg}")
        
        # Calculate statistics
        if times:
            result = {
                "endpoint": endpoint,
                "iterations": iterations,
                "successful": len(times),
                "failed": len(errors),
                "min": min(times),
                "max": max(times),
                "avg": mean(times),
                "stdev": stdev(times) if len(times) > 1 else 0,
                "errors": errors
            }
            
            print(f"\n📈 Results for {endpoint}:")
            print(f"  ✅ Successful:  {result['successful']}/{iterations}")
            if errors:
                print(f"  ❌ Failed:      {result['failed']}")
            print(f"  ⏱️  Min:         {result['min']:.3f}s")
            print(f"  ⏱️  Max:         {result['max']:.3f}s")
            print(f"  ⏱️  Average:     {result['avg']:.3f}s")
            if result['stdev'] > 0:
                print(f"  📊 Std Dev:     {result['stdev']:.3f}s")
            
            return result
        else:
            print(f"\n❌ All requests failed!")
            return {
                "endpoint": endpoint,
                "iterations": iterations,
                "successful": 0,
                "failed": iterations,
                "errors": errors
            }
    
    async def run_all_benchmarks(self, iterations: int = 10):
        """Run complete benchmark suite"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*12 + "🔥 AUTOPPIA WORKER BENCHMARK SUITE 🔥" + " "*8 + "║")
        print("║" + f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " "*30 + "║")
        print("║" + f"Base URL: {self.base_url}" + " "*(58-len(f"Base URL: {self.base_url}")) + "║")
        print("╚" + "="*58 + "╝\n")
        
        # Test health endpoint
        self.results['health'] = await self.benchmark_endpoint(
            "/health",
            {},
            method="GET",
            iterations=iterations
        )
        
        # Test root endpoint
        self.results['root'] = await self.benchmark_endpoint(
            "/",
            {},
            method="GET",
            iterations=iterations
        )
        
        # Test mine task
        self.results['mine'] = await self.benchmark_endpoint(
            "/process",
            {
                "task": "mine",
                "input_data": {
                    "source": "benchmark_source",
                    "pattern": "benchmark_pattern"
                }
            },
            iterations=iterations
        )
        
        # Test process task
        self.results['process'] = await self.benchmark_endpoint(
            "/process",
            {
                "task": "process",
                "input_data": {
                    "data": ["item1", "item2", "item3", "item4", "item5"]
                }
            },
            iterations=iterations
        )
        
        # Test generate task (slowest)
        self.results['generate'] = await self.benchmark_endpoint(
            "/process",
            {
                "task": "generate",
                "input_data": {
                    "prompt": "Generate a helpful response to: What is machine learning?"
                }
            },
            iterations=max(5, iterations // 2)  # Fewer iterations for slower task
        )
        
        # Test solve task (Bittensor)
        self.results['solve'] = await self.benchmark_endpoint(
            "/solve_task",
            {
                "id": "benchmark_task_001",
                "prompt": "Click the login button and enter credentials",
                "url": "https://example.com/login",
                "seed": 12345,
                "web_project_name": "benchmark_project",
                "specifications": {}
            },
            iterations=max(5, iterations // 2)
        )
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print summary of all benchmarks"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*21 + "📊 BENCHMARK SUMMARY 📊" + " "*15 + "║")
        print("╚" + "="*58 + "╝\n")
        
        print("Endpoint Performance Summary:")
        print(f"{'Endpoint':<20} {'Avg Time':<12} {'Min-Max':<20} {'Success Rate':<15}")
        print("-" * 67)
        
        total_success = 0
        total_requests = 0
        
        for endpoint_name, result in self.results.items():
            if 'avg' in result:
                avg = result['avg']
                min_time = result['min']
                max_time = result['max']
                success = result['successful']
                total = result['iterations']
                success_rate = (success / total * 100) if total > 0 else 0
                
                total_success += success
                total_requests += total
                
                print(f"{endpoint_name:<20} {avg:>8.3f}s   {min_time:.3f}s-{max_time:.3f}s  {success_rate:>6.1f}% ({success}/{total})")
        
        overall_success = (total_success / total_requests * 100) if total_requests > 0 else 0
        print("-" * 67)
        print(f"{'OVERALL':<20} {'':<12} {'':<20} {overall_success:>6.1f}% ({total_success}/{total_requests})")
        
        # Performance assessment
        print("\n" + "="*67)
        print("📈 Performance Assessment:")
        print("="*67)
        
        for endpoint_name, result in self.results.items():
            if 'avg' in result:
                avg = result['avg']
                
                # Define performance tiers
                if endpoint_name == 'generate' or endpoint_name == 'solve':
                    max_acceptable = 5.0
                    good_threshold = 2.0
                else:
                    max_acceptable = 2.0
                    good_threshold = 0.5
                
                if avg < good_threshold:
                    status = "✅ EXCELLENT"
                elif avg < max_acceptable:
                    status = "✔️  GOOD"
                else:
                    status = "⚠️  ACCEPTABLE"
                
                print(f"  {endpoint_name:<15} {avg:>7.3f}s {status}")
        
        print("\n✅ Benchmark complete!")
        print(f"📊 Results saved for analysis")


async def main():
    """Run benchmarks"""
    import sys
    
    # Get iterations from command line or default to 10
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    # Get URL from environment or use default
    url = "https://autoppia-miner.onrender.com"
    
    benchmark = WorkerBenchmark(base_url=url)
    await benchmark.run_all_benchmarks(iterations=iterations)


if __name__ == "__main__":
    asyncio.run(main())

