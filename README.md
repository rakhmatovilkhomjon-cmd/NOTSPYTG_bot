# NOTSPYTG_bot
# Complete Aiogram Telegram Bot Guide - Latest Version (2025)

## Table of Contents
1. [Getting Started](#getting-started)
2. [Environment Setup](#environment-setup)
3. [Creating Your First Bot](#creating-your-first-bot)
4. [Understanding Aiogram Basics](#understanding-aiogram-basics)
5. [Building a Restaurant Bot](#building-a-restaurant-bot)
6. [Advanced Features](#advanced-features)
7. [Deployment](#deployment)
8. [Extending to Other Projects](#extending-to-other-projects)

---

## Getting Started

### Step 1: Create a Bot with BotFather

1. **Open Telegram** and search for `@BotFather`
2. **Start a conversation** with BotFather by clicking "Start"
3. **Create a new bot** by sending: `/newbot`
4. **Choose a name** for your bot (e.g., "My Restaurant Bot")
5. **Choose a username** ending with "bot" (e.g., "myrestaurant_bot")
6. **Save your token** - BotFather will give you a token like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

⚠️ **Important**: Keep your token secret! Never share it publicly.

### Step 2: Optional Bot Settings

While talking to BotFather, you can also:
- Set bot description: `/setdescription`
- Set bot picture: `/setuserpic`
- Set commands menu: `/setcommands`

---

## Environment Setup

### Step 1: Install Python
Make sure you have Python 3.8+ installed. Check with:
```bash
python --version
```

### Step 2: Create Project Directory
```bash
mkdir my-telegram-bot
cd my-telegram-bot
```

### Step 3: Create Virtual Environment
```bash
# Create virtual environment
python -m venv bot_env

# Activate it
# On Windows:
bot_env\Scripts\activate
# On Mac/Linux:
source bot_env/bin/activate
```

### Step 4: Install Aiogram
```bash
pip install aiogram python-dotenv
```

### Step 5: Create Project Structure
```
my-telegram-bot/
├── main.py              # Main bot file
├── config.py            # Configuration
├── handlers/            # Message handlers
│   ├── __init__.py
│   ├── start.py
│   └── menu.py
├── keyboards/           # Inline keyboards
│   ├── __init__.py
│   └── main_keyboard.py
├── database/            # Database (simple JSON for now)
│   ├── __init__.py
│   └── db_helper.py
├── .env                 # Environment variables
└── requirements.txt     # Dependencies
```

Create these files and folders:
```bash
mkdir handlers keyboards database
touch main.py config.py .env requirements.txt
touch handlers/__init__.py handlers/start.py handlers/menu.py
touch keyboards/__init__.py keyboards/main_keyboard.py
touch database/__init__.py database/db_helper.py
```

---

## Creating Your First Bot

### Step 1: Environment Variables (`.env`)
```env
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_ID=123456789
```

### Step 2: Configuration (`config.py`)
```python
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class BotConfig:
    token: str
    admin_id: int

# Get configuration from environment
def get_config() -> BotConfig:
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN not found in environment variables")
    
    admin_id = os.getenv('ADMIN_ID')
    if not admin_id:
        raise ValueError("ADMIN_ID not found in environment variables")
    
    return BotConfig(
        token=token,
        admin_id=int(admin_id)
    )

config = get_config()
```

**How to get your Telegram ID:**
1. Send a message to `@userinfobot`
2. It will reply with your user ID

### Step 3: Database Helper (`database/db_helper.py`)
```python
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
```

### Step 4: Main Keyboard (`keyboards/main_keyboard.py`)
```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    """Create main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍽️ Menu", callback_data="menu"),
            InlineKeyboardButton(text="🛒 My Cart", callback_data="cart")
        ],
        [
            InlineKeyboardButton(text="📞 Contact", callback_data="contact"),
            InlineKeyboardButton(text="📍 Location", callback_data="location")
        ],
        [
            InlineKeyboardButton(text="⏰ Hours", callback_data="hours")
        ]
    ])
    return keyboard

def get_back_keyboard():
    """Create back to main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Main Menu", callback_data="back")]
    ])
    return keyboard
```

### Step 5: Start Handler (`handlers/start.py`)
```python
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.main_keyboard import get_main_keyboard

# Create router instance
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    """Handle /start command"""
    await message.answer(
        f"👋 Hello, {message.from_user.full_name}!\n"
        f"Welcome to our Restaurant Bot!\n\n"
        f"I can help you:\n"
        f"🍽️ Browse our menu\n"
        f"📞 Get contact information\n"
        f"📍 Find our location\n"
        f"⏰ Check opening hours",
        reply_markup=get_main_keyboard()
    )
```

### Step 6: Menu Handler (`handlers/menu.py`)
```python
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db_helper import db
from keyboards.main_keyboard import get_main_keyboard, get_back_keyboard

# Create router instance
router = Router()

@router.callback_query(F.data == "menu")
async def show_menu_categories(callback: CallbackQuery):
    """Show menu categories"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍕 Pizza", callback_data="category_pizza"),
            InlineKeyboardButton(text="🍔 Burgers", callback_data="category_burgers")
        ],
        [
            InlineKeyboardButton(text="🥤 Drinks", callback_data="category_drinks"),
            InlineKeyboardButton(text="🛒 Cart", callback_data="cart")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="back")
        ]
    ])
    
    await callback.message.edit_text(
        "🍽️ <b>Choose a category:</b>",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: CallbackQuery):
    """Show items in selected category"""
    category = callback.data.split("_")[1]
    items = db.get_menu_category(category)
    
    if not items:
        await callback.answer("This category is empty!", show_alert=True)
        return
    
    keyboard_buttons = []
    text = f"🍽️ <b>{category.title()}</b>\n\n"
    
    for item in items:
        text += f"<b>{item['name']}</b> - ${item['price']:.2f}\n"
        text += f"<i>{item['description']}</i>\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"➕ Add {item['name']}", 
                callback_data=f"add_{item['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    """Add item to cart"""
    item_id = int(callback.data.split("_")[1])
    item = db.get_item_by_id(item_id)
    
    if not item:
        await callback.answer("Item not found!", show_alert=True)
        return
    
    db.add_to_cart(callback.from_user.id, item_id)
    
    await callback.answer(f"✅ {item['name']} added to cart!", show_alert=True)

@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    """Show user's cart"""
    cart = db.get_cart(callback.from_user.id)
    
    if not cart["items"]:
        await callback.message.edit_text(
            "🛒 <b>Your cart is empty</b>\n\n"
            "Add some items from the menu!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🍽️ Browse Menu", callback_data="menu")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
            ])
        )
        await callback.answer()
        return
    
    text = "🛒 <b>Your Cart:</b>\n\n"
    total = 0
    
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if item:
            item_total = item["price"] * quantity
            total += item_total
            text += f"<b>{item['name']}</b>\n"
            text += f"${item['price']:.2f} x {quantity} = ${item_total:.2f}\n\n"
    
    delivery_fee = db.data.get("settings", {}).get("delivery_fee", 2.50)
    text += f"<b>Subtotal:</b> ${total:.2f}\n"
    text += f"<b>Delivery:</b> ${delivery_fee:.2f}\n"
    text += f"<b>Total:</b> ${total + delivery_fee:.2f}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Checkout", callback_data="checkout"),
            InlineKeyboardButton(text="🗑️ Clear Cart", callback_data="clear_cart")
        ],
        [
            InlineKeyboardButton(text="🍽️ Add More Items", callback_data="menu"),
            InlineKeyboardButton(text="⬅️ Back", callback_data="back")
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Clear user's cart"""
    db.clear_cart(callback.from_user.id)
    await callback.answer("🗑️ Cart cleared!", show_alert=True)
    await show_cart(callback)

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    """Process checkout"""
    cart = db.get_cart(callback.from_user.id)
    
    if not cart["items"]:
        await callback.answer("Your cart is empty!", show_alert=True)
        return
    
    # Here you would integrate with payment systems
    # For now, we'll just show order confirmation
    
    order_text = "🎉 <b>Order Confirmed!</b>\n\n"
    order_text += "📞 We'll call you shortly to confirm delivery details.\n"
    order_text += "⏱️ Estimated delivery: 30-45 minutes\n\n"
    order_text += "<b>Order Summary:</b>\n"
    
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if item:
            order_text += f"• {item['name']} x{quantity}\n"
    
    delivery_fee = db.data.get("settings", {}).get("delivery_fee", 2.50)
    order_text += f"\n<b>Total: ${cart['total'] + delivery_fee:.2f}</b>"
    
    # Clear the cart after order
    db.clear_cart(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back")]
    ])
    
    await callback.message.edit_text(order_text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    """Show contact information"""
    contact_text = """
📞 <b>Contact Information</b>

📱 Phone: +1 (555) 123-4567
📧 Email: info@restaurant.com
🌐 Website: www.restaurant.com

<b>Follow us:</b>
📘 Facebook: @restaurant
📷 Instagram: @restaurant
🐦 Twitter: @restaurant
    """
    
    await callback.message.edit_text(
        contact_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "location")
async def show_location(callback: CallbackQuery):
    """Show restaurant location"""
    await callback.message.edit_text(
        "📍 <b>Our Location</b>\n\n"
        "123 Main Street\n"
        "City Center, State 12345\n\n"
        "We're located in the heart of downtown!",
        reply_markup=get_back_keyboard()
    )
    # Send actual location
    await callback.message.answer_location(
        latitude=40.7128,  # Replace with actual coordinates
        longitude=-74.0060
    )
    await callback.answer()

@router.callback_query(F.data == "hours")
async def show_hours(callback: CallbackQuery):
    """Show opening hours"""
    hours_text = """
⏰ <b>Opening Hours</b>

<b>Monday - Thursday:</b> 11:00 AM - 10:00 PM
<b>Friday - Saturday:</b> 11:00 AM - 11:00 PM
<b>Sunday:</b> 12:00 PM - 9:00 PM

<b>Kitchen closes 30 minutes before closing time</b>
    """
    
    await callback.message.edit_text(
        hours_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    """Go back to main menu"""
    await callback.message.edit_text(
        f"👋 Welcome back, {callback.from_user.full_name}!\n\n"
        f"What would you like to do?",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()
```

### Step 7: Main Bot File (`main.py`)
```python
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Import handlers
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    
    # Initialize Bot instance with default bot properties
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize Dispatcher
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    
    # Start polling
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
```

### Step 8: Requirements File (`requirements.txt`)
```txt
aiogram==3.13.0
python-dotenv==1.0.0
```

### Step 9: Test Your Bot
1. **Add your bot token and admin ID** to `.env` file
2. **Install dependencies**:
```bash
pip install -r requirements.txt
```
3. **Run the bot**:
```bash
python main.py
```
4. **Test in Telegram** by sending `/start` to your bot

---

## Advanced Features

### Admin Panel (`handlers/admin.py`)
```python
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from database.db_helper import db

router = Router()

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == config.admin_id

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Show admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied!")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats"),
            InlineKeyboardButton(text="📝 Orders", callback_data="admin_orders")
        ],
        [
            InlineKeyboardButton(text="🍽️ Manage Menu", callback_data="admin_menu"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings")
        ]
    ])
    
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\n"
        "What would you like to manage?",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    """Show bot statistics"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    # Calculate statistics
    total_users = len(db.data.get("orders", {}))
    active_carts = sum(1 for user_data in db.data.get("orders", {}).values() 
                      if user_data.get("items"))
    
    stats_text = f"""
📊 <b>Bot Statistics</b>

👥 <b>Total Users:</b> {total_users}
📦 <b>Active Carts:</b> {active_carts}
🍽️ <b>Menu Items:</b> {sum(len(category) for category in db.data.get("menu", {}).values())}

<b>Menu Categories:</b>
"""
    
    for category, items in db.data.get("menu", {}).items():
        stats_text += f"• {category.title()}: {len(items)} items\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to Admin", callback_data="admin_back")]
    ])
    
    await callback.message.edit_text(stats_text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    """Go back to admin panel"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied!", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistics", callback_data="admin_stats"),
            InlineKeyboardButton(text="📝 Orders", callback_data="admin_orders")
        ],
        [
            InlineKeyboardButton(text="🍽️ Manage Menu", callback_data="admin_menu"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings")
        ]
    ])
    
    await callback.message.edit_text(
        "🔧 <b>Admin Panel</b>\n\n"
        "What would you like to manage?",
        reply_markup=keyboard
    )
    await callback.answer()
```

### Updated Main File with Admin (`main.py`)
```python
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Import handlers
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.admin import router as admin_router
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    
    # Initialize Bot instance
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize Dispatcher
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(admin_router)
    
    # Start polling
    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
```

---

## Deployment

### Production Configuration
For production, create a separate configuration file:

```python
# config_prod.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfig:
    token: str
    admin_id: int
    webhook_url: str = None
    webhook_path: str = "/webhook"
    webapp_host: str = "0.0.0.0"
    webapp_port: int = 8000

def get_config() -> BotConfig:
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN not found in environment variables")
    
    admin_id = os.getenv('ADMIN_ID')
    if not admin_id:
        raise ValueError("ADMIN_ID not found in environment variables")
        
    webhook_url = os.getenv('WEBHOOK_URL')
    
    return BotConfig(
        token=token,
        admin_id=int(admin_id),
        webhook_url=webhook_url
    )

config = get_config()
```

### Webhook Bot for Production (`webhook.py`)
```python
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.admin import router as admin_router
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup(bot: Bot) -> None:
    """Set webhook on startup"""
    if config.webhook_url:
        await bot.set_webhook(f"{config.webhook_url}{config.webhook_path}")
        logger.info(f"Webhook set to {config.webhook_url}{config.webhook_path}")

async def main() -> None:
    """Main function for webhook mode"""
    
    # Initialize Bot and Dispatcher
    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Register startup function
    dp.startup.register(on_startup)
    
    # Register routers
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(admin_router)
    
    # Create aiohttp application
    app = web.Application()
    
    # Create webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    
    # Register webhook handler
    webhook_requests_handler.register(app, path=config.webhook_path)
    
    # Setup application
    setup_application(app, dp, bot=bot)
    
    # Start server
    web.run_app(app, host=config.webapp_host, port=config.webapp_port)

if __name__ == "__main__":
    asyncio.run(main())
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory
RUN mkdir -p database

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - WEBHOOK_URL=${WEBHOOK_URL}
    volumes:
      - ./database:/app/database
    restart: unless-stopped

  # Optional: Add Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

---

## Extending to Other Projects

### 1. E-commerce Store Bot

```python
# handlers/shop.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(F.data.startswith("product_"))
async def show_product_details(callback: CallbackQuery):
    """Show detailed product information"""
    product_id = int(callback.data.split("_")[1])
    product = db.get_item_by_id(product_id)
    
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    
    # Product details with images, sizes, colors
    text = f"""
🛍️ <b>{product['name']}</b>

💰 <b>Price:</b> ${product['price']:.2f}
📝 <b>Description:</b> {product['description']}

<b>Available Sizes:</b> S, M, L, XL
<b>Available Colors:</b> Red, Blue, Black, White
<b>Stock:</b> {product.get('stock', 'Available')}
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Size S", callback_data=f"size_{product_id}_S"),
            InlineKeyboardButton(text="Size M", callback_data=f"size_{product_id}_M"),
            InlineKeyboardButton(text="Size L", callback_data=f"size_{product_id}_L")
        ],
        [
            InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"add_{product_id}"),
            InlineKeyboardButton(text="❤️ Wishlist", callback_data=f"wishlist_{product_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="shop")
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("size_"))
async def select_size(callback: CallbackQuery):
    """Handle size selection"""
    parts = callback.data.split("_")
    product_id, size = int(parts[1]), parts[2]
    
    # Store user's size preference
    user_preferences = db.get_user_preferences(callback.from_user.id)
    user_preferences[f"product_{product_id}_size"] = size
    db.save_user_preferences(callback.from_user.id, user_preferences)
    
    await callback.answer(f"✅ Size {size} selected!", show_alert=True)
```

### 2. Appointment Booking Bot

```python
# handlers/booking.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

router = Router()

@router.callback_query(F.data == "book_appointment")
async def show_services(callback: CallbackQuery):
    """Show available services"""
    services = [
        {"id": 1, "name": "Haircut", "duration": 30, "price": 25.00},
        {"id": 2, "name": "Hair Coloring", "duration": 90, "price": 80.00},
        {"id": 3, "name": "Manicure", "duration": 45, "price": 35.00},
        {"id": 4, "name": "Facial Treatment", "duration": 60, "price": 60.00}
    ]
    
    text = "💇‍♀️ <b>Select a Service:</b>\n\n"
    keyboard_buttons = []
    
    for service in services:
        text += f"<b>{service['name']}</b>\n"
        text += f"⏱️ {service['duration']} min | 💰 ${service['price']:.2f}\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📅 Book {service['name']}", 
                callback_data=f"service_{service['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data="back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("service_"))
async def show_calendar(callback: CallbackQuery):
    """Show available dates"""
    service_id = int(callback.data.split("_")[1])
    
    # Generate next 14 days
    keyboard_buttons = []
    today = datetime.now()
    
    for i in range(14):
        date = today + timedelta(days=i)
        if date.weekday() < 6:  # Monday to Saturday only
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=date.strftime("%A, %B %d"),
                    callback_data=f"date_{service_id}_{date.strftime('%Y-%m-%d')}"
                )
            ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Services", callback_data="book_appointment")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        "📅 <b>Select a Date:</b>",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("date_"))
async def show_time_slots(callback: CallbackQuery):
    """Show available time slots"""
    parts = callback.data.split("_")
    service_id, selected_date = int(parts[1]), parts[2]
    
    # Generate time slots (9 AM to 6 PM)
    time_slots = []
    start_hour = 9
    end_hour = 18
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:  # Every 30 minutes
            time_str = f"{hour:02d}:{minute:02d}"
            time_slots.append(time_str)
    
    keyboard_buttons = []
    text = f"🕐 <b>Available Times for {selected_date}:</b>\n\n"
    
    # Create rows of 3 time slots each
    for i in range(0, len(time_slots), 3):
        row = []
        for j in range(3):
            if i + j < len(time_slots):
                time_slot = time_slots[i + j]
                row.append(
                    InlineKeyboardButton(
                        text=time_slot,
                        callback_data=f"time_{service_id}_{selected_date}_{time_slot}"
                    )
                )
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Dates", callback_data=f"service_{service_id}")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("time_"))
async def confirm_booking(callback: CallbackQuery):
    """Confirm appointment booking"""
    parts = callback.data.split("_")
    service_id, selected_date, selected_time = int(parts[1]), parts[2], parts[3]
    
    # Get service details
    service = db.get_service_by_id(service_id)  # You'd implement this method
    
    # Create booking
    booking_data = {
        "user_id": callback.from_user.id,
        "service_id": service_id,
        "date": selected_date,
        "time": selected_time,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    # Save booking (implement this method)
    db.save_booking(booking_data)
    
    confirmation_text = f"""
✅ <b>Appointment Confirmed!</b>

👤 <b>Client:</b> {callback.from_user.full_name}
💇‍♀️ <b>Service:</b> {service['name']}
📅 <b>Date:</b> {selected_date}
🕐 <b>Time:</b> {selected_time}
💰 <b>Price:</b> ${service['price']:.2f}

📞 We'll send you a reminder 24 hours before your appointment.

<b>Need to reschedule?</b> Use /mybookings command.
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Book Another", callback_data="book_appointment")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back")]
    ])
    
    await callback.message.edit_text(confirmation_text, reply_markup=keyboard)
    await callback.answer()
```

### 3. Educational Course Platform

```python
# handlers/courses.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(F.data == "courses")
async def show_courses(callback: CallbackQuery):
    """Show available courses"""
    courses = [
        {
            "id": 1, 
            "name": "Python Programming", 
            "lessons": 12, 
            "duration": "6 weeks",
            "price": 99.00,
            "level": "Beginner"
        },
        {
            "id": 2, 
            "name": "Web Development", 
            "lessons": 15, 
            "duration": "8 weeks",
            "price": 149.00,
            "level": "Intermediate"
        },
        {
            "id": 3, 
            "name": "Data Science", 
            "lessons": 20, 
            "duration": "10 weeks",
            "price": 199.00,
            "level": "Advanced"
        }
    ]
    
    text = "📚 <b>Available Courses:</b>\n\n"
    keyboard_buttons = []
    
    for course in courses:
        text += f"<b>{course['name']}</b>\n"
        text += f"📊 Level: {course['level']}\n"
        text += f"📖 {course['lessons']} lessons\n"
        text += f"⏰ Duration: {course['duration']}\n"
        text += f"💰 Price: ${course['price']:.2f}\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📖 View {course['name']}",
                callback_data=f"course_{course['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data="back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("course_"))
async def show_course_details(callback: CallbackQuery):
    """Show detailed course information"""
    course_id = int(callback.data.split("_")[1])
    
    # Get course details and user progress
    course = db.get_course_by_id(course_id)
    user_progress = db.get_user_course_progress(callback.from_user.id, course_id)
    
    text = f"""
📚 <b>{course['name']}</b>

📊 <b>Level:</b> {course['level']}
📖 <b>Lessons:</b> {course['lessons']}
⏰ <b>Duration:</b> {course['duration']}
💰 <b>Price:</b> ${course['price']:.2f}

<b>📈 Your Progress:</b>
Completed: {user_progress.get('completed_lessons', 0)}/{course['lessons']} lessons
Progress: {(user_progress.get('completed_lessons', 0) / course['lessons'] * 100):.1f}%

<b>📝 Course Description:</b>
{course.get('description', 'Learn the fundamentals and advance your skills.')}
    """
    
    keyboard_buttons = []
    
    if user_progress.get('enrolled', False):
        keyboard_buttons.extend([
            [InlineKeyboardButton(text="▶️ Continue Learning", callback_data=f"lessons_{course_id}")],
            [InlineKeyboardButton(text="📊 View Progress", callback_data=f"progress_{course_id}")]
        ])
    else:
        keyboard_buttons.append([
            InlineKeyboardButton(text="🎓 Enroll Now", callback_data=f"enroll_{course_id}")
        ])
    
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="📖 Preview Lessons", callback_data=f"preview_{course_id}")],
        [InlineKeyboardButton(text="⬅️ Back to Courses", callback_data="courses")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("lessons_"))
async def show_lessons(callback: CallbackQuery):
    """Show course lessons"""
    course_id = int(callback.data.split("_")[1])
    
    lessons = db.get_course_lessons(course_id)
    user_progress = db.get_user_course_progress(callback.from_user.id, course_id)
    completed_lessons = user_progress.get('completed_lessons_ids', [])
    
    text = f"📖 <b>Course Lessons:</b>\n\n"
    keyboard_buttons = []
    
    for i, lesson in enumerate(lessons, 1):
        status = "✅" if lesson['id'] in completed_lessons else "🔒" if i > 1 and lessons[i-2]['id'] not in completed_lessons else "▶️"
        text += f"{status} <b>Lesson {i}:</b> {lesson['title']}\n"
        
        if lesson['id'] in completed_lessons or (i == 1) or (i > 1 and lessons[i-2]['id'] in completed_lessons):
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"📖 {lesson['title']}", 
                    callback_data=f"lesson_{course_id}_{lesson['id']}"
                )
            ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Course", callback_data=f"course_{course_id}")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
