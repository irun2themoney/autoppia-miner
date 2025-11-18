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
        }
        
        return strategies.get(self.detected_website, {})


# Global instance
website_detector = WebsiteDetector()

