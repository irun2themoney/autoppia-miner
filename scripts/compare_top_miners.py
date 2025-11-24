#!/usr/bin/env python3
"""
Compare our miner setup with top miners on Subnet 36
Analyzes metagraph data to find differences
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bittensor as bt
from config.settings import settings
import numpy as np

def compare_with_top_miners():
    """Compare our miner configuration with top miners"""
    print("🔍 Comparing Miner Setup with Top Performers")
    print("=" * 70)
    
    try:
        # Connect to network
        subtensor = bt.subtensor(network=settings.network)
        metagraph = subtensor.metagraph(settings.subnet_uid)
        
        our_uid = 160
        
        print(f"\n📊 Network Overview:")
        print(f"   Total Miners: {len(metagraph.uids)}")
        print(f"   Your UID: {our_uid}")
        print()
        
        # Get top miners by stake
        if hasattr(metagraph, 'S') and len(metagraph.S) > 0:
            # Handle both numpy array and tensor
            stakes = np.array(metagraph.S) if hasattr(metagraph.S, 'numpy') else metagraph.S
            sorted_indices = sorted(range(len(stakes)), key=lambda i: stakes[i], reverse=True)
            
            # Find our rank
            if our_uid < len(stakes):
                our_stake = stakes[our_uid]
                our_rank = sorted_indices.index(our_uid) + 1 if our_uid in sorted_indices else len(sorted_indices)
                
                print(f"📈 Your Performance:")
                print(f"   Rank: #{our_rank} out of {len(metagraph.uids)}")
                print(f"   Stake: {our_stake:.2f} TAO")
                print()
                
                # Analyze top 10 miners
                print("🏆 Top 10 Miners Analysis:")
                print("-" * 70)
                
                top_10 = sorted_indices[:10]
                for rank, idx in enumerate(top_10, 1):
                    uid = idx
                    stake = stakes[idx]
                    hotkey_short = metagraph.hotkeys[idx][:20] + "..." if len(metagraph.hotkeys[idx]) > 20 else metagraph.hotkeys[idx]
                    
                    # Get axon info
                    axon_info = ""
                    if idx < len(metagraph.axons):
                        axon = metagraph.axons[idx]
                        if hasattr(axon, 'ip') and hasattr(axon, 'port'):
                            axon_info = f"IP: {axon.ip}, Port: {axon.port}"
                    
                    marker = " ⭐ YOU" if uid == our_uid else ""
                    print(f"{rank:2d}. UID {uid:3d} | Stake: {stake:8.2f} TAO | {hotkey_short}{marker}")
                    if axon_info:
                        print(f"     {axon_info}")
                
                print()
                
                # Compare configuration
                print("⚙️  Configuration Comparison:")
                print("-" * 70)
                
                if our_uid < len(metagraph.axons):
                    our_axon = metagraph.axons[our_uid]
                    our_ip = our_axon.ip if hasattr(our_axon, 'ip') else 'N/A'
                    our_port = our_axon.port if hasattr(our_axon, 'port') else 'N/A'
                    
                    print(f"Your Configuration:")
                    print(f"   IP: {our_ip}")
                    print(f"   Port: {our_port}")
                    print(f"   Network: {settings.network}")
                    print(f"   Subnet: {settings.subnet_uid}")
                    print()
                    
                    # Check top miners' ports
                    print("Top Miners Port Analysis:")
                    ports_used = {}
                    for idx in top_10[:5]:
                        if idx < len(metagraph.axons):
                            axon = metagraph.axons[idx]
                            if hasattr(axon, 'port'):
                                port = axon.port
                                ports_used[port] = ports_used.get(port, 0) + 1
                    
                    if ports_used:
                        print("   Common ports used by top miners:")
                        for port, count in sorted(ports_used.items(), key=lambda x: x[1], reverse=True):
                            print(f"     Port {port}: {count} miners")
                        if our_port in ports_used:
                            print(f"   ✅ Your port {our_port} matches top miners")
                        else:
                            print(f"   ⚠️  Your port {our_port} differs from top miners")
                
                # Performance gap analysis
                if our_uid < len(stakes):
                    top_stake = stakes[sorted_indices[0]] if sorted_indices else 0
                    gap = top_stake - our_stake
                    percentage = (our_stake / top_stake * 100) if top_stake > 0 else 0
                    
                    print()
                    print("📊 Performance Gap:")
                    print(f"   Top miner stake: {top_stake:.2f} TAO")
                    print(f"   Your stake: {our_stake:.2f} TAO")
                    print(f"   Gap: {gap:.2f} TAO")
                    print(f"   Percentage: {percentage:.1f}% of top miner")
                    
                    if percentage < 10:
                        print("   ⚠️  Significant gap - focus on improving performance")
                    elif percentage < 50:
                        print("   📈 Room for improvement")
                    else:
                        print("   ✅ Competitive performance!")
        
        else:
            print("⚠️  Stake data not available in metagraph")
        
        print()
        print("💡 Recommendations:")
        print("   1. Ensure API is responding quickly (< 5s)")
        print("   2. Never return empty actions (critical)")
        print("   3. Generate accurate IWA-format actions")
        print("   4. Handle all task types correctly")
        print("   5. Monitor validator requests and success rate")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(compare_with_top_miners())