```

### 4. Enhanced Database Helper for Multiple Business Types

```python
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
```

### 5. Business Type Adapter

```python
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
```

---

## Quick Business Type Setup

### 1. Restaurant Setup (Default)
```bash
# No changes needed - already configured
python main.py
```

### 2. E-commerce Shop Setup
```python
# In your main.py, add this at the top:
from utils.business_adapter import BusinessAdapter
adapter = BusinessAdapter("shop")

# Update your handlers to use:
# - adapter.get_item_type() instead of hardcoded "menu"
# - adapter.get_main_categories() for categories
# - adapter.get_main_actions() for buttons
```

### 3. Appointment Booking Setup
```python
# Add booking-specific handlers
from handlers.booking import router as booking_router
dp.include_router(booking_router)

# Set business type
adapter = BusinessAdapter("booking")
```

### 4. Education Platform Setup
```python
# Add course-specific handlers  
from handlers.courses import router as courses_router
dp.include_router(courses_router)

# Set business type
adapter = BusinessAdapter("education")
```

---

## Testing Your Bot

### Unit Test Example (`tests/test_handlers.py`)
```python
import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import User, Chat, Message, CallbackQuery

from handlers.start import start_handler
from handlers.menu import show_menu_categories

@pytest.mark.asyncio
async def test_start_handler(mock_message):
    """Test start command handler"""
    await start_handler(mock_message)
    
    # Verify that answer was called
    mock_message.answer.assert_called_once()
    
    # Check if welcome message contains user name
    args, kwargs = mock_message.answer.call_args
    assert "Test" in args[0]  # User's first name should be in message
    assert "Welcome" in args[0]
    assert kwargs.get("reply_markup") is not None  # Should have keyboard

