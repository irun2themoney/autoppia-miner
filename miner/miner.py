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
        self.uid = None
    
    def _load_config(self):
        parser = argparse.ArgumentParser()
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)
        parser.add_argument("--network", default=settings.network)
        parser.add_argument("--axon.port", type=int, default=settings.axon_port)
        return bt.config(parser)
    
    def check_registration(self) -> bool:
        """Check if miner is registered"""
        # Sync metagraph first
        self.metagraph = self.subtensor.metagraph(settings.subnet_uid)
        
        if self.wallet.hotkey.ss58_address not in self.metagraph.hotkeys:
            return False
        
        self.uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
        return self.uid is not None
    
    async def process_task(self, synapse: bt.Synapse) -> bt.Synapse:
        """Process validator request"""
        try:
            # Extract task data from synapse
            task_id = getattr(synapse, "id", None) or getattr(synapse, "task_id", None) or "unknown"
            prompt = getattr(synapse, "prompt", "")
            url = getattr(synapse, "url", "")
            
            bt.logging.info(f"Processing task: {task_id}, prompt: {prompt[:50]}...")
            
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
                bt.logging.info(f"Task {task_id} processed successfully, {len(synapse.actions)} actions generated")
            else:
                synapse.actions = []
                synapse.success = False
                bt.logging.warning(f"API returned status {response.status_code} for task {task_id}")
            
        except Exception as e:
            synapse.actions = []
            synapse.success = False
            bt.logging.error(f"Error processing task: {e}")
        
        return synapse
    
    async def run(self):
        """Start miner"""
        # Setup logging
        bt.logging.set_config(
            config=bt.logging.config()
        )
        bt.logging.set_debug(settings.log_level == "DEBUG")
        
        # Check registration
        if not self.check_registration():
            bt.logging.error("❌ Miner not registered on subnet 36!")
            bt.logging.error(f"Hotkey: {self.wallet.hotkey.ss58_address}")
            bt.logging.error("Register with: btcli wallet register --netuid 36")
            return
        
        bt.logging.info(f"✅ Miner registered! UID: {self.uid}")
        
        # Get external IP for axon
        try:
            external_ip = self.subtensor.get_external_ip()
        except Exception as e:
            bt.logging.warning(f"Could not get external IP: {e}, using 0.0.0.0")
            external_ip = "0.0.0.0"
        
        # Create axon with metadata
        self.axon = bt.axon(
            wallet=self.wallet,
            port=self.config.axon.port,
            ip=external_ip,
        )
        
        # Attach forward function
        self.axon.attach(
            forward_fn=self.process_task,
        )
        
        # Start axon
        self.axon.start()
        bt.logging.info(f"✅ Axon started on {external_ip}:{self.config.axon.port}")
        
        # Serve axon to network (CRITICAL - this is what was missing!)
        try:
            self.subtensor.serve_axon(
                netuid=settings.subnet_uid,
                axon=self.axon,
            )
            bt.logging.info("✅ Axon served to subtensor network!")
        except Exception as e:
            bt.logging.error(f"❌ Failed to serve axon: {e}")
            bt.logging.error("Validators will not be able to discover your miner!")
            return
        
        # Periodic metagraph sync and axon re-serving
        async def sync_metagraph():
            while True:
                try:
                    await asyncio.sleep(180)  # Sync every 3 minutes
                    self.metagraph = self.subtensor.metagraph(settings.subnet_uid)
                    bt.logging.debug("Metagraph synced")
                    
                    # Re-serve axon periodically to ensure it stays registered
                    try:
                        self.subtensor.serve_axon(
                            netuid=settings.subnet_uid,
                            axon=self.axon,
                        )
                        bt.logging.debug("Axon re-served to network")
                    except Exception as e:
                        bt.logging.warning(f"Failed to re-serve axon: {e}")
                except Exception as e:
                    bt.logging.error(f"Error in metagraph sync: {e}")
        
        # Start sync task
        asyncio.create_task(sync_metagraph())
        
        bt.logging.info("🚀 Miner is running and ready to receive validator requests!")
        bt.logging.info(f"API URL: {settings.api_url}")
        
        # Serve forever
        await asyncio.Event().wait()


def main():
    miner = AutoppiaMiner()
    asyncio.run(miner.run())


if __name__ == "__main__":
    main()

