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
            [KeyboardButton(text="🎯 Focus Mode"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="🗑 Vazifalarni boshqarish"), KeyboardButton(text="⚠️ Jazolarim")],
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

# ============== YANGI KLAVIATURALAR ==============

def focus_action_keyboard(session_id: int):
    """Focus session amalllari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏹ To'xtatish", callback_data=f"end_focus_{session_id}")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data=f"focus_stats_{session_id}")]
        ]
    )
    return keyboard

def task_management_keyboard():
    """Vazifalarni boshqarish menyusi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Faol vazifalar", callback_data="show_active_tasks")],
            [InlineKeyboardButton(text="✅ Bajarilganlar", callback_data="show_completed_tasks")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="task_statistics")],
            [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_main")]
        ]
    )
    return keyboard

def camera_permission_keyboard(has_permission: bool):
    """Kamera ruxsati klaviaturasi"""
    if has_permission:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Ruxsatni bekor qilish", callback_data="camera_revoke")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="✅ Ruxsat berish", callback_data="camera_grant"),
                    InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_to_main")
                ]
            ]
        )
    return keyboard

def punishment_keyboard():
    """Jazo menyusi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚠️ Faol jazolar", callback_data="active_punishments")],
            [InlineKeyboardButton(text="✅ Bajarilgan jazolar", callback_data="completed_punishments")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="punishment_stats")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
        ]
    )
    return keyboard

def focus_reminder_keyboard(task_id: int, session_id: int):
    """Focus eslatmasi uchun klaviatura"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Boshlash", callback_data=f"start_focus_{session_id}")],
            [InlineKeyboardButton(text="⏰ 5 daqiqa kechiktirish", callback_data=f"snooze_focus_{task_id}")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"skip_focus_{task_id}")]
        ]
    )
    return keyboard

def break_time_keyboard():
    """Tanaffus vaqti klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="☕️ Choy ichyapman", callback_data="break_tea")],
            [InlineKeyboardButton(text="🚶‍♂️ Sayr qilyapman", callback_data="break_walk")],
            [InlineKeyboardButton(text="💧 Suv ichyapman", callback_data="break_water")],
            [InlineKeyboardButton(text="🧘‍♂️ Dam olyapman", callback_data="break_rest")]
        ]
    )
    return keyboard

def completion_verification_keyboard(task_id: int):
    """Bajarish tasdiqlovchi klaviatura"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📸 Rasm yuborish", callback_data=f"submit_photo_{task_id}")],
            [InlineKeyboardButton(text="📝 Izoh qo'shish", callback_data=f"add_notes_{task_id}")],
            [InlineKeyboardButton(text="✅ Tayyor", callback_data=f"verify_complete_{task_id}")]
        ]
    )
    return keyboard

def settings_keyboard():
    """Sozlamalar menyusi - yangilangan"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕐 Ish vaqtini o'zgartirish", callback_data="change_work_hours")],
            [InlineKeyboardButton(text="🌍 Vaqt mintaqasi", callback_data="change_timezone")],
            [InlineKeyboardButton(text="📸 Kamera sozlamalari", callback_data="camera_settings")],
            [InlineKeyboardButton(text="🔔 Bildirishnoma sozlamalari", callback_data="notification_settings")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_menu")]
        ]
    )
    return keyboard

