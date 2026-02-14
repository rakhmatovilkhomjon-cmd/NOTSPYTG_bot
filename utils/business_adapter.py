# utils/business_adapter.py
from typing import Dict, Any, List
from database.enhanced_db_helper import enhanced_db

class BusinessAdapter:
    """Adapter to easily switch between different business types"""
    
    def __init__(self, business_type: str):
        self.business_type = business_type
        self.db = enhanced_db
        
        # Set business type in database
        self.db.data["settings"]["business_type"] = business_type
        self.db.save_data()
    
    def get_main_categories(self) -> List[str]:
        """Get main categories based on business type"""
        category_mapping = {
            "restaurant": ["pizza", "burgers", "drinks", "desserts"],
            "shop": ["clothing", "electronics", "accessories", "books"],
            "booking": ["haircut", "massage", "consultation", "therapy"],
            "education": ["programming", "design", "business", "languages"]
        }
        return category_mapping.get(self.business_type, [])
    
    def get_item_type(self) -> str:
        """Get the database item type based on business"""
        type_mapping = {
            "restaurant": "menu",
            "shop": "products", 
            "booking": "services",
            "education": "courses"
        }
        return type_mapping.get(self.business_type, "menu")
    
    def get_main_actions(self) -> List[Dict[str, str]]:
        """Get main action buttons based on business type"""
        action_mapping = {
            "restaurant": [
                {"text": "🍽️ Menu", "callback": "menu"},
                {"text": "🛒 Cart", "callback": "cart"}
            ],
            "shop": [
                {"text": "🛍️ Shop", "callback": "shop"},
                {"text": "🛒 Cart", "callback": "cart"}
            ],
            "booking": [
                {"text": "📅 Book Appointment", "callback": "book"},
                {"text": "📋 My Bookings", "callback": "my_bookings"}
            ],
            "education": [
                {"text": "📚 Courses", "callback": "courses"},
                {"text": "📊 My Progress", "callback": "progress"}
            ]
        }
        return action_mapping.get(self.business_type, [])
    
    def get_welcome_message(self, user_name: str) -> str:
        """Get welcome message based on business type"""
        messages = {
            "restaurant": f"👋 Welcome to our Restaurant, {user_name}!\n\nReady to order some delicious food?",
            "shop": f"👋 Welcome to our Store, {user_name}!\n\nDiscover amazing products at great prices!",
            "booking": f"👋 Welcome, {user_name}!\n\nBook your appointment with our professional services.",
            "education": f"👋 Welcome to our Learning Platform, {user_name}!\n\nStart your educational journey today!"
        }
        return messages.get(self.business_type, f"👋 Welcome, {user_name}!")

# Usage example:
# adapter = BusinessAdapter("shop")  # Change to your business type