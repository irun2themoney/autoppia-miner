#!/usr/bin/env python3
"""
Pre-Deployment Validation Script
Validates that the miner is correctly configured and ready for validators
"""
import sys
import os
import time
import subprocess
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{RESET}")

def print_header(msg):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{msg}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def check_environment():
    """Check environment variables and configuration"""
    print_header("1. ENVIRONMENT & CONFIGURATION")
    
    issues = []
    
    # Check .env file exists
    env_file = project_root / ".env"
    if env_file.exists():
        print_success(".env file exists")
    else:
        print_warning(".env file not found (may use environment variables)")
    
    # Check critical settings
    try:
        from config.settings import settings
        
        checks = [
            ("Subnet UID", settings.subnet_uid, 36),
            ("Network", settings.network, "finney"),
            ("API Port", settings.api_port, 8080),
            ("Axon Port", settings.axon_port, 8091),
        ]
        
        for name, actual, expected in checks:
            if actual == expected:
                print_success(f"{name}: {actual} (correct)")
            else:
                print_error(f"{name}: {actual} (expected {expected})")
                issues.append(f"{name} is {actual}, should be {expected}")
        
        # Check API URL
        api_url = settings.api_url
        print_info(f"API URL: {api_url}")
        if "localhost" in api_url or "127.0.0.1" in api_url:
            print_warning("API URL points to localhost - ensure this matches deployment server")
        else:
            print_success(f"API URL: {api_url}")
            
    except Exception as e:
        print_error(f"Error loading settings: {e}")
        issues.append(f"Failed to load settings: {e}")
        return issues
    
    return issues

def check_wallet():
    """Check wallet configuration"""
    print_header("2. WALLET CONFIGURATION")
    
    issues = []
    
    try:
        import bittensor as bt
        from config.settings import settings
        
        # Try to load wallet
        wallet_name = os.getenv("WALLET_NAME", "default")
        wallet_hotkey = os.getenv("WALLET_HOTKEY", "default")
        
        print_info(f"Wallet: {wallet_name}/{wallet_hotkey}")
        
        try:
            wallet = bt.wallet(name=wallet_name, hotkey=wallet_hotkey)
            print_success(f"Wallet loaded: {wallet.hotkey.ss58_address}")
            
            # Check if wallet has balance
            try:
                subtensor = bt.subtensor(network=settings.network)
                balance = subtensor.get_balance(wallet.hotkey.ss58_address)
                print_info(f"Wallet balance: {balance} TAO")
                if balance == 0:
                    print_warning("Wallet balance is 0 - miner may not be able to register")
                else:
                    print_success(f"Wallet has balance: {balance} TAO")
            except Exception as e:
                print_warning(f"Could not check balance: {e}")
                
        except Exception as e:
            print_error(f"Failed to load wallet: {e}")
            issues.append(f"Wallet error: {e}")
            
    except Exception as e:
        print_error(f"Error checking wallet: {e}")
        issues.append(f"Wallet check failed: {e}")
    
    return issues

def check_registration():
    """Check if miner is registered on the network"""
    print_header("3. NETWORK REGISTRATION")
    
    issues = []
    
    try:
        import bittensor as bt
        from config.settings import settings
        
        wallet_name = os.getenv("WALLET_NAME", "default")
        wallet_hotkey = os.getenv("WALLET_HOTKEY", "default")
        wallet = bt.wallet(name=wallet_name, hotkey=wallet_hotkey)
        
        subtensor = bt.subtensor(network=settings.network)
        metagraph = subtensor.metagraph(settings.subnet_uid)
        
        if wallet.hotkey.ss58_address in metagraph.hotkeys:
            uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
            print_success(f"Miner is registered! UID: {uid}")
            
            # Check if miner is active
            if uid < len(metagraph.axons):
                axon_info = metagraph.axons[uid]
                print_info(f"Axon IP: {axon_info.ip}")
                print_info(f"Axon Port: {axon_info.port}")
                
                if axon_info.port == settings.axon_port:
                    print_success(f"Axon port matches: {axon_info.port}")
                else:
                    print_error(f"Axon port mismatch: {axon_info.port} (expected {settings.axon_port})")
                    issues.append(f"Axon port is {axon_info.port}, should be {settings.axon_port}")
            else:
                print_warning("Miner registered but axon info not available")
        else:
            print_error("Miner is NOT registered on the network!")
            issues.append("Miner not registered - run registration first")
            
    except Exception as e:
        print_error(f"Error checking registration: {e}")
        issues.append(f"Registration check failed: {e}")
    
    return issues

