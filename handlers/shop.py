# handlers/shop.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(F.data.startswith("product_"))
async def show_product_details(callback: CallbackQuery):
    """Show detailed product information"""
    product_id = int(callback.data.split("_")[1])
    product = db.get_item_by_id(product_id)
    
    if not product:
        await callback.answer("Product not found!", show_alert=True)
        return
    
    # Product details with images, sizes, colors
    text = f"""
🛍️ <b>{product['name']}</b>

💰 <b>Price:</b> ${product['price']:.2f}
📝 <b>Description:</b> {product['description']}

<b>Available Sizes:</b> S, M, L, XL
<b>Available Colors:</b> Red, Blue, Black, White
<b>Stock:</b> {product.get('stock', 'Available')}
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Size S", callback_data=f"size_{product_id}_S"),
            InlineKeyboardButton(text="Size M", callback_data=f"size_{product_id}_M"),
            InlineKeyboardButton(text="Size L", callback_data=f"size_{product_id}_L")
        ],
        [
            InlineKeyboardButton(text="🛒 Add to Cart", callback_data=f"add_{product_id}"),
            InlineKeyboardButton(text="❤️ Wishlist", callback_data=f"wishlist_{product_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="shop")
        ]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("size_"))
async def select_size(callback: CallbackQuery):
    """Handle size selection"""
    parts = callback.data.split("_")
    product_id, size = int(parts[1]), parts[2]
    
    # Store user's size preference
    user_preferences = db.get_user_preferences(callback.from_user.id)
    user_preferences[f"product_{product_id}_size"] = size
    db.save_user_preferences(callback.from_user.id, user_preferences)
    
    await callback.answer(f"✅ Size {size} selected!", show_alert=True)