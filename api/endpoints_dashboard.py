"""Real-time dashboard endpoints for monitoring"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter()

# Mount static files
# We need to mount this on the main app, but since we're in a router, 
# we'll assume the main app will handle the mounting or we can serve static files via a separate endpoint if needed.
# However, standard practice with APIRouter is to mount on the main app.
# For now, let's assume the main app mounts /static. 
# If not, we might need to adjust. 
# Actually, let's check if we can mount here. We can't mount on a router easily.
# So we'll assume the main app (api/api.py) needs to mount /static.
# But to be safe and self-contained, we can add a route for static files here if needed, 
# or better yet, update the main api.py.

# Let's check api/api.py first to see if we can mount there.
# But for now, let's setup the templates.

templates = Jinja2Templates(directory="api/templates")

# Lazy import to avoid circular dependency
def get_advanced_metrics():
    """Get the shared advanced_metrics instance"""
    from api.endpoints import advanced_metrics
    return advanced_metrics


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Real-time dashboard - Premium UI"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Cache wallet info to avoid OOM issues
_wallet_info_cache = {"data": None, "timestamp": 0}
_wallet_info_cache_ttl = 60  # Cache for 60 seconds

# Cache round info to avoid OOM issues
_round_info_cache = {"data": None, "timestamp": 0}
_round_info_cache_ttl = 30  # Cache for 30 seconds

def get_round_info():
    """Get current round information from Bittensor"""
    import time
    
    # Return cached data if still valid
    current_time = time.time()
    if _round_info_cache["data"] and (current_time - _round_info_cache["timestamp"]) < _round_info_cache_ttl:
        return _round_info_cache["data"]
    
    try:
        import bittensor as bt
        from config.settings import settings
        
        subtensor = bt.subtensor(network='finney')
        
        # Get current block number
        current_block = subtensor.get_current_block()
        
        # IWA rounds are typically ~1080 blocks (1-2 hours at ~12s per block)
        # Round 37 started at block 6,912,165 (from IWA Platform data)
        # We can estimate current round based on block number
        blocks_per_round = 1080  # Approximate, based on IWA Platform data
        
        # Estimate round number (this is approximate)
        # Round 37 started at block 6,912,165
        base_round = 37
        base_block = 6912165
        
        if current_block >= base_block:
            blocks_since_base = current_block - base_block
            rounds_since_base = blocks_since_base // blocks_per_round
            estimated_round = base_round + rounds_since_base
            blocks_into_round = blocks_since_base % blocks_per_round
        else:
            # If current block is before our base, estimate backwards
            blocks_before_base = base_block - current_block
            rounds_before_base = blocks_before_base // blocks_per_round
            estimated_round = base_round - rounds_before_base
            blocks_into_round = blocks_per_round - (blocks_before_base % blocks_per_round)
        
        # Calculate time until next round
        blocks_remaining = blocks_per_round - blocks_into_round
        seconds_per_block = 12  # Bittensor block time
        seconds_until_next_round = blocks_remaining * seconds_per_block
        
        result = {
            "current_round": estimated_round,
            "current_block": int(current_block),
            "blocks_into_round": blocks_into_round,
            "blocks_per_round": blocks_per_round,
            "blocks_remaining": blocks_remaining,
            "seconds_until_next_round": seconds_until_next_round,
            "round_progress": round((blocks_into_round / blocks_per_round) * 100, 1)
        }
        
        # Cache the result
        _round_info_cache["data"] = result
        _round_info_cache["timestamp"] = current_time
        return result
        
    except Exception as e:
        # Return cached data if available
        if _round_info_cache["data"]:
            return _round_info_cache["data"]
        
        # Return default values if error
        return {
            "current_round": 0,
            "current_block": 0,
            "blocks_into_round": 0,
            "blocks_per_round": 1080,
            "blocks_remaining": 1080,
            "seconds_until_next_round": 12960,  # ~3.6 hours default
            "round_progress": 0.0,
            "error": str(e)
        }

def get_wallet_info():
    """Get wallet balance and stake information from Bittensor (cached)"""
    import time
    
    # Return cached data if still valid
    current_time = time.time()
    if _wallet_info_cache["data"] and (current_time - _wallet_info_cache["timestamp"]) < _wallet_info_cache_ttl:
        return _wallet_info_cache["data"]
    
    try:
        import bittensor as bt
        from config.settings import settings
        
        wallet = bt.wallet(name='default', hotkey='default')
        subtensor = bt.subtensor(network='finney')
        
        # Get balance (lightweight operation)
        balance = subtensor.get_balance(wallet.coldkeypub.ss58_address)
        balance_tao = float(balance.tao) if hasattr(balance, 'tao') else float(balance)
        
        # Get stake and other metrics (memory-intensive, so we cache it)
        # Note: sync parameter not available in all Bittensor versions
        try:
            metagraph = subtensor.metagraph(settings.subnet_uid, sync=False)  # Try with sync=False first
        except TypeError:
            # Fallback: sync parameter not supported, use default
            metagraph = subtensor.metagraph(settings.subnet_uid)
        uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address) if wallet.hotkey.ss58_address in metagraph.hotkeys else None
        
        if uid is not None:
            total_stake = metagraph.S[uid].item() if hasattr(metagraph, 'S') and uid < len(metagraph.S) else 0
            
            # Try to get stake FROM your coldkey specifically
            your_stake = 0.0
            delegator_stake = 0.0
            try:
                # Try different method signatures
                try:
                    stake_from_you = subtensor.get_stake_for_coldkey_and_hotkey(
                        coldkey_ss58=wallet.coldkeypub.ss58_address,
                        hotkey_ss58=wallet.hotkey.ss58_address
                    )
                except TypeError:
                    # Try without netuid parameter
                    stake_from_you = subtensor.get_stake(
                        coldkey_ss58=wallet.coldkeypub.ss58_address,
                        hotkey_ss58=wallet.hotkey.ss58_address
                    )
                
                your_stake = float(stake_from_you.tao) if hasattr(stake_from_you, 'tao') else float(stake_from_you)
                delegator_stake = max(0, total_stake - your_stake)
            except Exception as e:
                # If we can't get the breakdown, we'll show total stake
                # and note that it may include delegators
                your_stake = 0.0  # Unknown - will show as 0.00
                delegator_stake = total_stake  # Assume all is delegator until we can verify
            
            rank = metagraph.R[uid].item() if hasattr(metagraph, 'R') and uid < len(metagraph.R) else 0
            trust = metagraph.T[uid].item() if hasattr(metagraph, 'T') and uid < len(metagraph.T) else 0
            incentive = metagraph.I[uid].item() if hasattr(metagraph, 'I') and uid < len(metagraph.I) else 0
            
            result = {
                "balance_tao": balance_tao,
                "stake_tao": float(total_stake),  # Total stake (for backwards compatibility)
                "your_stake_tao": float(your_stake),  # Your stake specifically
                "delegator_stake_tao": float(delegator_stake),  # Delegator stake
                "rank": float(rank),
                "trust": float(trust),
                "incentive": float(incentive),
                "uid": uid
            }
        else:
            result = {
                "balance_tao": balance_tao,
                "stake_tao": 0.0,
                "your_stake_tao": 0.0,
                "delegator_stake_tao": 0.0,
                "rank": 0.0,
                "trust": 0.0,
                "incentive": 0.0,
                "uid": None
            }
        
        # Cache the result
        _wallet_info_cache["data"] = result
        _wallet_info_cache["timestamp"] = current_time
        return result
        
    except Exception as e:
        # Return cached data if available, even if expired, to avoid showing errors
        if _wallet_info_cache["data"]:
            return _wallet_info_cache["data"]
        
        # Return zeros if there's an error and no cache
        return {
            "balance_tao": 0.0,
            "stake_tao": 0.0,
            "your_stake_tao": 0.0,
            "delegator_stake_tao": 0.0,
            "rank": 0.0,
            "trust": 0.0,
            "incentive": 0.0,
            "uid": None,
            "error": str(e)
        }


@router.get("/dashboard/metrics")
async def dashboard_metrics():
    """Get real-time metrics as JSON"""
    import subprocess
    import re
    from datetime import datetime
    
    advanced_metrics = get_advanced_metrics()
    metrics = advanced_metrics.get_comprehensive_metrics()
    # Health score will be recalculated after we update metrics from logs
    # Don't set it here as it might be based on stale data
    
    # WALLET INFO: Add wallet balance and stake information
    try:
        wallet_info = get_wallet_info()
        # Map the wallet_info keys to match what the dashboard expects
        metrics["wallet"] = {
            "balance": wallet_info.get("balance_tao", 0.0),
            "total_stake": wallet_info.get("stake_tao", 0.0),
            "your_stake": wallet_info.get("your_stake_tao", 0.0),
            "delegator_stake": wallet_info.get("delegator_stake_tao", 0.0),
            "rank": wallet_info.get("rank", 0.0),
            "trust": wallet_info.get("trust", 0.0),
            "incentive": wallet_info.get("incentive", 0.0),
            "uid": wallet_info.get("uid", None),
            # Also include original keys for backwards compatibility
            "balance_tao": wallet_info.get("balance_tao", 0.0),
            "stake_tao": wallet_info.get("stake_tao", 0.0),
            "your_stake_tao": wallet_info.get("your_stake_tao", 0.0),
            "delegator_stake_tao": wallet_info.get("delegator_stake_tao", 0.0),
        }
    except Exception as e:
        metrics["wallet"] = {
            "balance": 0.0,
            "total_stake": 0.0,
            "your_stake": 0.0,
            "delegator_stake": 0.0,
            "rank": 0.0,
            "trust": 0.0,
            "incentive": 0.0,
            "uid": None,
            "error": str(e)
        }
    
    # ROUND INFO: Add current round information
    try:
        round_info = get_round_info()
        metrics["round"] = round_info
    except Exception:
        metrics["round"] = {
            "current_round": 0,
            "seconds_until_next_round": 0,
            "round_progress": 0.0
        }
    
    # DYNAMIC ZERO: Add anti-overfitting metrics
    try:
        from api.utils.anti_overfitting import anti_overfitting
        from api.utils.task_diversity import task_diversity
        metrics["anti_overfitting"] = anti_overfitting.get_overfitting_metrics()
        metrics["task_diversity"] = task_diversity.get_diversity_metrics()
    except Exception:
        metrics["anti_overfitting"] = {}
        metrics["task_diversity"] = {}
    
    # Store current in-memory metrics (should only contain validator requests now)
    # But we'll still rebuild from logs to ensure accuracy and filter any old localhost data
    current_total_requests = metrics["overview"]["total_requests"]
    current_successful = metrics["overview"]["successful_requests"]
    current_failed = metrics["overview"]["failed_requests"]
    current_response_times = list(advanced_metrics.response_times) if hasattr(advanced_metrics, 'response_times') else []
    
    # Also get validator activity from in-memory (filters localhost)
    in_memory_validator_activity = []
    if hasattr(advanced_metrics, 'validator_activity'):
        for activity in advanced_metrics.validator_activity:
            ip = activity.get("ip", "")
            if ip and ip not in ["127.0.0.1", "localhost", "::1"]:
                if not ip.startswith("192.168.") and not ip.startswith("10.") and not ip.startswith("172.16.") and ip != "134.199.203.133":
                    in_memory_validator_activity.append(activity)
    
    # Supplement with historical log data (for recent activity display), but don't replace in-memory counts
    try:
        result = subprocess.run(
            ["journalctl", "-u", "autoppia-api", "--since", "24 hours ago", "--no-pager"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            log_lines = result.stdout.split('\n')
            historical_activity = []
            
            for line in log_lines:
                # Try multiple regex patterns to match different log formats
                match = None
                # Pattern 1: Standard format with quotes and status code
                match = re.search(r'(\w+\s+\d+\s+\d+:\d+:\d+).*?INFO:\s+([\d.]+):\d+\s+-\s+"POST\s+/solve_task.*?"\s+(\d+)', line)
                if not match:
                    # Pattern 2: Format with "HTTP/1.1" and status code
                    match = re.search(r'(\w+\s+\d+\s+\d+:\d+:\d+).*?INFO:\s+([\d.]+):\d+\s+-\s+"POST\s+/solve_task.*?HTTP/1\.1"\s+(\d+)', line)
                if match:
                    timestamp_str, ip, status_code = match.groups()
                    if ip in ["127.0.0.1", "localhost", "::1"]:
                        continue
                    try:
                        current_year = datetime.now().year
                        dt = datetime.strptime(f"{timestamp_str} {current_year}", "%b %d %H:%M:%S %Y")
                        historical_activity.append({
                            "time": dt.isoformat(),
                            "ip": ip,
                            "success": status_code == "200",
                            "response_time": 0.0,
                            "source": "validator"
                        })
                    except Exception:
                        pass
            
            validator_activity = [
                a for a in historical_activity 
                if a.get("ip") not in ["127.0.0.1", "localhost", "::1"] 
                and not a.get("ip", "").startswith("192.168.")
                and not a.get("ip", "").startswith("10.")
                and not a.get("ip", "").startswith("172.16.")
                and a.get("ip") != "134.199.203.133"
            ]
            
            # Merge with in-memory validator activity (more recent, may not be in logs yet)
            # Combine and deduplicate by time and IP, preserving response times from in-memory
            combined_activity = {}
            for activity in validator_activity + in_memory_validator_activity:
                key = f"{activity.get('ip')}_{activity.get('time', '')}"
                if key not in combined_activity:
                    combined_activity[key] = activity
                else:
                    # Keep more recent, but preserve response_time if available
                    existing = combined_activity[key]
                    new_time = activity.get("time", "")
                    existing_time = existing.get("time", "")
                    if new_time > existing_time:
                        # Newer activity - use it, but preserve response_time if existing has it and new doesn't
                        if existing.get("response_time", 0.0) > 0 and activity.get("response_time", 0.0) == 0.0:
                            activity["response_time"] = existing.get("response_time", 0.0)
                        combined_activity[key] = activity
                    elif existing.get("response_time", 0.0) == 0.0 and activity.get("response_time", 0.0) > 0:
                        # Existing has no response_time but new one does - update it
                        existing["response_time"] = activity.get("response_time", 0.0)
            
            validator_activity = list(combined_activity.values())
            
            # Sort by time (most recent first) for display
            validator_activity.sort(key=lambda x: x.get("time", x.get("timestamp", "")), reverse=True)
            
            # Use validator activity from logs as source of truth (filters out localhost)
            # In-memory metrics may include old localhost data, so we prioritize filtered validator activity
            validator_total = len(validator_activity)
            validator_successful = sum(1 for a in validator_activity if a.get("success", False) or a.get("success") == "True" or a.get("success") == "true")
            validator_failed = validator_total - validator_successful
            
            # Always use validator activity counts (filters localhost correctly)
            # In-memory may have old localhost data, so we trust the filtered logs
            metrics["overview"]["total_requests"] = validator_total
            metrics["overview"]["successful_requests"] = validator_successful
            metrics["overview"]["failed_requests"] = validator_failed
            
            # Only use in-memory if it has MORE validator requests (new requests not yet in logs)
            # But only if in-memory looks valid (not all failed, which indicates old localhost data)
            if current_total_requests > validator_total and current_successful > 0:
                # In-memory has more AND has successful requests (likely new validator requests)
                metrics["overview"]["total_requests"] = current_total_requests
                metrics["overview"]["successful_requests"] = current_successful
                metrics["overview"]["failed_requests"] = current_failed
            
            # Recalculate success rate based on updated counts
            if metrics["overview"]["total_requests"] > 0:
                metrics["overview"]["success_rate"] = round(
                    (metrics["overview"]["successful_requests"] / metrics["overview"]["total_requests"]) * 100, 2
                )
            
            # Calculate response times from in-memory data OR from validator activity
            # Priority: in-memory response_times > in-memory validator_activity > log-based validator_activity
            response_times_to_use = []
            
            # First, try in-memory response_times (most accurate)
            if current_response_times and len(current_response_times) > 0:
                response_times_to_use = list(current_response_times)
            
            # Second, try in-memory validator_activity response times
            if not response_times_to_use and in_memory_validator_activity:
                response_times_to_use = [a.get("response_time", 0.0) for a in in_memory_validator_activity if a.get("response_time", 0.0) > 0]
            
            # Third, try log-based validator_activity response times
            if not response_times_to_use:
                activity_response_times = [a.get("response_time", 0.0) for a in validator_activity if a.get("response_time", 0.0) > 0]
                if activity_response_times:
                    response_times_to_use = activity_response_times
            
            # Calculate metrics from response times
            if response_times_to_use and len(response_times_to_use) > 0:
                metrics["performance"]["avg_response_time"] = round(sum(response_times_to_use) / len(response_times_to_use), 3)
                sorted_times = sorted(response_times_to_use)
                if len(sorted_times) >= 20:
                    metrics["performance"]["p95_response_time"] = round(sorted_times[int(len(sorted_times) * 0.95)], 3)
                    metrics["performance"]["p99_response_time"] = round(sorted_times[int(len(sorted_times) * 0.99)], 3)
                elif len(sorted_times) >= 5:
                    # Use available data for p95 even if less than 20 samples
                    metrics["performance"]["p95_response_time"] = round(sorted_times[int(len(sorted_times) * 0.95)], 3)
            
            uptime_hours = metrics["overview"].get("uptime_hours", 0.0)
            # If uptime is 0, calculate it from start_time
            if uptime_hours == 0.0 and hasattr(advanced_metrics, 'start_time'):
                import time
                uptime_seconds = time.time() - advanced_metrics.start_time
                uptime_hours = max(0.01, uptime_seconds / 3600)  # At least 0.01 hours
                metrics["overview"]["uptime_hours"] = round(uptime_hours, 2)
            
            # Calculate requests per minute (only if we have requests and uptime)
            if uptime_hours > 0 and metrics["overview"]["total_requests"] > 0:
                metrics["performance"]["requests_per_minute"] = round(
                    metrics["overview"]["total_requests"] / (uptime_hours * 60), 2
                )
            elif metrics["overview"]["total_requests"] > 0:
                # If uptime is 0 but we have requests, use a default calculation
                # This handles the case where service just restarted but has historical data
                metrics["performance"]["requests_per_minute"] = 0.0
            
            # Health score should only be calculated if we have requests
            if metrics["overview"]["total_requests"] > 0:
                success_rate = metrics["overview"]["success_rate"]
                avg_response_time = metrics["performance"].get("avg_response_time", 0.0)
                # Response time score: 100% for <1s, decreasing for slower responses
                # Formula: max(0, 100 - (response_time * 10))
                # This gives: 1s = 90%, 2s = 80%, 5s = 50%, 10s = 0%
                response_time_score = max(0, min(100, 100 - (avg_response_time * 10)))
                # Uptime score: increases with uptime, capped at 100%
                # Formula: min(100, uptime_hours * 10)
                # This gives: 0.1h = 1%, 1h = 10%, 10h = 100%
                uptime_score = min(100, max(0, uptime_hours * 10))
                metrics["health_score"] = round(
                    success_rate * 0.5 + response_time_score * 0.3 + uptime_score * 0.2, 2
                )
            else:
                # No requests = no health score (can't evaluate performance)
                metrics["health_score"] = 0.0
            
            # Ensure recent_activity is sorted by time (most recent first) and limit to 20
            # (Already sorted above, but ensure it's still sorted)
            # Also ensure boolean values are properly formatted for JSON
            recent_activity_formatted = []
            for activity in validator_activity[:20]:
                formatted = {
                    "time": activity.get("time", activity.get("timestamp", "")),
                    "ip": activity.get("ip", "unknown"),
                    "success": bool(activity.get("success", False) if isinstance(activity.get("success"), bool) else str(activity.get("success", "False")).lower() == "true"),
                    "response_time": float(activity.get("response_time", 0.0)),
                    "source": activity.get("source", "validator")
                }
                recent_activity_formatted.append(formatted)
            
            metrics["validators"]["recent_activity"] = recent_activity_formatted
            metrics["validators"]["unique_validators"] = len(set(a["ip"] for a in validator_activity))
            
            from collections import Counter
            ip_counts = Counter(a["ip"] for a in validator_activity)
            metrics["validators"]["top_validators"] = [
                {"ip": ip, "requests": count} 
                for ip, count in ip_counts.most_common(5)
            ]
    except Exception:
        pass
    
    # Always recalculate health score at the end to ensure it's correct
    # This ensures health score is always calculated based on current metrics
    uptime_hours = metrics["overview"].get("uptime_hours", 0.0)
    # If uptime is 0, try to calculate it from start_time
    if uptime_hours == 0.0 and hasattr(advanced_metrics, 'start_time'):
        import time
        uptime_seconds = time.time() - advanced_metrics.start_time
        uptime_hours = max(0.01, uptime_seconds / 3600)  # At least 0.01 hours
        metrics["overview"]["uptime_hours"] = round(uptime_hours, 2)
    
    # Recalculate health score with proper bounds checking
    # Health score should be 0 if no requests have been processed
    if metrics["overview"]["total_requests"] > 0:
        success_rate = metrics["overview"].get("success_rate", 0)
        avg_response_time = metrics["performance"].get("avg_response_time", 0.0)
        # Response time score: 100% for <1s, decreasing for slower responses
        response_time_score = max(0, min(100, 100 - (avg_response_time * 10)))
        # Uptime score: increases with uptime, capped at 100%
        uptime_score = min(100, max(0, uptime_hours * 10))
        metrics["health_score"] = round(
            success_rate * 0.5 + response_time_score * 0.3 + uptime_score * 0.2, 2
        )
    else:
        # No requests = no health score (can't evaluate performance)
        metrics["health_score"] = 0.0
    
    # Add metadata about data freshness
    if validator_activity:
        latest_activity_time = validator_activity[0].get("time", "")
        if latest_activity_time:
            try:
                from datetime import datetime, timezone
                latest_dt = datetime.fromisoformat(latest_activity_time.replace('Z', '+00:00'))
                now_dt = datetime.now(timezone.utc)
                hours_since_activity = (now_dt - latest_dt).total_seconds() / 3600
                metrics["data_freshness"] = {
                    "latest_activity": latest_activity_time,
                    "hours_since_activity": round(hours_since_activity, 2),
                    "is_stale": hours_since_activity > 1.0  # Consider stale if > 1 hour
                }
            except Exception:
                pass
    
    # Ensure proper JSON serialization
    import json
    try:
        # Validate that metrics can be serialized to JSON
        json.dumps(metrics)
        return JSONResponse(content=metrics)
    except (TypeError, ValueError) as e:
        # If serialization fails, return error
        return JSONResponse(
            content={"error": f"Metrics serialization error: {str(e)}"},
            status_code=500
        )