@pytest.mark.asyncio
async def test_menu_callback(mock_callback):
    """Test menu callback handler"""
    await show_menu_categories(mock_callback)
    
    # Verify callback was answered and message was edited
    mock_callback.answer.assert_called_once()
    mock_callback.message.edit_text.assert_called_once()
    
    # Check if menu categories are shown
    args, kwargs = mock_callback.message.edit_text.call_args
    assert "Choose a category" in args[0]
    assert kwargs.get("reply_markup") is not None

# Run tests with: python -m pytest tests/
```

### Load Testing (`tests/load_test.py`)
```python
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def send_webhook_request(session, bot_token, user_id, text):
    """Send a webhook request to simulate user interaction"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": user_id,
        "text": text
    }
    
    async with session.post(url, json=data) as response:
        return await response.json()

async def load_test(bot_token, num_requests=100):
    """Run load test with multiple concurrent requests"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()
        
        for i in range(num_requests):
            user_id = 123456789 + i  # Different user IDs
            task = send_webhook_request(session, bot_token, user_id, "/start")
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = len(results) - successful
        
        print(f"Load Test Results:")
        print(f"Total Requests: {num_requests}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Requests/second: {num_requests/duration:.2f}")

# Usage:
# asyncio.run(load_test("YOUR_BOT_TOKEN", 50))
```

---

## Production Deployment

### Environment Configuration

Create `.env.production`:
```env
BOT_TOKEN=your_production_bot_token
ADMIN_ID=your_telegram_id
WEBHOOK_URL=https://yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/botdb
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

