# 📚 Official Miner Template

**Repository**: https://github.com/autoppia/autoppia_web_agents_subnet

---

## Overview

This is the **official miner template repository** for Subnet 36. It contains the reference implementation that all miners should follow.

---

## Key Components

### **1. Neurons** (`neurons/`)
- **Miner implementation** - Official miner code
- **Validator implementation** - Validator code (reference)
- **ApifiedWebAgent pattern** - The pattern we must follow

### **2. IWA Module** (`autoppia_iwa_module/`)
- Submodule reference to `autoppia_iwa`
- Contains BaseAction format definitions
- Benchmark system integration

### **3. Documentation** (`docs/`)
- Implementation guides
- Protocol specifications
- Best practices

---

## ApifiedWebAgent Pattern

### **The Pattern** (From Official Template)

**Architecture**:
```
Validator → HTTP API (/solve_task) → Your Agent → Actions → Validator
```

**Key Points**:
1. **Miner exposes HTTP API** (not direct synapse processing)
2. **Validators call HTTP API** (not Bittensor synapses directly)
3. **Actions returned in HTTP response** (IWA BaseAction format)
4. **Bittensor miner forwards synapses to HTTP API**

### **Our Implementation** ✅

We follow this pattern correctly:

1. ✅ **HTTP API**: `api/server.py` with `/solve_task` endpoint
2. ✅ **Bittensor Miner**: `miner/miner.py` forwards synapses to HTTP API
3. ✅ **Action Format**: `api/actions/converter.py` converts to IWA format
4. ✅ **Response Format**: `{actions, web_agent_id, recording}`

---

## Subnet Mechanics (From Repository)

### **Validator Role**
- Generates diverse web tasks using IWA
- Distributes tasks to miners
- Executes and verifies solutions
- Assigns weights on Bittensor Blockchain

### **Miner Role** (What We Do)
- Develop state-of-the-art Web Agents ✅
- Process incoming tasks ✅
- Generate precise action sequences ✅
- Continuously improve agent performance ✅

### **Task Distribution & Evaluation**

1. **Task Generation**: Validators create diverse web tasks via IWA
2. **Distribution**: Tasks sent to miners in randomized batches
3. **Task Solution**: Miners use web agents to solve tasks and return sequences of Actions
4. **Evaluation Process**:
   - Validator launches fresh browser instance
   - Executes the sequence of actions returned by miner
   - Takes snapshots after each action
   - Runs task-associated tests on snapshots
   - Generates final score based on test results

**This matches what we see in the playground!**

---

## IWA Benchmark (From Repository)

### **Components**:

1. **Web Environment Generation**: Metaprogramming + Gen AI create diverse demo websites
2. **Web Analysis Module**: Crawl and analyze domains for knowledge files
3. **Task Generation**: LLMs generate synthetic tasks for web environments
4. **Test Generation**: Executable tests determine task completion
5. **Web Agents**: Autonomous systems we build (our miner)
6. **Evaluation**: Browser execution + test verification

### **Test Types**:
- **HTML Verification**: Checks for specific strings and DOM structure
- **Backend Event Testing**: Validates server-side interactions
- **Visual Assessment**: Uses vision models to verify completion
- **LLM-based Evaluation**: Analyzes DOM/HTML to assess success
- **Hybrid Testing**: Combines multiple verification methods

**This explains why our actions must actually complete tasks!**

---

## How Our Implementation Compares

### **✅ What We Do Correctly**:

1. **ApifiedWebAgent Pattern**: ✅
   - HTTP API exposed
   - Bittensor miner forwards to API
   - Correct response format

2. **IWA BaseAction Format**: ✅
   - All action types supported
   - All selector types supported
   - Correct structure

3. **Subnet Mechanics**: ✅
   - Miner registered (UID: 160)
   - Axon served to network
   - Tasks processed correctly

4. **Task Processing**: ✅
   - Receives tasks from validators
   - Generates action sequences
   - Returns IWA format actions

### **📋 Key Differences**:

1. **Simplified Implementation**: 
   - We use `TemplateAgent` (simple, fast)
   - Official template may have more complex agents
   - **This is fine** - we focus on simplicity

2. **No IWA Module Import**:
   - We implement format manually
   - Official template may import IWA module
   - **This is fine** - we match the format correctly

3. **Lightweight Approach**:
   - We removed complex features
   - Focus on core functionality
   - **This aligns with Dynamic Zero** (focus on completion, not complexity)

---

## Key Insights

### **1. Evaluation Process**
From the repository, we learn:
- Validators execute actions in **fresh browser instances**
- They take **snapshots after each action**
- They run **predefined tests** on snapshots
- Success is **objective** (not subjective)

**This means**: Our actions must work in real browsers, not just look valid!

### **2. Task Generation**
- Tasks are **synthetically generated** by LLMs
- They use **random data** (e.g., random products)
- They have **low variety in type but high in combinations**

**This means**: We must handle diverse variations of the same task type!

### **3. Dynamic Environments**
- Websites are **dynamically generated**
- They **prevent memorization** by continuously generating new variations
- They mirror **real web complexity**

**This aligns with Dynamic Zero** - we can't memorize, we must adapt!

---

## References

- [Official Repository](https://github.com/autoppia/autoppia_web_agents_subnet)
- [Our Implementation](docs/MINER_IMPLEMENTATION.md)
- [IWA Library](docs/IWA_LIBRARY.md)

---

## Summary

**Our Implementation**: ✅ **Follows Official Pattern**

- ✅ ApifiedWebAgent pattern (HTTP API)
- ✅ IWA BaseAction format
- ✅ Subnet mechanics (Bittensor integration)
- ✅ Task processing (receive → solve → return)

**Key Difference**: We use a **simplified, lightweight approach** which is:
- ✅ Faster
- ✅ Easier to maintain
- ✅ Aligned with Dynamic Zero (focus on completion)
- ✅ Still fully compliant with requirements

**We're doing it right!** ✅

