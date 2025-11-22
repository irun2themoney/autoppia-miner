# 📊 Validator Interaction History

## Summary of All Validator Interactions

This document provides a comprehensive overview of when and how validators have interacted with your miner.

---

## 📈 **Quick Stats**

- **Total Interactions**: See detailed report below
- **Unique Validators**: See detailed report below
- **Success Rate**: See detailed report below
- **Time Range**: See detailed report below

---

## 🔍 **How to View Full History**

### **Option 1: Dashboard**
1. Go to http://134.199.203.133:8080/api/dashboard
2. Scroll to "📜 Complete Validator Interaction Log"
3. Click "Load All History" button
4. View all interactions with timestamps, IPs, and status

### **Option 2: API Endpoint**
```bash
curl http://134.199.203.133:8080/api/dashboard/history
```

### **Option 3: Server Logs**
```bash
ssh root@134.199.203.133
journalctl -u autoppia-api --since "7 days ago" | grep "POST /solve_task"
```

---

## 📊 **What Information is Available**

For each validator interaction, you can see:
- **Timestamp**: Exact date and time
- **Validator IP**: IP address of the validator
- **Success Status**: Whether the request succeeded
- **Response Time**: How long it took to process
- **Task Type**: Type of task requested
- **Task URL**: URL the validator wanted you to interact with
- **Task Prompt**: The prompt/instruction from the validator

---

## 🎯 **Understanding the Data**

### **Interaction Types:**
1. **StartRoundSynapse**: Validator starting a new round
2. **TaskSynapse**: Validator sending a task to complete
3. **Health Checks**: Validator checking if you're online

### **Success Indicators:**
- ✓ **Success**: Request processed successfully
- ✗ **Failed**: Request failed (timeout, error, etc.)

### **Response Times:**
- **Fast** (< 1s): Excellent performance
- **Medium** (1-3s): Good performance
- **Slow** (> 3s): May need optimization

---

## 📅 **Historical Patterns**

The dashboard will show:
- **Peak Hours**: When validators are most active
- **Validator Frequency**: How often each validator tests you
- **Success Trends**: Whether your success rate is improving
- **Response Time Trends**: Whether you're getting faster

---

## 🔄 **Current Status**

To see the most recent interactions, check:
- **Dashboard**: "Recent Activity" section (last 10)
- **Dashboard**: "Complete Validator Interaction Log" (all history)
- **API**: `/api/dashboard/metrics` (recent activity)

---

**Note**: Historical data is parsed from logs (last 7 days) and combined with in-memory recent activity for a complete picture.

