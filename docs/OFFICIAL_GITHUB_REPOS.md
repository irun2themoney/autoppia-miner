# 📚 Official Autoppia GitHub Repositories

**Last Updated**: November 19, 2025

## 🎯 **Key Repositories**

Based on [Autoppia's GitHub organization](https://github.com/autoppia):

### **1. autoppia_web_agents_subnet** ⭐ PRIMARY
- **URL**: https://github.com/autoppia/autoppia_web_agents_subnet
- **Language**: Python
- **Stars**: 5 | **Forks**: 11
- **Last Updated**: November 18, 2025
- **License**: MIT
- **Purpose**: Main subnet repository
  - Contains validator code
  - Miner examples and patterns
  - Protocol definitions (synapse types)
  - Communication protocol specifications

**What to Monitor**:
- `protocol.py` or `synapse.py` - Synapse type definitions
- `miners/` - Official miner examples
- `validators/` - Validator code (shows what they expect)
- Recent commits for protocol changes

---

### **2. autoppia_iwa** ⭐ CRITICAL
- **URL**: https://github.com/autoppia/autoppia_iwa
- **Language**: Python
- **Stars**: 6
- **Last Updated**: November 19, 2025
- **Purpose**: Infinite Web Arena (IWA) module
  - ApifiedWebAgent implementation
  - Task format definitions
  - Action format specifications
  - IWA-specific patterns

**What to Monitor**:
- ApifiedWebAgent class definition
- Task request/response formats
- Action format specifications
- IWA-specific requirements

---

### **3. autoppia_webs_demo**
- **URL**: https://github.com/autoppia/autoppia_webs_demo
- **Language**: TypeScript
- **Last Updated**: November 19, 2025
- **Purpose**: Demo project showing usage patterns

---

### **4. autoppia_backend_client**
- **URL**: https://github.com/autoppia/autoppia_backend_client
- **Language**: Python
- **Last Updated**: November 19, 2025
- **Purpose**: Backend client library

---

### **5. autoppia_web_operator**
- **URL**: https://github.com/autoppia/autoppia_web_operator
- **Language**: TypeScript
- **Last Updated**: June 30, 2025
- **Purpose**: Web operator interface

---

## 🔍 **What We Should Check**

### **Critical Files to Review**:

1. **Protocol Definitions** (`autoppia_web_agents_subnet`):
   - `StartRoundSynapse` definition
   - `TaskSynapse` definition
   - Any new synapse types
   - Protocol version changes

2. **Miner Patterns** (`autoppia_web_agents_subnet/miners/`):
   - How official miners handle synapses
   - Axon setup patterns
   - API integration methods
   - Error handling patterns

3. **ApifiedWebAgent** (`autoppia_iwa`):
   - Expected request format
   - Expected response format
   - Action format specifications
   - Task handling patterns

4. **Recent Updates**:
   - Check commits from November 18-19, 2025
   - Look for breaking changes
   - New requirements or patterns
   - Protocol updates

---

## ✅ **Our Compliance Status**

### **What We're Already Doing Right**:
- ✅ Using ApifiedWebAgent pattern (HTTP API server)
- ✅ Implementing `StartRoundSynapse` and `TaskSynapse`
- ✅ Following IWA BaseAction format
- ✅ Proper axon setup and serving
- ✅ API endpoint at `/solve_task`
- ✅ Correct response format with `actions`, `web_agent_id`, `recording`, `id`, `task_id`

### **What We Should Verify**:
- ⚠️ Check if our synapse definitions match latest official versions
- ⚠️ Verify our action format matches latest specifications
- ⚠️ Ensure we're using latest protocol patterns
- ⚠️ Check for any new requirements from recent updates

---

## 🚀 **Next Steps**

1. **Review Official Repos**:
   - Check `autoppia_web_agents_subnet` for protocol updates
   - Review `autoppia_iwa` for ApifiedWebAgent changes
   - Look for miner examples to compare patterns

2. **Update Our Implementation**:
   - Align with latest protocol definitions
   - Ensure action format matches latest spec
   - Update any deprecated patterns

3. **Monitor for Updates**:
   - Set up alerts for repository updates
   - Check weekly for new commits
   - Review changelogs/release notes

---

## 📝 **Repository Links**

- **Organization**: https://github.com/autoppia
- **Main Subnet Repo**: https://github.com/autoppia/autoppia_web_agents_subnet
- **IWA Module**: https://github.com/autoppia/autoppia_iwa
- **Web Demo**: https://github.com/autoppia/autoppia_webs_demo
- **Backend Client**: https://github.com/autoppia/autoppia_backend_client

---

**Status**: ✅ Monitoring official repositories for updates

**Self-Learning System**: Our `DocumentationLearner` now monitors these repositories automatically!

