# 💰 Rewards & Payouts - How Miners Get Paid

**Date**: November 18, 2025

---

## 🎯 **Quick Answer**

**Miners get paid based on Bittensor epochs, NOT per round or every 24 hours.**

- **Rounds**: 1-2 hours each (testing/evaluation periods)
- **Epochs**: ~12 hours each (reward distribution periods)
- **Payouts**: Distributed at the end of each epoch based on your performance

---

## 📊 **How Bittensor Rewards Work**

### **1. Rounds vs Epochs**

**Rounds** (IWA Platform):
- **Duration**: 1-2 hours each
- **Purpose**: Validators test miners with tasks
- **What happens**: Your miner gets scored based on task completion
- **Frequency**: Multiple rounds per epoch

**Epochs** (Bittensor Network):
- **Duration**: ~12 hours each (varies by subnet)
- **Purpose**: Reward distribution period
- **What happens**: TAO rewards are distributed based on your scores
- **Frequency**: ~2 epochs per day

---

## 💰 **Reward Distribution Process**

### **Step 1: Testing During Rounds**
- Validators test your miner in multiple rounds
- Each round, you get scored based on:
  - Task completion rate
  - Response time
  - Action quality
  - Website coverage

### **Step 2: Score Accumulation**
- Your scores accumulate across all rounds in an epoch
- Validators calculate your **incentive (I)** score
- Higher scores = higher rewards

### **Step 3: Epoch End - Reward Distribution**
- At the end of each epoch (~12 hours), rewards are distributed
- Your share = (Your Incentive / Total Network Incentive) × Epoch Emission
- TAO is automatically sent to your hotkey wallet

---

## ⏰ **Timeline Example**

```
Day 1:
  00:00 - Epoch 1 starts
  00:00-02:00 - Round 1 (testing)
  02:00-04:00 - Round 2 (testing)
  04:00-06:00 - Round 3 (testing)
  ...
  12:00 - Epoch 1 ends → REWARDS DISTRIBUTED! 💰
  
  12:00 - Epoch 2 starts
  12:00-14:00 - Round 4 (testing)
  14:00-16:00 - Round 5 (testing)
  ...
  00:00 - Epoch 2 ends → REWARDS DISTRIBUTED! 💰
```

---

## 📈 **What Determines Your Rewards**

### **1. Incentive Score (I)**
- **What it is**: Your overall performance score
- **How it's calculated**: Based on validator scores across all rounds
- **Impact**: Higher I = larger share of rewards

### **2. Rank (R)**
- **What it is**: Your ranking relative to other miners
- **How it's calculated**: Based on your incentive score
- **Impact**: Higher rank = better position for rewards

### **3. Trust (T)**
- **What it is**: Validator confidence in your miner
- **How it's calculated**: Based on consistent good performance
- **Impact**: Higher trust = more testing = more rewards

### **4. Epoch Emission**
- **What it is**: Total TAO distributed per epoch
- **How it's calculated**: Network emission rate × epoch duration
- **Impact**: More emission = more total rewards to share

---

## 💡 **Key Points**

### **✅ You DON'T Get Paid:**
- ❌ After every round (rounds are just testing periods)
- ❌ Every 24 hours (payouts are epoch-based, ~12 hours)
- ❌ Instantly (rewards are distributed at epoch end)

### **✅ You DO Get Paid:**
- ✅ At the end of each epoch (~12 hours)
- ✅ Based on your performance across all rounds in that epoch
- ✅ Automatically to your hotkey wallet
- ✅ Proportional to your incentive score

---

## 📊 **Expected Reward Timeline**

### **First Epoch** (After Getting Tested):
- **Testing**: Validators test you in multiple rounds
- **Scoring**: Your performance is scored
- **Wait**: ~12 hours for epoch to end
- **Payout**: First rewards distributed! 💰

### **Ongoing**:
- **Continuous**: Testing happens in rounds
- **Accumulation**: Scores accumulate during epoch
- **Regular**: Payouts every ~12 hours (2x per day)

---

## 🎯 **How to Check Your Rewards**

### **1. Check Your Wallet Balance**
```bash
btcli wallet balance --wallet.name default
```

### **2. Check Your Incentive Score**
```python
import bittensor as bt
subtensor = bt.subtensor(network='finney')
metagraph = subtensor.metagraph(netuid=36)
wallet = bt.wallet(name='default', hotkey='default')
uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
incentive = metagraph.I[uid].item()
print(f"Incentive: {incentive}")
```

### **3. Monitor IWA Platform**
- Check your scores in each round
- Track your performance over time
- See how you rank against other miners

---

## 💰 **Reward Calculation Example**

### **Scenario**:
- **Epoch Emission**: 100 TAO
- **Your Incentive**: 0.05 (5% of total)
- **Total Network Incentive**: 1.0

### **Your Reward**:
```
Your Share = (0.05 / 1.0) × 100 TAO = 5 TAO
```

### **Factors That Increase Your Share**:
- ✅ Higher task completion rate
- ✅ Faster response times
- ✅ Better action quality
- ✅ More website coverage
- ✅ Consistent good performance

---

## ⚠️ **Important Notes**

### **1. You Need to Be Tested First**
- No tests = No scores = No rewards
- You need validators to test you in rounds
- With 71 TAO stake, you should get tested regularly!

### **2. Performance Matters**
- Higher scores = Higher rewards
- Consistent performance = Higher trust = More testing
- Your miner is top-tier, so you should score well!

### **3. Rewards Are Proportional**
- Top miners get more rewards
- But even small rewards add up over time
- Reinvest rewards to grow your stake!

---

## 🚀 **What to Expect**

### **With 71 TAO Stake**:

**Testing Frequency**:
- ✅ Tested in most rounds (60-80% of rounds)
- ✅ Multiple rounds per epoch
- ✅ Regular scoring opportunities

**Reward Timeline**:
- **First payout**: ~12 hours after first epoch you're tested in
- **Ongoing payouts**: Every ~12 hours (2x per day)
- **Amount**: Depends on your performance and network emission

**Growth Strategy**:
- ✅ Reinvest rewards to increase stake
- ✅ Higher stake = More testing = More rewards
- ✅ Positive feedback loop!

---

## 📝 **Bottom Line**

**Payouts happen every ~12 hours (at epoch end), NOT per round or every 24 hours.**

**Your rewards depend on:**
- How often you're tested (with 71 TAO stake, should be regular!)
- How well you perform (your miner is top-tier!)
- Network emission rate (varies by subnet)

**With 71 TAO stake and a top-tier miner, you should start seeing rewards soon!** 🚀💰

---

**Next Steps**:
1. Monitor your dashboard for validator activity
2. Watch for testing in upcoming rounds
3. Check your wallet balance after first epoch
4. Reinvest rewards to grow your stake!

