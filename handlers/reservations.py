from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from database.db_helper import db
from keyboards.main_keyboard import get_main_keyboard


router = Router()


class ReservationStates(StatesGroup):
    """FSM states for managing a table reservation."""

    date = State()
    time = State()
    guests = State()
    name = State()
    phone = State()
    comment = State()
    confirming = State()


def _reservation_cancel_keyboard() -> InlineKeyboardMarkup:
    """Inline keyboard to cancel reservation flow."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="reservation_cancel")],
        ]
    )


async def _start_reservation_for(
    message: Message, state: FSMContext
) -> None:
    """
    Common entry point used both by /reserve command and the main-menu button.
    """
    await state.set_state(ReservationStates.date)
    await message.answer(
        "📅 <b>Stol band qilish</b>\n\n"
        "Iltimos, sana kiriting.\n"
        "Masalan: <code>2026-02-13</code> yoki oddiy «bugun» / «ertaga» deb yozishingiz mumkin.",
        reply_markup=_reservation_cancel_keyboard(),
    )


@router.message(Command("reserve"))
async def reserve_command(message: Message, state: FSMContext) -> None:
    """Start reservation flow via /reserve command."""
    await _start_reservation_for(message, state)


@router.callback_query(F.data == "reservation")
async def reserve_from_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """Start reservation flow via main menu button."""
    await _start_reservation_for(callback.message, state)
    await callback.answer()


@router.message(ReservationStates.date)
async def reservation_date(message: Message, state: FSMContext) -> None:
    """Capture reservation date (today/tomorrow or YYYY-MM-DD)."""
    text = (message.text or "").strip().lower()

    if text in {"bugun"}:
        from datetime import datetime

        date_str = datetime.utcnow().date().isoformat()
    elif text in {"ertaga"}:
        from datetime import datetime, timedelta

        date_str = (datetime.utcnow().date() + timedelta(days=1)).isoformat()
    else:
        # Minimalistic validation: expect YYYY-MM-DD
        parts = text.split("-")
        if len(parts) != 3 or any(not p.isdigit() for p in parts):
            await message.answer(
                "❗ Sana formati noto‘g‘ri.\n"
                "Iltimos, <code>YYYY-MM-DD</code> formatida yuboring. Masalan: <code>2026-02-13</code>.",
                reply_markup=_reservation_cancel_keyboard(),
            )
            return
        date_str = text

    await state.update_data(date=date_str)
    await state.set_state(ReservationStates.time)

    await message.answer(
        "⏰ <b>Qaysi vaqtda kelmoqchisiz?</b>\n\n"
        "Masalan: <code>19:30</code>",
        reply_markup=_reservation_cancel_keyboard(),
    )


@router.message(ReservationStates.time)
async def reservation_time(message: Message, state: FSMContext) -> None:
    """Capture reservation time (basic string, minimal validation)."""
    time_text = (message.text or "").strip()
    # Minimal validation: require ":" and some digits
    if ":" not in time_text or len(time_text) < 4:
        await message.answer(
            "❗ Vaqt formati noto‘g‘ri.\n"
            "Iltimos, masalan <code>19:30</code> ko‘rinishida yuboring.",
            reply_markup=_reservation_cancel_keyboard(),
        )
        return

    await state.update_data(time=time_text)
    await state.set_state(ReservationStates.guests)

    await message.answer(
        "👥 <b>Necha kishi uchun stol band qilmoqchisiz?</b>\n\n"
        "Faqat raqam yuboring. Masalan: <code>4</code>",
        reply_markup=_reservation_cancel_keyboard(),
    )


@router.message(ReservationStates.guests)
async def reservation_guests(message: Message, state: FSMContext) -> None:
    """Capture the number of guests."""
    try:
        guests = int((message.text or "").strip())
    except ValueError:
        await message.answer(
            "❗ Faqat raqam yuboring. Masalan: <code>4</code>.",
            reply_markup=_reservation_cancel_keyboard(),
        )
        return

    if guests <= 0:
        await message.answer(
            "❗ Mehmonlar soni 1 yoki undan katta bo‘lishi kerak.",
            reply_markup=_reservation_cancel_keyboard(),
        )
        return

    await state.update_data(guests=guests)
    await state.set_state(ReservationStates.name)

    await message.answer(
        "🧾 <b>Ismingizni yozing</b>\n\n"
        "Agar Telegram ismingiz bo‘yicha band qilinsin desangiz, shunchaki ismingizni yozing.",
        reply_markup=_reservation_cancel_keyboard(),
    )


@router.message(ReservationStates.name)
async def reservation_name(message: Message, state: FSMContext) -> None:
    """Capture customer name."""
    name = (message.text or "").strip() or message.from_user.full_name
    await state.update_data(name=name)
    await state.set_state(ReservationStates.phone)

    await message.answer(
        "📞 <b>Telefon raqamingizni yuboring</b>\n\n"
        "Masalan: “+998 90 123 45 67”.",
        reply_markup=_reservation_cancel_keyboard(),
    )


@router.message(ReservationStates.phone)
async def reservation_phone(message: Message, state: FSMContext) -> None:
    """Capture phone number and proceed to comment."""
    phone = (message.text or "").strip()
    await state.update_data(phone=phone)
    db.update_user_phone(message.from_user.id, phone)

    await state.set_state(ReservationStates.comment)

    await message.answer(
        "✏️ <b>Qo‘shimcha izoh (ixtiyoriy)</b>\n\n"
        "Masalan: “Deraza yonidagi stol bo‘lsin”, “Bolalar aravachasi uchun joy kerak” va hokazo.\n\n"
        "Agar izoh bo‘lmasa, shunchaki “yo‘q” deb yozing.",
        reply_markup=_reservation_cancel_keyboard(),
    )


@router.message(ReservationStates.comment)
async def reservation_comment(message: Message, state: FSMContext) -> None:
    """Capture optional comment and ask for confirmation."""
    raw_comment = (message.text or "").strip()
    comment = None if raw_comment.lower() in {"yo'q", "yo‘q", "y", "yoq"} else raw_comment

    await state.update_data(comment=comment)
    data = await state.get_data()

    lines = [
        "✅ <b>Rezervatsiyani tasdiqlash</b>\n",
        f"<b>Sana:</b> {data.get('date')}",
        f"<b>Vaqt:</b> {data.get('time')}",
        f"<b>Mehmonlar soni:</b> {data.get('guests')}",
        f"<b>Ism:</b> {data.get('name')}",
        f"<b>Telefon:</b> {data.get('phone')}",
    ]
    if comment:
        lines.append(f"<b>Izoh:</b> {comment}")

    lines.append("\nAgar ma’lumotlar to‘g‘ri bo‘lsa, «Tasdiqlash» tugmasini bosing.")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data="confirm_reservation"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish", callback_data="reservation_cancel"
                ),
            ]
        ]
    )

    await state.set_state(ReservationStates.confirming)
    await message.answer("\n".join(lines), reply_markup=keyboard)


@router.callback_query(ReservationStates.confirming, F.data == "confirm_reservation")
async def reservation_confirm(callback: CallbackQuery, state: FSMContext) -> None:
    """Persist reservation, notify admin, and thank the user."""
    data = await state.get_data()
    user_id = callback.from_user.id

    reservation = db.create_reservation(
        user_id=user_id,
        date=data["date"],
        time=data["time"],
        guests=int(data["guests"]),
        name=data["name"],
        phone=data["phone"],
        comment=data.get("comment"),
    )

    await state.clear()

    # Notify user
    await callback.message.edit_text(
        "🎉 <b>Stol muvaffaqiyatli band qilindi!</b>\n\n"
        f"📄 Rezervatsiya raqami: <b>#{reservation['id']}</b>\n"
        f"📅 Sana: <b>{reservation['date']}</b>\n"
        f"⏰ Vaqt: <b>{reservation['time']}</b>\n"
        f"👥 Mehmonlar soni: <b>{reservation['guests']}</b>",
        reply_markup=get_main_keyboard(),
    )
    await callback.answer()

    # Notify admin
    admin_lines = [
        f"📌 <b>Yangi rezervatsiya #{reservation['id']}</b>",
        f"👤 User ID: <code>{user_id}</code>",
        f"👤 Ism: {reservation['name']}",
        f"📱 Telefon: {reservation['phone']}",
        "",
        f"📅 Sana: {reservation['date']}",
        f"⏰ Vaqt: {reservation['time']}",
        f"👥 Mehmonlar soni: {reservation['guests']}",
    ]
    if reservation.get("comment"):
        admin_lines.append(f"✏️ Izoh: {reservation['comment']}")

    admin_text = "\n".join(admin_lines)

    try:
        await callback.message.bot.send_message(
            chat_id=config.admin_id,
            text=admin_text,
        )
    except Exception:
        # Avoid breaking user flow if admin notification fails.
        pass


@router.callback_query(
    StateFilter(
        ReservationStates.date,
        ReservationStates.time,
        ReservationStates.guests,
        ReservationStates.name,
        ReservationStates.phone,
        ReservationStates.comment,
        ReservationStates.confirming,
    ),
    F.data == "reservation_cancel",
)
async def reservation_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    """Allow user to cancel reservation at any step."""
    await state.clear()
    await callback.message.edit_text(
        "❌ Rezervatsiya bekor qilindi.\n\n"
        "Keyinroq qaytadan urinish mumkin.",
        reply_markup=get_main_keyboard(),
    )
    await callback.answer()