### Production Database Setup

For production, use PostgreSQL instead of JSON:

```python
# database/postgres_helper.py
import asyncpg
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class PostgresDatabaseHelper:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def init_pool(self):
        """Initialize connection pool"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        await self.create_tables()
    
    async def create_tables(self):
        """Create necessary tables"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(id),
                    items JSONB,
                    total DECIMAL(10,2),
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(id),
                    service_id INTEGER,
                    booking_date DATE,
                    booking_time TIME,
                    status TEXT DEFAULT 'confirmed',
                    created_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS user_progress (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(id),
                    course_id INTEGER,
                    completed_lessons JSONB DEFAULT '[]',
                    progress_percentage DECIMAL(5,2) DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
                CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
            ''')
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1", user_id
            )
            return dict(row) if row else None
    
    async def create_or_update_user(self, user_data: Dict[str, Any]):
        """Create or update user"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (id, first_name, last_name, username, updated_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (id) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    username = EXCLUDED.username,
                    updated_at = NOW()
            ''', user_data['id'], user_data.get('first_name'), 
                user_data.get('last_name'), user_data.get('username'))
    
    async def create_order(self, user_id: int, items: Dict, total: float) -> int:
        """Create new order"""
        async with self.pool.acquire() as conn:
            order_id = await conn.fetchval('''
                INSERT INTO orders (user_id, items, total)
                VALUES ($1, $2, $3) RETURNING id
            ''', user_id, json.dumps(items), total)
            return order_id
    
    async def get_user_orders(self, user_id: int) -> List[Dict]:
        """Get user's orders"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
                user_id
            )
            return [dict(row) for row in rows]
    
    async def close_pool(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()

# Usage in main.py:
# if os.getenv('DATABASE_URL'):
#     db = PostgresDatabaseHelper(os.getenv('DATABASE_URL'))
#     await db.init_pool()
```

