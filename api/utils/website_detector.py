"""Website detection and site-specific intelligence"""
from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)

# Import website error handler
try:
    from .website_error_handler import website_error_handler
except ImportError:
    website_error_handler = None


class WebsiteDetector:
    """
    Detects which Auto* website we're working with and provides
    site-specific intelligence
    """
    
    # Website patterns
    WEBSITE_PATTERNS = {
        "autocalendar": {
            "url_patterns": [r"autocalendar", r"calendar"],
            "keywords": ["calendar", "event", "schedule", "date", "month view", "day view"],
            "common_selectors": {
                "month_view": ["data-testid='month-view'", "aria-label='Month View'"],
                "date_picker": ["input[type='date']", ".date-picker"],
                "create_event": ["button:contains('Create Event')", "button:contains('New Event')"],
            }
        },
        "autocinema": {
            "url_patterns": [r"autocinema", r"cinema"],
            "keywords": ["movie", "cinema", "theater", "showtime", "ticket", "booking"],
            "common_selectors": {
                "movie_selection": ["button:contains('Select Movie')", ".movie-card"],
                "showtime": ["button:contains('Showtime')", ".showtime-slot"],
                "book_ticket": ["button:contains('Book')", "button:contains('Buy Ticket')"],
            }
        },
        "autodelivery": {
            "url_patterns": [r"autodelivery", r"delivery"],
            "keywords": ["delivery", "order", "address", "shipping", "track"],
            "common_selectors": {
                "address_form": ["input[name='address']", "textarea[name='address']"],
                "delivery_date": ["input[name='delivery-date']", ".delivery-date"],
                "submit_order": ["button:contains('Place Order')", "button:contains('Submit')"],
            }
        },
        "autozone": {
            "url_patterns": [r"autozone", r"zone"],
            "keywords": ["product", "cart", "checkout", "buy", "add to cart"],
            "common_selectors": {
                "add_to_cart": ["button:contains('Add to Cart')", "button:contains('Buy Now')"],
                "checkout": ["button:contains('Checkout')", "a:contains('Cart')"],
                "product_search": ["input[name='search']", "input[type='search']"],
            }
        },
        "autowork": {
            "url_patterns": [r"autowork", r"work"],
            "keywords": ["job", "application", "resume", "apply", "position"],
            "common_selectors": {
                "apply_button": ["button:contains('Apply')", "button:contains('Apply Now')"],
                "resume_upload": ["input[type='file']", "input[name='resume']"],
                "application_form": ["form", ".application-form"],
            }
        },
        "autolist": {
            "url_patterns": [r"autolist", r"list"],
            "keywords": ["list", "item", "add", "create", "entry", "todo", "task", "checklist", "add to list", "create list", "new item", "list item"],
            "common_selectors": {
                "add_item": [
                    "button:contains('Add')", 
                    "button:contains('New Item')",
                    "button:contains('Add Item')",
                    "button:contains('Create Item')",
                    "[data-action='add']",
                    "[data-testid='add-item']",
                    "button[aria-label*='Add']",
                    "button[aria-label*='New']",
                ],
                "list_item": [
                    ".list-item", 
                    "li",
                    "[data-item]",
                    "[data-list-item]",
                    ".item",
                    ".todo-item",
                    ".task-item",
                    "[data-testid='list-item']",
                ],
                "create_list": [
                    "button:contains('Create List')", 
                    "button:contains('New List')",
                    "button:contains('Add List')",
                    "[data-action='create-list']",
                    "[data-testid='create-list']",
                ],
                "item_input": [
                    "input[type='text']",
                    "input[name='item']",
                    "input[name='name']",
                    "textarea[name='item']",
                    "[data-testid='item-input']",
                ],
                "save_button": [
                    "button:contains('Save')",
                    "button:contains('Add')",
                    "button[type='submit']",
                    "[data-action='save']",
                ],
            }
        },
        "autobooks": {
            "url_patterns": [r"autobooks", r"book"],
            "keywords": ["book", "library", "read", "borrow", "return"],
            "common_selectors": {
                "book_search": ["input[name='search']", "input[placeholder*='book']"],
                "borrow_button": ["button:contains('Borrow')", "button:contains('Check Out')"],
                "return_button": ["button:contains('Return')", "button:contains('Check In')"],
            }
        },
        "autolodge": {
            "url_patterns": [r"autolodge", r"lodge", r"hotel"],
            "keywords": ["hotel", "booking", "reservation", "check-in", "room"],
            "common_selectors": {
                "book_room": ["button:contains('Book Room')", "button:contains('Reserve')"],
                "check_in": ["input[name='check-in']", ".check-in-date"],
                "check_out": ["input[name='check-out']", ".check-out-date"],
            }
        },
        "autoconnect": {
            "url_patterns": [r"autoconnect", r"connect", r"job", r"career"],
            "keywords": ["job", "apply", "application", "career", "position", "hiring", "job_title", "company", "apply for", "job posting", "job listing", "job search", "search jobs"],
            "common_selectors": {
                "job_search": [
                    "input[type='search']", 
                    "input[name='search']", 
                    "input[placeholder*='job']",
                    "input[placeholder*='search']",
                    "input[placeholder*='position']",
                    "[data-testid='job-search']",
                    "[data-search='job']",
                    ".job-search-input",
                ],
                "job_card": [
                    ".job-card", 
                    "[data-job-id]", 
                    ".job-listing", 
                    ".job-item",
                    "[data-job]",
                    ".job-posting",
                    "[data-testid='job-card']",
                    ".job",
                ],
                "apply_button": [
                    "button:contains('Apply')", 
                    "a[href*='apply']", 
                    "[data-action='apply']",
                    "button:contains('Apply Now')",
                    "button:contains('Apply for Job')",
                    "[data-testid='apply-button']",
                    "button[aria-label*='Apply']",
                ],
                "job_title": [
                    "h2.job-title", 
                    ".job-title", 
                    "[data-job-title]",
                    "h3.job-title",
                    "[data-title]",
                    ".title",
                ],
                "company_name": [
                    ".company-name", 
                    "[data-company]",
                    ".company",
                    "[data-company-name]",
                    ".employer",
                ],
                "search_button": [
                    "button:contains('Search')",
                    "button[type='submit']",
                    "[data-action='search']",
                    "button[aria-label*='Search']",
                ],
                "filter_button": [
                    "button:contains('Filter')",
                    "[data-filter]",
                    ".filter-button",
                ],
            }
        },
        "autocrm": {
            "url_patterns": [r"autocrm", r"crm"],
            "keywords": ["crm", "contact", "customer", "calendar", "meeting", "appointment", "client"],
            "common_selectors": {
                "contact_form": ["input[name='contact']", "input[name='customer']", "input[name='client']"],
                "calendar_view": ["button:contains('Calendar')", ".calendar-view", "[data-calendar]"],
                "meeting_button": ["button:contains('Schedule Meeting')", "button:contains('New Meeting')", "button:contains('Book Meeting')"],
                "contact_list": [".contact-list", "[data-contact]", ".contact-item"],
                "appointment": ["button:contains('Appointment')", "[data-appointment]"],
            }
        },
        "autodrive": {
            "url_patterns": [r"autodrive", r"drive"],
            "keywords": ["drive", "file", "upload", "download", "folder", "document", "storage"],
            "common_selectors": {
                "file_upload": ["input[type='file']", "button:contains('Upload')", "button:contains('Upload File')"],
                "file_list": [".file-list", "[data-file]", ".file-item"],
                "folder": [".folder", "[data-folder]", ".folder-item"],
                "download_button": ["button:contains('Download')", "a[download]", "button[data-action='download']"],
                "create_folder": ["button:contains('New Folder')", "button:contains('Create Folder')"],
            }
        },
        "automail": {
            "url_patterns": [r"automail", r"mail"],
            "keywords": ["mail", "email", "message", "inbox", "compose", "send", "reply", "send email", "new email", "compose email", "email message"],
            "common_selectors": {
                "compose_button": [
                    "button:contains('Compose')", 
                    "button:contains('New Email')", 
                    "button:contains('New Message')",
                    "button:contains('Write')",
                    "[data-action='compose']",
                    "[data-testid='compose']",
                    "button[aria-label*='Compose']",
                    "button[aria-label*='New']",
                ],
                "email_list": [
                    ".email-list", 
                    "[data-email]", 
                    ".email-item", 
                    ".message-item",
                    "[data-message]",
                    ".email",
                    ".message",
                    "[data-testid='email-item']",
                    "tr[data-email]",
                ],
                "send_button": [
                    "button:contains('Send')", 
                    "button[type='submit']", 
                    "button[data-action='send']",
                    "[data-testid='send']",
                    "button[aria-label*='Send']",
                ],
                "inbox": [
                    "a:contains('Inbox')", 
                    ".inbox", 
                    "[data-inbox]",
                    "[data-folder='inbox']",
                    "a[href*='inbox']",
                ],
                "reply_button": [
                    "button:contains('Reply')", 
                    "button:contains('Reply All')",
                    "[data-action='reply']",
                    "button[aria-label*='Reply']",
                ],
                "to_field": [
                    "input[name='to']",
                    "input[name='recipient']",
                    "[data-testid='to']",
                    "input[placeholder*='To']",
                ],
                "subject_field": [
                    "input[name='subject']",
                    "[data-testid='subject']",
                    "input[placeholder*='Subject']",
                ],
                "body_field": [
                    "textarea[name='body']",
                    "textarea[name='message']",
                    "[data-testid='body']",
                    ".email-body",
                    "iframe[title*='body']",
                ],
            }
        },
        "autodining": {
            "url_patterns": [r"autodining", r"dining", r"restaurant", r"opentable"],
            "keywords": ["restaurant", "dining", "reservation", "booking", "menu", "table", "reserve", "book table"],
            "common_selectors": {
                "restaurant_search": ["input[type='search']", "input[name='search']", "input[placeholder*='restaurant']", "input[placeholder*='dining']"],
                "restaurant_card": [".restaurant-card", "[data-restaurant]", ".restaurant-item", ".restaurant-listing"],
                "reserve_button": ["button:contains('Reserve')", "button:contains('Book Table')", "button:contains('Book')", "a[href*='reserve']"],
                "menu_button": ["button:contains('Menu')", "a:contains('Menu')", "[data-menu]"],
                "date_picker": ["input[name='date']", "input[name='reservation-date']", ".date-picker"],
                "time_picker": ["input[name='time']", "input[name='reservation-time']", ".time-picker"],
                "party_size": ["input[name='party']", "input[name='guests']", "select[name='party-size']"],
            }
        },
    }
    
    def __init__(self):
        self.detected_website = None
        self.website_context = {}
    
    def detect_website(self, url: str, prompt: str = "") -> Optional[str]:
        """
        Detect which Auto* website from URL and prompt - Enhanced accuracy
        Tok-style: More accurate detection for better site-specific optimization
        
        Returns:
            Website name (e.g., "autocalendar") or None
        """
        url_lower = url.lower() if url else ""
        prompt_lower = prompt.lower() if prompt else ""
        
        # Score each website (enhanced scoring)
        website_scores = {}
        
        for website, patterns in self.WEBSITE_PATTERNS.items():
            score = 0
            
            # Check URL patterns (strong indicator)
            for pattern in patterns["url_patterns"]:
                if re.search(pattern, url_lower, re.IGNORECASE):
                    score += 15  # Increased from 10 - URL match is very strong
            
            # Check keywords in prompt (enhanced matching)
            keyword_matches = 0
            for keyword in patterns["keywords"]:
                # Exact word match (stronger)
                if re.search(rf"\b{re.escape(keyword)}\b", prompt_lower, re.IGNORECASE):
                    score += 3  # Increased from 2 - exact word match
                    keyword_matches += 1
                # Partial match (weaker)
                elif keyword in prompt_lower:
                    score += 1  # Partial match is weaker
            
            # Bonus for multiple keyword matches (indicates strong match)
            if keyword_matches >= 3:
                score += 5  # Multiple keyword matches = strong indicator
            
            # Check for website-specific task patterns
            if website == "autolist":
                # AutoList specific patterns
                if any(word in prompt_lower for word in ["list", "item", "entry", "add to list", "create list"]):
                    score += 5
            elif website == "autoconnect":
                # AutoConnect specific patterns (job-related)
                if any(word in prompt_lower for word in ["job", "apply", "application", "career", "position", "hiring"]):
                    score += 5
            elif website == "automail":
                # AutoMail specific patterns
                if any(word in prompt_lower for word in ["email", "mail", "message", "inbox", "compose", "send"]):
                    score += 5
            
            if score > 0:
                website_scores[website] = score
        
        # Return highest scoring website (with threshold to avoid false positives)
        if website_scores:
            detected = max(website_scores.items(), key=lambda x: x[1])[0]
            # Only return if score is above threshold (avoid weak matches)
            if website_scores[detected] >= 5:  # Minimum threshold for detection
                self.detected_website = detected
                self.website_context = self.WEBSITE_PATTERNS[detected]
                logger.info(f"Detected website: {detected} (score: {website_scores[detected]})")
                return detected
        
        return None
    
    def get_website_context(self) -> Dict[str, Any]:
        """Get context for detected website"""
        return self.website_context.copy() if self.website_context else {}
    
    def get_site_specific_selectors(self, element_type: str) -> list:
        """
        Get site-specific selectors for element type - Enhanced with more strategies
        Tok-style: Multiple selector strategies for better success rate
        """
        if not self.website_context:
            return []
        
        common_selectors = self.website_context.get("common_selectors", {})
        selectors = common_selectors.get(element_type, [])
        
        # For weak websites (AutoList, AutoConnect, AutoMail), add more fallback selectors
        if self.detected_website in ["autolist", "autoconnect", "automail"]:
            # Add generic fallbacks for better coverage
            if element_type == "add_item" or element_type == "add_button":
                selectors.extend([
                    "button[type='button']",
                    "button:not([disabled])",
                    ".btn-primary",
                    "[role='button']",
                ])
            elif element_type == "job_card" or element_type == "list_item" or element_type == "email_item":
                selectors.extend([
                    "[data-id]",
                    "[data-item]",
                    ".card",
                    ".item",
                ])
            elif element_type == "search_input" or element_type == "job_search":
                selectors.extend([
                    "input[type='text']",
                    "input:not([type='hidden'])",
                    "[role='searchbox']",
                ])
        
        return selectors
    
    def get_site_specific_strategy(self) -> Dict[str, Any]:
        """Get site-specific strategy adjustments"""
        if not self.detected_website:
            return {}
        
        strategies = {
            "autocalendar": {
                "wait_after_navigation": 2.5,  # Calendar views load slowly (increased for quality)
                "wait_between_actions": 1.2,   # Calendar interactions need time (increased)
                "screenshot_frequency": "always",  # Calendar state is important
                "verification_enabled": True,  # Enable verification for quality
            },
            "autocinema": {
                "wait_after_navigation": 2.0,  # Increased for quality
                "wait_between_actions": 1.0,   # Increased for quality
                "screenshot_frequency": "after_important",
                "verification_enabled": True,
            },
            "autodelivery": {
                "wait_after_navigation": 2.0,  # Increased for quality
                "wait_between_actions": 0.8,   # Increased for quality
                "screenshot_frequency": "after_important",
                "verification_enabled": True,
            },
            "autozone": {
                "wait_after_navigation": 2.0,  # Increased for quality
                "wait_between_actions": 0.8,   # Increased for quality
                "screenshot_frequency": "after_important",
                "verification_enabled": True,
            },
            "autowork": {
                "wait_after_navigation": 2.5,  # Forms load slowly (increased)
                "wait_between_actions": 0.8,   # Increased for quality
                "screenshot_frequency": "always",  # Forms are important
                "verification_enabled": True,
            },
            "autolist": {
                # Tok's weak point (50%) - Enhanced strategy for better success
                "wait_after_navigation": 2.5,  # Increased significantly - list pages need time to load
                "wait_between_actions": 1.2,   # Increased - list operations need time
                "screenshot_frequency": "always",  # Always screenshot - list state is critical
                "verification_enabled": True,  # Enable verification for quality
                "retry_strategy": "multiple",  # Multiple retries for list operations
                "selector_strategy": "aggressive",  # Try multiple selectors
            },
            "autobooks": {
                "wait_after_navigation": 2.0,  # Increased for quality
                "wait_between_actions": 0.8,   # Increased for quality
                "screenshot_frequency": "after_important",
                "verification_enabled": True,
            },
            "autolodge": {
                "wait_after_navigation": 2.5,  # Booking forms load slowly (increased)
                "wait_between_actions": 1.0,   # Increased for quality
                "screenshot_frequency": "always",  # Bookings are important
                "verification_enabled": True,
            },
            "autoconnect": {
                # Tok's weak point (50%) - Enhanced strategy for better success
                "wait_after_navigation": 3.0,  # Increased significantly - job pages load very slowly
                "wait_between_actions": 1.5,   # Increased - job search and apply need more time
                "screenshot_frequency": "always",  # Always screenshot - job applications are critical
                "verification_enabled": True,  # Enable verification for quality
                "retry_strategy": "multiple",  # Multiple retries for job operations
                "selector_strategy": "aggressive",  # Try multiple selectors (job cards vary)
            },
            "autocrm": {
                "wait_after_navigation": 2.5,  # CRM pages load slowly
                "wait_between_actions": 1.0,   # CRM interactions need time
                "screenshot_frequency": "always",  # CRM data is important
                "verification_enabled": True,  # Enable verification for quality
            },
            "autodrive": {
                "wait_after_navigation": 2.0,  # Drive pages load moderately
                "wait_between_actions": 1.0,   # File operations need time
                "screenshot_frequency": "after_important",  # File operations are important
                "verification_enabled": True,  # Enable verification for quality
            },
            "automail": {
                # Tok's weak point (50%) - Enhanced strategy for better success
                "wait_after_navigation": 2.5,  # Increased - mail pages need time to load
                "wait_between_actions": 1.2,   # Increased - email compose/send needs time
                "screenshot_frequency": "always",  # Always screenshot - email state is critical
                "verification_enabled": True,  # Enable verification for quality
                "retry_strategy": "multiple",  # Multiple retries for email operations
                "selector_strategy": "aggressive",  # Try multiple selectors (email UIs vary)
            },
            "autodining": {
                "wait_after_navigation": 2.5,  # Restaurant pages load slowly (menus, images)
                "wait_between_actions": 1.0,   # Reservation interactions need time
                "screenshot_frequency": "always",  # Reservations are critical
                "verification_enabled": True,  # Enable verification for quality
            },
        }
        
        return strategies.get(self.detected_website, {})
    
    def get_website_error_recovery(
        self,
        failed_action: Dict[str, Any],
        error_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get website-specific error recovery actions
        Tok-style: Different recovery strategies for different websites
        """
        if not self.detected_website or not website_error_handler:
            return []
        
        return website_error_handler.get_website_specific_recovery(
            self.detected_website,
            failed_action,
            error_type
        )


# Global instance
website_detector = WebsiteDetector()

