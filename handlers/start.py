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
        f"👋 Salom, {message.from_user.full_name}!\n"
        f"Restoran botimizga xush kelibsiz!\n\n"
        f"Men sizga quyidagilarda yordam bera olaman:\n"
        f"🍽️ Menyudan taomlarni ko‘rish\n"
        f"📞 Aloqa ma’lumotlarini olish\n"
        f"📍 Manzilimizni ko‘rish\n"
        f"⏰ Ish vaqtlarini bilib olish",
        reply_markup=get_main_keyboard()
    )