### Redis Caching Setup

```python
# utils/cache.py
import redis.asyncio as redis
import json
import os
from typing import Any, Optional

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def init_redis(self):
        """Initialize Redis connection"""
        self.redis_client = redis.from_url(self.redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache with expiration"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.setex(
                key, expire, json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

# Global cache instance
cache = CacheManager(os.getenv('REDIS_URL', 'redis://localhost:6379'))

# Usage in handlers:
# # Cache user's cart
# await cache.set(f"cart:{user_id}", cart_data, expire=1800)  # 30 minutes
# 
# # Get cached cart
# cached_cart = await cache.get(f"cart:{user_id}")
```

### Monitoring and Logging

```python
# utils/monitoring.py
import logging
import time
from functools import wraps
from typing import Callable
from aiogram.types import Update
import os

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(funcName)s:%(lineno)d'
)

logger = logging.getLogger(__name__)

class BotMetrics:
    def __init__(self):
        self.total_messages = 0
        self.total_callbacks = 0
        self.user_sessions = {}
        self.error_count = 0
        self.start_time = time.time()
    
    def log_message(self, user_id: int):
        """Log incoming message"""
        self.total_messages += 1
        self.user_sessions[user_id] = time.time()
        logger.info(f"Message from user {user_id}. Total messages: {self.total_messages}")
    
    def log_callback(self, user_id: int, callback_data: str):
        """Log callback query"""
        self.total_callbacks += 1
        logger.info(f"Callback '{callback_data}' from user {user_id}")
    
    def log_error(self, error: Exception, user_id: int = None):
        """Log error"""
        self.error_count += 1
        logger.error(f"Error occurred for user {user_id}: {error}", exc_info=True)
    
    def get_stats(self) -> dict:
        """Get bot statistics"""
        uptime = time.time() - self.start_time
        return {
            "uptime_seconds": uptime,
            "total_messages": self.total_messages,
            "total_callbacks": self.total_callbacks,
            "active_users": len(self.user_sessions),
            "error_count": self.error_count,
            "messages_per_hour": (self.total_messages / uptime) * 3600 if uptime > 0 else 0
        }

# Global metrics instance
metrics = BotMetrics()

# Decorator for monitoring handler performance
def monitor_performance(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Handler {func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Handler {func.__name__} failed after {duration:.3f}s: {e}")
            metrics.log_error(e)
            raise
    return wrapper

# Middleware for automatic monitoring
class MonitoringMiddleware:
    async def __call__(self, handler, event: Update, data: dict):
        # Log the event
        if event.message:
            metrics.log_message(event.message.from_user.id)
        elif event.callback_query:
            metrics.log_callback(
                event.callback_query.from_user.id, 
                event.callback_query.data
            )
        
        # Process the event
        try:
            return await handler(event, data)
        except Exception as e:
            user_id = None
            if event.message:
                user_id = event.message.from_user.id
            elif event.callback_query:
                user_id = event.callback_query.from_user.id
            
            metrics.log_error(e, user_id)
            raise

# Usage in main.py:
# dp.middleware.setup(MonitoringMiddleware())
```

