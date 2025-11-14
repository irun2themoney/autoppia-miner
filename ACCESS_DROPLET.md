# 🔧 Accessing Your DigitalOcean Droplet

## Problem: Console Not Loading

The DigitalOcean web console is often unreliable. **SSH is the recommended and most reliable method.**

---

## ✅ Solution 1: SSH Access (Recommended)

### From Your Local Machine:

```bash
# Basic SSH connection
ssh root@134.199.201.62

# If you have SSH keys set up
ssh -i ~/.ssh/your_key root@134.199.201.62

# If using password authentication
ssh root@134.199.201.62
# Then enter your password when prompted
```

### Troubleshooting SSH:

**If SSH doesn't work, try:**

```bash
# Check if droplet is online
ping 134.199.201.62

# Check SSH port (should be 22)
nc -zv 134.199.201.62 22

# Verbose SSH (shows what's happening)
ssh -v root@134.199.201.62
```

---

## ✅ Solution 2: Fix Console Access

### Option A: Try Different Browser
- Use Chrome, Firefox, or Safari
- Clear browser cache
- Try incognito/private mode

### Option B: Check DigitalOcean Status
1. Go to: https://status.digitalocean.com
2. Check if there are any console issues

### Option C: Reset Console Access
1. Go to DigitalOcean Dashboard
2. Click on your droplet
3. Click "Access" → "Reset Console"
4. Wait 1-2 minutes
5. Try console again

---

## ✅ Solution 3: Verify Droplet Status

### Check if Droplet is Running:

```bash
# From your local machine, check if droplet responds
curl -I http://134.199.201.62:8080/health

# Or ping it
ping -c 4 134.199.201.62
```

### Check via DigitalOcean API:

```bash
# If you have doctl installed
doctl compute droplet list

# Or check in web dashboard:
# https://cloud.digitalocean.com/droplets
```

---

## ✅ Solution 4: Alternative Access Methods

### If SSH Keys Don't Work:

1. **Reset Root Password** (via DigitalOcean Dashboard):
   - Go to your droplet
   - Click "Access" → "Reset Root Password"
   - Check email for new password
   - Use password to SSH: `ssh root@134.199.201.62`

2. **Use DigitalOcean Recovery Console**:
   - Go to droplet → "Recovery" tab
   - Boot from recovery ISO
   - Access via console

3. **Reboot Droplet** (via Dashboard):
   - Sometimes a reboot fixes console issues
   - Dashboard → Droplet → "Power" → "Reboot"

---

## 🔍 Quick Diagnostics

### Test if Services are Running (from outside):

```bash
# Test API
curl http://134.199.201.62:8080/health

# Test if ports are open
nc -zv 134.199.201.62 8080  # API
nc -zv 134.199.201.62 8091  # Miner axon
nc -zv 134.199.201.62 22    # SSH
```

---

## 🚨 If Nothing Works

### Last Resort Options:

1. **Power Cycle Droplet**:
   - Dashboard → Droplet → "Power" → "Power Off"
   - Wait 30 seconds
   - "Power" → "Power On"
   - Wait 2-3 minutes for boot
   - Try SSH again

2. **Contact DigitalOcean Support**:
   - They can help with console/access issues
   - Support is usually responsive

3. **Create New Droplet** (if critical):
   - Export your configuration
   - Create new droplet
   - Restore from backup/config

---

## 📝 Quick SSH Setup (If Needed)

### Generate SSH Key (if you don't have one):

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key to clipboard (Mac)
pbcopy < ~/.ssh/id_ed25519.pub

# Or view it
cat ~/.ssh/id_ed25519.pub
```

### Add SSH Key to DigitalOcean:

1. Go to: https://cloud.digitalocean.com/account/security
2. Click "Add SSH Key"
3. Paste your public key
4. Name it (e.g., "My Mac")
5. Save

### Add Key to Existing Droplet:

1. Dashboard → Droplet → "Settings" → "Resize/Droplet Settings"
2. Or use `doctl`:
   ```bash
   doctl compute ssh-key list
   doctl compute droplet create --ssh-keys YOUR_KEY_ID ...
   ```

---

## ✅ Once You're In (via SSH)

### Quick Commands to Run:

```bash
# Check API status
systemctl status autoppia-api

# Check miner status
systemctl status autoppia-miner

# View API logs
journalctl -u autoppia-api -n 50

# View miner logs
journalctl -u autoppia-miner -n 50

# Test API locally
curl http://localhost:8080/health

# Check if services are running
ps aux | grep -E "api.py|miner.py"
```

---

## 🎯 Most Likely Solution

**99% of the time, SSH works when console doesn't:**

```bash
ssh root@134.199.201.62
```

If you get "Connection refused" or timeout:
- Check firewall rules
- Verify droplet is running
- Check your local network/firewall

If you get "Permission denied":
- You need the root password or SSH key
- Reset password via DigitalOcean dashboard

---

**Need help?** Share the error message you get when trying to SSH, and I can help troubleshoot further!

