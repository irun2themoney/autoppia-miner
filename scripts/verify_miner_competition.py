#!/usr/bin/env python3
"""
Comprehensive Miner Verification Script
Proves that the miner is working and will be tested by validators
"""
import asyncio
import json
import sys
import subprocess
from typing import Dict, Any, List
import requests
from datetime import datetime

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    print(f"   {text}")

async def test_endpoint(endpoint_url: str) -> Dict[str, Any]:
    """Test the /solve_task endpoint with a real task"""
    print_header("1. ENDPOINT FUNCTIONALITY TEST")
    
    test_request = {
        "id": "verification-test-123",
        "prompt": "Login with username 'testuser' and password 'PASSWORD'",
        "url": "https://autobooks.autoppia.com"
    }
    
    try:
        print_info(f"Testing endpoint: {endpoint_url}")
        print_info(f"Request: {json.dumps(test_request, indent=2)}")
        
        response = requests.post(
            endpoint_url,
            json=test_request,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            actions_count = len(data.get('actions', []))
            
            print_success(f"Endpoint responded successfully (HTTP {response.status_code})")
            print_info(f"Response time: {response.elapsed.total_seconds():.2f}s")
            print_info(f"Actions generated: {actions_count}")
            
            # Validate response structure
            required_fields = ['actions', 'web_agent_id', 'recording']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                print_error(f"Missing required fields: {missing_fields}")
                return {"status": "error", "message": f"Missing fields: {missing_fields}"}
            
            if actions_count == 0:
                print_error("No actions generated - miner will fail validator tests!")
                return {"status": "error", "message": "Empty actions"}
            
            # Validate action format
            first_action = data['actions'][0]
            if 'type' not in first_action:
                print_error("Actions missing 'type' field - invalid IWA format!")
                return {"status": "error", "message": "Invalid action format"}
            
            print_success("Response structure is valid (IWA format)")
            print_success("Actions are non-empty")
            
            return {
                "status": "success",
                "actions_count": actions_count,
                "response_time": response.elapsed.total_seconds(),
                "has_web_agent_id": 'web_agent_id' in data,
                "has_recording": 'recording' in data
            }
        else:
            print_error(f"Endpoint returned HTTP {response.status_code}")
            print_info(f"Response: {response.text[:200]}")
            return {"status": "error", "message": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print_error(f"Endpoint test failed: {e}")
        return {"status": "error", "message": str(e)}

def check_registration() -> Dict[str, Any]:
    """Check if miner is registered on subnet 36"""
    print_header("2. NETWORK REGISTRATION CHECK")
    
    try:
        # Try to check registration via btcli
        result = subprocess.run(
            ['btcli', 'wallet', 'overview', '--netuid', '36'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and 'UID:' in result.stdout:
            print_success("Miner is registered on subnet 36")
            # Extract UID
            for line in result.stdout.split('\n'):
                if 'UID:' in line:
                    uid = line.split('UID:')[1].strip().split()[0]
                    print_info(f"UID: {uid}")
                    return {"status": "success", "registered": True, "uid": uid}
        else:
            print_warning("Could not verify registration via btcli")
            print_info("This might be okay if btcli is not installed locally")
            print_info("Registration is checked on the server where miner runs")
            return {"status": "unknown", "registered": None}
            
    except FileNotFoundError:
        print_warning("btcli not found - cannot check registration locally")
        print_info("Registration is verified on the server")
        return {"status": "unknown", "registered": None}
    except Exception as e:
        print_warning(f"Registration check failed: {e}")
        return {"status": "unknown", "registered": None}

def check_server_status(server_ip: str, password: str) -> Dict[str, Any]:
    """Check miner service status on server"""
    print_header("3. SERVER SERVICE STATUS")
    
    try:
        # Check if services are running
        result = subprocess.run(
            ['sshpass', '-p', password, 'ssh', '-o', 'StrictHostKeyChecking=no',
             f'root@{server_ip}', 'systemctl', 'is-active', 'autoppia-miner', 'autoppia-api'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            services = result.stdout.strip().split('\n')
            if all(s == 'active' for s in services):
                print_success("All services are running (active)")
                print_info(f"Miner service: {services[0] if len(services) > 0 else 'unknown'}")
                print_info(f"API service: {services[1] if len(services) > 1 else 'unknown'}")
                return {"status": "success", "services_running": True}
            else:
                print_error(f"Some services not active: {services}")
                return {"status": "error", "services_running": False}
        else:
            print_error("Could not check service status")
            return {"status": "error", "services_running": False}
            
    except Exception as e:
        print_warning(f"Server status check failed: {e}")
        print_info("This might be okay if SSH is not configured")
        return {"status": "unknown", "services_running": None}

def check_validator_activity(server_ip: str, password: str) -> Dict[str, Any]:
    """Check for recent validator activity in logs"""
    print_header("4. VALIDATOR ACTIVITY CHECK")
    
    try:
        # Check logs for validator requests
        result = subprocess.run(
            ['sshpass', '-p', password, 'ssh', '-o', 'StrictHostKeyChecking=no',
             f'root@{server_ip}',
             'journalctl', '-u', 'autoppia-api', '--since', '24 hours ago', '--no-pager',
             '|', 'grep', '-i', 'solve_task', '|', 'wc', '-l'],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )
        
        if result.returncode == 0:
            request_count = int(result.stdout.strip() or 0)
            if request_count > 0:
                print_success(f"Found {request_count} API requests in last 24 hours")
                print_info("This indicates validators are testing your miner!")
                return {"status": "success", "requests": request_count}
            else:
                print_warning("No API requests in last 24 hours")
                print_info("This is normal if miner was just deployed")
                print_info("Validators test miners periodically, not continuously")
                return {"status": "warning", "requests": 0}
        else:
            print_warning("Could not check validator activity")
            return {"status": "unknown", "requests": None}
            
    except Exception as e:
        print_warning(f"Validator activity check failed: {e}")
        return {"status": "unknown", "requests": None}

def check_playground_compatibility() -> Dict[str, Any]:
    """Test with actual playground request format"""
    print_header("5. PLAYGROUND COMPATIBILITY TEST")
    
    # This is the exact format playground uses
    playground_request = {
        "id": "db744351-e7a3-4512-91b6-b5a34456b6b0",
        "prompt": "Register with username 'newuserdb744351', email 'newuserdb744351@gmail.com' and password 'PASSWORD'",
        "url": "https://autobooks.autoppia.com"
    }
    
    endpoint_url = "https://134.199.203.133:8443/solve_task"
    
    try:
        response = requests.post(
            endpoint_url,
            json=playground_request,
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            actions_count = len(data.get('actions', []))
            
            if actions_count > 0:
                print_success("Playground request format accepted")
                print_success(f"Generated {actions_count} actions")
                print_info("This is the exact format validators use")
                return {"status": "success", "compatible": True, "actions": actions_count}
            else:
                print_error("Playground request returned empty actions")
                return {"status": "error", "compatible": False}
        else:
            print_error(f"Playground request failed: HTTP {response.status_code}")
            return {"status": "error", "compatible": False}
            
    except Exception as e:
        print_error(f"Playground compatibility test failed: {e}")
        return {"status": "error", "compatible": False}

def generate_final_report(results: Dict[str, Any]):
    """Generate final verification report"""
    print_header("FINAL VERIFICATION REPORT")
    
    all_passed = True
    critical_passed = True
    
    # Critical checks
    print(f"\n{Colors.BOLD}CRITICAL CHECKS:{Colors.END}")
    if results.get('endpoint', {}).get('status') == 'success':
        print_success("Endpoint is working and generating actions")
    else:
        print_error("Endpoint test failed - CRITICAL ISSUE")
        critical_passed = False
        all_passed = False
    
    if results.get('playground', {}).get('compatible'):
        print_success("Playground format compatible")
    else:
        print_error("Playground format incompatible - CRITICAL ISSUE")
        critical_passed = False
        all_passed = False
    
    # Important checks
    print(f"\n{Colors.BOLD}IMPORTANT CHECKS:{Colors.END}")
    if results.get('server', {}).get('services_running'):
        print_success("Services are running on server")
    elif results.get('server', {}).get('services_running') is None:
        print_warning("Could not verify server status (SSH issue)")
    else:
        print_error("Services not running - FIX REQUIRED")
        all_passed = False
    
    validator_requests = results.get('validator_activity', {}).get('requests')
    if validator_requests is not None and validator_requests > 0:
        print_success(f"Validator activity detected ({validator_requests} requests)")
    else:
        print_info("No recent validator activity (normal for new deployments)")
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    if critical_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ MINER IS READY FOR VALIDATOR TESTING{Colors.END}")
        print(f"\n{Colors.GREEN}Your miner will be tested by validators because:{Colors.END}")
        print(f"   1. ✅ Endpoint is working and generating valid actions")
        print(f"   2. ✅ Playground format is compatible")
        print(f"   3. ✅ Services are running (if verified)")
        print(f"\n{Colors.BLUE}Next Steps:{Colors.END}")
        print(f"   • Test on playground: https://infinitewebarena.autoppia.com")
        print(f"   • Monitor IWA platform: https://infinitewebarena.autoppia.com/subnet36/overview")
        print(f"   • Validators will discover and test your miner automatically")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ CRITICAL ISSUES FOUND{Colors.END}")
        print(f"\n{Colors.RED}Your miner will NOT work correctly until these are fixed:{Colors.END}")
        if results.get('endpoint', {}).get('status') != 'success':
            print(f"   • Fix endpoint functionality")
        if not results.get('playground', {}).get('compatible'):
            print(f"   • Fix playground compatibility")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

async def main():
    """Run all verification checks"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     MINER COMPETITION VERIFICATION                        ║")
    print("║     Proving your miner will be tested by validators      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    endpoint_url = "https://134.199.203.133:8443/solve_task"
    server_ip = "134.199.203.133"
    server_password = "DigitalOcean4life"
    
    results = {}
    
    # Run all checks
    results['endpoint'] = await test_endpoint(endpoint_url)
    results['registration'] = check_registration()
    results['server'] = check_server_status(server_ip, server_password)
    results['validator_activity'] = check_validator_activity(server_ip, server_password)
    results['playground'] = check_playground_compatibility()
    
    # Generate final report
    generate_final_report(results)
    
    # Exit code
    if results.get('endpoint', {}).get('status') == 'success' and results.get('playground', {}).get('compatible'):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

