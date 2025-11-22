import os

file_path = '/opt/autoppia-miner/miner/miner.py'

with open(file_path, 'r') as f:
    content = f.read()

target = '''        self.axon.attach(
            forward_fn=self.process_task,
        )'''

replacement = '''        # Register StartRoundSynapse handler explicitly
        self.axon.attach(
            forward_fn=self.process_start_round,
            blacklist_fn=None,
            priority_fn=None,
        ).attach(
            forward_fn=self.process_task,
            blacklist_fn=None,
            priority_fn=None,
        )'''

if target in content:
    new_content = content.replace(target, replacement)
    with open(file_path, 'w') as f:
        f.write(new_content)
    print("Successfully patched miner.py")
else:
    if "process_start_round" in content and "self.axon.attach" in content:
         print("File might already be patched or content mismatch.")
    else:
         print("Could not find target string to replace.")