### Health Check Endpoint

```python
# utils/health_check.py
from aiohttp import web
from utils.monitoring import metrics
import json

async def health_check(request):
    """Health check endpoint"""
    stats = metrics.get_stats()
    
    # Add additional health checks
    health_status = {
        "status": "healthy",
        "timestamp": int(time.time()),
        "bot_stats": stats,
        "database": await check_database_health(),
        "cache": await check_cache_health()
    }
    
    return web.json_response(health_status)

async def check_database_health():
    """Check database connectivity"""
    try:
        # Add your database health check here
        # For JSON file database:
        import os
        if os.path.exists("database/data.json"):
            return {"status": "healthy", "type": "json_file"}
        else:
            return {"status": "unhealthy", "error": "database_file_missing"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

async def check_cache_health():
    """Check cache connectivity"""
    try:
        from utils.cache import cache
        if cache.redis_client:
            await cache.redis_client.ping()
            return {"status": "healthy", "type": "redis"}
        else:
            return {"status": "disabled", "type": "none"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Add to webhook.py:
# app.router.add_get('/health', health_check)
```

### Deployment Scripts

Create `deploy.sh`:
```bash
#!/bin/bash

# Deployment script for production

set -e

echo "🚀 Starting deployment..."

# Pull latest code
git pull origin main

# Build Docker image
docker-compose build

# Backup database (if using file-based storage)
if [ -f "database/data.json" ]; then
    cp database/data.json database/data.json.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Database backed up"
fi

# Stop existing container
docker-compose down

# Start new container
docker-compose up -d

# Wait for health check
echo "⏳ Waiting for bot to start..."
sleep 10

# Check if bot is healthy
HEALTH_STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
if [ "$HEALTH_STATUS" = "healthy" ]; then
    echo "✅ Deployment successful! Bot is healthy."
else
    echo "❌ Deployment failed! Bot is not healthy."
    exit 1
fi

echo "🎉 Deployment completed successfully!"
```

