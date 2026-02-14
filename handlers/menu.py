from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db_helper import db
from keyboards.main_keyboard import get_main_keyboard, get_back_keyboard

# Create router instance
router = Router()

@router.callback_query(F.data == "menu")
async def show_menu_categories(callback: CallbackQuery):
    """Show menu categories"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🍕 Pizza", callback_data="category_pizza"),
            InlineKeyboardButton(text="🍔 Burgers", callback_data="category_burgers")
        ],
        [
            InlineKeyboardButton(text="🥤 Drinks", callback_data="category_drinks"),
            InlineKeyboardButton(text="🛒 Cart", callback_data="cart")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="back")
        ]
    ])
    
    await callback.message.edit_text(
        "🍽️ <b>Choose a category:</b>",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: CallbackQuery):
    """Show items in selected category"""
    category = callback.data.split("_")[1]
    items = db.get_menu_category(category)
    
    if not items:
        await callback.answer("This category is empty!", show_alert=True)
        return
    
    keyboard_buttons = []
    text = f"🍽️ <b>{category.title()}</b>\n\n"
    
    for item in items:
        text += f"<b>{item['name']}</b> - ${item['price']:.2f}\n"
        text += f"<i>{item['description']}</i>\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"➕ Add {item['name']}", 
                callback_data=f"add_{item['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="menu")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    """Add item to cart"""
    item_id = int(callback.data.split("_")[1])
    item = db.get_item_by_id(item_id)
    
    if not item:
        await callback.answer("Item not found!", show_alert=True)
        return
    
    db.add_to_cart(callback.from_user.id, item_id)
    
    await callback.answer(f"✅ {item['name']} added to cart!", show_alert=True)

@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    """Show user's cart"""
    cart = db.get_cart(callback.from_user.id)
    
    if not cart["items"]:
        await callback.message.edit_text(
            "🛒 <b>Your cart is empty</b>\n\n"
            "Add some items from the menu!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🍽️ Browse Menu", callback_data="menu")],
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back")]
            ])
        )
        await callback.answer()
        return
    
    text = "🛒 <b>Your Cart:</b>\n\n"
    total = 0
    
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if item:
            item_total = item["price"] * quantity
            total += item_total
            text += f"<b>{item['name']}</b>\n"
            text += f"${item['price']:.2f} x {quantity} = ${item_total:.2f}\n\n"
    
    delivery_fee = db.data.get("settings", {}).get("delivery_fee", 2.50)
    text += f"<b>Subtotal:</b> ${total:.2f}\n"
    text += f"<b>Delivery:</b> ${delivery_fee:.2f}\n"
    text += f"<b>Total:</b> ${total + delivery_fee:.2f}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Checkout", callback_data="checkout"),
            InlineKeyboardButton(text="🗑️ Clear Cart", callback_data="clear_cart")
        ],
        [
            InlineKeyboardButton(text="🍽️ Add More Items", callback_data="menu"),
            InlineKeyboardButton(text="⬅️ Back", callback_data="back")
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Clear user's cart"""
    db.clear_cart(callback.from_user.id)
    await callback.answer("🗑️ Cart cleared!", show_alert=True)
    await show_cart(callback)

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery):
    """Process checkout"""
    cart = db.get_cart(callback.from_user.id)
    
    if not cart["items"]:
        await callback.answer("Your cart is empty!", show_alert=True)
        return
    
    # Here you would integrate with payment systems
    # For now, we'll just show order confirmation
    
    order_text = "🎉 <b>Order Confirmed!</b>\n\n"
    order_text += "📞 We'll call you shortly to confirm delivery details.\n"
    order_text += "⏱️ Estimated delivery: 30-45 minutes\n\n"
    order_text += "<b>Order Summary:</b>\n"
    
    for item_id, quantity in cart["items"].items():
        item = db.get_item_by_id(int(item_id))
        if item:
            order_text += f"• {item['name']} x{quantity}\n"
    
    delivery_fee = db.data.get("settings", {}).get("delivery_fee", 2.50)
    order_text += f"\n<b>Total: ${cart['total'] + delivery_fee:.2f}</b>"
    
    # Clear the cart after order
    db.clear_cart(callback.from_user.id)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back")]
    ])
    
    await callback.message.edit_text(order_text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    """Show contact information"""
    contact_text = """
📞 <b>Contact Information</b>

📱 Phone: +1 (555) 123-4567
📧 Email: info@restaurant.com
🌐 Website: www.restaurant.com

<b>Follow us:</b>
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
        "📍 <b>Our Location</b>\n\n"
        "123 Main Street\n"
        "City Center, State 12345\n\n"
        "We're located in the heart of downtown!",
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
⏰ <b>Opening Hours</b>

<b>Monday - Thursday:</b> 11:00 AM - 10:00 PM
<b>Friday - Saturday:</b> 11:00 AM - 11:00 PM
<b>Sunday:</b> 12:00 PM - 9:00 PM

<b>Kitchen closes 30 minutes before closing time</b>
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
        f"👋 Welcome back, {callback.from_user.full_name}!\n\n"
        f"What would you like to do?",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()