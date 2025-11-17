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
        try:
            print("Checking registration with existing metagraph...", flush=True)
            # Use existing metagraph (already synced in __init__)
            # Just refresh it if needed
            if self.metagraph is None or len(self.metagraph.hotkeys) == 0:
                print("Metagraph empty, syncing...", flush=True)
                bt.logging.info("Syncing metagraph...")
                self.metagraph = self.subtensor.metagraph(settings.subnet_uid)
            
            print(f"Metagraph has {len(self.metagraph.hotkeys)} hotkeys", flush=True)
            bt.logging.info(f"Metagraph synced. Total hotkeys: {len(self.metagraph.hotkeys)}")
            
            if self.wallet.hotkey.ss58_address not in self.metagraph.hotkeys:
                bt.logging.warning(f"Hotkey {self.wallet.hotkey.ss58_address} not found in metagraph")
                return False
            
            self.uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
            print(f"Found UID: {self.uid}", flush=True)
            bt.logging.info(f"Found UID: {self.uid}")
            return self.uid is not None
        except Exception as e:
            print(f"Error checking registration: {e}", flush=True)
            bt.logging.error(f"Error checking registration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
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
        print("Starting miner...", flush=True)
        # Setup logging
        bt.logging.set_config(
            config=bt.logging.config()
        )
        bt.logging.set_debug(settings.log_level == "DEBUG")
        print("Logging configured", flush=True)
        bt.logging.info("Miner starting up...")
        print("About to check registration...", flush=True)
        
        # Check registration
        print("Calling check_registration()...", flush=True)
        if not self.check_registration():
            print("Registration check returned False", flush=True)
            bt.logging.error("❌ Miner not registered on subnet 36!")
            bt.logging.error(f"Hotkey: {self.wallet.hotkey.ss58_address}")
            bt.logging.error("Register with: btcli wallet register --netuid 36")
            return
        
        print(f"✅ Miner registered! UID: {self.uid}", flush=True)
        bt.logging.info(f"✅ Miner registered! UID: {self.uid}")
        
        # Get external IP for axon
        print("Getting external IP...", flush=True)
        try:
            # Try to get external IP from metagraph or use local IP
            external_ip = self.metagraph.axons[self.uid].ip if self.uid is not None and self.uid < len(self.metagraph.axons) else "0.0.0.0"
            if external_ip == "0.0.0.0" or not external_ip:
                # Fallback: try to get from system
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                external_ip = s.getsockname()[0]
                s.close()
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

