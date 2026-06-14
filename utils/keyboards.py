"""
Telegram bot keyboards
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils.translations import get_text

def language_selection_keyboard():
    """Til tanlash klaviaturasi"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz")],
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )
    return keyboard

def main_menu_keyboard(language: str = "uz"):
    """Asosiy menyu"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=get_text("btn_my_tasks", language)), 
                KeyboardButton(text=get_text("btn_schedule", language))
            ],
            [
                KeyboardButton(text=get_text("btn_add_task", language)), 
                KeyboardButton(text=get_text("btn_ai_schedule", language))
            ],
            [
                KeyboardButton(text=get_text("btn_focus_mode", language)), 
                KeyboardButton(text=get_text("btn_statistics", language))
            ],
            [
                KeyboardButton(text=get_text("btn_manage_tasks", language)), 
                KeyboardButton(text=get_text("btn_punishments", language))
            ],
            [
                KeyboardButton(text=get_text("btn_settings", language)), 
                KeyboardButton(text=get_text("btn_help", language))
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def task_category_keyboard(language: str = "uz"):
    """Vazifa kategoriyasi tanlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("cat_sat", language), callback_data="cat_sat")],
            [InlineKeyboardButton(text=get_text("cat_ielts", language), callback_data="cat_ielts")],
            [InlineKeyboardButton(text=get_text("cat_python", language), callback_data="cat_python")],
            [InlineKeyboardButton(text=get_text("cat_startup", language), callback_data="cat_startup")],
            [InlineKeyboardButton(text=get_text("cat_gym", language), callback_data="cat_gym")],
            [InlineKeyboardButton(text=get_text("cat_book", language), callback_data="cat_book")],
            [InlineKeyboardButton(text=get_text("cat_other", language), callback_data="cat_other")]
        ]
    )
    return keyboard

def priority_keyboard(language: str = "uz"):
    """Prioritet tanlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=get_text("priority_high", language), callback_data="priority_3")],
            [InlineKeyboardButton(text=get_text("priority_medium", language), callback_data="priority_2")],
            [InlineKeyboardButton(text=get_text("priority_low", language), callback_data="priority_1")]
        ]
    )
    return keyboard

def duration_keyboard(language: str = "uz"):
    """Davomiylik tanlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("dur_30min", language), callback_data="dur_30"),
                InlineKeyboardButton(text=get_text("dur_1hour", language), callback_data="dur_60")
            ],
            [
                InlineKeyboardButton(text=get_text("dur_1_5hours", language), callback_data="dur_90"),
                InlineKeyboardButton(text=get_text("dur_2hours", language), callback_data="dur_120")
            ],
            [InlineKeyboardButton(text=get_text("dur_other", language), callback_data="dur_custom")]
        ]
    )
    return keyboard

def confirm_schedule_keyboard(language: str = "uz"):
    """Jadvalni tasdiqlash"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("btn_confirm", language), callback_data="confirm_schedule"),
                InlineKeyboardButton(text=get_text("btn_regenerate", language), callback_data="regenerate_schedule")
            ],
            [InlineKeyboardButton(text=get_text("btn_cancel", language), callback_data="cancel_schedule")]
        ]
    )
    return keyboard

def task_action_keyboard(task_id: int, language: str = "uz"):
    """Vazifa amalllari"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=get_text("btn_completed", language), callback_data=f"complete_{task_id}"),
                InlineKeyboardButton(text=get_text("btn_later", language), callback_data=f"snooze_{task_id}")
            ],
            [InlineKeyboardButton(text=get_text("btn_delete", language), callback_data=f"delete_{task_id}")]
        ]
    )
    return keyboard

def day_navigation_keyboard(current_day: int, language: str = "uz"):
    """Kunlar bo'yicha navigatsiya"""
    days_keys = ["day_mon", "day_tue", "day_wed", "day_thu", "day_fri", "day_sat", "day_sun"]
    buttons = []
    
    row = []
    for i, day_key in enumerate(days_keys):
        emoji = "📍" if i == current_day else ""
        day_text = get_text(day_key, language)
        row.append(InlineKeyboardButton(
            text=f"{emoji}{day_text}", 
            callback_data=f"day_{i}"
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton(text=get_text("btn_back", language), callback_data="back_to_menu")])
    
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

def yes_no_keyboard(action: str, language: str = "uz"):
    """Ha/Yo'q klaviaturasi"""
    yes_text = {"uz": "✅ Ha", "ru": "✅ Да", "en": "✅ Yes"}
    no_text = {"uz": "❌ Yo'q", "ru": "❌ Нет", "en": "❌ No"}
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text.get(language, yes_text["uz"]), callback_data=f"yes_{action}"),
                InlineKeyboardButton(text=no_text.get(language, no_text["uz"]), callback_data=f"no_{action}")
            ]
        ]
    )
    return keyboard

def settings_keyboard(language: str = "uz"):
    """Sozlamalar menyusi"""
    settings_texts = {
        "work_hours": {"uz": "🕐 Ish vaqtini o'zgartirish", "ru": "🕐 Изменить рабочее время", "en": "🕐 Change work hours"},
        "timezone": {"uz": "🌍 Vaqt mintaqasi", "ru": "🌍 Часовой пояс", "en": "🌍 Timezone"},
        "camera": {"uz": "📸 Kamera sozlamalari", "ru": "📸 Настройки камеры", "en": "📸 Camera settings"},
        "notifications": {"uz": "🔔 Bildirishnoma sozlamalari", "ru": "🔔 Настройки уведомлений", "en": "🔔 Notification settings"},
        "language": {"uz": "🌐 Tilni o'zgartirish", "ru": "🌐 Изменить язык", "en": "🌐 Change language"}
    }
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=settings_texts["work_hours"].get(language, settings_texts["work_hours"]["uz"]), callback_data="change_work_hours")],
            [InlineKeyboardButton(text=settings_texts["timezone"].get(language, settings_texts["timezone"]["uz"]), callback_data="change_timezone")],
            [InlineKeyboardButton(text=settings_texts["camera"].get(language, settings_texts["camera"]["uz"]), callback_data="camera_settings")],
            [InlineKeyboardButton(text=settings_texts["notifications"].get(language, settings_texts["notifications"]["uz"]), callback_data="notification_settings")],
            [InlineKeyboardButton(text=settings_texts["language"].get(language, settings_texts["language"]["uz"]), callback_data="change_language")],
            [InlineKeyboardButton(text=get_text("btn_back", language), callback_data="back_to_menu")]
        ]
    )
    return keyboard

def back_to_main_keyboard(language: str = "uz"):
    """Asosiy menyuga qaytish"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=get_text("btn_back_menu", language))]
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

