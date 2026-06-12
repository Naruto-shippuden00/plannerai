"""
Telegram bot keyboards
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    """Asosiy menyu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Vazifalarim"), KeyboardButton(text="📅 Jadval")],
            [KeyboardButton(text="➕ Vazifa qo'shish"), KeyboardButton(text="🤖 AI Jadval")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="✅ Bajarilganlar")],
            [KeyboardButton(text="⚙️ Sozlamalar"), KeyboardButton(text="❓ Yordam")]
        ],
        resize_keyboard=True
    )
    return keyboard

def task_category_keyboard():
    """Vazifa kategoriyasi tanlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 SAT", callback_data="cat_sat")],
            [InlineKeyboardButton(text="🗣 IELTS", callback_data="cat_ielts")],
            [InlineKeyboardButton(text="🐍 Python", callback_data="cat_python")],
            [InlineKeyboardButton(text="💡 Startup", callback_data="cat_startup")],
            [InlineKeyboardButton(text="💪 Gym", callback_data="cat_gym")],
            [InlineKeyboardButton(text="📖 Kitob", callback_data="cat_book")],
            [InlineKeyboardButton(text="➕ Boshqa", callback_data="cat_other")]
        ]
    )
    return keyboard

def priority_keyboard():
    """Prioritet tanlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔴 Juda muhim (3)", callback_data="priority_3")],
            [InlineKeyboardButton(text="🟡 O'rtacha (2)", callback_data="priority_2")],
            [InlineKeyboardButton(text="🟢 Past (1)", callback_data="priority_1")]
        ]
    )
    return keyboard

def duration_keyboard():
    """Davomiylik tanlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="30 min", callback_data="dur_30"),
                InlineKeyboardButton(text="1 soat", callback_data="dur_60")
            ],
            [
                InlineKeyboardButton(text="1.5 soat", callback_data="dur_90"),
                InlineKeyboardButton(text="2 soat", callback_data="dur_120")
            ],
            [InlineKeyboardButton(text="➕ Boshqa", callback_data="dur_custom")]
        ]
    )
    return keyboard

def confirm_schedule_keyboard():
    """Jadvalni tasdiqlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_schedule"),
                InlineKeyboardButton(text="🔄 Qayta tuzish", callback_data="regenerate_schedule")
            ],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_schedule")]
        ]
    )
    return keyboard

def task_action_keyboard(task_id: int):
    """Vazifa amalllari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"complete_{task_id}"),
                InlineKeyboardButton(text="⏰ Keyinroq", callback_data=f"snooze_{task_id}")
            ],
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_{task_id}")]
        ]
    )
    return keyboard

def day_navigation_keyboard(current_day: int):
    """Kunlar bo'yicha navigatsiya"""
    days = ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan", "Yak"]
    buttons = []
    
    row = []
    for i, day in enumerate(days):
        emoji = "📍" if i == current_day else ""
        row.append(InlineKeyboardButton(
            text=f"{emoji}{day}", 
            callback_data=f"day_{i}"
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def weekly_test_keyboard():
    """Haftalik test klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 SAT Test", callback_data="test_sat")],
            [InlineKeyboardButton(text="🐍 Python Test", callback_data="test_python")],
            [InlineKeyboardButton(text="📖 Kitob Test", callback_data="test_book")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def test_answer_keyboard(question_num: int):
    """Test javob variantlari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="A", callback_data=f"ans_{question_num}_0"),
                InlineKeyboardButton(text="B", callback_data=f"ans_{question_num}_1")
            ],
            [
                InlineKeyboardButton(text="C", callback_data=f"ans_{question_num}_2"),
                InlineKeyboardButton(text="D", callback_data=f"ans_{question_num}_3")
            ]
        ]
    )
    return keyboard

def yes_no_keyboard(action: str):
    """Ha/Yo'q klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha", callback_data=f"yes_{action}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=f"no_{action}")
            ]
        ]
    )
    return keyboard

def settings_keyboard():
    """Sozlamalar menyusi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕐 Ish vaqtini o'zgartirish", callback_data="change_work_hours")],
            [InlineKeyboardButton(text="🌍 Vaqt mintaqasi", callback_data="change_timezone")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

def back_to_main_keyboard():
    """Asosiy menyuga qaytish"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Bosh menyu")]
        ],
        resize_keyboard=True
    )
    return keyboard

