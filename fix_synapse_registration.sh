#!/bin/bash
# Fix for StartRoundSynapse UnknownSynapseError
# This script patches the miner to properly register the StartRoundSynapse handler

echo "🔧 Fixing StartRoundSynapse registration..."

cd /opt/autoppia-miner

# Create backup
cp miner/miner.py miner/miner.py.backup

# Apply fix - replace the axon.attach section
sed -i '213,219s/.*/        # Attach synapse handlers\n        # Register StartRoundSynapse handler explicitly\n        print("Attaching forward functions...", flush=True)\n        self.axon.attach(\n            forward_fn=self.process_start_round,\n            blacklist_fn=None,\n            priority_fn=None,\n        ).attach(\n            forward_fn=self.process_task,\n            blacklist_fn=None,\n            priority_fn=None,\n        )\n        print("Forward functions attached", flush=True)/' miner/miner.py

echo "✅ Fix applied"
echo "📋 Restarting miner service..."

systemctl restart autoppia-miner

sleep 3

echo "✅ Miner restarted"
echo "📊 Checking for validator requests..."

journalctl -u autoppia-miner --since "10 seconds ago" --no-pager | tail -10
