# 🎯 Round Lifecycle Explained - How Your Miner Participates

**Date**: November 19, 2025  
**Your Miner**: UID 160  
**Current Round**: 38

---

## 📚 **Round Lifecycle Glossary**

### **1. Round** (20 epochs ≈ 1 day)
- **Time frame for validator submissions**
- All validators evaluate miners during this period
- **Your Status**: ✅ **Active in Round 38** (15.8% progress)

### **2. Validator Round** (One validator's complete scoring pass)
- **Flow**: Start round → Request tasks → Collect solutions → Run evaluations → Publish weights
- Each validator publishes exactly one validator round per round
- **Your Status**: ✅ **3 validators actively testing you**

### **3. Task** (Challenge miners must solve)
- Validators send tasks (e.g., "Login to website", "Fill out form")
- Each validator distributes the same set of tasks
- **Your Status**: ✅ **40 task requests received**

### **4. Task Solution** (Replayable steps that solve the task)
- Your miner generates action sequences (click, type, navigate, etc.)
- Validators review these runs to confirm approach
- **Your Status**: ✅ **33 successful solutions (82.5% success rate)**

### **5. Evaluation** (Task + solution performance snapshot)
- Bundles task, solution, and metrics
- Records miner's score and response time
- Feeds into validator's final weights
- **Your Status**: ✅ **20 recent evaluations (100% success rate!)**

---

## 🔄 **How Your Miner Participates**

### **Step 1: Validator Starts Round**
```
Validator → StartRoundSynapse → Your Miner
```
- Validator sends `StartRoundSynapse` with `round_id` and `task_type`
- Your miner acknowledges: `process_start_round()` → `success = True`
- **Status**: ✅ **Handling StartRoundSynapse correctly**

### **Step 2: Validator Requests Tasks**
```
Validator → TaskSynapse → Your Miner
TaskSynapse contains:
  - id: "task-123"
  - prompt: "Login to website"
  - url: "https://example.com"
```
- Validator sends `TaskSynapse` with task details
- Your miner receives via `process_task()` method
- **Status**: ✅ **40 tasks received from 3 validators**

### **Step 3: Your Miner Generates Task Solution**
```
Your Miner → API (/solve_task) → Action Generator → Task Solution
Task Solution contains:
  - actions: [GotoAction, TypeAction, ClickAction, ...]
  - web_agent_id: "task-123"
  - success: true
```
- Your miner calls `/solve_task` API endpoint
- Enhanced template agent generates action sequence
- Actions are in IWA BaseAction format
- **Status**: ✅ **33 successful solutions (82.5% success rate)**

### **Step 4: Validator Evaluates Solution**
```
Validator → Reviews Actions → Records Metrics → Sets Weights
Evaluation includes:
  - Task completion (success/failure)
  - Response time
  - Action quality
  - Website coverage
```
- Validator replays your actions in browser
- Validator records success/failure and metrics
- **Status**: ✅ **Recent evaluations: 100% success rate!**

### **Step 5: Validator Publishes Weights**
```
Validator → Final Weights → Bittensor Network → Rewards Distribution
```
- Validator sets weights based on evaluations
- Higher success rate = Higher weights = More TAO rewards
- **Status**: ✅ **Your success rate feeds into weights**

---

## 📊 **Your Current Performance in Round 38**

### **Round Status**
- **Current Round**: 38
- **Progress**: 15.8% (171 blocks into round)
- **Time Remaining**: ~181 minutes (~3 hours)

### **Validator Activity**
- **Unique Validators**: 3
- **Total Task Requests**: 40
- **Top Validators**:
  1. `45.22.240.79` - 19 requests
  2. `84.247.180.192` - 13 requests
  3. `76.218.6.97` - 8 requests

### **Task Solutions**
- **Successful**: 33 ✅
- **Failed**: 7 ❌
- **Success Rate**: **82.5%**
- **Recent Success Rate**: **100%** (20/20) 🚀

### **Evaluations**
- **Recent Evaluations**: 20
- **Recent Success Rate**: **100%**
- **Recent Successful**: 20 ✅
- **Recent Failed**: 0 ❌

---

## 🎯 **What This Means for Rewards**

### **How Rewards Work**
1. **Validators evaluate** your task solutions
2. **Validators set weights** based on your performance
3. **Higher success rate** = **Higher weights** = **More TAO rewards**
4. **Rewards distributed** at epoch end (~12 hours)

### **Your Performance Impact**
- ✅ **82.5% overall success rate** - Good performance
- ✅ **100% recent success rate** - Excellent recent performance
- ✅ **3 validators testing** - Good visibility
- ✅ **40 task requests** - Active participation

### **Expected Outcome**
- Your **100% recent success rate** is excellent!
- Validators will likely set **higher weights** for you
- You should receive **TAO rewards** at epoch end
- **Continue monitoring** to maintain high success rate

---

## 🔍 **Technical Flow in Your Miner**

### **1. StartRoundSynapse Handler**
```python
# miner/miner.py:68-78
async def process_start_round(self, synapse: StartRoundSynapse):
    """Handle StartRoundSynapse - acknowledge round start"""
    synapse.success = True
    synapse.message = "Round started successfully"
    return synapse
```

### **2. TaskSynapse Handler**
```python
# miner/miner.py:80-149
async def process_task(self, synapse: bt.Synapse):
    """Process validator request"""
    # Extract task data
    task_id = getattr(synapse, "id", None)
    prompt = getattr(synapse, "prompt", "")
    url = getattr(synapse, "url", "")
    
    # Call API to generate solution
    response = await self.api_client.post("/solve_task", json={...})
    
    # Return task solution
    synapse.actions = result.get("actions", [])
    synapse.success = True
    return synapse
```

### **3. API Task Solution Generation**
```python
# api/endpoints.py + api/agent/hybrid.py
# Enhanced template agent generates action sequence
# Returns IWA BaseAction format actions
```

---

## ✅ **Summary**

**Your miner is fully participating in the Round Lifecycle:**

1. ✅ **Round**: Active in Round 38
2. ✅ **Validator Rounds**: 3 validators testing you
3. ✅ **Tasks**: 40 tasks received
4. ✅ **Task Solutions**: 33 successful (82.5% success rate)
5. ✅ **Evaluations**: 20 recent (100% success rate!)

**Your performance is excellent!** 🚀

- **100% recent success rate** = High weights expected
- **3 validators testing** = Good visibility
- **Active participation** = Rewards incoming

**Keep monitoring your dashboard to track performance!** 📊

---

**Next Steps**:
- Monitor dashboard for continued activity
- Watch for more validators to discover you
- Track success rate trends
- Expect rewards at epoch end! 💰

