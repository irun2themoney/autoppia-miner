#!/usr/bin/env python3
"""
Quick verification script to check if the Autoppia Worker is set up correctly
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} NOT FOUND: {filepath}")
        return False

def check_env_var(var_name, description):
    """Check if an environment variable is set"""
    value = os.getenv(var_name)
    if value and value != "your_api_key_here" and value != "":
        masked_value = value[:20] + "..." if len(value) > 20 else value
        print(f"✓ {description}: {masked_value}")
        return True
    else:
        print(f"⚠ {description}: Not set or using placeholder")
        return False

def main():
    """Run verification checks"""
    print("=" * 60)
    print("Autoppia Worker Setup Verification")
    print("=" * 60)
    print()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check essential files
    print("Checking files...")
    files_ok = True
    files_ok &= check_file_exists("worker.py", "Worker implementation")
    files_ok &= check_file_exists("api.py", "API server")
    files_ok &= check_file_exists("requirements.txt", "Dependencies file")
    files_ok &= check_file_exists(".env", "Environment file")
    files_ok &= check_file_exists("config.yaml", "Configuration file")
    files_ok &= check_file_exists("template.json", "Template metadata")
    print()
    
    # Check environment variables
    print("Checking environment variables...")
    env_ok = True
    env_ok &= check_env_var("CHUTES_API_KEY", "Chutes API Key")
    env_ok &= check_env_var("WORKER_NAME", "Worker Name")
    env_ok &= check_env_var("WORKER_VERSION", "Worker Version")
    print()
    
    # Check Python packages
    print("Checking Python packages...")
    packages_ok = True
    try:
        import httpx
        print("✓ httpx installed")
    except ImportError:
        print("✗ httpx NOT installed - run: pip install -r requirements.txt")
        packages_ok = False
    
    try:
        import pydantic
        print("✓ pydantic installed")
    except ImportError:
        print("✗ pydantic NOT installed - run: pip install -r requirements.txt")
        packages_ok = False
    
    try:
        from loguru import logger
        print("✓ loguru installed")
    except ImportError:
        print("✗ loguru NOT installed - run: pip install -r requirements.txt")
        packages_ok = False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv NOT installed - run: pip install -r requirements.txt")
        packages_ok = False
    
    print()
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if files_ok and env_ok and packages_ok:
        print("✓ All checks passed! Worker is ready to use.")
        print()
        print("Next steps:")
        print("  1. Test the worker: python3 example_usage.py")
        print("  2. Run the API server: python3 api.py")
        print("  3. Check health: curl http://localhost:8080/health")
        return 0
    else:
        print("⚠ Some checks failed. Please review the issues above.")
        if not packages_ok:
            print()
            print("To install dependencies, run:")
            print("  pip3 install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

