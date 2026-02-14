# database/enhanced_db_helper.py
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class EnhancedDatabaseHelper:
    def __init__(self, db_file: str = "database/data.json"):
        self.db_file = db_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return self.get_default_data()
    
    def get_default_data(self) -> Dict[str, Any]:
        """Get default data structure"""
        return {
            "business_type": "restaurant",  # restaurant, shop, booking, education
            "menu": {},
            "products": {},
            "services": {},
            "courses": {},
            "users": {},
            "orders": {},
            "bookings": {},
            "enrollments": {},
            "settings": {
                "business_name": "My Business",
                "currency": "$",
                "tax_rate": 0.08,
                "service_fee": 0.00
            }
        }
    
    def save_data(self):
        """Save data to JSON file"""
        Path(self.db_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    # User management
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user data"""
        user_str = str(user_id)
        return self.data.get("users", {}).get(user_str, {})
    
    def save_user(self, user_id: int, user_data: Dict[str, Any]):
        """Save user data"""
        user_str = str(user_id)
        if "users" not in self.data:
            self.data["users"] = {}
        self.data["users"][user_str] = user_data
        self.save_data()
    
    # Generic item management (works for menu, products, services, courses)
    def get_items_by_category(self, item_type: str, category: str) -> List[Dict]:
        """Get items by category"""
        return self.data.get(item_type, {}).get(category, [])
    
    def get_item_by_id(self, item_type: str, item_id: int) -> Optional[Dict]:
        """Get item by ID from any category"""
        for category in self.data.get(item_type, {}).values():
            for item in category:
                if item.get("id") == item_id:
                    return item
        return None
    
    def add_item(self, item_type: str, category: str, item_data: Dict[str, Any]):
        """Add new item to category"""
        if item_type not in self.data:
            self.data[item_type] = {}
        if category not in self.data[item_type]:
            self.data[item_type][category] = []
        
        # Auto-generate ID if not provided
        if "id" not in item_data:
            max_id = 0
            for cat_items in self.data[item_type].values():
                for item in cat_items:
                    max_id = max(max_id, item.get("id", 0))
            item_data["id"] = max_id + 1
        
        self.data[item_type][category].append(item_data)
        self.save_data()
        return item_data["id"]
    
    # Cart/Order management
    def add_to_cart(self, user_id: int, item_id: int, quantity: int = 1, item_type: str = "menu"):
        """Add item to user's cart"""
        user_str = str(user_id)
        if user_str not in self.data["orders"]:
            self.data["orders"][user_str] = {"items": {}, "total": 0, "item_type": item_type}
        
        item_key = f"{item_type}_{item_id}"
        if item_key in self.data["orders"][user_str]["items"]:
            self.data["orders"][user_str]["items"][item_key] += quantity
        else:
            self.data["orders"][user_str]["items"][item_key] = quantity
        
        self.update_cart_total(user_id, item_type)
        self.save_data()
    
    def update_cart_total(self, user_id: int, item_type: str = "menu"):
        """Update cart total"""
        user_str = str(user_id)
        total = 0
        if user_str in self.data["orders"]:
            for item_key, quantity in self.data["orders"][user_str]["items"].items():
                if item_key.startswith(f"{item_type}_"):
                    item_id = int(item_key.split("_")[1])
                    item = self.get_item_by_id(item_type, item_id)
                    if item:
                        total += item.get("price", 0) * quantity
        
        self.data["orders"][user_str]["total"] = total
    
    # Booking management
    def save_booking(self, booking_data: Dict[str, Any]) -> int:
        """Save appointment booking"""
        if "bookings" not in self.data:
            self.data["bookings"] = {}
        
        # Generate booking ID
        booking_id = len(self.data["bookings"]) + 1
        booking_data["id"] = booking_id
        booking_data["created_at"] = datetime.now().isoformat()
        
        self.data["bookings"][str(booking_id)] = booking_data
        self.save_data()
        return booking_id
    
    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Get all bookings for a user"""
        user_bookings = []
        for booking in self.data.get("bookings", {}).values():
            if booking.get("user_id") == user_id:
                user_bookings.append(booking)
        return sorted(user_bookings, key=lambda x: x.get("date", ""))
    
    # Course/Education management
    def get_course_by_id(self, course_id: int) -> Optional[Dict]:
        """Get course by ID"""
        return self.get_item_by_id("courses", course_id)
    
    def get_user_course_progress(self, user_id: int, course_id: int) -> Dict:
        """Get user's progress in a course"""
        user_str = str(user_id)
        course_str = str(course_id)
        
        if "enrollments" not in self.data:
            self.data["enrollments"] = {}
        
        if user_str not in self.data["enrollments"]:
            self.data["enrollments"][user_str] = {}
        
        return self.data["enrollments"][user_str].get(course_str, {
            "enrolled": False,
            "completed_lessons": 0,
            "completed_lessons_ids": [],
            "progress_percentage": 0
        })
    
    def enroll_user_in_course(self, user_id: int, course_id: int):
        """Enroll user in a course"""
        user_str = str(user_id)
        course_str = str(course_id)
        
        if "enrollments" not in self.data:
            self.data["enrollments"] = {}
        
        if user_str not in self.data["enrollments"]:
            self.data["enrollments"][user_str] = {}
        
        self.data["enrollments"][user_str][course_str] = {
            "enrolled": True,
            "enrolled_at": datetime.now().isoformat(),
            "completed_lessons": 0,
            "completed_lessons_ids": [],
            "progress_percentage": 0
        }
        
        self.save_data()
    
    def mark_lesson_complete(self, user_id: int, course_id: int, lesson_id: int):
        """Mark a lesson as completed"""
        user_str = str(user_id)
        course_str = str(course_id)
        
        progress = self.get_user_course_progress(user_id, course_id)
        
        if lesson_id not in progress["completed_lessons_ids"]:
            progress["completed_lessons_ids"].append(lesson_id)
            progress["completed_lessons"] = len(progress["completed_lessons_ids"])
            
            # Calculate progress percentage
            course = self.get_course_by_id(course_id)
            if course:
                total_lessons = course.get("lessons", 1)
                progress["progress_percentage"] = (progress["completed_lessons"] / total_lessons) * 100
        
        self.data["enrollments"][user_str][course_str] = progress
        self.save_data()

# Global enhanced database instance
enhanced_db = EnhancedDatabaseHelper()