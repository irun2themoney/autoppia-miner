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
            bt.logging.info(f"✅ StartRoundSynapse processed successfully: round_id={synapse.round_id}, task_type={synapse.task_type}")
            synapse.success = True
            synapse.message = "Round started successfully"
            bt.logging.info(f"📊 Round registration confirmed: {synapse.round_id}")
        except Exception as e:
            synapse.success = False
            synapse.message = f"Error: {e}"
            bt.logging.error(f"❌ Error processing StartRoundSynapse: {e}")
        return synapse
    
    def _is_start_round_synapse(self, synapse: bt.Synapse) -> bool:
        """Robust detection of StartRoundSynapse (handles Bittensor deserialization issues)"""
        # Method 1: Direct type check
        if isinstance(synapse, StartRoundSynapse):
            return True

        # Method 2: Attribute-based detection (Bittensor may deserialize as generic Synapse)
        has_round_id = hasattr(synapse, "round_id") and getattr(synapse, "round_id", None) is not None
        has_task_type = hasattr(synapse, "task_type") and getattr(synapse, "task_type", None) is not None
        has_no_prompt = not hasattr(synapse, "prompt") or getattr(synapse, "prompt", None) is None or getattr(synapse, "prompt", "") == ""
        has_no_actions = not hasattr(synapse, "actions") or getattr(synapse, "actions", None) is None or getattr(synapse, "actions", []) == []

        # More flexible detection - also check for alternative attribute names
        # Some deserializations might use different field names
        round_id_alt = getattr(synapse, "round_id", None) or getattr(synapse, "round", None) or getattr(synapse, "id", None)
        task_type_alt = getattr(synapse, "task_type", None) or getattr(synapse, "task", None) or getattr(synapse, "type", None)

        has_round_id_alt = round_id_alt is not None
        has_task_type_alt = task_type_alt is not None

        # DEBUG: Log detection logic
        detection_result = has_round_id and has_task_type and has_no_prompt and has_no_actions
        alt_detection_result = has_round_id_alt and has_task_type_alt and has_no_prompt and has_no_actions

        if detection_result or alt_detection_result:
            bt.logging.info(f"🎯 STARTROUND_DETECTED: round_id={getattr(synapse, 'round_id', None)}, task_type={getattr(synapse, 'task_type', None)}, has_prompt={not has_no_prompt}, has_actions={not has_no_actions}")
            print(f"🎯 STARTROUND_DETECTED: round_id={round_id_alt}, task_type={task_type_alt}", flush=True)

        # Must have round_id AND task_type AND no task-related fields
        return detection_result or alt_detection_result

    def _convert_to_start_round_synapse(self, synapse: bt.Synapse) -> StartRoundSynapse:
        """Convert generic synapse to StartRoundSynapse"""
        start_round = StartRoundSynapse(
            round_id=getattr(synapse, "round_id", None),
            task_type=getattr(synapse, "task_type", None)
        )

        # Copy response fields if they exist
        for attr in ["success", "message"]:
            if hasattr(synapse, attr):
                setattr(start_round, attr, getattr(synapse, attr))

        return start_round

    def _get_validator_ip(self, synapse: bt.Synapse) -> str:
        """Extract validator identifier from synapse for logging"""
        try:
            # Method 1: Check dendrite info
            if hasattr(synapse, 'dendrite') and synapse.dendrite:
                if hasattr(synapse.dendrite, 'ip') and synapse.dendrite.ip:
                    return synapse.dendrite.ip
                elif hasattr(synapse.dendrite, 'hotkey') and synapse.dendrite.hotkey:
                    return str(synapse.dendrite.hotkey)[:16]

            # Method 2: Check axon_info
            if hasattr(synapse, 'axon_info') and synapse.axon_info:
                if hasattr(synapse.axon_info, 'ip') and synapse.axon_info.ip:
                    return synapse.axon_info.ip

            # Method 3: Check for any IP-like attributes
            for attr in ['source_ip', 'ip', 'validator_ip']:
                if hasattr(synapse, attr):
                    value = getattr(synapse, attr)
                    if value and isinstance(value, str):
                        return value

        except Exception:
            pass  # Fall through to default

        return "unknown"
    
    async def process_task(self, synapse: bt.Synapse) -> bt.Synapse:
        """Process validator request - handles TaskSynapse (StartRoundSynapse handled separately)"""
        try:
            bt.logging.info(f"Processing task synapse: type={type(synapse)}, id={getattr(synapse, 'id', 'unknown')}")

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
        
        # Create axon - CRITICAL FIX: Configure to accept all synapse types
        # The issue: Bittensor was rejecting StartRoundSynapse before it reached our forward function
        # Solution: Ensure axon accepts all synapse types and routes them through forward
        print("Creating axon...", flush=True)
        self.axon = bt.axon(
            wallet=self.wallet,
            port=self.config.axon.port,  # Axon port: 8091 (CRITICAL - must be 8091)
            ip=external_ip,  # External IP: 134.199.203.133
            external_ip=external_ip,  # External IP for API discovery
            # CRITICAL: Don't restrict synapse types - accept all and route through forward
            # Validators use convention: API is on port 8080 (standard)
        )
        print(f"Axon created: ip={external_ip}, port={self.config.axon.port}", flush=True)
        bt.logging.info(f"Axon created: ip={external_ip}, port={self.config.axon.port}")
        print(f"Validator API endpoint: {api_url}/solve_task", flush=True)
        bt.logging.info(f"Validator API endpoint: {api_url}/solve_task")
        
        # CRITICAL FIX: Register custom synapse types with axon's forward_class_types
        # Bittensor's axon uses forward_class_types dict to validate incoming synapses
        # Without registration, Bittensor rejects StartRoundSynapse with UnknownSynapseError
        print("Registering custom synapse types with axon...", flush=True)
        try:
            # forward_class_types is a dict mapping synapse names to classes
            # Add our custom synapse types so Bittensor recognizes them
            if hasattr(self.axon, 'forward_class_types'):
                # Ensure it's a dict (might be initialized as empty dict or list)
                if isinstance(self.axon.forward_class_types, dict):
                    self.axon.forward_class_types['StartRoundSynapse'] = StartRoundSynapse
                    self.axon.forward_class_types['TaskSynapse'] = TaskSynapse
                    bt.logging.info(f"✅ Registered StartRoundSynapse and TaskSynapse with axon")
                    print(f"✅ Registered custom synapse types: {list(self.axon.forward_class_types.keys())}", flush=True)
                else:
                    # If it's not a dict, try to convert or set it
                    self.axon.forward_class_types = {
                        'Synapse': bt.Synapse,
                        'StartRoundSynapse': StartRoundSynapse,
                        'TaskSynapse': TaskSynapse
                    }
                    bt.logging.info(f"✅ Initialized forward_class_types with custom synapses")
                    print(f"✅ Initialized synapse registry with custom types", flush=True)
            else:
                bt.logging.warning("⚠️ Axon doesn't have forward_class_types attribute")
                print("⚠️ Cannot register synapse types (axon structure may have changed)", flush=True)
        except Exception as e:
            bt.logging.error(f"❌ Failed to register synapse types: {e}")
            print(f"⚠️ Synapse registration failed (non-critical): {e}", flush=True)
            # Continue anyway - forward function will handle via attribute detection
        
        # Attach forward function - handles all synapse types
        # Use a wrapper that catches all synapse types, including StartRoundSynapse
        print("Attaching forward function...", flush=True)
        
        async def forward_wrapper(synapse: bt.Synapse) -> bt.Synapse:
            """Universal synapse handler - handles StartRoundSynapse, TaskSynapse, and generic synapses"""
            validator_ip = "unknown"

            try:
                # Get validator identifier for logging
                validator_ip = self._get_validator_ip(synapse)
                synapse_name = getattr(synapse, '__class__', {}).__name__ if hasattr(synapse, '__class__') else 'Synapse'
                
                # CRITICAL: Check for StartRoundSynapse first (handles Bittensor deserialization issues)
                if self._is_start_round_synapse(synapse):
                    bt.logging.info(f"🔄 ROUND_START: {validator_ip} - Detected StartRoundSynapse: round_id={getattr(synapse, 'round_id', None)}, task_type={getattr(synapse, 'task_type', None)}")
                    print(f"🔄 ROUND_START: {validator_ip} - Processing StartRoundSynapse", flush=True)

                    try:
                        # Convert to StartRoundSynapse if needed
                        start_round_synapse = synapse if isinstance(synapse, StartRoundSynapse) else self._convert_to_start_round_synapse(synapse)

                        # Process the round start
                        result = await self.process_start_round(start_round_synapse)

                        bt.logging.info(f"✅ ROUND_START_SUCCESS: {validator_ip} - Round {getattr(result, 'round_id', 'unknown')} started successfully")
                        print(f"✅ ROUND_START_SUCCESS: {validator_ip} - Round started", flush=True)
                        return result

                    except Exception as e:
                        bt.logging.error(f"❌ ROUND_START_ERROR: {validator_ip} - Failed to process StartRoundSynapse: {e}")
                        print(f"❌ ROUND_START_ERROR: {validator_ip} - {e}", flush=True)

                        # Return valid response even on error to prevent breaking the round
                        error_response = StartRoundSynapse(
                            round_id=getattr(synapse, "round_id", "unknown"),
                            task_type=getattr(synapse, "task_type", "unknown"),
                            success=False,
                            message=f"Round start failed: {e}"
                        )
                        return error_response
                
                # Handle regular task synapses
                bt.logging.info(f"📋 TASK_RECEIVED: {validator_ip} - Processing {synapse_name}: id={getattr(synapse, 'id', 'unknown')}")
                print(f"📋 TASK_RECEIVED: {validator_ip} - Processing {synapse_name}", flush=True)
                
                result = await self.process_task(synapse)

                bt.logging.info(f"📤 TASK_RESPONSE: {validator_ip} - Completed {synapse_name}: success={getattr(result, 'success', False)}, actions={len(getattr(result, 'actions', []))}")
                return result

            except Exception as e:
                # Comprehensive error handling - never let UnknownSynapseError propagate
                bt.logging.error(f"💥 CRITICAL_ERROR: {validator_ip} - Forward wrapper failed: {e}")
                bt.logging.debug(f"Traceback: {traceback.format_exc()}")

                # DEBUG: Log synapse attributes to understand deserialization issues
                try:
                    synapse_attrs = {}
                    for attr in dir(synapse):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(synapse, attr)
                                if not callable(value):
                                    synapse_attrs[attr] = str(value)[:100]  # Limit string length
                            except:
                                synapse_attrs[attr] = "<error getting value>"

                    bt.logging.info(f"🔍 SYNAPSE_DEBUG: {validator_ip} - Synapse type: {type(synapse)}, attrs: {synapse_attrs}")
                    print(f"🔍 SYNAPSE_DEBUG: {validator_ip} - Type: {type(synapse)}, Key attrs: round_id={getattr(synapse, 'round_id', 'MISSING')}, task_type={getattr(synapse, 'task_type', 'MISSING')}, prompt={getattr(synapse, 'prompt', 'MISSING')[:50] if getattr(synapse, 'prompt', None) else 'MISSING'}", flush=True)
                except Exception as debug_e:
                    bt.logging.error(f"Debug logging failed: {debug_e}")

                # Ensure we return a valid synapse response
                try:
                    # Try to set basic response fields
                    if not hasattr(synapse, 'success'):
                        synapse.success = False
                    if not hasattr(synapse, 'actions'):
                        synapse.actions = []
                    if hasattr(synapse, 'message'):
                        synapse.message = f"Processing error: {e}"
                except Exception:
                    # If we can't modify the synapse, create a basic response
                    synapse = bt.Synapse()
                    synapse.success = False
                    synapse.actions = []

                return synapse
        
        # CRITICAL FIX: Attach forward function with error handling
        # Wrap forward function to catch UnknownSynapseError and handle it gracefully
        async def forward_with_error_handling(synapse: bt.Synapse) -> bt.Synapse:
            """Wrapper that catches synapse errors and routes to forward_wrapper"""
            try:
                return await forward_wrapper(synapse)
            except Exception as e:
                # Catch any synapse-related errors (including UnknownSynapseError)
                error_type = type(e).__name__
                if "UnknownSynapse" in error_type or "Synapse" in error_type:
                    bt.logging.warning(f"⚠️ Synapse error caught: {e} - Attempting to handle as generic synapse")
                    # Try to handle as generic synapse with attribute detection
                    try:
                        return await forward_wrapper(synapse)
                    except Exception as e2:
                        bt.logging.error(f"❌ Failed to handle synapse even with fallback: {e2}")
                        # Return minimal valid response
                        if self._is_start_round_synapse(synapse):
                            return StartRoundSynapse(
                                round_id=getattr(synapse, "round_id", "unknown"),
                                task_type=getattr(synapse, "task_type", "unknown"),
                                success=False,
                                message=f"Synapse handling error: {e2}"
                            )
                        else:
                            result = TaskSynapse()
                            result.success = False
                            result.actions = []
                            result.message = f"Synapse handling error: {e2}"
                            return result
                else:
                    # Re-raise non-synapse errors
                    raise
        
        # NOTE: verify_fn approach didn't work - Bittensor's signature checking is too strict
        # The UnknownSynapseError happens at protocol level before verify_fn is called
        # Our forward function handles all synapse types via attribute detection
        self.axon.attach(
            forward_fn=forward_with_error_handling,
        )
        print("Forward function attached with error handling", flush=True)
        bt.logging.info("✅ Forward function configured to handle all synapse types via attribute detection")
        
        # CRITICAL: Our forward function handles all synapse types via attribute detection
        # This allows us to process StartRoundSynapse even if Bittensor deserializes it as generic Synapse
        # The error handling wrapper ensures UnknownSynapseError doesn't break the connection
        bt.logging.info("✅ Forward function configured to handle StartRoundSynapse and TaskSynapse via attribute detection with error handling")
        
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

