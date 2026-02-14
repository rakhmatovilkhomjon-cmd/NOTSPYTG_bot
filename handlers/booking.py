# handlers/booking.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

router = Router()

@router.callback_query(F.data == "book_appointment")
async def show_services(callback: CallbackQuery):
    """Show available services"""
    services = [
        {"id": 1, "name": "Haircut", "duration": 30, "price": 25.00},
        {"id": 2, "name": "Hair Coloring", "duration": 90, "price": 80.00},
        {"id": 3, "name": "Manicure", "duration": 45, "price": 35.00},
        {"id": 4, "name": "Facial Treatment", "duration": 60, "price": 60.00}
    ]
    
    text = "💇‍♀️ <b>Select a Service:</b>\n\n"
    keyboard_buttons = []
    
    for service in services:
        text += f"<b>{service['name']}</b>\n"
        text += f"⏱️ {service['duration']} min | 💰 ${service['price']:.2f}\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📅 Book {service['name']}", 
                callback_data=f"service_{service['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data="back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("service_"))
async def show_calendar(callback: CallbackQuery):
    """Show available dates"""
    service_id = int(callback.data.split("_")[1])
    
    # Generate next 14 days
    keyboard_buttons = []
    today = datetime.now()
    
    for i in range(14):
        date = today + timedelta(days=i)
        if date.weekday() < 6:  # Monday to Saturday only
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=date.strftime("%A, %B %d"),
                    callback_data=f"date_{service_id}_{date.strftime('%Y-%m-%d')}"
                )
            ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Services", callback_data="book_appointment")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(
        "📅 <b>Select a Date:</b>",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("date_"))
async def show_time_slots(callback: CallbackQuery):
    """Show available time slots"""
    parts = callback.data.split("_")
    service_id, selected_date = int(parts[1]), parts[2]
    
    # Generate time slots (9 AM to 6 PM)
    time_slots = []
    start_hour = 9
    end_hour = 18
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:  # Every 30 minutes
            time_str = f"{hour:02d}:{minute:02d}"
            time_slots.append(time_str)
    
    keyboard_buttons = []
    text = f"🕐 <b>Available Times for {selected_date}:</b>\n\n"
    
    # Create rows of 3 time slots each
    for i in range(0, len(time_slots), 3):
        row = []
        for j in range(3):
            if i + j < len(time_slots):
                time_slot = time_slots[i + j]
                row.append(
                    InlineKeyboardButton(
                        text=time_slot,
                        callback_data=f"time_{service_id}_{selected_date}_{time_slot}"
                    )
                )
        keyboard_buttons.append(row)
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Dates", callback_data=f"service_{service_id}")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("time_"))
async def confirm_booking(callback: CallbackQuery):
    """Confirm appointment booking"""
    parts = callback.data.split("_")
    service_id, selected_date, selected_time = int(parts[1]), parts[2], parts[3]
    
    # Get service details
    service = db.get_service_by_id(service_id)  # You'd implement this method
    
    # Create booking
    booking_data = {
        "user_id": callback.from_user.id,
        "service_id": service_id,
        "date": selected_date,
        "time": selected_time,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }
    
    # Save booking (implement this method)
    db.save_booking(booking_data)
    
    confirmation_text = f"""
✅ <b>Appointment Confirmed!</b>

👤 <b>Client:</b> {callback.from_user.full_name}
💇‍♀️ <b>Service:</b> {service['name']}
📅 <b>Date:</b> {selected_date}
🕐 <b>Time:</b> {selected_time}
💰 <b>Price:</b> ${service['price']:.2f}

📞 We'll send you a reminder 24 hours before your appointment.

<b>Need to reschedule?</b> Use /mybookings command.
    """
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Book Another", callback_data="book_appointment")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="back")]
    ])
    
    await callback.message.edit_text(confirmation_text, reply_markup=keyboard)
    await callback.answer()