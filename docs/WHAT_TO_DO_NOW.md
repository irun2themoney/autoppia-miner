# 🎯 What To Do Now - Active Monitoring Guide

**Date**: November 19, 2025  
**Your Status**: ✅ Fully deployed and ready

---

## ⏰ **Timeline - What to Expect**

### **NOT Weeks - Hours to Days!**

**Discovery**: 15-30 minutes (validators find you)  
**First Tests**: 30-60 minutes (validators start testing)  
**First Rewards**: ~12 hours (after first epoch you're tested in)  
**Regular Rewards**: Every ~12 hours (2x per day)

---

## 📊 **What You Should Do RIGHT NOW**

### **1. Monitor Your Dashboard** (Every Few Hours)
**URL**: `http://134.199.203.133:8080/api/dashboard`

**What to Watch For**:
- ✅ **Total Requests** increasing (means validators are testing you)
- ✅ **Recent Activity** showing validator IPs (not localhost)
- ✅ **Success Rate** (aim for 80%+)
- ✅ **Health Score** (aim for 70%+)
- ✅ **Current Round** and countdown timer

**Check**: Every 2-4 hours for the first day, then daily

---

### **2. Monitor Validator Activity** (Real-Time)
```bash
# Watch for validator requests in real-time
ssh root@134.199.203.133 "journalctl -u autoppia-api -f | grep 'POST.*solve_task'"

# Check recent validator activity (last 30 minutes)
ssh root@134.199.203.133 "journalctl -u autoppia-api --since '30 minutes ago' | grep -E 'POST.*solve_task|INFO.*:\d+:\d+' | tail -30"
```

**What to Look For**:
- ✅ Requests from external IPs (not 127.0.0.1)
- ✅ Status code 200 (successful)
- ✅ Validator IPs (e.g., 45.22.240.79, 84.247.180.192)

---

### **3. Check IWA Platform** (Daily)
**URL**: `https://infinitewebarena.autoppia.com/subnet36/overview`

**What to Check**:
- ✅ Your UID (160) appearing in rounds
- ✅ Your scores in each round
- ✅ Your rank compared to other miners
- ✅ Task completion rates

**Check**: Once per day

---

### **4. Monitor Your Wallet** (After First Epoch)
```bash
# Check wallet balance
btcli wallet balance --wallet.name default

# Check your incentive score
python3 -c "
import bittensor as bt
subtensor = bt.subtensor(network='finney')
metagraph = subtensor.metagraph(netuid=36)
wallet = bt.wallet(name='default', hotkey='default')
uid = metagraph.hotkeys.index(wallet.hotkey.ss58_address)
incentive = metagraph.I[uid].item()
rank = metagraph.R[uid].item()
trust = metagraph.T[uid].item()
print(f'UID: {uid}')
print(f'Incentive: {incentive:.6f}')
print(f'Rank: {rank:.2f}')
print(f'Trust: {trust:.6f}')
"
```

**Check**: After first epoch (~12 hours), then daily

---

## 🎯 **Expected Timeline**

### **Today (Day 1)**
- **0-30 min**: Validators discover you
- **30-60 min**: First test requests arrive
- **Rest of day**: Regular testing begins
- **End of day**: Check dashboard for activity

### **Tomorrow (Day 2)**
- **Morning**: Check for first rewards (if tested in epoch 1)
- **Throughout day**: Monitor success rates
- **Evening**: Review performance metrics

### **This Week**
- **Daily**: Check dashboard and wallet
- **Every 2-3 days**: Review IWA Platform rankings
- **End of week**: Analyze performance trends

### **Ongoing**
- **Daily**: Quick dashboard check (5 minutes)
- **Weekly**: Full performance review
- **Monthly**: Optimize based on data

---

## 📈 **Success Indicators**

### **✅ Good Signs**
- ✅ Validator requests coming in regularly
- ✅ Success rate 80%+
- ✅ Response times < 1s
- ✅ Health score 70%+
- ✅ Multiple validators testing you
- ✅ Wallet balance increasing

### **⚠️ Warning Signs**
- ⚠️ No validator activity for 24h+ (check stake/rank)
- ⚠️ Success rate < 50% (need optimization)
- ⚠️ Response times > 2s (performance issue)
- ⚠️ High error rates (>10%) (need debugging)

---

## 🚀 **Proactive Steps You Can Take**

### **1. Optimize Based on Data** (After First Week)
- Review which task types you're failing
- Optimize selectors for common failures
- Improve action sequences based on feedback
- Adjust wait times if needed

### **2. Monitor Competition** (Weekly)
- Check top miners on IWA Platform
- Learn from their strategies
- Identify areas for improvement

### **3. Reinvest Rewards** (As You Earn)
- Stake earned TAO back into miner
- Higher stake = More testing = More rewards
- Create positive feedback loop

### **4. Stay Updated** (Ongoing)
- Monitor Autoppia Discord for updates
- Check official documentation changes
- Your self-learning system helps with this!

---

## 💰 **Reward Expectations**

### **With 71 TAO Stake**:
- **Testing Frequency**: 60-80% of rounds
- **First Payout**: ~12 hours after first epoch you're tested in
- **Ongoing Payouts**: Every ~12 hours (2x per day)
- **Amount**: Depends on performance and network emission

### **Realistic Timeline**:
- **Day 1**: Get tested, accumulate scores
- **Day 2**: First rewards (if tested in epoch 1)
- **Week 1**: Regular rewards, establish baseline
- **Month 1**: Optimize based on data, grow stake

---

## 📊 **Monitoring Checklist**

### **Daily (5 minutes)**
- [ ] Check dashboard: `http://134.199.203.133:8080/api/dashboard`
- [ ] Verify services are running
- [ ] Check for new validator activity

### **Weekly (30 minutes)**
- [ ] Review IWA Platform rankings
- [ ] Analyze success rates and trends
- [ ] Check wallet balance and incentive
- [ ] Review error logs for issues

### **Monthly (1 hour)**
- [ ] Full performance analysis
- [ ] Compare with top miners
- [ ] Plan optimizations
- [ ] Reinvest rewards

---

## 🎯 **Bottom Line**

**You DON'T need to wait weeks!**

**What to do**:
1. ✅ **Monitor dashboard** (every few hours first day, then daily)
2. ✅ **Check for validator activity** (should start within 30-60 minutes)
3. ✅ **Watch for first rewards** (after first epoch, ~12 hours)
4. ✅ **Optimize based on data** (after first week)

**Timeline**:
- **Hours**: Validators discover and test you
- **Days**: First rewards arrive
- **Weeks**: Optimize and grow

**Your miner is ready - just monitor and let it work!** 🚀

---

## 🔗 **Quick Links**

- **Dashboard**: `http://134.199.203.133:8080/api/dashboard`
- **IWA Platform**: `https://infinitewebarena.autoppia.com/subnet36/overview`
- **Health Check**: `http://134.199.203.133:8080/health`
- **Metrics API**: `http://134.199.203.133:8080/api/dashboard/metrics`

---

**Next Steps**: Check your dashboard now and monitor for validator activity! 🎉

