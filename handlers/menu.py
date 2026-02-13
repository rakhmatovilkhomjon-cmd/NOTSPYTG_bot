from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db_helper import db
from keyboards.main_keyboard import get_main_keyboard, get_back_keyboard

# Create router instance
router = Router()


@router.callback_query(F.data == "menu")
async def show_menu_categories(callback: CallbackQuery):
    """Show menu categories."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🍕 Pitsa", callback_data="category_pizza"),
                InlineKeyboardButton(text="🍔 Burgerlar", callback_data="category_burgers"),
            ],
            [
                InlineKeyboardButton(text="🥤 Ichimliklar", callback_data="category_drinks"),
                InlineKeyboardButton(text="🛒 Savatcha", callback_data="cart"),
            ],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")],
        ]
    )

    await callback.message.edit_text(
        "🍽️ <b>Kategoriyani tanlang:</b>",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: CallbackQuery):
    """Show items in selected category."""
    category = callback.data.split("_", maxsplit=1)[1]
    items = db.get_menu_category(category)

    if not items:
        await callback.answer("Bu kategoriya hozircha bo‘sh!", show_alert=True)
        return

    keyboard_buttons = []

    # Category nomini foydalanuvchi uchun qulay ko‘rinishda chiqarish
    if category == "pizza":
        category_title = "Pitsalar"
    elif category == "burgers":
        category_title = "Burgerlar"
    elif category == "drinks":
        category_title = "Ichimliklar"
    else:
        category_title = category.title()

    text = f"🍽️ <b>{category_title}</b>\n\n"

    for item in items:
        text += f"<b>{item['name']}</b> - ${item['price']:.2f}\n"
        text += f"<i>{item['description']}</i>\n\n"

        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text=f"➕ {item['name']}ni qo‘shish",
                    callback_data=f"add_{item['id']}",
                )
            ]
        )

    keyboard_buttons.append(
        [InlineKeyboardButton(text="⬅️ Menyuga qaytish", callback_data="menu")]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    """Add item to cart."""
    item_id = int(callback.data.split("_", maxsplit=1)[1])
    item = db.get_item_by_id(item_id)

    if not item:
        await callback.answer("Taom topilmadi!", show_alert=True)
        return

    db.add_to_cart(callback.from_user.id, item_id)

    await callback.answer(f"✅ {item['name']} savatchaga qo‘shildi!", show_alert=True)


@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    """Show user's cart with quantity controls."""
    cart = db.get_cart(callback.from_user.id)

    if not cart["items"]:
        await callback.message.edit_text(
            "🛒 <b>Savatchingiz bo‘sh</b>\n\n"
            "Menyudan bir nechta taom qo‘shing!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🍽️ Menyuni ko‘rish", callback_data="menu"
                        )
                    ],
                    [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")],
                ]
            ),
        )
        await callback.answer()
        return

    text = "🛒 <b>Sizning savatchingiz:</b>\n\n"

    keyboard_buttons = []
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if not item:
            continue

        item_total = float(item["price"]) * int(quantity)
        text += f"<b>{item['name']}</b>\n"
        text += (
            f"${item['price']:.2f} x {quantity} = ${item_total:.2f}\n"
            "Miqdorni o‘zgartirish uchun tugmalardan foydalaning.\n\n"
        )

        keyboard_buttons.append(
            [
                InlineKeyboardButton(
                    text=f"➖", callback_data=f"cart_dec_{item['id']}"
                ),
                InlineKeyboardButton(
                    text=f"{quantity} dona", callback_data="cart_nop"
                ),
                InlineKeyboardButton(
                    text=f"➕", callback_data=f"cart_inc_{item['id']}"
                ),
            ]
        )

    delivery_fee = db.data.get("settings", {}).get("delivery_fee", 2.50)
    text += f"<b>Oraliq jami (taomlar):</b> ${cart['total']:.2f}\n"
    text += f"<b>Yetkazib berish:</b> ${delivery_fee:.2f}\n"
    text += f"<b>Umumiy summa:</b> ${cart['total'] + delivery_fee:.2f}"

    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="✅ Buyurtmani rasmiylashtirish", callback_data="checkout"
            ),
            InlineKeyboardButton(
                text="🗑️ Savatchani tozalash", callback_data="clear_cart"
            ),
        ]
    )
    keyboard_buttons.append(
        [
            InlineKeyboardButton(
                text="🍽️ Yana taom qo‘shish", callback_data="menu"
            ),
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back"),
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Clear user's cart."""
    db.clear_cart(callback.from_user.id)
    await callback.answer("🗑️ Savatcha tozalandi!", show_alert=True)
    await show_cart(callback)


@router.callback_query(F.data.startswith("cart_inc_"))
async def cart_increment(callback: CallbackQuery):
    """Increase quantity of an item directly from the cart view."""
    item_id = int(callback.data.split("_", maxsplit=2)[2])
    db.change_cart_item_quantity(callback.from_user.id, item_id, delta=1)
    await show_cart(callback)
    await callback.answer()


@router.callback_query(F.data.startswith("cart_dec_"))
async def cart_decrement(callback: CallbackQuery):
    """Decrease quantity of an item directly from the cart view."""
    item_id = int(callback.data.split("_", maxsplit=2)[2])
    db.change_cart_item_quantity(callback.from_user.id, item_id, delta=-1)
    await show_cart(callback)
    await callback.answer()


@router.callback_query(F.data == "cart_nop")
async def cart_nop(callback: CallbackQuery):
    """Dummy handler for quantity label buttons to avoid `data not handled` warnings."""
    await callback.answer()


@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    """Show contact information"""
    contact_text = """
📞 <b>Aloqa ma’lumotlari</b>

📱 Telefon: +1 (555) 123-4567
📧 Email: info@restaurant.com
🌐 Veb-sayt: www.restaurant.com

<b>Bizni kuzatib boring:</b>
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
        "📍 <b>Manzilimiz</b>\n\n"
        "123 Main Street\n"
        "City Center, State 12345\n\n"
        "Shahar markazining o‘rtasida joylashganmiz!",
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
⏰ <b>Ish vaqti</b>

<b>Dushanba – Payshanba:</b> 11:00 - 22:00
<b>Juma – Shanba:</b> 11:00 - 23:00
<b>Yakshanba:</b> 12:00 - 21:00

<b>Oshxona yopilishidan 30 daqiqa oldin buyurtmalar qabul qilish to‘xtatiladi</b>
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
        f"👋 Yana xush kelibsiz, {callback.from_user.full_name}!\n\n"
        f"Nima qilishni xohlaysiz?",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()