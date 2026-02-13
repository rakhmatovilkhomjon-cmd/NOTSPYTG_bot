from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db_helper import db


router = Router()


def _profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Oxirgi buyurtmalar", callback_data="profile_orders"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Rezervatsiyalarim", callback_data="profile_reservations"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Bosh menyuga qaytish", callback_data="back"
                )
            ],
        ]
    )


@router.message(Command("profile"))
@router.callback_query(F.data == "profile")
async def show_profile(event) -> None:
    """
    Show basic profile, loyalty, and quick links to history.

    Works for both /profile command (Message) and main-menu button (CallbackQuery).
    """
    if isinstance(event, Message):
        message = event
        user = event.from_user
    else:
        callback: CallbackQuery = event
        message = callback.message
        user = callback.from_user
        await callback.answer()

    profile = db.get_user_profile(user.id)

    text_lines = [
        "👤 <b>Profil</b>\n",
        f"<b>Ism:</b> {profile.get('full_name') or user.full_name}",
        f"<b>Username:</b> @{(profile.get('username') or user.username or '—')}",
        f"<b>Telefon:</b> {profile.get('phone') or '—'}",
        "",
        "<b>Sodiqlik dasturi</b>",
        f"💰 Jami xarajatlar: ${profile.get('total_spent', 0.0):.2f}",
        f"⭐ Bonus ballar: {profile.get('points', 0)}",
    ]

    await message.answer("\n".join(text_lines), reply_markup=_profile_keyboard())


@router.callback_query(F.data == "profile_orders")
async def profile_orders(callback: CallbackQuery) -> None:
    """Show last few orders for the user."""
    orders = db.list_user_orders(callback.from_user.id, limit=5)

    if not orders:
        await callback.message.edit_text(
            "📦 Sizda hali hech qanday buyurtma yo‘q.",
            reply_markup=_profile_keyboard(),
        )
        await callback.answer()
        return

    lines = ["📦 <b>Oxirgi buyurtmalaringiz</b>\n"]

    for order in orders:
        lines.append(f"🧾 Buyurtma #{order['id']} — ${order['total']:.2f}")
        lines.append(f"📅 {order.get('created_at', '')}")
        lines.append(f"📌 Holat: {order.get('status', 'new')}")
        item_names = []
        for item in order["items"]:
            menu_item = db.get_item_by_id(int(item["item_id"]))
            name = menu_item.get("name") if menu_item else f"ID {item['item_id']}"
            item_names.append(f"{name} x{item['quantity']}")
        if item_names:
            lines.append("• " + ", ".join(item_names))
        lines.append("")  # blank line between orders

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=_profile_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "profile_reservations")
async def profile_reservations(callback: CallbackQuery) -> None:
    """Show recent reservations for the user."""
    reservations = db.list_user_reservations(callback.from_user.id, limit=5)

    if not reservations:
        await callback.message.edit_text(
            "📅 Sizda hozircha aktiv rezervatsiyalar yo‘q.",
            reply_markup=_profile_keyboard(),
        )
        await callback.answer()
        return

    lines = ["📅 <b>Rezervatsiyalar tarixi</b>\n"]

    for r in reservations:
        lines.append(f"📄 #{r['id']} — {r['date']} {r['time']}")
        lines.append(f"👥 Mehmonlar: {r['guests']}")
        lines.append(f"📌 Holat: {r.get('status', 'new')}")
        if r.get("comment"):
            lines.append(f"✏️ Izoh: {r['comment']}")
        lines.append("")  # blank line

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=_profile_keyboard(),
    )
    await callback.answer()

