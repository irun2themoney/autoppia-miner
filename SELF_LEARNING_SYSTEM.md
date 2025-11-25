# 🧠 Self-Learning and Self-Enhancing Miner System

## Overview

The miner now includes a **self-learning and self-enhancing system** that:
1. **Learns from successes and failures**
2. **Adapts selector strategies** based on effectiveness
3. **Improves action sequences** over time
4. **Tracks patterns** in successful task completions
5. **Provides insights** for continuous improvement

---

## 🎯 Key Features

### 1. **Learning System** (`api/utils/learning_system.py`)

**What it does:**
- Tracks task success/failure rates
- Records successful action patterns
- Learns which selectors work best
- Adapts to different task types
- Persists learning data to disk

**Key Functions:**
- `record_task_result()` - Record execution results
- `get_successful_pattern()` - Find similar successful patterns
- `get_best_selectors()` - Get best performing selectors
- `enhance_actions()` - Improve actions using learned patterns

### 2. **Feedback Analyzer** (`api/utils/feedback_analyzer.py`)

**What it does:**
- Analyzes execution results from playground/validators
- Identifies patterns in failures
- Suggests improvements
- Tracks selector and action failures

**Key Functions:**
- `analyze_execution_result()` - Analyze task execution
- `get_improvement_suggestions()` - Get improvement recommendations
- `analyze_empty_actions_issue()` - Diagnose empty actions problems

### 3. **Adaptive Selector** (`api/utils/adaptive_selector.py`)

**What it does:**
- Learns which selector types work best for different elements
- Adapts selector generation based on success rates
- Provides confidence scores for selectors
- Suggests best selector strategies

**Key Functions:**
- `get_best_selector_strategy()` - Get best selector approach
- `should_prefer_attribute_selector()` - Determine selector preference
- `adapt_selector_based_on_feedback()` - Improve selectors
- `get_selector_confidence()` - Get confidence score

---

## 📊 How It Works

### Learning Flow:

```
1. Task Executed
   ↓
2. Record Result (success/failure)
   ↓
3. Analyze Patterns
   ↓
4. Update Selector Success Rates
   ↓
5. Save Learning Data
   ↓
6. Use Learned Patterns for Future Tasks
```

### Enhancement Flow:

```
1. Generate Actions
   ↓
2. Check for Similar Successful Patterns
   ↓
3. Enhance Actions Using Learned Patterns
   ↓
4. Improve Selectors Based on Success Rates
   ↓
5. Return Enhanced Actions
```

---

## 🔌 API Endpoints

### Get Learning Statistics

```bash
GET /learning/stats
```

**Response:**
```json
{
  "total_tasks": 100,
  "successful_tasks": 75,
  "failed_tasks": 25,
  "success_rate": 0.75,
  "selector_tracked": 50,
  "task_patterns": 10,
  "action_type_usage": {
    "ClickAction": 200,
    "TypeAction": 150,
    "NavigateAction": 100
  }
}
```

### Record Feedback

```bash
POST /learning/feedback
Content-Type: application/json

{
  "task_id": "task-123",
  "task_type": "login",
  "prompt": "Login to the website",
  "url": "https://example.com",
  "success": true,
  "execution_time": 1.5,
  "error": null,
  "actions": [...]
}
```

**Response:**
```json
{
  "status": "recorded",
  "analysis": {
    "success": true,
    "issues": [],
    "suggestions": []
  },
  "suggestions": [
    "Improve selector generation for buttons"
  ]
}
```

---

## 💾 Data Storage

### Learning Data Files:

1. **`learning_data.pkl`** - Main learning data (pickle format)
   - Successful actions
   - Failed actions
   - Selector effectiveness
   - Task type success rates

2. **`selector_success.json`** - Selector success rates
   - Selector key → success rate mapping
   - Updated after each task

3. **`task_patterns.json`** - Successful task patterns
   - Task type → list of successful patterns
   - Keeps last 100 patterns per task type

---

## 🚀 Usage

### Automatic Learning

The system **automatically learns** from:
- Task execution results (when feedback is provided)
- Selector success/failure rates
- Action sequence effectiveness

### Manual Feedback

To provide feedback manually:

```python
import requests

feedback = {
    "task_id": "task-123",
    "task_type": "login",
    "prompt": "Login to the website",
    "url": "https://example.com",
    "success": True,
    "execution_time": 1.5,
    "actions": [...]
}

response = requests.post(
    "http://134.199.203.133:8080/learning/feedback",
    json=feedback
)
```

### View Statistics

```bash
curl http://134.199.203.133:8080/learning/stats
```

---

## 📈 Benefits

1. **Continuous Improvement**
   - Miner gets better over time
   - Learns from mistakes
   - Adapts to different scenarios

2. **Better Selectors**
   - Tracks which selectors work best
   - Prefers successful selector types
   - Avoids selectors with low success rates

3. **Pattern Recognition**
   - Learns successful action sequences
   - Reuses patterns for similar tasks
   - Reduces trial and error

4. **Performance Insights**
   - Tracks success rates
   - Identifies improvement areas
   - Provides actionable suggestions

---

## 🔧 Configuration

### Enable/Disable Learning

Learning is **enabled by default** if modules are available.

To disable, remove or comment out the imports in `api/endpoints.py`:

```python
# LEARNING_ENABLED = False  # Disable learning
```

### Data Persistence

Learning data is saved:
- **Every 10 tasks** (automatic)
- **On shutdown** (if implemented)
- **Manually** via API (if needed)

---

## 🎯 Future Enhancements

1. **NLP-Based Pattern Matching**
   - Better similarity detection
   - Semantic understanding of prompts

2. **Real-Time Adaptation**
   - Immediate selector improvement
   - Dynamic strategy adjustment

3. **Cross-Task Learning**
   - Learn from similar tasks
   - Transfer knowledge between task types

4. **Predictive Enhancement**
   - Predict likely failures
   - Proactively improve actions

---

## 📝 Notes

- Learning data persists across restarts
- Statistics are cumulative
- Patterns are kept for last 100 successful tasks per type
- Selector success rates are continuously updated

---

**Status**: ✅ **Active and Learning**

The miner is now **self-learning and self-enhancing**! 🧠✨