### Docker Production Setup

Update `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_ID=${ADMIN_ID}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - LOG_LEVEL=INFO
    volumes:
      - ./database:/app/database
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - redis
      - postgres
    networks:
      - bot-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=botdb
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - bot-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - bot-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - telegram-bot
    restart: unless-stopped
    networks:
      - bot-network

volumes:
  postgres_data:
  redis_data:

networks:
  bot-network:
    driver: bridge
```

### Nginx Configuration

Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream bot {
        server telegram-bot:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=bot_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Webhook endpoint
        location /webhook {
            limit_req zone=bot_limit burst=20 nodelay;
            proxy_pass http://bot;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://bot;
        }

        # Block other endpoints
        location / {
            return 404;
        }
    }
}
```

---

## Scaling and Performance Optimization

### 1. Database Connection Pooling

```python
# database/connection_pool.py
import asyncpg
import asyncio
from typing import Optional

class DatabasePool:
    def __init__(self, database_url: str, min_size: int = 10, max_size: int = 20):
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def create_pool(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=60,
            server_settings={
                'jit': 'off'  # Disable JIT for better connection reuse
            }
        )
    
    async def execute_query(self, query: str, *args):
        """Execute a query"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_transaction(self, queries: list):
        """Execute multiple queries in a transaction"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                results = []
                for query, args in queries:
                    result = await conn.fetch(query, *args)
                    results.append(result)
                return results
    
    async def close_pool(self):
        """Close the pool"""
        if self.pool:
            await self.pool.close()

