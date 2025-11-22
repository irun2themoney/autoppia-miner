# 📚 Autoppia IWA Library

**Repository**: https://github.com/autoppia/autoppia_iwa

---

## Overview

The `autoppia_iwa` repository is the **core Infinite Web Arena (IWA) library** that defines:

- **IWA BaseAction format** (the action format we must use)
- **Benchmark system** (how validators test agents)
- **Validation logic** (how success is determined)
- **Browser execution** (how actions are executed)

---

## What It Contains

### **1. IWA BaseAction Format** ✅ **CRITICAL FOR US**

This defines the exact action format our miner must return:

```python
# Action Types
- NavigateAction
- ClickAction
- TypeAction
- WaitAction
- ScreenshotAction
- ScrollAction

# Selector Types
- tagContainsSelector
- attributeValueSelector
- xpathSelector
- cssSelector
```

**This is what we implement in `api/actions/converter.py`**

### **2. Benchmark System**

The benchmark system:
- Generates tasks using LLMs
- Sends tasks to agents via HTTP API (`/solve_task`)
- Executes actions in real browsers
- Validates success using predefined tests
- Generates metrics and reports

**This is what the playground uses!**

### **3. Validation Logic**

How validators determine success:
- **Frontend Tests**: DOM analysis, network activity, visual verification
- **Backend Tests**: Event tracking, state validation, process flow
- **Predefined Conditions**: Logical criteria, not subjective evaluation

**This is how our actions are evaluated**

---

## Do We Use It?

### **Current Implementation**: ✅ **We Implement the Format Manually**

**Why**:
- We don't import the library (not in `requirements.txt`)
- We manually implement BaseAction format in `api/actions/converter.py`
- This is **correct** - we just need to match the format, not import the library

### **Should We Use It?**

**Option 1: Keep Manual Implementation** (Current) ✅
- ✅ **Pros**: No external dependency, full control
- ✅ **Pros**: Lighter, faster
- ✅ **Cons**: Must manually maintain format compatibility

**Option 2: Import the Library**
- ✅ **Pros**: Always up-to-date format, official implementation
- ❌ **Cons**: Additional dependency
- ❌ **Cons**: May include features we don't need

**Recommendation**: ✅ **Keep manual implementation** (current approach is correct)

---

## Key Insights from Repository

### **1. Action Format is Critical**

From the repository, we can see:
- Actions must be in exact BaseAction format
- Selectors must match specific types
- This is what validators expect

### **2. Benchmark = Validator Testing**

The benchmark system:
- Uses the same evaluation as validators
- Tests via HTTP API (`/solve_task`)
- Validates using the same logic

**This confirms**: Playground tests = Validator tests

### **3. Validation is Objective**

Success is determined by:
- Predefined conditions (not AI evaluation)
- Logical criteria (events, state changes)
- Frontend + Backend verification

**This means**: Our actions must actually complete tasks, not just look valid

---

## How We Use It

### **Reference for Format**

We use the repository as a **reference** to ensure our action format matches:

1. **Action Types**: We implement all required types
2. **Selector Types**: We support all selector formats
3. **Structure**: We match the exact JSON structure

### **Understanding Validation**

The repository helps us understand:
- How validators evaluate our actions
- What makes a task successful
- How to structure actions for success

---

## Installation (If Needed)

If we wanted to use it directly:

```bash
pip install git+https://github.com/autoppia/autoppia_iwa.git
```

**But we don't need to** - we just need to match the format.

---

## Key Files in Repository

- `autoppia_iwa/` - Core library
- `modules/` - IWA modules
- `tests/` - Test suite
- `docs/` - Documentation
- `readme.md` - Main documentation

---

## References

- [Repository](https://github.com/autoppia/autoppia_iwa)
- [Our Implementation](api/actions/converter.py)
- [Official Sources](docs/OFFICIAL_SOURCES.md)

---

## Summary

**For our miner**:
- ✅ We correctly implement BaseAction format manually
- ✅ We don't need to import the library
- ✅ We use it as a reference for format compatibility
- ✅ Our approach is correct and efficient

**The repository is**:
- 📚 **Reference**: For understanding format requirements
- 🧪 **Benchmark**: What the playground uses
- ✅ **Validation**: How our actions are evaluated

**We're doing it right!** ✅

