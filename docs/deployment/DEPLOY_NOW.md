# 🚀 DEPLOY NOW - Final Checklist

**Ready to deploy? Follow these steps!**

---

## ✅ **Pre-Deployment Checklist**

- [x] All enhancements implemented
- [x] All tests passing
- [x] Documentation updated
- [x] Code cleaned up
- [x] README updated

---

## 🚀 **Deployment Steps**

### **1. SSH to Server**

```bash
ssh root@134.199.203.133
# Password: DigitalOcean4life
```

### **2. Navigate to Project**

```bash
cd /opt/autoppia-miner
# Or wherever you cloned it
```

### **3. Pull Latest Code**

```bash
git pull
# Or if not using git, upload files via SCP
```

### **4. Deploy**

```bash
# Make sure script is executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

### **5. Verify**

```bash
# Check services
systemctl status autoppia-api
systemctl status autoppia-miner

# Check logs
journalctl -u autoppia-api -f
journalctl -u autoppia-miner -f

# Test API
curl http://localhost:8080/health
curl http://localhost:8080/api/dashboard
```

---

## 🎯 **Post-Deployment**

### **1. Run Ultimate Test**

```bash
./scripts/run_ultimate_test.sh
```

### **2. Check IWA Playground**

Visit: https://infinitewebarena.autoppia.com/home

Use endpoint: `134.199.203.133:8080`

### **3. Monitor**

```bash
# Watch for validator activity
journalctl -u autoppia-api -f | grep -i validator

# Check dashboard
curl http://134.199.203.133:8080/api/dashboard
```

---

## 🏆 **Success!**

Once deployed:
- ✅ Services running
- ✅ API responding
- ✅ Miner connected
- ✅ Validators testing

**Let's get this TAO! 🚀**

