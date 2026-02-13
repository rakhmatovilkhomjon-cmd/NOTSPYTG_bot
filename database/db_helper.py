import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


def _now_iso() -> str:
    """Return current UTC time in ISO format (without microseconds)."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass
class OrderItem:
    """Represents a single item in an order."""

    item_id: int
    quantity: int
    price: float


class DatabaseHelper:
    """
    Lightweight JSON-based storage for the bot.

    This class is intentionally simple and pedagogical so that you can later
    migrate to a real database (PostgreSQL, etc.) by replacing only this file.
    """

    def __init__(self, db_file: str = "database/data.json"):
        self.db_file = db_file
        self.data = self.load_data()

    # ---------------------------------------------------------------------
    # Low-level persistence
    # ---------------------------------------------------------------------
    def load_data(self) -> Dict[str, Any]:
        """
        Load JSON data from disk and ensure the structure matches
        the current expected schema.
        """
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}

        # --- Default structure ------------------------------------------------
        data.setdefault(
            "menu",
            {
                "pizza": [
                    {
                        "id": 1,
                        "name": "Margherita pitsa",
                        "price": 12.00,
                        "description": "Yangi pomidor, mozzarella, rayhon",
                    },
                    {
                        "id": 2,
                        "name": "Pepperoni pitsa",
                        "price": 14.00,
                        "description": "Pepperoni kolbasasi, mozzarella, pomidor sousi",
                    },
                    {
                        "id": 3,
                        "name": "Gavayi pitsasi",
                        "price": 15.00,
                        "description": "Vetchina, ananas, mozzarella",
                    },
                ],
                "burgers": [
                    {
                        "id": 4,
                        "name": "Klassik burger",
                        "price": 10.00,
                        "description": "Mol go‘shti kotleti, salat bargi, pomidor, piyoz",
                    },
                    {
                        "id": 5,
                        "name": "Pishloqli burger",
                        "price": 11.00,
                        "description": "Mol go‘shti kotleti, pishloq, salat bargi, pomidor",
                    },
                    {
                        "id": 6,
                        "name": "Sabzavotli burger",
                        "price": 9.00,
                        "description": "O‘simlik asosidagi kotlet, salat bargi, pomidor",
                    },
                ],
                "drinks": [
                    {
                        "id": 7,
                        "name": "Coca Cola",
                        "price": 3.00,
                        "description": "Klassik gazli ichimlik",
                    },
                    {
                        "id": 8,
                        "name": "Qahva",
                        "price": 4.00,
                        "description": "Yangi damlangan qahva",
                    },
                    {
                        "id": 9,
                        "name": "Apelsin sharbati",
                        "price": 5.00,
                        "description": "Yangi siqilgan apelsin sharbati",
                    },
                ],
            },
        )

        # Backwards compatibility: old versions stored carts under "orders"
        # as a dict: {user_id: {"items": {...}, "total": ...}}.
        if "carts" not in data:
            if isinstance(data.get("orders"), dict):
                # Interpret the previous "orders" dict as carts.
                data["carts"] = data["orders"]
                data["orders"] = []
            else:
                data["carts"] = {}

        # New collections for professional features
        data.setdefault("orders", [])  # list of order objects
        data.setdefault("reservations", [])  # list of reservation objects
        data.setdefault("users", {})  # user profiles & loyalty info

        # Settings with sensible defaults
        settings = data.setdefault("settings", {})
        settings.setdefault("delivery_fee", 2.50)
        settings.setdefault("min_order", 15.00)
        settings.setdefault("is_open", True)

        # Persist any structural fixes
        self.save_data_dict(data)
        return data

    def save_data(self) -> None:
        """Persist the in-memory data back to disk."""
        self.save_data_dict(self.data)

    def save_data_dict(self, data: Dict[str, Any]) -> None:
        """Low-level helper that writes the provided dict to disk."""
        Path(self.db_file).parent.mkdir(parents=True, exist_ok=True)

        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ---------------------------------------------------------------------
    # Menu helpers
    # ---------------------------------------------------------------------
    def get_menu_category(self, category: str) -> List[Dict[str, Any]]:
        """Return all menu items for the given category."""
        return self.data.get("menu", {}).get(category, [])

    def get_item_by_id(self, item_id: int) -> Dict[str, Any]:
        """Return a menu item by its numeric ID, or an empty dict if not found."""
        for category in self.data.get("menu", {}).values():
            for item in category:
                if item["id"] == item_id:
                    return item
        return {}

    # ---------------------------------------------------------------------
    # Cart helpers (per-user cart, not yet an order)
    # ---------------------------------------------------------------------
    def _ensure_cart(self, user_id: int) -> Dict[str, Any]:
        """Internal helper to ensure a cart structure exists for a user."""
        user_str = str(user_id)
        carts = self.data.setdefault("carts", {})
        if user_str not in carts:
            carts[user_str] = {"items": {}, "total": 0.0}
        return carts[user_str]

    def add_to_cart(self, user_id: int, item_id: int, quantity: int = 1) -> None:
        """Add an item to the user's cart (or increase quantity)."""
        cart = self._ensure_cart(user_id)
        item_key = str(item_id)
        cart["items"][item_key] = cart["items"].get(item_key, 0) + quantity

        self.update_cart_total(user_id)
        self.save_data()

    def update_cart_total(self, user_id: int) -> None:
        """Recalculate and store the total price of the user's cart."""
        user_str = str(user_id)
        carts = self.data.get("carts", {})
        cart = carts.get(user_str)
        if not cart:
            return

        total = 0.0
        for item_id, quantity in cart["items"].items():
            item = self.get_item_by_id(int(item_id))
            if item:
                total += float(item["price"]) * int(quantity)

        cart["total"] = total

    def get_cart(self, user_id: int) -> Dict[str, Any]:
        """Retrieve the user's cart. Ensures a default empty structure."""
        return self._ensure_cart(user_id)

    def clear_cart(self, user_id: int) -> None:
        """Remove all items from the user's cart."""
        user_str = str(user_id)
        carts = self.data.get("carts", {})
        if user_str in carts:
            carts[user_str] = {"items": {}, "total": 0.0}
            self.save_data()

    def change_cart_item_quantity(
        self, user_id: int, item_id: int, delta: int
    ) -> None:
        """
        Increase or decrease quantity of an item in the cart.

        If the resulting quantity is <= 0, the item is removed.
        """
        cart = self._ensure_cart(user_id)
        item_key = str(item_id)
        current = cart["items"].get(item_key, 0)
        new_quantity = current + delta

        if new_quantity > 0:
            cart["items"][item_key] = new_quantity
        elif item_key in cart["items"]:
            del cart["items"][item_key]

        self.update_cart_total(user_id)
        self.save_data()

    # ---------------------------------------------------------------------
    # Users & loyalty helpers
    # ---------------------------------------------------------------------
    def register_or_update_user(
        self, user_id: int, full_name: str, username: Optional[str] = None
    ) -> None:
        """Create or update a basic user profile."""
        user_str = str(user_id)
        users = self.data.setdefault("users", {})
        profile = users.get(user_str, {})
        profile.setdefault("total_spent", 0.0)
        profile.setdefault("points", 0)

        profile["full_name"] = full_name
        profile["username"] = username
        users[user_str] = profile
        self.save_data()

    def update_user_phone(self, user_id: int, phone: str) -> None:
        """Store / update phone number for a user."""
        user_str = str(user_id)
        users = self.data.setdefault("users", {})
        profile = users.get(user_str, {})
        profile.setdefault("total_spent", 0.0)
        profile.setdefault("points", 0)
        profile["phone"] = phone
        users[user_str] = profile
        self.save_data()

    def add_loyalty(self, user_id: int, total_paid: float, points: int = 0) -> None:
        """
        Increase user's total_spent and optionally add loyalty points.

        The exact loyalty program rules are applied by callers.
        """
        user_str = str(user_id)
        users = self.data.setdefault("users", {})
        profile = users.get(user_str, {})
        profile.setdefault("full_name", "")
        profile.setdefault("username", None)
        profile.setdefault("phone", None)

        profile["total_spent"] = float(profile.get("total_spent", 0.0)) + float(
            total_paid
        )
        profile["points"] = int(profile.get("points", 0)) + int(points)

        users[user_str] = profile
        self.save_data()

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Return stored profile and loyalty information for a user."""
        return self.data.get("users", {}).get(
            str(user_id),
            {"full_name": "", "username": None, "phone": None, "total_spent": 0.0, "points": 0},
        )

    # ---------------------------------------------------------------------
    # Orders helpers
    # ---------------------------------------------------------------------
    def _next_order_id(self) -> int:
        """Generate the next incremental order ID."""
        orders: List[Dict[str, Any]] = self.data.setdefault("orders", [])
        if not orders:
            return 1
        return max(o.get("id", 0) for o in orders) + 1

    def create_order(
        self,
        user_id: int,
        items: List[OrderItem],
        delivery_type: str,
        delivery_address: Optional[str],
        phone: str,
        comment: Optional[str],
        delivery_fee: float,
        discount: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Persist a new order and return its representation.

        This method is called by the checkout FSM when the user confirms.
        """
        subtotal = sum(i.price * i.quantity for i in items)
        total_before_discount = subtotal + delivery_fee
        total = max(0.0, total_before_discount - discount)

        order_id = self._next_order_id()
        created_at = _now_iso()

        order_dict = {
            "id": order_id,
            "user_id": str(user_id),
            "items": [
                {"item_id": i.item_id, "quantity": i.quantity, "price": i.price}
                for i in items
            ],
            "subtotal": subtotal,
            "delivery_fee": delivery_fee,
            "discount": discount,
            "total": total,
            "delivery_type": delivery_type,
            "address": delivery_address,
            "phone": phone,
            "comment": comment,
            "status": "new",
            "created_at": created_at,
            "updated_at": created_at,
        }

        self.data.setdefault("orders", []).append(order_dict)
        self.save_data()

        # Update loyalty information
        self.add_loyalty(user_id, total_paid=total)
        return order_dict

    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Look up a single order by its numeric ID."""
        for order in self.data.get("orders", []):
            if order.get("id") == order_id:
                return order
        return None

    def update_order_status(self, order_id: int, new_status: str) -> Optional[Dict[str, Any]]:
        """Update the status of an order (used by admin controls)."""
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        order["status"] = new_status
        order["updated_at"] = _now_iso()
        self.save_data()
        return order

    def list_user_orders(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Return the most recent orders for the given user."""
        orders = [
            o
            for o in self.data.get("orders", [])
            if str(o.get("user_id")) == str(user_id)
        ]
        # Sort newest first by created_at if present
        orders.sort(key=lambda o: o.get("created_at", ""), reverse=True)
        return orders[:limit]

    def list_orders_for_today(self) -> List[Dict[str, Any]]:
        """Return all orders created today (UTC-based)."""
        today = datetime.utcnow().date().isoformat()
        result = []
        for o in self.data.get("orders", []):
            created = o.get("created_at", "")
            if created.startswith(today):
                result.append(o)
        return result

    # ---------------------------------------------------------------------
    # Reservations helpers
    # ---------------------------------------------------------------------
    def _next_reservation_id(self) -> int:
        """Generate the next incremental reservation ID."""
        reservations: List[Dict[str, Any]] = self.data.setdefault("reservations", [])
        if not reservations:
            return 1
        return max(r.get("id", 0) for r in reservations) + 1

    def create_reservation(
        self,
        user_id: int,
        date: str,
        time: str,
        guests: int,
        name: str,
        phone: str,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create and store a new reservation."""
        reservation_id = self._next_reservation_id()
        created_at = _now_iso()

        reservation = {
            "id": reservation_id,
            "user_id": str(user_id),
            "date": date,
            "time": time,
            "guests": guests,
            "name": name,
            "phone": phone,
            "comment": comment,
            "status": "new",
            "created_at": created_at,
            "updated_at": created_at,
        }
        self.data.setdefault("reservations", []).append(reservation)
        self.save_data()
        return reservation

    def list_user_reservations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Return recent reservations for a user."""
        reservations = [
            r
            for r in self.data.get("reservations", [])
            if str(r.get("user_id")) == str(user_id)
        ]
        reservations.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return reservations[:limit]


# Global database instance
db = DatabaseHelper()