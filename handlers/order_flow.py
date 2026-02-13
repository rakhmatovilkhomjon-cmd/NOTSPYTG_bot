from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from database.db_helper import db, OrderItem
from keyboards.main_keyboard import get_main_keyboard


router = Router()


class CheckoutStates(StatesGroup):
    """FSM states for the checkout flow."""

    choosing_type = State()
    entering_address = State()
    entering_phone = State()
    entering_comment = State()
    confirming = State()


def _checkout_cancel_keyboard() -> InlineKeyboardMarkup:
    """Small helper for a cancel/back keyboard used during checkout."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="checkout_cancel")],
            [InlineKeyboardButton(text="⬅️ Savatchaga qaytish", callback_data="cart")],
        ]
    )


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Entry point for checkout from the cart.

    1) Validates cart, restaurant open status, and minimal order amount.
    2) Asks user to choose delivery vs pickup.
    """
    user_id = callback.from_user.id
    cart = db.get_cart(user_id)

    if not cart["items"]:
        await callback.answer("Savatchingiz bo‘sh!", show_alert=True)
        return

    settings = db.data.get("settings", {})
    if not settings.get("is_open", True):
        await callback.answer(
            "⚠️ Hozircha buyurtmalar qabul qilinmayapti. Iltimos, birozdan so‘ng urinib ko‘ring.",
            show_alert=True,
        )
        return

    min_order = float(settings.get("min_order", 0.0))
    if cart["total"] < min_order:
        await callback.answer(
            f"⚠️ Minimal buyurtma summasi ${min_order:.2f}. "
            f"Hozir sizning buyurtmangiz ${cart['total']:.2f}. "
            "Iltimos, yana biror taom qo‘shing.",
            show_alert=True,
        )
        return

    # Save/update basic user profile for future loyalty/profile screens
    db.register_or_update_user(
        user_id=user_id,
        full_name=callback.from_user.full_name,
        username=callback.from_user.username,
    )

    await state.set_state(CheckoutStates.choosing_type)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚚 Yetkazib berish", callback_data="delivery_type_delivery"
                ),
                InlineKeyboardButton(
                    text="🏃‍♂️ Olib ketaman", callback_data="delivery_type_pickup"
                ),
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="checkout_cancel")],
        ]
    )

    await callback.message.edit_text(
        "🚀 <b>Buyurtmani rasmiylashtirish</b>\n\n"
        "Iltimos, buyurtma turini tanlang:",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(CheckoutStates.choosing_type, F.data.startswith("delivery_type_"))
async def choose_delivery_type(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle user choice between delivery and pickup."""
    _, _, delivery_type = callback.data.split("_", maxsplit=2)
    await state.update_data(delivery_type=delivery_type)

    if delivery_type == "delivery":
        await state.set_state(CheckoutStates.entering_address)
        await callback.message.edit_text(
            "📍 <b>Manzilni yuboring</b>\n\n"
            "Iltimos, yetkazib berish manzilini matn ko‘rinishida yozing.\n"
            "Masalan: “Toshkent, Chilonzor, 10-daha, 12-uy, 45-xonadon”.",
            reply_markup=_checkout_cancel_keyboard(),
        )
    else:
        # Pickup – skip address and go straight to phone
        await state.set_state(CheckoutStates.entering_phone)
        await callback.message.edit_text(
            "📞 <b>Telefon raqamingizni yuboring</b>\n\n"
            "Masalan: “+998 90 123 45 67”.",
            reply_markup=_checkout_cancel_keyboard(),
        )

    await callback.answer()


@router.message(CheckoutStates.entering_address)
async def enter_address(message: Message, state: FSMContext) -> None:
    """Store delivery address and ask for phone number."""
    address = message.text.strip()
    await state.update_data(address=address)
    await state.set_state(CheckoutStates.entering_phone)

    await message.answer(
        "📞 <b>Telefon raqamingizni yuboring</b>\n\n"
        "Masalan: “+998 90 123 45 67”.",
        reply_markup=_checkout_cancel_keyboard(),
    )


@router.message(CheckoutStates.entering_phone)
async def enter_phone(message: Message, state: FSMContext) -> None:
    """Store phone number and ask for an optional comment."""
    phone = message.text.strip()
    await state.update_data(phone=phone)
    db.update_user_phone(message.from_user.id, phone)

    await state.set_state(CheckoutStates.entering_comment)

    await message.answer(
        "✏️ <b>Qo‘shimcha izoh</b>\n\n"
        "Agar maxsus iltimosingiz bo‘lsa, yozib qoldiring.\n"
        "Masalan: “Pitsani 8 bo‘lakka bo‘ling”, “Piyozsiz” va hokazo.\n\n"
        "Agar izoh bo‘lmasa, shunchaki “yo‘q” deb yozing.",
        reply_markup=_checkout_cancel_keyboard(),
    )


@router.message(CheckoutStates.entering_comment)
async def enter_comment(message: Message, state: FSMContext) -> None:
    """Store optional comment and show final confirmation summary."""
    raw_comment = message.text.strip()
    comment = None if raw_comment.lower() in {"yo'q", "yo‘q", "y", "yoq"} else raw_comment

    await state.update_data(comment=comment)
    data = await state.get_data()

    user_id = message.from_user.id
    cart = db.get_cart(user_id)

    if not cart["items"]:
        # Cart was cleared in the meantime
        await message.answer("Savatchingiz bo‘sh. Iltimos, yana buyurtma tanlang.")
        await state.clear()
        return

    settings = db.data.get("settings", {})
    delivery_fee = float(settings.get("delivery_fee", 2.50))

    # Build order summary
    text_lines = [
        "✅ <b>Buyurtmani tasdiqlash</b>\n",
        "<b>Taomlar:</b>",
    ]

    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if not item:
            continue
        text_lines.append(
            f"• {item['name']} — ${item['price']:.2f} x {quantity} = "
            f"${float(item['price']) * int(quantity):.2f}"
        )

    text_lines.append("")
    text_lines.append(f"<b>Oraliq jami (taomlar):</b> ${cart['total']:.2f}")
    text_lines.append(f"<b>Yetkazib berish:</b> ${delivery_fee:.2f}")
    text_lines.append(f"<b>Umumiy summa:</b> ${cart['total'] + delivery_fee:.2f}\n")

    delivery_type = data.get("delivery_type", "delivery")
    if delivery_type == "delivery":
        text_lines.append("<b>Turi:</b> Yetkazib berish")
        text_lines.append(f"<b>Manzil:</b> {data.get('address')}")
    else:
        text_lines.append("<b>Turi:</b> Olib ketish (self-pickup)")
        text_lines.append("<b>Manzil:</b> Restoran manzili (joyida olib ketish)")

    text_lines.append(f"<b>Telefon:</b> {data.get('phone')}")
    if comment:
        text_lines.append(f"<b>Izoh:</b> {comment}")

    text_lines.append("\nAgar hammasi to‘g‘ri bo‘lsa, «Tasdiqlash» tugmasini bosing.")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data="confirm_order"
                ),
                InlineKeyboardButton(
                    text="❌ Bekor qilish", callback_data="checkout_cancel"
                ),
            ]
        ]
    )

    await state.set_state(CheckoutStates.confirming)
    await message.answer("\n".join(text_lines), reply_markup=keyboard)


@router.callback_query(CheckoutStates.confirming, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext) -> None:
    """Create the order in storage, notify admin, and thank the user."""
    user_id = callback.from_user.id
    data = await state.get_data()

    cart = db.get_cart(user_id)
    if not cart["items"]:
        await callback.answer("Savatchingiz bo‘sh. Iltimos, qaytadan buyurtma qiling.", show_alert=True)
        await state.clear()
        return

    settings = db.data.get("settings", {})
    delivery_fee = float(settings.get("delivery_fee", 2.50))

    # Build OrderItem list from cart
    order_items: list[OrderItem] = []
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if not item:
            continue
        order_items.append(
            OrderItem(
                item_id=item["id"],
                quantity=int(quantity),
                price=float(item["price"]),
            )
        )

    order = db.create_order(
        user_id=user_id,
        items=order_items,
        delivery_type=data.get("delivery_type", "delivery"),
        delivery_address=data.get("address"),
        phone=data.get("phone") or (callback.from_user.username or ""),
        comment=data.get("comment"),
        delivery_fee=delivery_fee,
        discount=0.0,
    )

    # Clear the cart and FSM state
    db.clear_cart(user_id)
    await state.clear()

    # Notify user
    await callback.message.edit_text(
        "🎉 <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"📦 Buyurtma raqami: <b>#{order['id']}</b>\n"
        "📞 Tez orada operatorimiz siz bilan bog‘lanadi.\n"
        "⏱️ Taxminiy yetkazib berish vaqti: 30–45 daqiqa.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back")]
            ]
        ),
    )
    await callback.answer()

    # Notify admin with order details
    admin_text_lines = [
        f"🆕 <b>Yangi buyurtma #{order['id']}</b>",
        f"👤 User ID: <code>{user_id}</code>",
        f"👤 Ism: {callback.from_user.full_name}",
        f"📱 Telefon: {order.get('phone') or '—'}",
        "",
        "<b>Taomlar:</b>",
    ]
    for item in order["items"]:
        menu_item = db.get_item_by_id(int(item["item_id"]))
        name = menu_item.get("name") if menu_item else f"ID {item['item_id']}"
        admin_text_lines.append(
            f"• {name} — ${item['price']:.2f} x {item['quantity']} = "
            f"${item['price'] * item['quantity']:.2f}"
        )

    admin_text_lines.extend(
        [
            "",
            f"<b>Oraliq jami:</b> ${order['subtotal']:.2f}",
            f"<b>Yetkazib berish:</b> ${order['delivery_fee']:.2f}",
            f"<b>Chegirma:</b> ${order['discount']:.2f}",
            f"<b>Umumiy summa:</b> ${order['total']:.2f}",
            "",
        ]
    )

    if order["delivery_type"] == "delivery":
        admin_text_lines.append("<b>Turi:</b> Yetkazib berish")
        admin_text_lines.append(f"<b>Manzil:</b> {order.get('address') or '—'}")
    else:
        admin_text_lines.append("<b>Turi:</b> Olib ketish (self-pickup)")

    if order.get("comment"):
        admin_text_lines.append(f"<b>Izoh:</b> {order['comment']}")

    admin_text = "\n".join(admin_text_lines)

    # Build inline keyboard for changing order status from admin side
    admin_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Qabul qilindi",
                    callback_data=f"order_status_{order['id']}_accepted",
                ),
                InlineKeyboardButton(
                    text="🍳 Tayyorlanmoqda",
                    callback_data=f"order_status_{order['id']}_cooking",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🚚 Yo‘lda",
                    callback_data=f"order_status_{order['id']}_on_the_way",
                ),
                InlineKeyboardButton(
                    text="✔️ Yetkazildi",
                    callback_data=f"order_status_{order['id']}_completed",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Bekor qiling",
                    callback_data=f"order_status_{order['id']}_cancelled",
                )
            ],
        ]
    )

    try:
        await callback.message.bot.send_message(
            chat_id=config.admin_id,
            text=admin_text,
            reply_markup=admin_keyboard,
        )
    except Exception:
        # In development environments admin_id may not be configured correctly.
        # We intentionally swallow errors here to avoid breaking user flow.
        pass


@router.callback_query(
    StateFilter(
        CheckoutStates.choosing_type,
        CheckoutStates.entering_address,
        CheckoutStates.entering_phone,
        CheckoutStates.entering_comment,
        CheckoutStates.confirming,
    ),
    F.data == "checkout_cancel",
)
async def cancel_checkout(callback: CallbackQuery, state: FSMContext) -> None:
    """Allow the user to cancel checkout at any step and return to the main menu."""
    await state.clear()
    await callback.message.edit_text(
        "❌ Buyurtmani rasmiylashtirish bekor qilindi.\n\n"
        "Istalgan vaqtda qaytadan buyurtma berishingiz mumkin.",
        reply_markup=get_main_keyboard(),
    )
    await callback.answer()

