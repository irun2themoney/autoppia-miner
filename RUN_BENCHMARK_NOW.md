# 🚀 Run Official Benchmark - Step by Step Guide

## ✅ Pre-Flight Check

**Your API Status**: ✅ Running on `localhost:8080`

**Important**: The playground needs a **publicly accessible** endpoint. You have two options:

### Option 1: Use Your Production Server (Recommended)
- **Endpoint**: `134.199.203.133:8443` (HTTPS)
- This is your production server endpoint
- Already configured and ready

### Option 2: Use Local Development (For Testing)
- You'll need to expose your local API publicly
- Use a tunnel service (ngrok, cloudflared, etc.)

---

## 📋 Step-by-Step Instructions

### **Step 1: Open the Playground**
👉 **Go to**: https://infinitewebarena.autoppia.com/playground

### **Step 2: Configure the Benchmark**

#### **2.1 Select Web Projects** ⭐ REQUIRED
- Click **"Select projects..."** button
- Choose: **"Autoppia Work"** (contains BOOK_A_CONSULTATION)
- Or select **all projects** for comprehensive testing

#### **2.2 Select Use Cases** ⭐ REQUIRED
- Click **"Select use cases..."** button
- Choose: **"BOOK_A_CONSULTATION"**
- Or select **all use cases** for full coverage

#### **2.3 Number of Runs** ⭐ REQUIRED
- Enter: **5** (for quick test)
- Or **10-20** (for comprehensive test)
- More runs = more accurate results but takes longer

#### **2.4 Agent Endpoint (IP:Port)** ⭐ REQUIRED
- **If using production server**: Enter `134.199.203.133:8443`
- **Format**: `ip:port` (NO `https://` prefix)
- The playground will add `https://` automatically

### **Step 3: Run the Benchmark**
- Click the **"Run Benchmark"** button
- **⚠️ IMPORTANT**: Keep the browser tab open - don't close it!
- Wait for completion (typically 5-10 minutes for 5 runs)

### **Step 4: Monitor Progress**

**Open Dashboard** (in another browser tab):
```
http://134.199.203.133:8080/dashboard
```

**Watch for**:
- ✅ Total requests increasing
- ✅ Success rate updating
- ✅ Response times
- ✅ Any errors in the logs

### **Step 5: Check Results**

**In Playground**:
- Success rate should be > 0% (ideally > 50%)
- Actions should be generated for each task
- Tasks should complete successfully

**In Dashboard**:
- Check total requests count
- Verify success rate
- Look for any error patterns

---

## 🎯 Expected Results

### **Success Indicators**:
- ✅ Success rate > 0% (ideally > 50%)
- ✅ Actions generated for each task (non-empty)
- ✅ Response times < 90 seconds
- ✅ Tasks complete successfully (not all failed)

### **If Tasks Fail**:
1. Check dashboard for errors
2. Verify API is accessible from the internet
3. Check response format matches IWA spec
4. Verify CORS is enabled (should be already)

---

## 🔍 Troubleshooting

### **"Failed to fetch" Error**
- Verify your API is publicly accessible
- Check firewall allows port 8443 (HTTPS) or 8080 (HTTP)
- Test endpoint manually: `curl https://134.199.203.133:8443/health`

### **Empty Actions**
- Check API logs for errors
- Verify task format is correct
- Test endpoint directly with a sample task

### **Timeout Errors**
- Response time should be < 90 seconds
- Check if API is overloaded
- Verify network connectivity

---

## 📊 What Gets Tested

The playground will test:
- ✅ Task completion accuracy
- ✅ Action quality and correctness
- ✅ Response time
- ✅ Website coverage
- ✅ Multi-step task handling
- ✅ Error recovery

---

## ✅ Ready to Go!

1. ✅ **API is ready** - All optimizations applied
2. 🎯 **Go to playground** - https://infinitewebarena.autoppia.com/playground
3. 📋 **Configure** - Follow steps above
4. ▶️ **Run** - Click "Run Benchmark"
5. 📊 **Monitor** - Watch dashboard for results

**Good luck! 🚀**

