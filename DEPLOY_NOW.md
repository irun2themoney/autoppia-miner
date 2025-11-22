# 🚀 DEPLOY NOW - Manual Steps

**Code is committed and pushed!** ✅

---

## 📋 Manual Deployment Steps

### **Step 1: SSH to Server**
```bash
ssh root@134.199.203.133
# Password: DigitalOcean4life
```

### **Step 2: Update Code**
```bash
cd /opt/autoppia-miner
git pull
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Restart API**
```bash
systemctl restart autoppia-api
```

### **Step 5: Verify**
```bash
# Check service status
systemctl status autoppia-api

# Test endpoint
curl -k -X POST https://134.199.203.133:8443/solve_task \
  -H "Content-Type: application/json" \
  -d '{"id":"test","prompt":"click button","url":""}'
```

---

## ✅ Expected Result

After deployment, the endpoint should return:
```json
{
  "actions": [...],  // Non-empty array
  "web_agent_id": "test",
  "recording": ""
}
```

---

## 🧪 Test on Playground

1. Go to: https://infinitewebarena.autoppia.com
2. Click: "Test Your Agent"
3. Enter: `https://134.199.203.133:8443/solve_task`
4. Run benchmark

**Expected**: Actions should now be non-empty!

