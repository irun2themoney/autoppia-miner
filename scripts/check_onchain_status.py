#!/usr/bin/env python3
"""
Check on-chain status for miner
Monitors Active Status, Last Update, Incentive, and Emissions
Based on expert LLM feedback - these are the key indicators of validator acceptance
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bittensor as bt
from config.settings import settings
import numpy as np
import time

def check_onchain_status():
    """Check and display on-chain status"""
    try:
        # Initialize subtensor
        subtensor = bt.subtensor(network=settings.network)
        metagraph = subtensor.metagraph(settings.subnet_uid)
        
        # Get wallet
        wallet = bt.wallet(name=settings.wallet_name, hotkey=settings.wallet_hotkey)
        
        # Find UID
        if wallet.hotkey.ss58_address not in metagraph.hotkeys:
            print(f"❌ Hotkey {wallet.hotkey.ss58_address} not found in metagraph")
            return
        
        uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
        
        # Get current block
        current_block = subtensor.get_current_block()
        
        # Get status values
        active_status = int(metagraph.active[uid]) if hasattr(metagraph, 'active') else 0
        last_update = int(metagraph.last_update[uid]) if hasattr(metagraph, 'last_update') else 0
        incentive = float(metagraph.incentive[uid]) if hasattr(metagraph, 'incentive') else 0.0
        emissions = float(metagraph.E[uid]) if hasattr(metagraph, 'E') else 0.0
        stake = float(metagraph.S[uid]) if hasattr(metagraph, 'S') else 0.0
        trust = float(metagraph.T[uid]) if hasattr(metagraph, 'T') else 0.0
        
        # Calculate blocks since last update
        blocks_since_update = current_block - last_update if last_update > 0 else 0
        
        # Calculate time estimate (assuming ~12s per block)
        hours_since_update = (blocks_since_update * 12) / 3600 if blocks_since_update > 0 else 0
        
        # Display status
        print("=" * 70)
        print("📊 ON-CHAIN STATUS CHECK")
        print("=" * 70)
        print(f"UID: {uid}")
        print(f"Current Block: {current_block:,}")
        print()
        print("--- CRITICAL METRICS ---")
        print(f"Active Status: {active_status} {'✅' if active_status == 1 else '❌'}")
        print(f"Incentive: {incentive:.6f}τ {'✅' if incentive > 0 else '❌'}")
        print(f"Emissions: {emissions:.6f}τ {'✅' if emissions > 0 else '❌'}")
        print()
        print("--- UPDATE STATUS ---")
        print(f"Last Update Block: {last_update:,}")
        print(f"Blocks Since Update: {blocks_since_update:,}")
        print(f"Time Since Update: ~{hours_since_update:.1f} hours")
        print()
        print("--- OTHER METRICS ---")
        print(f"Stake: {stake:.2f} TAO")
        print(f"Trust: {trust:.6f}")
        print()
        
        # Expert LLM guidance: Check for incentive without active status
        if incentive > 0 and active_status == 0:
            print("🎯 INCENTIVE DETECTED! Active status update is imminent.")
            print("   (Validators are accepting responses, Active Status should update soon)")
        elif incentive == 0 and active_status == 0:
            print("⚠️  No incentive yet - validators may not be accepting responses")
            print("   Check logs for IWA validation status and response times")
        elif active_status == 1:
            print("✅ ACTIVE! Miner is active and being evaluated")
        
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_onchain_status()

