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
from .protocol import StartRoundSynapse, TaskSynapse

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
    
    async def process_start_round(self, synapse: StartRoundSynapse) -> StartRoundSynapse:
        """Handle StartRoundSynapse - acknowledge round start"""
        try:
            bt.logging.info(f"StartRoundSynapse received: round_id={synapse.round_id}, task_type={synapse.task_type}")
            synapse.success = True
            synapse.message = "Round started successfully"
        except Exception as e:
            synapse.success = False
            synapse.message = f"Error: {e}"
            bt.logging.error(f"Error processing StartRoundSynapse: {e}")
        return synapse
    
    async def process_task(self, synapse: bt.Synapse) -> bt.Synapse:
        """Process validator request - handles both TaskSynapse and generic Synapse"""
        try:
            # Handle StartRoundSynapse - check by attributes since Bittensor may deserialize as generic Synapse
            # Validators send StartRoundSynapse with round_id and task_type attributes
            has_round_id = hasattr(synapse, "round_id") and getattr(synapse, "round_id", None) is not None
            has_task_type_attr = hasattr(synapse, "task_type") and getattr(synapse, "task_type", None) is not None
            is_start_round = isinstance(synapse, StartRoundSynapse) or (has_round_id and has_task_type_attr and not hasattr(synapse, "prompt"))
            
            if is_start_round:
                # Convert generic synapse to StartRoundSynapse if needed
                if not isinstance(synapse, StartRoundSynapse):
                    start_round_synapse = StartRoundSynapse(
                        round_id=getattr(synapse, "round_id", None),
                        task_type=getattr(synapse, "task_type", None)
                    )
                    # Copy any other attributes
                    for attr in ["success", "message"]:
                        if hasattr(synapse, attr):
                            setattr(start_round_synapse, attr, getattr(synapse, attr))
                    return await self.process_start_round(start_round_synapse)
                else:
                    return await self.process_start_round(synapse)
            
            # Handle TaskSynapse or generic synapse
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
                
                # Set additional fields if TaskSynapse
                if isinstance(synapse, TaskSynapse):
                    synapse.web_agent_id = result.get("web_agent_id", task_id)
                    synapse.recording = result.get("recording", "")
                    synapse.task_id = result.get("task_id", task_id)
                
                bt.logging.info(f"Task {task_id} processed successfully, {len(synapse.actions)} actions generated")
            else:
                synapse.actions = []
                synapse.success = False
                bt.logging.warning(f"API returned status {response.status_code} for task {task_id}")
            
        except Exception as e:
            synapse.actions = []
            synapse.success = False
            bt.logging.error(f"Error processing task: {e}")
            import traceback
            traceback.print_exc()
        
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
        
        # Get external IP for axon (OPTIMIZED: consolidated logic)
        print("Getting external IP...", flush=True)
        external_ip = None
        
        # Method 1: Try to get from metagraph (most reliable)
        if self.uid is not None and hasattr(self.metagraph, 'axons') and self.uid < len(self.metagraph.axons):
            try:
                metagraph_ip = self.metagraph.axons[self.uid].ip
                if metagraph_ip and metagraph_ip != "0.0.0.0":
                    external_ip = metagraph_ip
                    print(f"✅ Got IP from metagraph: {external_ip}", flush=True)
                    bt.logging.info(f"Using IP from metagraph: {external_ip}")
            except Exception as e:
                bt.logging.debug(f"Could not get IP from metagraph: {e}")
        
        # Method 2: Try to get from external service (if metagraph failed)
        if not external_ip or external_ip == "0.0.0.0":
            print("Getting IP from external service...", flush=True)
            # Try multiple services for reliability (OPTIMIZED: use existing httpx client)
            for service in ["https://api.ipify.org", "https://ifconfig.me", "https://icanhazip.com"]:
                try:
                    response = httpx.get(service, timeout=5)
                    if response.status_code == 200:
                        external_ip = response.text.strip()
                        if external_ip and external_ip != "0.0.0.0":
                            print(f"✅ Got IP from {service}: {external_ip}", flush=True)
                            bt.logging.info(f"Using external IP: {external_ip}")
                            break
                except Exception:
                    continue
        
        # Method 3: Fallback to system method (local network IP)
        if not external_ip or external_ip == "0.0.0.0":
            try:
                print("Getting IP from system...", flush=True)
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    external_ip = s.getsockname()[0]
                print(f"⚠️  Got local IP from system: {external_ip} (may not be publicly accessible)", flush=True)
                bt.logging.warning(f"Using local IP: {external_ip} - this may not be accessible from internet!")
            except Exception as e:
                print(f"Error getting IP from system: {e}", flush=True)
                external_ip = "0.0.0.0"
        
        # Final check
        if not external_ip or external_ip == "0.0.0.0":
            print("❌ WARNING: Could not determine external IP, using 0.0.0.0", flush=True)
            print("   Validators may not be able to connect!", flush=True)
            bt.logging.error("CRITICAL: Could not determine external IP! Validators cannot connect!")
            external_ip = "0.0.0.0"
        
        print(f"Final external IP: {external_ip}", flush=True)
        bt.logging.info(f"Final external IP: {external_ip}")
        
        # Log API URL for validators
        api_url = f"http://{external_ip}:{settings.api_port}"
        print(f"Validator API endpoint: {api_url}/solve_task", flush=True)
        bt.logging.info(f"Validator API endpoint: {api_url}/solve_task")
        
        # Create axon - MATCH EXACT CONFIGURATION FROM WHEN VALIDATORS WERE CONNECTING
        # On Nov 18 when validators connected, axon was created WITHOUT external_port
        # The external_port parameter may have caused the axon port to be set incorrectly
        print("Creating axon...", flush=True)
        self.axon = bt.axon(
            wallet=self.wallet,
            port=self.config.axon.port,  # Axon port: 8091 (CRITICAL - must be 8091)
            ip=external_ip,  # External IP: 134.199.203.133
            external_ip=external_ip,  # External IP for API discovery
            # NOTE: external_port was added AFTER validators stopped connecting
            # Removing it to match the working configuration from Nov 18
            # Validators use convention: API is on port 8080 (standard)
        )
        print(f"Axon created: ip={external_ip}, port={self.config.axon.port}", flush=True)
        bt.logging.info(f"Axon created: ip={external_ip}, port={self.config.axon.port}")
        print(f"Validator API endpoint: {api_url}/solve_task", flush=True)
        bt.logging.info(f"Validator API endpoint: {api_url}/solve_task")
        
        # Attach forward function - handles all synapse types
        # Use a wrapper that catches all synapse types, including StartRoundSynapse
        print("Attaching forward function...", flush=True)
        
        async def forward_wrapper(synapse: bt.Synapse) -> bt.Synapse:
            """Wrapper to handle all synapse types, including custom ones"""
            try:
                # Log that we received a synapse (for debugging)
                synapse_name = getattr(synapse, '__class__', {}).__name__ if hasattr(synapse, '__class__') else 'Synapse'
                
                # Try to get validator IP from synapse
                validator_ip = "unknown"
                try:
                    # Bittensor synapse may have dendrite information
                    if hasattr(synapse, 'dendrite') and synapse.dendrite:
                        if hasattr(synapse.dendrite, 'ip'):
                            validator_ip = synapse.dendrite.ip
                        elif hasattr(synapse.dendrite, 'hotkey'):
                            # Use hotkey as identifier if IP not available
                            validator_ip = str(synapse.dendrite.hotkey)[:16] if synapse.dendrite.hotkey else "unknown"
                    # Also check for axon_info which might have source info
                    if hasattr(synapse, 'axon_info') and synapse.axon_info:
                        if hasattr(synapse.axon_info, 'ip'):
                            validator_ip = synapse.axon_info.ip
                except Exception:
                    pass  # If we can't get IP, use "unknown"
                
                # CRITICAL FIX: Check for StartRoundSynapse BEFORE processing
                # Bittensor may deserialize StartRoundSynapse as generic Synapse, so we check attributes
                has_round_id = hasattr(synapse, "round_id") and getattr(synapse, "round_id", None) is not None
                has_task_type = hasattr(synapse, "task_type") and getattr(synapse, "task_type", None) is not None
                has_prompt = hasattr(synapse, "prompt") and getattr(synapse, "prompt", None) is not None
                
                # If it looks like StartRoundSynapse (has round_id and task_type but no prompt)
                if (has_round_id and has_task_type and not has_prompt) or isinstance(synapse, StartRoundSynapse):
                    bt.logging.info(f"ROUND_START: {validator_ip} - Processing StartRoundSynapse: round_id={getattr(synapse, 'round_id', None)}")
                    print(f"ROUND_START: {validator_ip} - Processing StartRoundSynapse", flush=True)
                    try:
                        # Convert to StartRoundSynapse if needed
                        if not isinstance(synapse, StartRoundSynapse):
                            start_round = StartRoundSynapse(
                                round_id=getattr(synapse, "round_id", None),
                                task_type=getattr(synapse, "task_type", None)
                            )
                            # Copy response fields
                            for attr in ["success", "message"]:
                                if hasattr(synapse, attr):
                                    setattr(start_round, attr, getattr(synapse, attr))
                            result = await self.process_start_round(start_round)
                        else:
                            result = await self.process_start_round(synapse)
                        bt.logging.info(f"ROUND_START_SUCCESS: {validator_ip} - Round {getattr(result, 'round_id', 'unknown')} started")
                        print(f"ROUND_START_SUCCESS: {validator_ip} - Round started", flush=True)
                        return result
                    except Exception as e:
                        bt.logging.error(f"ROUND_START_ERROR: {validator_ip} - Error processing StartRoundSynapse: {e}")
                        print(f"ROUND_START_ERROR: {validator_ip} - {e}", flush=True)
                        # Return valid response even on error
                        if not isinstance(synapse, StartRoundSynapse):
                            synapse = StartRoundSynapse(
                                round_id=getattr(synapse, "round_id", None),
                                task_type=getattr(synapse, "task_type", None)
                            )
                        synapse.success = False
                        synapse.message = f"Error: {e}"
                        return synapse
                
                # Log validator connection with IP
                bt.logging.info(f"VALIDATOR_CONNECTION: {validator_ip} - Received synapse: {synapse_name}")
                print(f"VALIDATOR_CONNECTION: {validator_ip} - Received synapse: {synapse_name}", flush=True)
                
                # Process regular task synapse
                result = await self.process_task(synapse)
                bt.logging.info(f"VALIDATOR_RESPONSE: {validator_ip} - Successfully processed synapse: {synapse_name}")
                return result
            except Exception as e:
                # Log error but don't fail - return a valid response
                validator_ip = "unknown"
                try:
                    if hasattr(synapse, 'dendrite') and synapse.dendrite and hasattr(synapse.dendrite, 'ip'):
                        validator_ip = synapse.dendrite.ip
                except Exception:
                    pass
                bt.logging.warning(f"VALIDATOR_ERROR: {validator_ip} - Error processing synapse in forward_wrapper: {e}")
                import traceback
                bt.logging.debug(f"Traceback: {traceback.format_exc()}")
                # Set default response to prevent further errors
                if not hasattr(synapse, 'success'):
                    synapse.success = False
                if not hasattr(synapse, 'actions'):
                    synapse.actions = []
                # Return synapse even on error - this prevents UnknownSynapseError from propagating
                return synapse
        
        self.axon.attach(
            forward_fn=forward_wrapper,
        )
        print("Forward function attached", flush=True)
        
        # Note: Bittensor may not support custom synapse type registration
        # Our forward function handles this by checking synapse attributes
        # This allows us to process StartRoundSynapse even if Bittensor deserializes it as generic Synapse
        bt.logging.info("Forward function configured to handle StartRoundSynapse and TaskSynapse via attribute detection")
        
        # Start axon
        print("Starting axon...", flush=True)
        self.axon.start()
        print(f"✅ Axon started on {external_ip}:{self.config.axon.port}", flush=True)
        bt.logging.info(f"✅ Axon started on {external_ip}:{self.config.axon.port}")
        
        # Serve axon to network (CRITICAL - this is what was missing!)
        print("Serving axon to network...", flush=True)
        try:
            self.subtensor.serve_axon(
                netuid=settings.subnet_uid,
                axon=self.axon,
            )
            print("✅ Axon served to subtensor network!", flush=True)
            bt.logging.info("✅ Axon served to subtensor network!")
        except Exception as e:
            print(f"❌ Failed to serve axon: {e}", flush=True)
            bt.logging.error(f"❌ Failed to serve axon: {e}")
            bt.logging.error("Validators will not be able to discover your miner!")
            import traceback
            traceback.print_exc()
            return
        
        # PERFORMANCE OPT: More frequent metagraph sync and axon re-serving for better visibility
        async def sync_metagraph():
            while True:
                try:
                    await asyncio.sleep(120)  # Sync every 2 minutes (more frequent for better discovery)
                    self.metagraph = self.subtensor.metagraph(settings.subnet_uid)
                    bt.logging.debug("Metagraph synced")
                    
                    # Re-serve axon periodically to ensure it stays registered
                    # PERFORMANCE OPT: More frequent re-serving increases validator discovery
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

