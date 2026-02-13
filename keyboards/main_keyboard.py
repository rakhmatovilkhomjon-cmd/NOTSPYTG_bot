from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard for the restaurant bot."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🍽️ Menyu", callback_data="menu"),
                InlineKeyboardButton(text="🛒 Savatcham", callback_data="cart"),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Rezervatsiya", callback_data="reservation"
                ),
                InlineKeyboardButton(text="👤 Profil", callback_data="profile"),
            ],
            [
                InlineKeyboardButton(text="📞 Aloqa", callback_data="contact"),
                InlineKeyboardButton(text="📍 Manzil", callback_data="location"),
            ],
            [InlineKeyboardButton(text="⏰ Ish vaqti", callback_data="hours")],
        ]
    )
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Create back to main menu keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Bosh menyuga qaytish", callback_data="back"
                )
            ]
        ]
    )
    return keyboard