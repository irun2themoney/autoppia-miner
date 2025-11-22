# 🎯 Dynamic Zero Requirements - How to Pass Benchmark Tests

**Source**: [Dynamic Zero Article](https://autoppia.substack.com/p/dynamic-zero-the-overfitting-punisher)

---

## 📋 **Critical Requirements**

### **1. Completion + Precision** ⭐ **MOST IMPORTANT**
- **Requirement**: Tasks must be **SOLVED**, not just attempted
- **What this means**: Actions must actually **COMPLETE** the task goal
- **Example**: "Book a consultation" → Actions must search, filter, select, and **book** the consultation

### **2. Time Factor REMOVED**
- **Was**: 15% of score
- **Now**: 0% (doesn't matter)
- **Impact**: Don't worry about speed - focus on **completing the task correctly**

### **3. Efficiency Rewards REMOVED**
- **Was**: Rewarded fewer actions
- **Now**: No longer rewarded
- **Impact**: Generate **comprehensive action sequences** - use as many actions as needed

### **4. Focus on RELIABLE Task Completion**
- **Requirement**: Actions must reliably solve tasks
- **What this means**: Generate actions that **accomplish the goal**, not just valid actions

---

## ❌ **Why Benchmarks Are Failing**

### **Current Problem**:
1. **Generic Actions**: Generating Wait, Click button, Screenshot
2. **No Task Completion**: Actions don't actually solve the task
3. **Missing Search/Filter**: No TypeAction to search for consultations
4. **Missing Booking**: No click on "Book" button to complete the task

### **What Benchmark Expects**:
For "Book a consultation whose name contains 'ah M.'...":
1. ✅ **Search** for consultations (TypeAction with name)
2. ✅ **Filter** by criteria (ClickAction on filters)
3. ✅ **Select** matching consultation (ClickAction)
4. ✅ **Book** it (ClickAction on "Book" button)

---

## ✅ **What Needs to Happen**

### **1. Generate Task-Specific Actions**
- **Not**: Generic "Click button"
- **But**: "Type 'ah M.' in search field", "Click Book button"

### **2. Complete Action Sequences**
- **Not**: Just valid actions
- **But**: Actions that **accomplish the goal**

### **3. Comprehensive Sequences**
- **Dynamic Zero allows more actions** - use them!
- Generate complete workflows: Search → Filter → Select → Book

### **4. Always Generate Actions**
- Even if filters are empty, generate basic booking sequence
- Always attempt to complete the task

---

## 🔧 **Implementation**

### **Booking Handler Must**:
1. **Always generate actions** (even with empty filters)
2. **Include search actions** (TypeAction)
3. **Include filter actions** (ClickAction on filters)
4. **Include selection actions** (ClickAction on consultation)
5. **Include booking actions** (ClickAction on "Book")

### **Action Format**:
- Actions use `action_type` internally
- Converted to `type` (ClickAction, TypeAction, etc.) by converter
- Selectors must be in correct IWA format

---

## 🎯 **Success Criteria**

**Benchmark Passes When**:
- ✅ Actions include search/filter operations (TypeAction)
- ✅ Actions include selection operations (ClickAction)
- ✅ Actions include booking operations (ClickAction on "Book")
- ✅ Actions attempt to **COMPLETE** the task
- ✅ Actions are in correct IWA format

**Benchmark Fails When**:
- ❌ Actions are generic (Wait, Click button, Screenshot)
- ❌ No search/filter actions
- ❌ No booking actions
- ❌ Actions don't accomplish the goal

---

## 📊 **Current Status**

**Fixed**:
- ✅ Selector format (correct IWA format)
- ✅ Booking task detection (parser detects booking)
- ✅ Booking handler exists (generates actions)

**Still Needs Fix**:
- ⚠️ Booking handler not being called (condition not matching?)
- ⚠️ Actions not being converted properly
- ⚠️ Missing TypeActions (search/filter)

---

**Next Steps**: Ensure booking handler is called and generates complete action sequences that attempt to solve the task.

