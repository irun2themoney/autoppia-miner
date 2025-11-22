# 🧪 Quick Benchmark Test Steps

## ✅ **Step 1: Verify API is Running**

Open your browser and go to:
```
http://134.199.203.133:8080/health
```

**Expected**: Should show `{"status":"healthy",...}`

If it doesn't load, your API might be down. Check with:
```bash
ssh root@134.199.203.133 "systemctl status autoppia-api"
```

---

## 🎯 **Step 2: Test on IWA Playground**

### **2.1. Open Playground**
1. Go to: **https://infinitewebarena.autoppia.com/playground**
2. Wait for page to load

### **2.2. Enter Your Endpoint**
In the "API Endpoint" or "Agent URL" field, enter:
```
134.199.203.133:8080
```

**Note**: Some versions might need the full URL:
```
http://134.199.203.133:8080
```

### **2.3. Run Benchmark**
1. Click **"Run Benchmark"** or **"Start Test"** button
2. **Keep this tab open** - don't close it
3. Wait for benchmark to complete (may take 5-10 minutes)

---

## 📊 **Step 3: Monitor in Real-Time**

### **Option A: Watch Dashboard** (Easiest)
Open in another tab:
```
http://134.199.203.133:8080/dashboard
```

Watch for:
- ✅ Total requests increasing
- ✅ Success rate updating
- ✅ New validator interactions

### **Option B: Watch Logs** (More Detailed)
Open a terminal and run:
```bash
ssh root@134.199.203.133
journalctl -u autoppia-api -f | grep solve_task
```

You should see requests coming in as the benchmark runs.

---

## ✅ **Step 4: Check Results**

### **In Playground**:
- Look for success rate (should be > 50%)
- Check if tasks completed
- Note any errors

### **In Dashboard**:
- Check total requests increased
- Verify success rate
- Look for any errors

---

## 🎯 **Step 5: Verify R/T/I Scores**

**Wait 1-2 hours** after benchmark completes, then:

### **Check Dashboard**:
Go to: `http://134.199.203.133:8080/dashboard`

Look at "Wallet" section:
- **Rank**: Should be > 0 (if benchmark passed)
- **Trust**: Should be > 0
- **Incentive**: Should be > 0

### **If Still 0**:
- Benchmark may not have passed
- Wait longer (scores update periodically)
- Check with Dr. Riiveer on Discord

---

## ❌ **Troubleshooting**

### **API Not Loading?**
```bash
# Check if API is running
ssh root@134.199.203.133 "systemctl status autoppia-api"

# Restart if needed
ssh root@134.199.203.133 "systemctl restart autoppia-api"
```

### **Playground Shows Error?**
- Check browser console (F12) for errors
- Verify API endpoint is correct
- Make sure API is accessible from internet

### **Benchmark Times Out?**
- Check API response times in logs
- Verify timeout is set to 90s
- Check server resources

---

## 🚀 **Ready to Test?**

1. ✅ Verify API is accessible: `http://134.199.203.133:8080/health`
2. ✅ Open playground: `https://infinitewebarena.autoppia.com/playground`
3. ✅ Enter endpoint: `134.199.203.133:8080`
4. ✅ Click "Run Benchmark"
5. ✅ Monitor dashboard/logs
6. ✅ Wait for results
7. ✅ Check R/T/I scores in 1-2 hours

---

**Let me know when you're ready and I'll help monitor the results!**

