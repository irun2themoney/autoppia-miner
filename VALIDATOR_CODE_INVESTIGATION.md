# 🔍 Validator Code Investigation Plan

## Goal
Find the Autoppia Subnet 36 validator code to understand:
1. Validator selection criteria (min_last_update, active_status requirements)
2. Pruning logic (what triggers Active Status = 0)
3. Query selection algorithm (why miners are skipped)

---

## 🎯 Search Strategy

### 1. GitHub Repository Search

**Search Terms**:
- `autoppia subnet 36 validator`
- `bittensor subnet 36 autoppia`
- `infinite web arena validator`
- `subnet36 validator github`

**Likely Repository Names**:
- `autoppia-validator`
- `subnet-36-validator`
- `bittensor-subnet-36`
- `autoppia-subnet`

### 2. Key Files to Find

**Validator Selection Logic**:
- `validator/forward.py` - Main validator loop
- `validator/utils.py` - Selection utilities
- `validator/selection.py` - Miner selection algorithm
- `validator/query.py` - Query distribution logic

**Pruning Logic**:
- `validator/pruning.py` - Pruning criteria
- `validator/active_status.py` - Active status calculation
- `validator/scoring.py` - Miner scoring system

**Configuration**:
- `config.py` - Validator configuration
- `constants.py` - Network constants (min_last_update, etc.)

---

## 🔎 What to Look For

### Critical Variables

**Last Update Threshold**:
```python
# Look for variables like:
min_last_update = 360  # blocks
max_block_age = 7200  # blocks
stale_threshold = 1000  # blocks
```

**Active Status Requirements**:
```python
# Look for checks like:
if miner.active == 0:
    skip_miner()
    
if miner.last_update < current_block - min_last_update:
    skip_miner()
```

**Selection Criteria**:
```python
# Look for filtering logic:
def select_miners(miners):
    filtered = [
        m for m in miners 
        if m.active == 1 
        and m.last_update > current_block - min_last_update
        and m.stake > min_stake
    ]
    return filtered
```

### Key Functions to Find

1. **`select_miners()`** or **`get_query_set()`**
   - How validators choose which miners to query
   - What filters are applied
   - What thresholds exist

2. **`calculate_active_status()`** or **`update_active_status()`**
   - How Active Status is determined
   - What triggers Active Status = 0
   - What's needed for Active Status = 1

3. **`should_prune()`** or **`is_prunable()`**
   - Pruning criteria
   - When miners are marked for pruning
   - How to avoid pruning

---

## 📋 Investigation Checklist

### Step 1: Find Repository
- [ ] Search GitHub for Autoppia validator code
- [ ] Check Bittensor official repositories
- [ ] Look for Subnet 36 specific repos
- [ ] Check if code is public or private

### Step 2: Analyze Selection Logic
- [ ] Find miner selection function
- [ ] Identify min_last_update threshold
- [ ] Check active_status requirements
- [ ] Understand pruning criteria

### Step 3: Document Findings
- [ ] Document exact thresholds found
- [ ] Note any workarounds or exceptions
- [ ] Identify what's needed to break cycle
- [ ] Create action plan based on findings

---

## 🎯 Expected Findings

### Likely Scenarios

**Scenario 1: Strict Last Update Requirement**
```python
# Validators skip miners with old last_update
if miner.last_update < current_block - 3600:  # ~12 hours
    skip_miner()
```
**Solution**: Need recent successful response to update last_update

**Scenario 2: Active Status Filter**
```python
# Only query active miners
if miner.active == 0:
    skip_miner()
```
**Solution**: Need to get Active Status = 1 first (chicken-and-egg)

**Scenario 3: Combined Criteria**
```python
# Both active status AND recent update required
if miner.active == 0 or miner.last_update < current_block - 3600:
    skip_miner()
```
**Solution**: Need manual query to break cycle

---

## 📊 What to Do With Findings

### If Threshold Found:
1. **Document exact value** (e.g., min_last_update = 3600 blocks)
2. **Calculate time needed** (e.g., 3600 blocks = ~12 hours)
3. **Determine if achievable** (can we get query within threshold?)
4. **Plan action** (manual query vs. wait vs. re-register)

### If No Public Code:
1. **Note that code is private**
2. **Focus on community outreach**
3. **Ask validators directly**
4. **Document any responses**

---

## 🔗 Resources to Check

### Official Bittensor
- Bittensor GitHub organization
- Subnet 36 documentation
- Validator examples/templates

### Community Resources
- Autoppia Discord/Telegram
- Bittensor community forums
- Subnet-specific documentation

### Code Search
- GitHub search: `bittensor subnet 36`
- GitHub search: `autoppia validator`
- GitHub search: `infinite web arena`

---

## ✅ Success Criteria

**Investigation Complete When**:
- ✅ Found validator code OR confirmed it's private
- ✅ Identified selection criteria OR documented what's unknown
- ✅ Understand pruning logic OR know it's network-controlled
- ✅ Have actionable next steps based on findings

---

**Status**: Ready to investigate  
**Next**: Search for Autoppia validator repository

