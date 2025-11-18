# IWA Overview Analysis - Key Insights for Miner Enhancement

**Source**: [IWA Platform Overview](https://infinitewebarena.autoppia.com/subnet36/overview)  
**Analysis Date**: November 18, 2025  
**Current Round**: 36 (59% complete, 444 blocks remaining)

## 🎯 Critical Performance Metrics

### Top Miner Benchmarks (Round 33)
- **Tok (UID 105)**: 
  - Rank: #1
  - Avg Score: **57.7%**
  - Avg Response Time: **9 seconds**
  - Validators: 3
  - Avg Tasks Per Validator: 33
  - Websites: 13

### Current Round 36 Scores (Validator: Autoppia)
1. **!Crypto! (UID 127)**: 86.8% ⭐
2. **Tok (UID 105)**: 84.2%
3. **Autoppia_1 (UID 72)**: 81.6%
4. **junior-bot (UID 172)**: 71.1%
5. **Browser Use (UID 214)**: 0.0%

**Winner Average Score**: 64.1% across all validators

## 📊 Key Insights

### 1. **Scoring Windows Matter**
- Scores are tracked over **7R, 15R, 30R, and All rounds**
- This means **consistency over time** is critical
- A single bad round can hurt your 7R score, but 30R/All scores provide buffer

### 2. **Response Time is Critical**
- Top miner (Tok) averages **9 seconds** response time
- Our current response time: **~0.01s** (excellent!)
- However, we need to balance speed with **accuracy**

### 3. **Active Use Cases (Round 36)**
Validators are currently testing:
- **APPLY_FOR_JOB**: Apply for specific job positions
- **VIEW_JOB**: Retrieve job posting details
- **SEARCH_JOBS**: Search for jobs with specific criteria
- **NEW_CALENDAR_EVENT_ADDED**: Add calendar events with specific constraints

### 4. **Website Coverage**
- **13 active websites** in Round 33
- Current validators testing:
  - **AutoConnect**: Job-related tasks (3 validators)
  - **AutoCRM**: Calendar tasks (1 validator)
- Other websites likely include: AutoCinema, AutoDrive, AutoCalendar, AutoList, AutoWork, AutoBooks

### 5. **Competitive Landscape**
- **5 active miners** in Round 36
- Top scores range from **71.1% to 86.8%**
- Our miner needs to consistently score **>80%** to compete

### 6. **Task Volume**
- Average **33-38 tasks per validator**
- **2-4 validators** active per round
- Total: ~100-150 tasks per round

## 🚀 Actionable Recommendations

### Priority 1: Job Application Use Cases (CRITICAL)
**Why**: 3 out of 4 validators are testing AutoConnect job tasks

**Enhancements Needed**:
1. **APPLY_FOR_JOB Pattern**:
   - Extract job_title, company name, location from prompt
   - Navigate to job listings
   - Filter/search for matching job
   - Click "Apply" button
   - Fill application form if required

2. **VIEW_JOB Pattern**:
   - Extract job title, location, company from prompt
   - Handle "NOT contain" constraints (e.g., "location does NOT contain 'rce'")
   - Navigate to job details page
   - Extract and return job information

3. **SEARCH_JOBS Pattern**:
   - Extract search query from prompt
   - Handle negative constraints (e.g., "does NOT contain 'tnm'")
   - Navigate to search page
   - Enter search query
   - Handle pagination if needed

**Implementation**:
```python
# Add to api/actions/generator.py
JOB_APPLICATION_PATTERNS = {
    "apply_for_job": {
        "keywords": ["apply", "job", "position", "job_title", "company"],
        "actions": ["navigate", "search", "click", "fill_form", "submit"]
    },
    "view_job": {
        "keywords": ["view", "retrieve", "details", "job posting", "job title"],
        "actions": ["navigate", "search", "click", "extract"]
    },
    "search_jobs": {
        "keywords": ["search", "jobs", "query", "find jobs"],
        "actions": ["navigate", "type", "click", "wait"]
    }
}
```

### Priority 2: Calendar Event Use Cases
**Why**: 1 validator actively testing AutoCRM calendar tasks

**Enhancements Needed**:
1. **NEW_CALENDAR_EVENT_ADDED Pattern**:
   - Extract: label, time, date, event_type
   - Handle time constraints (e.g., "less_equal '4:30pm'")
   - Handle date constraints (e.g., "NOT equal to '2025-10-10'")
   - Navigate to calendar
   - Click "Add Event" or "New Event"
   - Fill form with extracted data
   - Submit

**Implementation**:
- Already have calendar patterns, but need to enhance:
  - Time constraint parsing (less_equal, greater_equal, etc.)
  - Date constraint parsing (NOT equal, contains, etc.)
  - Event type filtering

### Priority 3: Negative Constraint Handling
**Why**: Multiple tasks use "NOT contain", "does NOT contain", "NOT equal"

**Enhancements Needed**:
1. **Enhanced Task Parser**:
   - Detect negative constraints in prompts
   - Extract exclusion criteria
   - Pass to action generator

2. **Action Generator Logic**:
   - When searching/filtering, exclude items matching negative criteria
   - Use multiple selector strategies to find non-matching elements

**Implementation**:
```python
# In api/utils/task_parser.py
def extract_negative_constraints(prompt: str) -> Dict[str, List[str]]:
    """Extract negative constraints like 'NOT contain', 'does NOT contain'"""
    constraints = {
        "exclude_text": [],
        "exclude_location": [],
        "exclude_date": []
    }
    
    # Pattern: "does NOT contain 'text'"
    not_contains = re.findall(r"does?\s+NOT\s+contain\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
    constraints["exclude_text"].extend(not_contains)
    
    # Pattern: "NOT equal to 'value'"
    not_equal = re.findall(r"NOT\s+equal\s+to\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
    constraints["exclude_text"].extend(not_equal)
    
    return constraints
```

### Priority 4: AutoConnect Website Intelligence
**Why**: Most validators are testing AutoConnect

**Enhancements Needed**:
1. **AutoConnect Detection**:
   - Detect AutoConnect URLs
   - Apply AutoConnect-specific selectors
   - Handle job listing pages, job detail pages, application forms

2. **AutoConnect Selectors**:
   - Job search input: `input[type="search"]`, `input[name*="search"]`, `input[placeholder*="job"]`
   - Job cards: `.job-card`, `[data-job-id]`, `.job-listing`
   - Apply button: `button:contains("Apply")`, `a[href*="apply"]`, `[data-action="apply"]`
   - Job title: `h2.job-title`, `.job-title`, `[data-job-title]`
   - Company name: `.company-name`, `[data-company]`

**Implementation**:
```python
# In api/utils/website_detector.py
AUTOCONNECT_STRATEGIES = {
    "autoconnect": {
        "url_patterns": ["autoconnect", "job", "career"],
        "selectors": {
            "job_search": [
                "input[type='search']",
                "input[name*='search']",
                "input[placeholder*='job']",
                "#job-search",
                ".search-input"
            ],
            "job_card": [
                ".job-card",
                "[data-job-id]",
                ".job-listing",
                ".job-item"
            ],
            "apply_button": [
                "button:contains('Apply')",
                "a[href*='apply']",
                "[data-action='apply']",
                ".apply-button"
            ]
        },
        "wait_after_navigation": 2.5,
        "wait_between_actions": 1.0
    }
}
```

### Priority 5: Response Time Optimization
**Why**: Top miner averages 9s, but we're at 0.01s (may be too fast, missing verification)

**Balance Needed**:
- Current: 0.01s (too fast, may miss verification steps)
- Target: **3-5 seconds** (fast but thorough)
- Add verification steps for critical actions (job application, calendar events)

**Implementation**:
- Keep fast response for simple tasks
- Add verification waits for complex tasks (job applications, form submissions)
- Use smart waits based on action type

### Priority 6: Multi-Validator Strategy
**Why**: 2-4 validators per round, each with different use cases

**Enhancements Needed**:
1. **Validator-Specific Learning**:
   - Track which validators prefer which use cases
   - Optimize for each validator's patterns
   - Already implemented via `validator_learner.py` ✅

2. **Use Case Distribution**:
   - Ensure we handle all use cases well
   - Don't over-optimize for one use case (Dynamic Zero)

## 📈 Success Metrics to Track

1. **Score Targets**:
   - Short-term (7R): >70%
   - Medium-term (15R): >75%
   - Long-term (30R): >80%
   - All-time: >80%

2. **Response Time**:
   - Target: 3-5 seconds (balanced)
   - Current: 0.01s (too fast, may need verification)

3. **Use Case Coverage**:
   - Job applications: >80% success
   - Job viewing: >85% success
   - Job searching: >85% success
   - Calendar events: >80% success

4. **Website Coverage**:
   - AutoConnect: >80% success
   - AutoCRM: >80% success
   - Other websites: >75% success

## 🎯 Immediate Action Items

1. ✅ **Dynamic Zero**: Already implemented
2. ✅ **Anti-Overfitting**: Already implemented
3. ✅ **Task Diversity**: Already implemented
4. ⚠️ **Job Application Patterns**: NEEDS ENHANCEMENT
5. ⚠️ **Negative Constraint Handling**: NEEDS ENHANCEMENT
6. ⚠️ **AutoConnect Intelligence**: NEEDS ENHANCEMENT
7. ⚠️ **Response Time Balance**: NEEDS ADJUSTMENT

## 📝 Notes

- **Browser Use** is enabled (OpenAI CUA and Anthropic CUA disabled)
- **Dynamic Zero V1** is active - our anti-overfitting system is critical
- **13 websites** need coverage - we should prioritize the most tested ones
- **Rolling window scoring** means we need consistent performance, not just peak performance

---

**Next Steps**: Implement Priority 1-3 enhancements to compete with top miners (80%+ scores).

