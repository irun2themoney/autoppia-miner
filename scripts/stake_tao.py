#!/usr/bin/env python3
"""
Script to stake TAO to your miner's hotkey
Usage: python3 scripts/stake_tao.py [amount]
"""

import sys
import bittensor as bt
from config.settings import settings

def stake_tao(amount: float):
    """Stake TAO to the miner's hotkey"""
    
    print("=" * 60)
    print("Staking TAO to Miner")
    print("=" * 60)
    print()
    
    # Initialize wallet
    try:
        wallet = bt.wallet(name='default', hotkey='default')
        print(f"✅ Wallet loaded: {wallet.name}")
        print(f"   Hotkey: {wallet.hotkey.ss58_address}")
        print()
    except Exception as e:
        print(f"❌ Error loading wallet: {e}")
        return False
    
    # Initialize subtensor
    try:
        subtensor = bt.subtensor(network='finney')
        print(f"✅ Connected to Bittensor network: finney")
        print()
    except Exception as e:
        print(f"❌ Error connecting to subtensor: {e}")
        return False
    
    # Check balance
    try:
        balance = subtensor.get_balance(wallet.coldkeypub.ss58_address)
        print(f"💰 Current balance: {balance} TAO")
        print()
        
        if balance < amount:
            print(f"❌ Insufficient balance!")
            print(f"   Required: {amount} TAO")
            print(f"   Available: {balance} TAO")
            return False
    except Exception as e:
        print(f"❌ Error checking balance: {e}")
        return False
    
    # Check current stake
    try:
        metagraph = subtensor.metagraph(settings.subnet_uid)
        uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address) if wallet.hotkey.ss58_address in metagraph.hotkeys else None
        
        if uid is None:
            print("❌ Miner not found in metagraph!")
            return False
        
        current_stake = metagraph.S[uid].item() if hasattr(metagraph, 'S') and uid < len(metagraph.S) else 0
        print(f"📊 Current stake: {current_stake} TAO")
        print(f"   UID: {uid}")
        print()
    except Exception as e:
        print(f"❌ Error checking current stake: {e}")
        return False
    
    # Confirm staking
    print("=" * 60)
    print("Staking Details:")
    print(f"  Amount: {amount} TAO")
    print(f"  To: UID {uid} ({wallet.hotkey.ss58_address})")
    print(f"  Current stake: {current_stake} TAO")
    print(f"  New stake: {current_stake + amount} TAO")
    print("=" * 60)
    print()
    
    # Stake the TAO
    try:
        print("🔄 Staking TAO...")
        result = subtensor.add_stake(
            wallet=wallet,
            hotkey_ss58=wallet.hotkey.ss58_address,
            amount=amount,
            netuid=settings.subnet_uid,
            wait_for_inclusion=True,
            prompt=False
        )
        
        if result:
            print()
            print("=" * 60)
            print("✅ SUCCESS! TAO staked successfully!")
            print("=" * 60)
            print()
            
            # Verify new stake
            metagraph = subtensor.metagraph(settings.subnet_uid)
            new_stake = metagraph.S[uid].item() if hasattr(metagraph, 'S') and uid < len(metagraph.S) else 0
            print(f"📊 New stake: {new_stake} TAO")
            print()
            print("🎉 Your miner now has stake and should get higher priority!")
            return True
        else:
            print("❌ Staking failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error staking TAO: {e}")
        print()
        print("This might require manual confirmation. Try running:")
        print(f"  btcli wallet stake --wallet.name default --wallet.hotkey default --amount {amount} --netuid {settings.subnet_uid}")
        return False

if __name__ == "__main__":
    # Get amount from command line or use default
    if len(sys.argv) > 1:
        try:
            amount = float(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid amount: {sys.argv[1]}")
            sys.exit(1)
    else:
        amount = 0.3  # Default to 0.3 TAO
    
    success = stake_tao(amount)
    sys.exit(0 if success else 1)

