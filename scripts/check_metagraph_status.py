#!/usr/bin/env python3
"""Check miner status on metagraph"""
import bittensor as bt
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings

def check_metagraph_status():
    """Check miner status on metagraph"""
    print("🔍 Checking Metagraph Status...")
    print("=" * 60)
    
    # Load wallet
    wallet = bt.wallet(name="default", hotkey="default")
    print(f"Hotkey: {wallet.hotkey.ss58_address}")
    
    # Connect to subtensor
    subtensor = bt.subtensor(network="finney")
    metagraph = subtensor.metagraph(36)
    
    # Find UID
    if wallet.hotkey.ss58_address not in metagraph.hotkeys:
        print("❌ ERROR: Hotkey not found in metagraph!")
        print("   Miner may not be registered!")
        return False
    
    uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
    print(f"✅ UID: {uid}")
    print(f"   Total miners: {len(metagraph.hotkeys)}")
    print(f"   Active validators: {sum(metagraph.validator_permit)}")
    
    # Check axon info
    if uid >= len(metagraph.axons):
        print("❌ ERROR: Axon info not available!")
        return False
    
    axon = metagraph.axons[uid]
    print(f"\n📡 Axon Information:")
    print(f"   IP: {axon.ip}")
    print(f"   Port: {axon.port}")
    print(f"   IP Type: {type(axon.ip)}")
    
    # Critical check: Is IP 0.0.0.0?
    if axon.ip == "0.0.0.0" or str(axon.ip) == "0.0.0.0":
        print("\n❌ CRITICAL ISSUE: Axon IP is 0.0.0.0!")
        print("   Validators cannot connect to 0.0.0.0")
        print("   This is why you're not receiving requests!")
        return False
    else:
        print(f"   ✅ IP is valid: {axon.ip}")
    
    # Check if IP matches server IP
    expected_ip = "134.199.203.133"
    if str(axon.ip) != expected_ip:
        print(f"\n⚠️  WARNING: Axon IP ({axon.ip}) doesn't match server IP ({expected_ip})")
        print("   This might prevent validators from connecting")
    else:
        print(f"   ✅ IP matches server IP: {expected_ip}")
    
    # Check axon metadata
    print(f"\n📋 Axon Metadata:")
    if hasattr(axon, 'ip_str'):
        print(f"   IP String: {axon.ip_str}")
    if hasattr(axon, 'hotkey'):
        print(f"   Hotkey: {axon.hotkey}")
    if hasattr(axon, 'coldkey'):
        print(f"   Coldkey: {axon.coldkey}")
    
    return True

if __name__ == "__main__":
    try:
        success = check_metagraph_status()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