# Usage:
# db_pool = DatabasePool(DATABASE_URL)
# await db_pool.create_pool()
```

### 2. Message Queue for Heavy Operations

```python
# utils/task_queue.py
import asyncio
import json
from typing import Any, Dict, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Task:
    id: str
    type: str
    data: Dict[str, Any]
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.handlers: Dict[str, Callable] = {}
        self.running = False
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a task handler"""
        self.handlers[task_type] = handler
    
    async def add_task(self, task_type: str, data: Dict[str, Any]) -> str:
        """Add a task to the queue"""
        task_id = f"{task_type}_{int(datetime.now().timestamp())}"
        task = Task(
            id=task_id,
            type=task_type,
            data=data,
            created_at=datetime.now()
        )
        await self.queue.put(task)
        return task_id
    
    async def process_tasks(self):
        """Process tasks from the queue"""
        self.running = True
        while self.running:
            try:
                # Wait for a task with timeout
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                
                if task.type in self.handlers:
                    try:
                        await self.handlers[task.type](task.data)
                        print(f"✅ Task {task.id} completed")
                    except Exception as e:
                        task.attempts += 1
                        if task.attempts < task.max_attempts:
                            # Retry the task
                            await self.queue.put(task)
                            print(f"🔄 Task {task.id} failed, retrying ({task.attempts}/{task.max_attempts})")
                        else:
                            print(f"❌ Task {task.id} failed permanently: {e}")
                else:
                    print(f"⚠️ No handler for task type: {task.type}")
                
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                print(f"Error processing task: {e}")
    
    async def stop(self):
        """Stop the task processor"""
        self.running = False
        await self.queue.join()  # Wait for all tasks to complete

# Example usage:
task_queue = TaskQueue()

# Register handlers
async def send_notification_handler(data: Dict[str, Any]):
    """Handle notification sending"""
    user_id = data['user_id']
    message = data['message']
    # Send notification logic here
    await asyncio.sleep(1)  # Simulate work
    print(f"Notification sent to user {user_id}: {message}")

async def process_order_handler(data: Dict[str, Any]):
    """Handle order processing"""
    order_id = data['order_id']
    # Process order logic here
    await asyncio.sleep(2)  # Simulate work
    print(f"Order {order_id} processed")

task_queue.register_handler('send_notification', send_notification_handler)
task_queue.register_handler('process_order', process_order_handler)

# In your main application:
# # Start task processor
# asyncio.create_task(task_queue.process_tasks())
# 
# # Add tasks
# await task_queue.add_task('send_notification', {
#     'user_id': 123456789,
#     'message': 'Your order is ready!'
# })
```

### 3. Rate Limiting

```python
# utils/rate_limiter.py
import time
from typing import Dict, Optional
from dataclasses import dataclass, field

@dataclass
class RateLimitBucket:
    tokens: int
    last_refill: float = field(default_factory=time.time)
    max_tokens: int = 10
    refill_rate: float = 1.0  # tokens per second

class RateLimiter:
    def __init__(self):
        self.buckets: Dict[int, RateLimitBucket] = {}
    
    def is_allowed(self, user_id: int, tokens_required: int = 1) -> bool:
        """Check if user is allowed to perform action"""
        current_time = time.time()
        
        if user_id not in self.buckets:
            self.buckets[user_id] = RateLimitBucket(tokens=10)
        
        bucket = self.buckets[user_id]
        
        # Refill tokens based on time passed
        time_passed = current_time - bucket.last_refill
        tokens_to_add = int(time_passed * bucket.refill_rate)
        
        if tokens_to_add > 0:
            bucket.tokens = min(bucket.max_tokens, bucket.tokens + tokens_to_add)
            bucket.last_refill = current_time
        
        # Check if enough tokens available
        if bucket.tokens >= tokens_required:
            bucket.tokens -= tokens_required
            return True
        
        return False
    
    def get_wait_time(self, user_id: int, tokens_required: int = 1) -> float:
        """Get wait time until user can perform action"""
        if user_id not in self.buckets:
            return 0.0
        
        bucket = self.buckets[user_id]
        if bucket.tokens >= tokens_required:
            return 0.0
        
        tokens_needed = tokens_required - bucket.tokens
        return tokens_needed / bucket.refill_rate

# Global rate limiter
rate_limiter = RateLimiter()

# Middleware for rate limiting
class RateLimitMiddleware:
    async def __call__(self, handler, event, data):
        user_id = None
        
        if event.message:
            user_id = event.message.from_user.id
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
        
        if user_id and not rate_limiter.is_allowed(user_id):
            wait_time = rate_limiter.get_wait_time(user_id)
            
            if event.message:
                await event.message.answer(
                    f"⏳ Too many requests! Please wait {wait_time:.1f} seconds."
                )
            elif event.callback_query:
                await event.callback_query.answer(
                    f"Too many requests! Wait {wait_time:.1f}s", 
                    show_alert=True
                )
            return
        
        return await handler(event, data)

# Usage in main.py:
# dp.middleware.setup(RateLimitMiddleware())
```

---

## Final Deployment Checklist

### Pre-Deployment
- [ ] **Environment variables configured**
- [ ] **Database properly set up and migrated**  
- [ ] **Redis cache configured (if using)**
- [ ] **SSL certificates installed**
- [ ] **Domain/subdomain configured**
- [ ] **Webhook URL tested**
- [ ] **Load testing completed**
- [ ] **Error handling tested**
- [ ] **Backup strategy implemented**

### Security
- [ ] **Bot token secured**
- [ ] **Admin access restricted**
- [ ] **Rate limiting enabled**
- [ ] **Input validation implemented**
- [ ] **SQL injection protection**
- [ ] **HTTPS enforced**
- [ ] **Firewall configured**

### Monitoring
- [ ] **Logging configured**
- [ ] **Health checks implemented**
- [ ] **Performance monitoring**
- [ ] **Error alerting**
- [ ] **Usage analytics**

### Post-Deployment
- [ ] **Bot functionality tested**
- [ ] **Admin panel accessible**
- [ ] **Database operations working**
- [ ] **Cache performance verified**
- [ ] **Monitoring dashboards working**

---

## Conclusion

This comprehensive guide provides everything you need to build, deploy, and scale a production-ready Telegram bot using the latest aiogram version. The modular structure makes it easy to adapt for any business type, from restaurants to e-commerce stores, booking systems to educational platforms.

### Key Benefits of This Approach:
- ✅ **Latest aiogram syntax** - Uses aiogram 3.x with proper routing
- ✅ **Production-ready** - Includes monitoring, caching, and error handling
- ✅ **Scalable architecture** - Easy to extend and modify
- ✅ **Multiple business types** - Adaptable template for various use cases
- ✅ **Comprehensive testing** - Unit tests and load testing included
- ✅ **Docker deployment** - Container-ready with docker-compose
- ✅ **Database flexibility** - JSON for development, PostgreSQL for production

### Next Steps:
1. **Start with the basic bot** and test core functionality
2. **Choose your business type** and customize accordingly  
3. **Add payment integration** for real transactions
4. **Implement advanced features** as needed
5. **Deploy to production** using the provided configurations
6. **Monitor and optimize** based on usage patterns

Remember: Start small, test thoroughly, and scale gradually. This foundation will serve you well for any Telegram bot project!

### Resources:
- **Aiogram Documentation**: https://docs.aiogram.dev/
- **Telegram Bot API**: https://core.telegram.org/bots/api  
- **PostgreSQL**: https://www.postgresql.org/
- **Redis**: https://redis.io/
- **Docker**: https://www.docker.com/fixture
