# handlers/courses.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(F.data == "courses")
async def show_courses(callback: CallbackQuery):
    """Show available courses"""
    courses = [
        {
            "id": 1, 
            "name": "Python Programming", 
            "lessons": 12, 
            "duration": "6 weeks",
            "price": 99.00,
            "level": "Beginner"
        },
        {
            "id": 2, 
            "name": "Web Development", 
            "lessons": 15, 
            "duration": "8 weeks",
            "price": 149.00,
            "level": "Intermediate"
        },
        {
            "id": 3, 
            "name": "Data Science", 
            "lessons": 20, 
            "duration": "10 weeks",
            "price": 199.00,
            "level": "Advanced"
        }
    ]
    
    text = "📚 <b>Available Courses:</b>\n\n"
    keyboard_buttons = []
    
    for course in courses:
        text += f"<b>{course['name']}</b>\n"
        text += f"📊 Level: {course['level']}\n"
        text += f"📖 {course['lessons']} lessons\n"
        text += f"⏰ Duration: {course['duration']}\n"
        text += f"💰 Price: ${course['price']:.2f}\n\n"
        
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📖 View {course['name']}",
                callback_data=f"course_{course['id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back", callback_data="back")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("course_"))
async def show_course_details(callback: CallbackQuery):
    """Show detailed course information"""
    course_id = int(callback.data.split("_")[1])
    
    # Get course details and user progress
    course = db.get_course_by_id(course_id)
    user_progress = db.get_user_course_progress(callback.from_user.id, course_id)
    
    text = f"""
📚 <b>{course['name']}</b>

📊 <b>Level:</b> {course['level']}
📖 <b>Lessons:</b> {course['lessons']}
⏰ <b>Duration:</b> {course['duration']}
💰 <b>Price:</b> ${course['price']:.2f}

<b>📈 Your Progress:</b>
Completed: {user_progress.get('completed_lessons', 0)}/{course['lessons']} lessons
Progress: {(user_progress.get('completed_lessons', 0) / course['lessons'] * 100):.1f}%

<b>📝 Course Description:</b>
{course.get('description', 'Learn the fundamentals and advance your skills.')}
    """
    
    keyboard_buttons = []
    
    if user_progress.get('enrolled', False):
        keyboard_buttons.extend([
            [InlineKeyboardButton(text="▶️ Continue Learning", callback_data=f"lessons_{course_id}")],
            [InlineKeyboardButton(text="📊 View Progress", callback_data=f"progress_{course_id}")]
        ])
    else:
        keyboard_buttons.append([
            InlineKeyboardButton(text="🎓 Enroll Now", callback_data=f"enroll_{course_id}")
        ])
    
    keyboard_buttons.extend([
        [InlineKeyboardButton(text="📖 Preview Lessons", callback_data=f"preview_{course_id}")],
        [InlineKeyboardButton(text="⬅️ Back to Courses", callback_data="courses")]
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("lessons_"))
async def show_lessons(callback: CallbackQuery):
    """Show course lessons"""
    course_id = int(callback.data.split("_")[1])
    
    lessons = db.get_course_lessons(course_id)
    user_progress = db.get_user_course_progress(callback.from_user.id, course_id)
    completed_lessons = user_progress.get('completed_lessons_ids', [])
    
    text = f"📖 <b>Course Lessons:</b>\n\n"
    keyboard_buttons = []
    
    for i, lesson in enumerate(lessons, 1):
        status = "✅" if lesson['id'] in completed_lessons else "🔒" if i > 1 and lessons[i-2]['id'] not in completed_lessons else "▶️"
        text += f"{status} <b>Lesson {i}:</b> {lesson['title']}\n"
        
        if lesson['id'] in completed_lessons or (i == 1) or (i > 1 and lessons[i-2]['id'] in completed_lessons):
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"📖 {lesson['title']}", 
                    callback_data=f"lesson_{course_id}_{lesson['id']}"
                )
            ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Back to Course", callback_data=f"course_{course_id}")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()