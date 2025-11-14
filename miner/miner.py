"""
Bittensor Miner for Subnet 36
Connects to network and forwards requests to API
"""
import os
import asyncio
import argparse
from typing import Optional
from dotenv import load_dotenv
import bittensor as bt
import httpx
from config.settings import settings

load_dotenv()


class AutoppiaMiner:
    def __init__(self, config: Optional[bt.config] = None):
        self.config = config or self._load_config()
        self.wallet = bt.wallet(name=self.config.wallet.name, hotkey=self.config.wallet.hotkey)
        self.subtensor = bt.subtensor(network=self.config.network)
        self.metagraph = self.subtensor.metagraph(settings.subnet_uid)
        self.axon = None
        self.api_client = httpx.AsyncClient(
            base_url=settings.api_url,
            timeout=settings.api_timeout
        )
    
    def _load_config(self):
        parser = argparse.ArgumentParser()
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)
        parser.add_argument("--network", default=settings.network)
        parser.add_argument("--axon.port", type=int, default=settings.axon_port)
        return bt.config(parser)
    
    def check_registration(self) -> bool:
        """Check if miner is registered"""
        if self.wallet.hotkey.ss58_address not in self.metagraph.hotkeys:
            return False
        uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
        return uid is not None
    
    async def process_task(self, synapse: bt.Synapse) -> bt.Synapse:
        """Process validator request"""
        try:
            # Extract task data from synapse
            task_id = getattr(synapse, "id", None) or getattr(synapse, "task_id", None) or "unknown"
            prompt = getattr(synapse, "prompt", "")
            url = getattr(synapse, "url", "")
            
            # Call API
            response = await asyncio.wait_for(
                self.api_client.post(
                    "/solve_task",
                    json={
                        "id": task_id,
                        "prompt": prompt,
                        "url": url
                    }
                ),
                timeout=settings.api_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                synapse.actions = result.get("actions", [])
                synapse.success = True
                synapse.task_type = "generic"
            else:
                synapse.actions = []
                synapse.success = False
            
        except Exception as e:
            synapse.actions = []
            synapse.success = False
        
        return synapse
    
    async def run(self):
        """Start miner"""
        if not self.check_registration():
            print("❌ Miner not registered!")
            return
        
        # Create axon
        self.axon = bt.axon(
            wallet=self.wallet,
            port=self.config.axon.port,
        )
        
        # Attach forward function
        self.axon.attach(
            forward_fn=self.process_task,
        )
        
        # Start axon
        self.axon.start()
        print(f"✅ Miner started on port {self.config.axon.port}")
        
        # Serve forever
        await asyncio.Event().wait()


def main():
    miner = AutoppiaMiner()
    asyncio.run(miner.run())


if __name__ == "__main__":
    main()

