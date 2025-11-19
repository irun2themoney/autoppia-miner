"""Self-learning system that references official Autoppia documentation"""
import asyncio
import logging
import re
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import aiohttp
import hashlib

logger = logging.getLogger(__name__)


class DocumentationLearner:
    """Continuously learns from official Autoppia documentation"""
    
    # Official Autoppia sources to monitor
    OFFICIAL_SOURCES = {
        "github": "https://api.github.com/repos/autoppia/autoppia/contents/docs",
        "substack": "https://autoppia.substack.com",
        "discord": None,  # Would need Discord API integration
        "iwa_platform": "https://infinitewebarena.autoppia.com",
    }
    
    def __init__(self, enabled: bool = True, check_interval: int = 3600):
        """
        Initialize documentation learner
        
        Args:
            enabled: Whether self-learning is enabled
            check_interval: How often to check for updates (seconds)
        """
        self.enabled = enabled
        self.check_interval = check_interval
        self.cache_dir = "/tmp/autoppia_docs_cache"
        self.learned_patterns_file = "/tmp/autoppia_learned_patterns.json"
        self.last_check_file = "/tmp/autoppia_last_check.json"
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Load previously learned patterns
        self.learned_patterns = self._load_learned_patterns()
        self.last_check_times = self._load_last_check_times()
        
        # Background task
        self._background_task: Optional[asyncio.Task] = None
        
    def _load_learned_patterns(self) -> Dict[str, Any]:
        """Load previously learned patterns"""
        if os.path.exists(self.learned_patterns_file):
            try:
                with open(self.learned_patterns_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load learned patterns: {e}")
        return {
            "patterns": {},
            "best_practices": [],
            "updates": [],
            "last_updated": None
        }
    
    def _save_learned_patterns(self):
        """Save learned patterns to disk"""
        try:
            self.learned_patterns["last_updated"] = datetime.now().isoformat()
            with open(self.learned_patterns_file, 'w') as f:
                json.dump(self.learned_patterns, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save learned patterns: {e}")
    
    def _load_last_check_times(self) -> Dict[str, str]:
        """Load last check times for each source"""
        if os.path.exists(self.last_check_file):
            try:
                with open(self.last_check_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_last_check_times(self):
        """Save last check times"""
        try:
            with open(self.last_check_file, 'w') as f:
                json.dump(self.last_check_times, f, indent=2)
        except Exception:
            pass
    
    async def fetch_github_docs(self) -> List[Dict[str, Any]]:
        """Fetch documentation from GitHub"""
        if not HAS_AIOHTTP:
            logger.debug("aiohttp not available - skipping GitHub fetch")
            return []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.OFFICIAL_SOURCES["github"],
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data if isinstance(data, list) else []
        except Exception as e:
            logger.debug(f"Failed to fetch GitHub docs: {e}")
        return []
    
    async def fetch_substack_articles(self) -> List[Dict[str, Any]]:
        """Fetch articles from Autoppia Substack"""
        # Note: Substack doesn't have a public API, would need web scraping
        # For now, return empty list - can be enhanced later
        return []
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """Check all sources for updates"""
        if not self.enabled:
            return {"status": "disabled"}
        
        updates = {
            "github": [],
            "substack": [],
            "patterns_found": [],
            "best_practices_found": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Check GitHub
            github_docs = await self.fetch_github_docs()
            if github_docs:
                updates["github"] = github_docs
                # Extract patterns from GitHub docs
                patterns = self._extract_patterns_from_docs(github_docs)
                updates["patterns_found"].extend(patterns)
            
            # Check Substack (if implemented)
            # substack_articles = await self.fetch_substack_articles()
            
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
        
        return updates
    
    def _extract_patterns_from_docs(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract patterns and best practices from documentation"""
        patterns = []
        
        for doc in docs:
            if doc.get("type") == "file" and doc.get("name", "").endswith((".md", ".txt")):
                # Extract patterns from markdown files
                # This would need to download and parse the actual content
                # For now, return metadata
                patterns.append({
                    "source": "github",
                    "file": doc.get("name"),
                    "url": doc.get("download_url"),
                    "type": "documentation"
                })
        
        return patterns
    
    def _extract_best_practices(self, content: str) -> List[str]:
        """Extract best practices from documentation content"""
        practices = []
        
        # Look for common patterns in Autoppia docs
        # Examples: "best practice", "recommended", "should", "must"
        patterns = [
            r"best practice[s]?:?\s+(.+?)(?:\.|$)",
            r"recommended:?\s+(.+?)(?:\.|$)",
            r"should\s+(.+?)(?:\.|$)",
            r"must\s+(.+?)(?:\.|$)",
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                practices.append(match.group(1).strip())
        
        return practices
    
    def _extract_action_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Extract action patterns from documentation"""
        patterns = []
        
        # Look for code examples, action sequences, etc.
        # This is a simplified version - can be enhanced
        
        # Look for JSON action examples
        json_pattern = r'\{[^{}]*"action_type"[^{}]*\}'
        matches = re.finditer(json_pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            try:
                action = json.loads(match.group(0))
                patterns.append({
                    "type": "action_example",
                    "action": action
                })
            except:
                pass
        
        return patterns
    
    async def learn_from_documentation(self) -> Dict[str, Any]:
        """Main learning function - checks docs and extracts knowledge"""
        if not self.enabled:
            return {"status": "disabled"}
        
        logger.info("Checking official Autoppia documentation for updates...")
        
        updates = await self.check_for_updates()
        
        # Process updates and extract knowledge
        new_patterns = []
        new_practices = []
        
        for pattern in updates.get("patterns_found", []):
            if pattern not in self.learned_patterns.get("patterns", {}):
                new_patterns.append(pattern)
        
        # Update learned patterns
        if new_patterns or new_practices:
            self.learned_patterns.setdefault("patterns", {}).update({
                p.get("file", "unknown"): p for p in new_patterns
            })
            self.learned_patterns.setdefault("best_practices", []).extend(new_practices)
            self._save_learned_patterns()
            
            logger.info(f"Learned {len(new_patterns)} new patterns from documentation")
        
        # Update last check time
        self.last_check_times["last_check"] = datetime.now().isoformat()
        self._save_last_check_times()
        
        return {
            "status": "success",
            "new_patterns": len(new_patterns),
            "new_practices": len(new_practices),
            "total_patterns": len(self.learned_patterns.get("patterns", {}))
        }
    
    async def background_learning_loop(self):
        """Background task that continuously learns from documentation"""
        logger.info("Starting background documentation learning loop...")
        
        # Wait a bit before first check to let server fully start
        await asyncio.sleep(30)
        
        while self.enabled:
            try:
                result = await self.learn_from_documentation()
                if result.get("status") == "success":
                    logger.info(f"Documentation learning: {result.get('new_patterns', 0)} new patterns, {result.get('new_practices', 0)} new practices")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background learning: {e}")
            
            # Wait before next check
            try:
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
    
    def start_background_learning(self):
        """Start background learning task"""
        if self.enabled and self._background_task is None:
            try:
                # Try to get existing event loop
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Loop is already running, create task
                        self._background_task = loop.create_task(self.background_learning_loop())
                    else:
                        # Loop exists but not running, schedule task
                        self._background_task = loop.create_task(self.background_learning_loop())
                except RuntimeError:
                    # No event loop exists, create one in background thread
                    import threading
                    def run_loop():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        self._background_task = new_loop.create_task(self.background_learning_loop())
                        new_loop.run_forever()
                    thread = threading.Thread(target=run_loop, daemon=True)
                    thread.start()
                
                logger.info("Background documentation learning started")
            except Exception as e:
                logger.warning(f"Failed to start background learning: {e}")
    
    def stop_background_learning(self):
        """Stop background learning task"""
        if self._background_task and not self._background_task.done():
            self._background_task.cancel()
            try:
                # Give it a moment to cancel gracefully
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Can't wait in running loop, just cancel
                    pass
                else:
                    loop.run_until_complete(
                        asyncio.wait_for(self._background_task, timeout=2.0)
                    )
            except (asyncio.TimeoutError, asyncio.CancelledError, RuntimeError):
                pass
            self._background_task = None
            logger.info("Background documentation learning stopped")
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """Get all learned patterns"""
        return self.learned_patterns.copy()
    
    def apply_learned_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply learned patterns to current context (non-destructive)"""
        if not self.enabled:
            return context
        
        # This would apply learned patterns to enhance the context
        # For now, return context unchanged (safe default)
        # Can be enhanced to actually apply patterns
        
        enhanced_context = context.copy()
        
        # Example: Add learned best practices as suggestions
        if self.learned_patterns.get("best_practices"):
            enhanced_context["learned_suggestions"] = self.learned_patterns["best_practices"][:5]
        
        return enhanced_context