def check_api_endpoint():
    """Check if API endpoint is accessible"""
    print_header("4. API ENDPOINT ACCESSIBILITY")
    
    issues = []
    
    try:
        from config.settings import settings
        
        # Extract host and port from API URL
        api_url = settings.api_url
        if "localhost" in api_url or "127.0.0.1" in api_url:
            # For local testing
            test_url = f"http://localhost:{settings.api_port}"
        else:
            # For remote testing
            test_url = api_url
        
        print_info(f"Testing API at: {test_url}")
        
        # Test health endpoint
        try:
            response = requests.get(f"{test_url}/health", timeout=5)
            if response.status_code == 200:
                print_success("API health endpoint responding")
            else:
                print_error(f"API health endpoint returned {response.status_code}")
                issues.append(f"API health check failed: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"Cannot connect to API at {test_url}")
            print_warning("This is expected if API is not running locally")
            print_info("Ensure API is running on deployment server")
        except requests.exceptions.Timeout:
            print_error(f"API timeout at {test_url}")
            issues.append("API endpoint timeout")
        except Exception as e:
            print_warning(f"API check error: {e}")
        
        # Test solve_task endpoint exists
        try:
            response = requests.options(f"{test_url}/solve_task", timeout=5)
            if response.status_code in [200, 204]:
                print_success("solve_task endpoint accessible")
            else:
                print_warning(f"solve_task endpoint returned {response.status_code}")
        except Exception as e:
            print_warning(f"Could not test solve_task endpoint: {e}")
            
    except Exception as e:
        print_error(f"Error checking API: {e}")
        issues.append(f"API check failed: {e}")
    
    return issues

def check_ports():
    """Check if required ports are available"""
    print_header("5. PORT AVAILABILITY")
    
    issues = []
    
    try:
        from config.settings import settings
        
        import socket
        
        def check_port(port, name):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print_success(f"{name} (port {port}): Port is in use (service may be running)")
            else:
                print_warning(f"{name} (port {port}): Port is available (service not running locally)")
        
        check_port(settings.api_port, "API Port")
        check_port(settings.axon_port, "Axon Port")
        
    except Exception as e:
        print_warning(f"Could not check ports: {e}")
    
    return issues

def check_miner_code():
    """Check miner code for critical configuration"""
    print_header("6. MINER CODE VALIDATION")
    
    issues = []
    
    miner_file = project_root / "miner" / "miner.py"
    
    if not miner_file.exists():
        print_error("miner/miner.py not found!")
        issues.append("miner/miner.py missing")
        return issues
    
    print_success("miner/miner.py exists")
    
    # Read and check for critical patterns
    with open(miner_file, 'r') as f:
        content = f.read()
    
    checks = [
        ("bt.axon", "bt.axon() call found"),
        ("serve_axon", "serve_axon() call found"),
        ("port=self.config.axon.port", "Axon port configuration found"),
        ("external_ip", "External IP configuration found"),
    ]
    
    for pattern, description in checks:
        if pattern in content:
            print_success(description)
        else:
            print_warning(f"{description} - pattern '{pattern}' not found")
    
    # Check for external_port (should NOT be present)
    if "external_port" in content and "external_port=settings.api_port" in content:
        print_error("external_port parameter found - this may cause issues!")
        print_warning("external_port should NOT be set in bt.axon()")
        issues.append("external_port parameter in bt.axon() may cause port conflicts")
    else:
        print_success("No external_port parameter (correct)")
    
    return issues

def check_ip_detection():
    """Check IP detection logic"""
    print_header("7. IP DETECTION")
    
    issues = []
    
    try:
        from config.settings import settings
        
        # Try to detect IP using the same method as miner
        print_info("Testing IP detection methods...")
        
        # Method 1: External service
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            if response.status_code == 200:
                detected_ip = response.text.strip()
                print_success(f"IP detected via ipify.org: {detected_ip}")
            else:
                print_warning("Could not detect IP via ipify.org")
        except Exception as e:
            print_warning(f"IP detection via ipify.org failed: {e}")
        
        # Method 2: ifconfig.me
        try:
            response = requests.get("https://ifconfig.me", timeout=5)
            if response.status_code == 200:
                detected_ip = response.text.strip()
                print_success(f"IP detected via ifconfig.me: {detected_ip}")
        except Exception as e:
            print_warning(f"IP detection via ifconfig.me failed: {e}")
        
        print_info("On deployment server, miner will detect IP automatically")
        
    except Exception as e:
        print_warning(f"IP detection check error: {e}")
    
    return issues

def simulate_validator_request():
    """Simulate a validator request to test the API"""
    print_header("8. VALIDATOR REQUEST SIMULATION")
    
    issues = []
    
    try:
        from config.settings import settings
        
        api_url = settings.api_url
        if "localhost" in api_url or "127.0.0.1" in api_url:
            test_url = f"http://localhost:{settings.api_port}"
        else:
            test_url = api_url
        
        print_info(f"Simulating validator request to: {test_url}/solve_task")
        
        test_payload = {
            "id": "test-123",
            "prompt": "Test task",
            "url": "https://example.com"
        }
        
        try:
            response = requests.post(
                f"{test_url}/solve_task",
                json=test_payload,
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print_success("Validator request simulation: SUCCESS")
                data = response.json()
                if "actions" in data:
                    print_success(f"Response contains actions: {len(data.get('actions', []))} actions")
                else:
                    print_warning("Response missing 'actions' field")
            else:
                print_error(f"Validator request simulation: FAILED (status {response.status_code})")
                issues.append(f"API returned {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print_warning("Cannot connect to API (expected if not running locally)")
            print_info("This will work on deployment server when API is running")
        except requests.exceptions.Timeout:
            print_error("API request timeout")
            issues.append("API request timeout")
        except Exception as e:
            print_error(f"Request simulation error: {e}")
            issues.append(f"Request error: {e}")
            
    except Exception as e:
        print_warning(f"Simulation check error: {e}")
    
    return issues

def main():
    """Run all validation checks"""
    print(f"\n{BOLD}{BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     PRE-DEPLOYMENT VALIDATION - MINER CONFIGURATION      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{RESET}\n")
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_environment())
    all_issues.extend(check_wallet())
    all_issues.extend(check_registration())
    all_issues.extend(check_api_endpoint())
    all_issues.extend(check_ports())
    all_issues.extend(check_miner_code())
    all_issues.extend(check_ip_detection())
    all_issues.extend(simulate_validator_request())
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    if not all_issues:
        print_success("All critical checks passed!")
        print_info("Your miner is ready for deployment")
        print_info("Validators should be able to connect once deployed")
        return 0
    else:
        print_error(f"Found {len(all_issues)} issue(s) that need attention:")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. {issue}")
        print_warning("\nPlease fix these issues before deployment")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

