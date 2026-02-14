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