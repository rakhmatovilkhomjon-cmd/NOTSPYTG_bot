from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from database.db_helper import db


router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id == config.admin_id


def _admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Bugungi buyurtmalar", callback_data="admin_today_orders"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⚙️ Qabul qilish holati", callback_data="admin_toggle_open"
                )
            ],
        ]
    )


@router.message(Command("admin"))
async def admin_entry(message: Message) -> None:
    """Entry point for admin panel via /admin command."""
    if not _is_admin(message.from_user.id):
        await message.answer("⛔ Sizda admin huquqlari mavjud emas.")
        return

    settings = db.data.get("settings", {})
    is_open = settings.get("is_open", True)
    status_text = "🟢 Buyurtmalar qabul qilinmoqda" if is_open else "🔴 Buyurtmalar vaqtincha to‘xtatilgan"

    await message.answer(
        f"👨‍🍳 <b>Admin panel</b>\n\n{status_text}",
        reply_markup=_admin_main_keyboard(),
    )


@router.callback_query(F.data == "admin_today_orders")
async def admin_today_orders(callback: CallbackQuery) -> None:
    """Show today's orders to the admin."""
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return

    orders = db.list_orders_for_today()
    if not orders:
        await callback.message.edit_text(
            "📦 Bugun hali buyurtmalar yo‘q.",
            reply_markup=_admin_main_keyboard(),
        )
        await callback.answer()
        return

    lines = ["📦 <b>Bugungi buyurtmalar</b>\n"]

    for order in orders:
        lines.append(f"🧾 #{order['id']} — ${order['total']:.2f}")
        lines.append(f"👤 User ID: <code>{order['user_id']}</code>")
        lines.append(f"📅 {order.get('created_at', '')}")
        lines.append(f"📌 Holat: {order.get('status', 'new')}")
        lines.append("")  # blank line

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=_admin_main_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin_toggle_open")
async def admin_toggle_open(callback: CallbackQuery) -> None:
    """Toggle whether the restaurant is currently accepting orders."""
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return

    settings = db.data.setdefault("settings", {})
    current = settings.get("is_open", True)
    settings["is_open"] = not current
    db.save_data()

    new_status_text = (
        "🟢 Endi buyurtmalar qabul qilinmoqda."
        if settings["is_open"]
        else "🔴 Buyurtmalar vaqtincha to‘xtatildi."
    )

    await callback.message.edit_text(
        f"⚙️ Qabul qilish holati o‘zgartirildi.\n\n{new_status_text}",
        reply_markup=_admin_main_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_status_"))
async def admin_change_order_status(callback: CallbackQuery) -> None:
    """
    Handle order status change callbacks.

    Callback data format: order_status_<order_id>_<new_status>
    Example: order_status_3_accepted
    """
    if not _is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo‘q", show_alert=True)
        return

    try:
        _, _, order_id_str, new_status = callback.data.split("_", maxsplit=3)
        order_id = int(order_id_str)
    except ValueError:
        await callback.answer("Noto‘g‘ri buyurtma identifikatori.", show_alert=True)
        return

    order = db.update_order_status(order_id, new_status)
    if not order:
        await callback.answer("Buyurtma topilmadi.", show_alert=True)
        return

    await callback.answer("Holat yangilandi.")

