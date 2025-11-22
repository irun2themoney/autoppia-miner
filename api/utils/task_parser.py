"""Advanced task parsing and extraction"""
import re
from typing import Dict, Any, Optional, List


class TaskParser:
    """Parse and extract information from task prompts"""
    
    def __init__(self):
        # Common patterns for extraction
        self.credential_patterns = {
            "username": [
                r"username[:\s]+([^\s<]+)",
                r"user[:\s]+([^\s<]+)",
                r"login[:\s]+([^\s<]+)",
            ],
            "password": [
                r"password[:\s]+([^\s<]+)",
                r"pass[:\s]+([^\s<]+)",
            ],
            "email": [
                r"email[:\s]+([^\s@]+@[^\s@]+\.[^\s@]+)",
                r"e-mail[:\s]+([^\s@]+@[^\s@]+\.[^\s@]+)",
            ],
        }
        
        self.url_patterns = [
            r"https?://[^\s]+",
            r"www\.[^\s]+",
            r"navigate to ([^\s]+)",
            r"go to ([^\s]+)",
        ]
        
        self.text_patterns = [
            r"type ['\"]([^'\"]+)['\"]",
            r"enter ['\"]([^'\"]+)['\"]",
            r"fill with ['\"]([^'\"]+)['\"]",
            r"contains the word ['\"]([^'\"]+)['\"]",
            r"contains ['\"]([^'\"]+)['\"]",
        ]
    
    def extract_credentials(self, prompt: str) -> Dict[str, Optional[str]]:
        """Extract credentials from prompt - Enhanced with more patterns"""
        prompt_lower = prompt.lower()
        credentials = {}
        
        # Enhanced patterns for better extraction
        enhanced_patterns = {
            "username": [
                r"username[:\s=]+([^\s<,]+)",
                r"user[:\s=]+([^\s<,]+)",
                r"login[:\s=]+([^\s<,]+)",
                r"user\s+name[:\s=]+([^\s<,]+)",
                r"uname[:\s=]+([^\s<,]+)",
            ],
            "password": [
                r"password[:\s=]+([^\s<,]+)",
                r"pass[:\s=]+([^\s<,]+)",
                r"pwd[:\s=]+([^\s<,]+)",
            ],
            "email": [
                r"email[:\s=]+([^\s<,]+@[^\s<,]+)",
                r"e-mail[:\s=]+([^\s<,]+@[^\s<,]+)",
                r"mail[:\s=]+([^\s<,]+@[^\s<,]+)",
            ],
        }
        
        for cred_type, patterns in enhanced_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower, re.IGNORECASE)
                if match:
                    value = match.group(1)
                    # Clean up common placeholders and separators
                    value = value.replace("<web_agent_id>", "").strip()
                    # CRITICAL: Strip quotes from beginning and end (Dynamic Zero requirement)
                    value = value.strip("'\"")
                    value = value.rstrip(".,;:!?")  # Remove trailing punctuation
                    if value and len(value) > 0:
                        credentials[cred_type] = value
                        break
        
        # CRITICAL FIX: Also try extracting email from the original prompt (case-sensitive)
        # The email pattern might fail if quotes are in the way
        if not credentials.get("email"):
            email_patterns = [
                r"email:\s*['\"]([^'\"]+@[^'\"]+)['\"]",
                r"email:\s*([^\s,]+@[^\s,]+)",
                r"email\s+['\"]([^'\"]+@[^'\"]+)['\"]",
            ]
            for pattern in email_patterns:
                match = re.search(pattern, prompt, re.IGNORECASE)
                if match:
                    email = match.group(1).replace("<web_agent_id>", "").strip("'\"")
                    if email and "@" in email:
                        credentials["email"] = email
                        break
        
        return credentials
    
    def extract_url(self, prompt: str, default_url: str = "") -> str:
        """Extract URL from prompt"""
        # CRITICAL: Ensure default_url is a string (not a dict)
        if default_url is None:
            default_url = ""
        elif isinstance(default_url, dict):
            default_url = default_url.get("url", default_url.get("href", "")) if isinstance(default_url, dict) else str(default_url)
        elif not isinstance(default_url, str):
            default_url = str(default_url) if default_url else ""
        
        for pattern in self.url_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                url = match.group(1) if match.groups() else match.group(0)
                # Ensure url is a string before calling startswith
                if not isinstance(url, str):
                    url = str(url) if url else ""
                # Ensure protocol
                if url and isinstance(url, str) and not url.startswith(("http://", "https://")):
                    url = "https://" + url
                return url
        
        return default_url
    
    def extract_text_to_type(self, prompt: str) -> Optional[str]:
        """Extract text that needs to be typed"""
        for pattern in self.text_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_target_element(self, prompt: str) -> Optional[str]:
        """Extract target element description - Enhanced patterns"""
        prompt_lower = prompt.lower()
        
        # Enhanced patterns for better extraction
        patterns = [
            r"click (?:the |a |on )?([^,\.]+?)(?: button|link|element|tab|option)?",
            r"select (?:the |a )?([^,\.]+?)(?: button|link|element|option|view)?",
            r"choose (?:the |a )?([^,\.]+?)(?: button|link|element|option)?",
            r"find (?:the |a )?([^,\.]+?)(?: button|link|element)?",
            r"switch (?:to |the )?([^,\.]+?)(?: view|mode|tab)?",
            r"toggle (?:the |to )?([^,\.]+?)(?: view|mode)?",
            r"view (?:the |a )?([^,\.]+?)(?: view|mode)?",
            r"change (?:to |the )?([^,\.]+?)(?: view|mode)?",
            r"open (?:the |a )?([^,\.]+?)(?: button|link|tab)?",
            r"press (?:the |a )?([^,\.]+?)(?: button|key)?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                target = match.group(1).strip()
                # Remove common words
                target = re.sub(r"\b(the|a|an|on|in|at|to|for|with|from)\b", "", target).strip()
                if target and len(target) > 1:
                    return target
        
        # Try to extract from common phrases
        common_targets = {
            "month view": "month",
            "week view": "week",
            "day view": "day",
            "year view": "year",
            "login button": "login",
            "submit button": "submit",
            "search button": "search",
            "profile": "profile",
            "settings": "settings",
        }
        
        for phrase, target in common_targets.items():
            if phrase in prompt_lower:
                return target
        
        return None
    
    def extract_negative_constraints(self, prompt: str) -> Dict[str, List[str]]:
        """Extract negative constraints like 'NOT contain', 'does NOT contain', 'NOT equal'"""
        constraints = {
            "exclude_text": [],
            "exclude_location": [],
            "exclude_date": [],
            "exclude_company": [],
            "exclude_job_title": [],
        }
        
        # Pattern: "does NOT contain 'text'"
        not_contains = re.findall(r"does?\s+NOT\s+contain\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        constraints["exclude_text"].extend(not_contains)
        
        # Pattern: "NOT contain 'text'"
        not_contains2 = re.findall(r"NOT\s+contain\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        constraints["exclude_text"].extend(not_contains2)
        
        # Pattern: "NOT equal to 'value'"
        not_equal = re.findall(r"NOT\s+equal\s+to\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        constraints["exclude_text"].extend(not_equal)
        
        # Pattern: "location does NOT contain"
        location_not = re.findall(r"location\s+does?\s+NOT\s+contain\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        constraints["exclude_location"].extend(location_not)
        
        # Pattern: "company does NOT contain"
        company_not = re.findall(r"company\s+does?\s+NOT\s+contain\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        constraints["exclude_company"].extend(company_not)
        
        # Pattern: "date is NOT equal to"
        date_not = re.findall(r"date\s+is\s+NOT\s+equal\s+to\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        constraints["exclude_date"].extend(date_not)
        
        return constraints
    
    def extract_job_info(self, prompt: str) -> Dict[str, Any]:
        """Extract job-related information from prompt"""
        job_info = {
            "job_title": None,
            "company": None,
            "location": None,
            "use_case": None,
            "constraints": {},
        }
        
        prompt_lower = prompt.lower()
        
        # Detect use case
        if "apply_for_job" in prompt_lower or "apply for" in prompt_lower:
            job_info["use_case"] = "APPLY_FOR_JOB"
        elif "view_job" in prompt_lower or "retrieve details" in prompt_lower or "job posting" in prompt_lower:
            job_info["use_case"] = "VIEW_JOB"
        elif "search_jobs" in prompt_lower or "search for jobs" in prompt_lower:
            job_info["use_case"] = "SEARCH_JOBS"
        
        # Extract job_title
        # Pattern: "job_title is equal to 'X'"
        job_title_match = re.search(r"job[_\s]?title\s+is\s+equal\s+to\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if job_title_match:
            job_info["job_title"] = job_title_match.group(1)
        
        # Pattern: "job title is equal to 'X'"
        job_title_match2 = re.search(r"job\s+title\s+is\s+equal\s+to\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if job_title_match2:
            job_info["job_title"] = job_title_match2.group(1)
        
        # Pattern: "title is equal to 'X'"
        title_match = re.search(r"title\s+is\s+equal\s+to\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if title_match and not job_info["job_title"]:
            job_info["job_title"] = title_match.group(1)
        
        # Extract company
        # Pattern: "company that contains 'X'"
        company_match = re.search(r"company\s+(?:that\s+)?contains\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if company_match:
            job_info["company"] = company_match.group(1)
        
        # Pattern: "company name contains 'X'"
        company_match2 = re.search(r"company\s+name\s+contains\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if company_match2:
            job_info["company"] = company_match2.group(1)
        
        # Extract location
        # Pattern: "location does NOT contain 'X'"
        location_match = re.search(r"location\s+(?:does\s+NOT\s+contain|contains)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if location_match:
            job_info["location"] = location_match.group(1)
        
        # Extract search query
        # Pattern: "query that does NOT contain 'X'"
        query_match = re.search(r"query\s+(?:that\s+)?(?:does\s+NOT\s+contain|contains)\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if query_match:
            job_info["search_query"] = query_match.group(1)
        
        # Extract negative constraints
        job_info["constraints"] = self.extract_negative_constraints(prompt)
        
        return job_info
    
    def extract_booking_info(self, prompt: str) -> Dict[str, Any]:
        """Extract booking/consultation information from prompt"""
        booking_info = {
            "filters": {},
            "use_case": "BOOK_A_CONSULTATION",
        }
        
        # Extract name contains
        name_match = re.search(r"name contains ['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if name_match:
            booking_info["filters"]["name_contains"] = name_match.group(1)
        
        # Extract rate does not contain
        rate_match = re.search(r"rate does not contain ['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if rate_match:
            booking_info["filters"]["rate_not_contains"] = rate_match.group(1)
        
        # Extract role is not equal to
        role_match = re.search(r"role is not equal to ['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if role_match:
            booking_info["filters"]["role_not_equal"] = role_match.group(1)
        
        # Extract country is not equal to
        country_match = re.search(r"country is not equal to ['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE)
        if country_match:
            booking_info["filters"]["country_not_equal"] = country_match.group(1)
        
        # Extract rating equals
        rating_match = re.search(r"rating equals ([\d.]+)", prompt, re.IGNORECASE)
        if rating_match:
            booking_info["filters"]["rating_equals"] = rating_match.group(1)
        
        return booking_info
    
    def parse_task(self, prompt: str, url: str = "") -> Dict[str, Any]:
        """Parse task and extract all relevant information - Enhanced"""
        # CRITICAL: Ensure url is always a string (not a dict)
        # This prevents 'dict' object has no attribute 'startswith' errors
        if url is None:
            url = ""
        elif isinstance(url, dict):
            url = url.get("url", url.get("href", "")) if isinstance(url, dict) else str(url)
        elif not isinstance(url, str):
            url = str(url) if url else ""
        
        prompt_lower = prompt.lower()
        
        # Enhanced task type detection
        has_login = any(word in prompt_lower for word in ["login", "sign in", "log in", "authenticate"])
        has_form = any(word in prompt_lower for word in ["form", "fill", "submit", "enter", "register"])
        has_search = any(word in prompt_lower for word in ["search", "find", "look for", "seek"])
        has_modify = any(word in prompt_lower for word in ["modify", "edit", "change", "update", "delete", "remove"])
        has_click = any(word in prompt_lower for word in ["click", "select", "choose", "switch", "toggle", "view"])
        has_type = any(word in prompt_lower for word in ["type", "enter", "input", "write"])
        has_comment = any(word in prompt_lower for word in ["comment", "post", "reply", "write a comment"])
        has_scroll = any(word in prompt_lower for word in ["scroll", "move down", "move up"])
        has_extract = any(word in prompt_lower for word in ["extract", "get", "read", "retrieve", "fetch"])
        has_multistep = any(word in prompt_lower for word in ["and", "then", "after", "before", "first", "next"])
        
        # Booking/Consultation task detection (HIGH PRIORITY)
        has_booking = any(phrase in prompt_lower for phrase in ["book a consultation", "book consultation", "book a", "booking"])
        has_consultation = "consultation" in prompt_lower
        
        # Job-related task detection (HIGH PRIORITY)
        has_job_apply = any(phrase in prompt_lower for phrase in ["apply for", "apply_for_job", "apply to job"])
        has_job_view = any(phrase in prompt_lower for phrase in ["view job", "view_job", "retrieve details", "job posting", "job details"])
        has_job_search = any(phrase in prompt_lower for phrase in ["search jobs", "search_jobs", "search for jobs", "find jobs"])
        has_job = has_job_apply or has_job_view or has_job_search or "job" in prompt_lower
        
        # Determine task type with priority (booking and job tasks have high priority)
        if has_booking or has_consultation:
            task_type = "booking"
        elif has_job_apply:
            task_type = "job_apply"
        elif has_job_view:
            task_type = "job_view"
        elif has_job_search:
            task_type = "job_search"
        elif has_login:
            task_type = "login"
        elif has_form:
            task_type = "form"
        elif has_modify:
            task_type = "modify"
        elif has_search:
            task_type = "search"
        elif has_comment:
            task_type = "comment"
        elif has_click:
            task_type = "click"
        elif has_type:
            task_type = "type"
        elif has_scroll:
            task_type = "scroll"
        elif has_extract:
            task_type = "extract"
        elif has_multistep:
            task_type = "multistep"
        else:
            task_type = "generic"
        
        # Extract booking information if booking-related
        booking_info = {}
        if has_booking or has_consultation:
            booking_info = self.extract_booking_info(prompt)
        
        # Extract job information if job-related
        job_info = {}
        if has_job:
            job_info = self.extract_job_info(prompt)
        
        # Extract negative constraints
        negative_constraints = self.extract_negative_constraints(prompt)
        
        parsed = {
            "original_prompt": prompt,
            "url": self.extract_url(prompt, url),
            "credentials": self.extract_credentials(prompt),
            "text_to_type": self.extract_text_to_type(prompt),
            "target_element": self.extract_target_element(prompt),
            "has_login": has_login,
            "has_form": has_form,
            "has_search": has_search,
            "has_modify": has_modify,
            "has_click": has_click,
            "has_type": has_type,
            "has_comment": has_comment,
            "has_scroll": has_scroll,
            "has_extract": has_extract,
            "has_multistep": has_multistep,
            "has_booking": has_booking or has_consultation,
            "has_job": has_job,
            "has_job_apply": has_job_apply,
            "has_job_view": has_job_view,
            "has_job_search": has_job_search,
            "task_type": task_type,
            "booking_info": booking_info,
            "job_info": job_info,
            "negative_constraints": negative_constraints,
        }
        
        return parsed

