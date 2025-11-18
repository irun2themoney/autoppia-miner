"""Website detection and site-specific intelligence"""
from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


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
            "keywords": ["list", "item", "add", "create", "entry"],
            "common_selectors": {
                "add_item": ["button:contains('Add')", "button:contains('New Item')"],
                "list_item": [".list-item", "li"],
                "create_list": ["button:contains('Create List')", "button:contains('New List')"],
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
            "keywords": ["job", "apply", "application", "career", "position", "hiring", "job_title", "company"],
            "common_selectors": {
                "job_search": ["input[type='search']", "input[name='search']", "input[placeholder*='job']"],
                "job_card": [".job-card", "[data-job-id]", ".job-listing", ".job-item"],
                "apply_button": ["button:contains('Apply')", "a[href*='apply']", "[data-action='apply']"],
                "job_title": ["h2.job-title", ".job-title", "[data-job-title]"],
                "company_name": [".company-name", "[data-company]"],
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
            "keywords": ["mail", "email", "message", "inbox", "compose", "send", "reply"],
            "common_selectors": {
                "compose_button": ["button:contains('Compose')", "button:contains('New Email')", "button:contains('New Message')"],
                "email_list": [".email-list", "[data-email]", ".email-item", ".message-item"],
                "send_button": ["button:contains('Send')", "button[type='submit']", "button[data-action='send']"],
                "inbox": ["a:contains('Inbox')", ".inbox", "[data-inbox]"],
                "reply_button": ["button:contains('Reply')", "button:contains('Reply All')"],
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
        Detect which Auto* website from URL and prompt
        
        Returns:
            Website name (e.g., "autocalendar") or None
        """
        url_lower = url.lower() if url else ""
        prompt_lower = prompt.lower() if prompt else ""
        
        # Score each website
        website_scores = {}
        
        for website, patterns in self.WEBSITE_PATTERNS.items():
            score = 0
            
            # Check URL patterns
            for pattern in patterns["url_patterns"]:
                if re.search(pattern, url_lower, re.IGNORECASE):
                    score += 10  # URL match is strong indicator
            
            # Check keywords in prompt
            for keyword in patterns["keywords"]:
                if keyword in prompt_lower:
                    score += 2  # Keyword match is weaker indicator
            
            if score > 0:
                website_scores[website] = score
        
        # Return highest scoring website
        if website_scores:
            detected = max(website_scores.items(), key=lambda x: x[1])[0]
            self.detected_website = detected
            self.website_context = self.WEBSITE_PATTERNS[detected]
            logger.info(f"Detected website: {detected} (score: {website_scores[detected]})")
            return detected
        
        return None
    
    def get_website_context(self) -> Dict[str, Any]:
        """Get context for detected website"""
        return self.website_context.copy() if self.website_context else {}
    
    def get_site_specific_selectors(self, element_type: str) -> list:
        """Get site-specific selectors for element type"""
        if not self.website_context:
            return []
        
        common_selectors = self.website_context.get("common_selectors", {})
        return common_selectors.get(element_type, [])
    
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
                "wait_after_navigation": 1.5,  # Increased for quality
                "wait_between_actions": 0.8,   # Increased for quality
                "screenshot_frequency": "after_important",
                "verification_enabled": True,
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
                "wait_after_navigation": 2.5,  # Job pages load slowly (increased for quality)
                "wait_between_actions": 1.0,   # Job interactions need time
                "screenshot_frequency": "always",  # Job applications are critical
                "verification_enabled": True,  # Enable verification for quality
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
                "wait_after_navigation": 2.0,  # Mail pages load moderately
                "wait_between_actions": 0.8,   # Email interactions are quick
                "screenshot_frequency": "after_important",  # Email actions are important
                "verification_enabled": True,  # Enable verification for quality
            },
            "autodining": {
                "wait_after_navigation": 2.5,  # Restaurant pages load slowly (menus, images)
                "wait_between_actions": 1.0,   # Reservation interactions need time
                "screenshot_frequency": "always",  # Reservations are critical
                "verification_enabled": True,  # Enable verification for quality
            },
        }
        
        return strategies.get(self.detected_website, {})


# Global instance
website_detector = WebsiteDetector()

