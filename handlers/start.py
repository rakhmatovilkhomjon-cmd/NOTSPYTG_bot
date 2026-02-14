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