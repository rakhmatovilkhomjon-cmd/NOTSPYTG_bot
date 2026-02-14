import json
import os
from typing import Dict, List, Any
from pathlib import Path

class DatabaseHelper:
    def __init__(self, db_file: str = "database/data.json"):
        self.db_file = db_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default data structure
        default_data = {
            "menu": {
                "pizza": [
                    {"id": 1, "name": "Margherita", "price": 12.00, "description": "Fresh tomatoes, mozzarella, basil"},
                    {"id": 2, "name": "Pepperoni", "price": 14.00, "description": "Pepperoni, mozzarella, tomato sauce"},
                    {"id": 3, "name": "Hawaiian", "price": 15.00, "description": "Ham, pineapple, mozzarella"}
                ],
                "burgers": [
                    {"id": 4, "name": "Classic Burger", "price": 10.00, "description": "Beef patty, lettuce, tomato, onion"},
                    {"id": 5, "name": "Cheese Burger", "price": 11.00, "description": "Beef patty, cheese, lettuce, tomato"},
                    {"id": 6, "name": "Veggie Burger", "price": 9.00, "description": "Plant-based patty, lettuce, tomato"}
                ],
                "drinks": [
                    {"id": 7, "name": "Coca Cola", "price": 3.00, "description": "Classic soft drink"},
                    {"id": 8, "name": "Coffee", "price": 4.00, "description": "Fresh brewed coffee"},
                    {"id": 9, "name": "Orange Juice", "price": 5.00, "description": "Fresh squeezed orange juice"}
                ]
            },
            "orders": {},
            "settings": {
                "delivery_fee": 2.50,
                "min_order": 15.00
            }
        }
        
        # Save default data
        self.save_data_dict(default_data)
        return default_data
    
    def save_data(self):
        self.save_data_dict(self.data)
    
    def save_data_dict(self, data: Dict[str, Any]):
        # Create directory if it doesn't exist
        Path(self.db_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_menu_category(self, category: str) -> List[Dict]:
        return self.data.get("menu", {}).get(category, [])
    
    def get_item_by_id(self, item_id: int) -> Dict:
        for category in self.data.get("menu", {}).values():
            for item in category:
                if item["id"] == item_id:
                    return item
        return {}
    
    def add_to_cart(self, user_id: int, item_id: int, quantity: int = 1):
        user_str = str(user_id)
        if user_str not in self.data["orders"]:
            self.data["orders"][user_str] = {"items": {}, "total": 0}
        
        if str(item_id) in self.data["orders"][user_str]["items"]:
            self.data["orders"][user_str]["items"][str(item_id)] += quantity
        else:
            self.data["orders"][user_str]["items"][str(item_id)] = quantity
        
        self.update_cart_total(user_id)
        self.save_data()
    
    def update_cart_total(self, user_id: int):
        user_str = str(user_id)
        total = 0
        if user_str in self.data["orders"]:
            for item_id, quantity in self.data["orders"][user_str]["items"].items():
                item = self.get_item_by_id(int(item_id))
                if item:
                    total += item["price"] * quantity
        
        self.data["orders"][user_str]["total"] = total
    
    def get_cart(self, user_id: int) -> Dict:
        return self.data["orders"].get(str(user_id), {"items": {}, "total": 0})
    
    def clear_cart(self, user_id: int):
        user_str = str(user_id)
        if user_str in self.data["orders"]:
            self.data["orders"][user_str] = {"items": {}, "total": 0}
            self.save_data()

# Global database instance
db = DatabaseHelper()