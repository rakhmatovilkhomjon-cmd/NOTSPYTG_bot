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