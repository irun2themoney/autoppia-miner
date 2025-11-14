# 📖 Simple Step-by-Step Deployment Guide

## What We're Doing

We're going to install the API on your DigitalOcean server so it can be tested on InfiniteWeb Arena.

**Your Server IP**: `134.199.201.62`

---

## Step 1: Open Terminal on Your Computer

1. On Mac: Press `Command + Space`, type "Terminal", press Enter
2. On Windows: Press `Windows + R`, type "cmd", press Enter
3. On Linux: Press `Ctrl + Alt + T`

You should see a black window with text. This is your terminal.

---

## Step 2: Connect to Your Server

Type this command and press Enter:

```bash
ssh root@134.199.201.62
```

**What this does**: Connects your computer to your DigitalOcean server.

**What will happen**:
- It might ask "Are you sure you want to continue connecting?" - Type `yes` and press Enter
- It might ask for a password - Enter the password you set when creating the droplet
- If you used SSH keys, it might not ask for a password

**You'll know it worked when**: You see something like `root@your-droplet-name:~#`

---

## Step 3: Install Everything (Copy and Paste This)

Once you're connected to your server, copy and paste this entire block:

```bash
apt update && apt upgrade -y && apt install -y python3 python3-pip git curl ufw && git clone https://github.com/irun2themoney/autoppia-miner.git && cd autoppia-miner && pip3 install -r requirements.txt
```

**What this does**: 
- Updates your server
- Installs Python and other tools
- Downloads the code
- Installs the required software

**This will take 2-5 minutes**. Just wait for it to finish.

**You'll know it worked when**: You see `root@your-droplet-name:~/autoppia-miner#`

---

## Step 4: Set Up the Configuration File

Type this command:

```bash
cp env.example .env
```

**What this does**: Creates a configuration file.

---

## Step 5: Add Your API Key

Type this command:

```bash
nano .env
```

**What this does**: Opens a text editor.

**Now you need to**:
1. Find the line that says `CHUTES_API_KEY=`
2. Replace it with: `CHUTES_API_KEY=your_actual_api_key_here`
   - Replace `your_actual_api_key_here` with your real Chutes API key
3. Press `Ctrl + X` to exit
4. Press `Y` to save
5. Press `Enter` to confirm

**Example of what it should look like**:
```
CHUTES_API_KEY=sk-abc123xyz789...
```

---

## Step 6: Open the Firewall

Type these commands one at a time:

```bash
ufw allow 22/tcp
```

Press Enter, then:

```bash
ufw allow 8080/tcp
```

Press Enter, then:

```bash
ufw --force enable
```

**What this does**: Allows connections to your server on port 8080.

---

## Step 7: Create the Service File

Type this command:

```bash
cat > /etc/systemd/system/autoppia-api.service << 'EOF'
[Unit]
Description=Autoppia HTTP API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/autoppia-miner
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="PORT=8080"
ExecStart=/usr/bin/python3 /root/autoppia-miner/api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

**What this does**: Creates a service that will automatically start your API.

---

## Step 8: Start the Service

Type these commands one at a time:

```bash
systemctl daemon-reload
```

Press Enter, then:

```bash
systemctl enable autoppia-api
```

Press Enter, then:

```bash
systemctl start autoppia-api
```

**What this does**: Starts your API server.

---

## Step 9: Check if It's Working

Type this command:

```bash
systemctl status autoppia-api
```

**What to look for**: You should see `Active: active (running)` in green.

If you see that, press `Q` to exit.

---

## Step 10: Test the Endpoint

Type this command:

```bash
curl http://localhost:8080/health
```

**What you should see**: Something like `{"status":"healthy",...}`

If you see that, **it's working!** ✅

---

## Step 11: Configure DigitalOcean Firewall (IMPORTANT!)

**You need to do this in your web browser, not in the terminal:**

1. Go to: https://cloud.digitalocean.com/networking/firewalls
2. Click **"Create Firewall"** (or edit existing one)
3. Give it a name like "autoppia-api"
4. Under **"Inbound Rules"**, click **"Add Rule"**:
   - Type: `Custom`
   - Protocol: `TCP`
   - Port Range: `8080`
   - Sources: `All IPv4, All IPv6`
5. Also add SSH rule:
   - Type: `SSH`
   - Port: `22`
   - Sources: `All IPv4, All IPv6`
6. Under **"Outbound Rules"**, make sure it says "Allow All"
7. Click **"Create Firewall"**
8. On the next page, under **"Apply to Droplets"**, select your droplet (the one with IP 134.199.201.62)
9. Click **"Apply"**

**This is important!** Without this, the platform won't be able to connect to your server.

---

## Step 12: Test from Your Computer

**Now go back to your terminal on your computer** (not the server).

If you're still connected to the server, type `exit` to disconnect.

Then type this command:

```bash
curl http://134.199.201.62:8080/health
```

**What you should see**: `{"status":"healthy",...}`

If you see that, **everything is working!** ✅

---

## Step 13: Use in InfiniteWeb Arena

1. Go to: https://infinitewebarena.autoppia.com/
2. Click **"Benchmark Your Agent"** or **"Agent Run"**
3. When it asks for **"Agent Endpoint (IP:Port)"**, enter:
   ```
   134.199.201.62:8080
   ```
4. Click **"Run Benchmark"** or similar

---

## Troubleshooting

### "Connection refused" when testing

**Problem**: The firewall might not be configured.

**Solution**: 
1. Make sure you completed Step 11 (DigitalOcean Firewall)
2. Check if the service is running: `systemctl status autoppia-api`
3. Check if port is open: `ufw status` (should show 8080)

### "Permission denied" when SSH'ing

**Problem**: Wrong password or SSH key not set up.

**Solution**: 
- Make sure you're using the correct password
- Or set up SSH keys in DigitalOcean dashboard

### Service won't start

**Problem**: Missing API key or other configuration issue.

**Solution**:
1. Check logs: `journalctl -u autoppia-api -n 50`
2. Make sure `.env` file has your API key: `cat .env`
3. Check if Python is installed: `python3 --version`

### Can't find the .env file

**Problem**: You might be in the wrong directory.

**Solution**:
```bash
cd /root/autoppia-miner
ls -la .env
```

If it doesn't exist, create it:
```bash
cp env.example .env
nano .env
```

---

## Quick Reference Commands

**View logs**:
```bash
journalctl -u autoppia-api -f
```
(Press Ctrl+C to exit)

**Restart service**:
```bash
systemctl restart autoppia-api
```

**Check status**:
```bash
systemctl status autoppia-api
```

**Stop service**:
```bash
systemctl stop autoppia-api
```

**Start service**:
```bash
systemctl start autoppia-api
```

---

## Summary

✅ **Your endpoint**: `134.199.201.62:8080`

✅ **For InfiniteWeb Arena**: Use `134.199.201.62:8080`

✅ **Test it**: `curl http://134.199.201.62:8080/health`

If you get stuck on any step, let me know which step number and what error message you see!

