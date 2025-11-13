"""
Bittensor Miner for Autoppia Subnet 36
Connects to Bittensor network and processes validator requests via HTTP API
"""

import os
import asyncio
import time
import json
from typing import Dict, Any, Optional
from loguru import logger
from dotenv import load_dotenv
import bittensor as bt
import httpx

load_dotenv()

# Subnet configuration
SUBNET_UID = 36  # Autoppia Web Agents subnet
NETWORK = "finney"  # Mainnet
API_URL = os.getenv("API_URL", "https://autoppia-miner.onrender.com")
API_TIMEOUT = 30.0


class AutoppiaMiner:
    """
    Bittensor Miner for Autoppia Subnet 36
    Connects to the network and forwards validator requests to HTTP API
    """
    
    def __init__(self, config: Optional[bt.config] = None):
        """Initialize the miner"""
        self.config = config or self._load_config()
        self.wallet = bt.wallet(name=self.config.wallet.name, hotkey=self.config.wallet.hotkey)
        self.subtensor = bt.subtensor(network=self.config.network)
        self.metagraph = self.subtensor.metagraph(SUBNET_UID)
        self.axon = None
        self.api_client = httpx.AsyncClient(
            base_url=API_URL,
            timeout=API_TIMEOUT
        )
        
        logger.info(f"🔧 Initializing Autoppia Miner")
        logger.info(f"   Wallet: {self.wallet.name} / {self.wallet.hotkey_str}")
        logger.info(f"   Network: {self.config.network}")
        logger.info(f"   Subnet: {SUBNET_UID}")
        logger.info(f"   API URL: {API_URL}")
    
    def _load_config(self) -> bt.config:
        """Load Bittensor configuration"""
        parser = bt.argument_parser()
        parser.add_argument("--netuid", type=int, default=SUBNET_UID, help="Subnet UID")
        parser.add_argument("--network", type=str, default=NETWORK, help="Network (finney, test)")
        parser.add_argument("--api.url", type=str, default=API_URL, help="HTTP API URL")
        return bt.config(parser)
    
    async def process_task(self, synapse: bt.Synapse) -> bt.Synapse:
        """
        Process a task from a validator
        Forwards the request to the HTTP API and returns the response
        """
        try:
            logger.info(f"📥 Received task from validator: {synapse.dendrite.hotkey}")
            
            # Prepare request for HTTP API
            task_data = {
                "id": getattr(synapse, "task_id", f"bt_{int(time.time())}"),
                "prompt": getattr(synapse, "prompt", ""),
                "url": getattr(synapse, "url", ""),
            }
            
            # Add optional fields if present
            if hasattr(synapse, "seed"):
                task_data["seed"] = synapse.seed
            if hasattr(synapse, "web_project_name"):
                task_data["web_project_name"] = synapse.web_project_name
            if hasattr(synapse, "specifications"):
                task_data["specifications"] = synapse.specifications
            
            logger.debug(f"Task data: {json.dumps(task_data, indent=2)}")
            
            # Call HTTP API
            response = await self.api_client.post(
                "/solve_task",
                json=task_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Task processed successfully: {result.get('task_type', 'unknown')}")
                
                # Set response fields on synapse
                synapse.actions = result.get("actions", [])
                synapse.success = result.get("success", False)
                synapse.task_type = result.get("task_type", "generic")
                synapse.message = result.get("message", "Task completed")
                
                return synapse
            else:
                logger.error(f"❌ API error: {response.status_code} - {response.text}")
                synapse.actions = []
                synapse.success = False
                synapse.message = f"API error: {response.status_code}"
                return synapse
                
        except Exception as e:
            logger.error(f"❌ Error processing task: {str(e)}")
            synapse.actions = []
            synapse.success = False
            synapse.message = f"Error: {str(e)}"
            return synapse
    
    def check_registration(self) -> bool:
        """Check if miner is registered on the subnet"""
        try:
            # Check if hotkey is registered
            if self.wallet.hotkey.ss58_address not in self.metagraph.hotkeys:
                logger.warning("⚠️  Miner not registered on subnet 36")
                logger.info(f"   Register with: btcli subnet register --netuid {SUBNET_UID} --wallet.name {self.wallet.name} --wallet.hotkey {self.wallet.hotkey_str}")
                return False
            
            uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
            logger.info(f"✅ Miner registered! UID: {uid}")
            return True
        except Exception as e:
            logger.error(f"❌ Error checking registration: {str(e)}")
            return False
    
    async def run(self):
        """Run the miner"""
        try:
            # Check registration
            if not self.check_registration():
                logger.error("❌ Miner not registered. Please register first.")
                return
            
            # Get UID
            uid = self.metagraph.hotkeys.index(self.wallet.hotkey.ss58_address)
            logger.info(f"🚀 Starting miner (UID: {uid})")
            
            # Create axon (server that receives validator requests)
            self.axon = bt.axon(
                wallet=self.wallet,
                port=self.config.axon.port,
                ip=self.config.axon.ip or self._get_external_ip(),
            )
            
            # Attach forward function
            self.axon.attach(forward_fn=self.process_task)
            
            # Start axon
            self.axon.start()
            logger.info(f"🌐 Axon started on {self.axon.ip}:{self.axon.port}")
            
            # Serve axon on network
            self.subtensor.serve_axon(
                netuid=SUBNET_UID,
                axon=self.axon
            )
            logger.info("✅ Miner serving on network!")
            
            # Update metagraph periodically
            last_block = self.metagraph.block
            while True:
                try:
                    # Update metagraph every 100 blocks
                    current_block = self.metagraph.block
                    if current_block - last_block >= 100:
                        self.metagraph = self.subtensor.metagraph(SUBNET_UID)
                        last_block = current_block
                        logger.info(f"📊 Metagraph updated (block: {current_block}, miners: {len(self.metagraph.hotkeys)})")
                    
                    await asyncio.sleep(12)  # Wait ~12 seconds (block time)
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Shutting down miner...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in main loop: {str(e)}")
                    await asyncio.sleep(12)
        
        except Exception as e:
            logger.error(f"❌ Fatal error: {str(e)}")
        finally:
            if self.axon:
                self.axon.stop()
            await self.api_client.aclose()
    
    def _get_external_ip(self) -> str:
        """Get external IP address"""
        try:
            # Try to get external IP from API
            import httpx
            response = httpx.get("https://api.ipify.org", timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except Exception:
            pass
        
        try:
            # Fallback to local IP
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "0.0.0.0"  # Let Bittensor auto-detect


def main():
    """Main entry point"""
    # Load config
    config = bt.argument_parser().parse_args()
    config.netuid = SUBNET_UID
    config.network = NETWORK
    
    # Create and run miner
    miner = AutoppiaMiner(config)
    
    # Run async
    asyncio.run(miner.run())


if __name__ == "__main__":
    main()

