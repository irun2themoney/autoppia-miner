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

try:
load_dotenv()
except Exception:
    pass  # Continue even if .env file can't be loaded

# Subnet configuration
SUBNET_UID = 36  # Autoppia Web Agents subnet
NETWORK = "finney"  # Mainnet
# Default to DigitalOcean VPS IP (can be overridden via .env)
API_URL = os.getenv("API_URL", "http://134.199.203.133:8080")
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
            timeout=API_TIMEOUT,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        
        logger.info(f"🔧 Initializing Autoppia Miner")
        logger.info(f"   Wallet: {self.wallet.name} / {self.wallet.hotkey_str}")
        logger.info(f"   Network: {self.config.network}")
        logger.info(f"   Subnet: {SUBNET_UID}")
        logger.info(f"   API URL: {API_URL}")
    
    def _load_config(self) -> bt.config:
        """Load Bittensor configuration"""
        # For bittensor 9.x, use bt.cli() to create config from command line args
        config = bt.cli()
        config.netuid = SUBNET_UID
        config.network = NETWORK
        return config
    
    async def process_task(self, synapse: bt.Synapse) -> bt.Synapse:
        """
        Process a task from a validator
        Forwards the request to the HTTP API and returns the response
        
        This method handles the Autoppia protocol synapse structure:
        - Input: prompt, url, task_id, seed, web_project_name, specifications
        - Output: actions, success, task_type, message
        """
        try:
            validator_hotkey = getattr(synapse.dendrite, 'hotkey', 'unknown')
            logger.info(f"📥 Received task from validator: {validator_hotkey}")
            
            # Extract all possible fields from synapse (Autoppia protocol)
            prompt = getattr(synapse, "prompt", "")
            url = getattr(synapse, "url", "")
            task_id = getattr(synapse, "task_id", None) or getattr(synapse, "id", None) or f"bt_{int(time.time())}")
            
            # Validate required fields
            if not prompt:
                logger.warning("⚠️  No prompt provided in synapse")
                prompt = "Generic task"
            
            # Prepare request for HTTP API (matches Autoppia spec)
            task_data = {
                "id": task_id,
                "prompt": prompt,
                "url": url or "",
            }
            
            # Add optional fields if present (Autoppia protocol extensions)
            if hasattr(synapse, "seed") and synapse.seed is not None:
                task_data["seed"] = synapse.seed
            if hasattr(synapse, "web_project_name") and synapse.web_project_name:
                task_data["web_project_name"] = synapse.web_project_name
            if hasattr(synapse, "specifications") and synapse.specifications:
                task_data["specifications"] = synapse.specifications
            
            logger.debug(f"Task data: {json.dumps(task_data, indent=2)}")
            
            # Call HTTP API with timeout
            try:
                response = await asyncio.wait_for(
                    self.api_client.post("/solve_task", json=task_data),
                    timeout=API_TIMEOUT
            )
            except asyncio.TimeoutError:
                logger.error(f"❌ API timeout after {API_TIMEOUT}s")
                synapse.actions = []
                synapse.success = False
                synapse.task_type = "error"
                synapse.message = f"API timeout after {API_TIMEOUT}s"
                return synapse
            
            if response.status_code == 200:
                result = response.json()
                task_type = result.get("task_type", "generic")
                actions = result.get("actions", [])
                success = result.get("success", False)
                
                logger.info(f"✅ Task processed: {task_type} with {len(actions)} actions (success: {success})")
                
                # Set response fields on synapse (Autoppia protocol)
                synapse.actions = actions
                synapse.success = success
                synapse.task_type = task_type
                synapse.message = result.get("message", "Task completed successfully")
                
                return synapse
            else:
                error_text = response.text[:200] if response.text else "No error message"
                logger.error(f"❌ API error: {response.status_code} - {error_text}")
                synapse.actions = []
                synapse.success = False
                synapse.task_type = "error"
                synapse.message = f"API error: {response.status_code}"
                return synapse
                
        except httpx.RequestError as e:
            logger.error(f"❌ Network error calling API: {str(e)}")
            synapse.actions = []
            synapse.success = False
            synapse.task_type = "error"
            synapse.message = f"Network error: {str(e)}"
            return synapse
        except Exception as e:
            logger.error(f"❌ Unexpected error processing task: {str(e)}", exc_info=True)
            synapse.actions = []
            synapse.success = False
            synapse.task_type = "error"
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
            # Use getattr for safe access to config attributes
            axon_port = getattr(self.config.axon, 'port', 8091) if hasattr(self.config, 'axon') else 8091
            axon_ip = (getattr(self.config.axon, 'ip', None) if hasattr(self.config, 'axon') else None) or self._get_external_ip()
            
            self.axon = bt.axon(
                wallet=self.wallet,
                port=axon_port,
                ip=axon_ip,
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
            last_block = 0
            while True:
                try:
                    # Update metagraph every 100 blocks
                    # Refresh metagraph first to get current block info
                    self.metagraph = self.subtensor.metagraph(SUBNET_UID)
                    current_block = self.metagraph.block
                    
                    if current_block - last_block >= 100:
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
        """Get external IP address - non-blocking with timeout"""
        try:
            # Try to get external IP from API using non-blocking socket
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)  # Short timeout
            try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
                if ip:
            return ip
            except socket.timeout:
                pass
            except Exception:
                pass
            finally:
                try:
                    s.close()
                except Exception:
                    pass
        except Exception:
            pass
        
        # Fallback to localhost - let Bittensor auto-detect external IP
        return "0.0.0.0"


def main():
    """Main entry point"""
    # Load config using bt.cli() for bittensor 9.x
    config = bt.cli()
    config.netuid = SUBNET_UID
    config.network = NETWORK
    
    # Create and run miner
    miner = AutoppiaMiner(config)
    
    # Run async
    asyncio.run(miner.run())


if __name__ == "__main__":
    main()

