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

def task_management_keyboard(language: str = "uz"):
    """Vazifalarni boshqarish menyusi"""
    texts = {
        "active": {"uz": "📝 Faol vazifalar", "ru": "📝 Активные задачи", "en": "📝 Active tasks"},
        "completed": {"uz": "✅ Bajarilganlar", "ru": "✅ Выполненные", "en": "✅ Completed"},
        "stats": {"uz": "📊 Statistika", "ru": "📊 Статистика", "en": "📊 Statistics"},
        "home": {"uz": "🏠 Bosh menyu", "ru": "🏠 Главное меню", "en": "🏠 Main Menu"}
    }
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts["active"].get(language, texts["active"]["uz"]), callback_data="show_active_tasks")],
            [InlineKeyboardButton(text=texts["completed"].get(language, texts["completed"]["uz"]), callback_data="show_completed_tasks")],
            [InlineKeyboardButton(text=texts["stats"].get(language, texts["stats"]["uz"]), callback_data="task_statistics")],
            [InlineKeyboardButton(text=texts["home"].get(language, texts["home"]["uz"]), callback_data="back_to_main")]
        ]
    )
    return keyboard

def camera_permission_keyboard(has_permission: bool, language: str = "uz"):
    """Kamera ruxsati klaviaturasi"""
    if has_permission:
        revoke_text = {"uz": "❌ Ruxsatni bekor qilish", "ru": "❌ Отменить разрешение", "en": "❌ Revoke permission"}
        back_text = get_text("btn_back", language)
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=revoke_text.get(language, revoke_text["uz"]), callback_data="camera_revoke")],
                [InlineKeyboardButton(text=back_text, callback_data="back_to_main")]
            ]
        )
    else:
        grant_text = {"uz": "✅ Ruxsat berish", "ru": "✅ Разрешить", "en": "✅ Grant permission"}
        cancel_text = {"uz": "❌ Bekor qilish", "ru": "❌ Отменить", "en": "❌ Cancel"}
        
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=grant_text.get(language, grant_text["uz"]), callback_data="camera_grant"),
                    InlineKeyboardButton(text=cancel_text.get(language, cancel_text["uz"]), callback_data="back_to_main")
                ]
            ]
        )
    return keyboard

def punishment_keyboard(language: str = "uz"):
    """Jazo menyusi"""
    texts = {
        "active": {"uz": "⚠️ Faol jazolar", "ru": "⚠️ Активные наказания", "en": "⚠️ Active punishments"},
        "completed": {"uz": "✅ Bajarilgan jazolar", "ru": "✅ Выполненные наказания", "en": "✅ Completed punishments"},
        "stats": {"uz": "📊 Statistika", "ru": "📊 Статистика", "en": "📊 Statistics"},
        "back": {"uz": "🔙 Orqaga", "ru": "🔙 Назад", "en": "🔙 Back"}
    }
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts["active"].get(language, texts["active"]["uz"]), callback_data="active_punishments")],
            [InlineKeyboardButton(text=texts["completed"].get(language, texts["completed"]["uz"]), callback_data="completed_punishments")],
            [InlineKeyboardButton(text=texts["stats"].get(language, texts["stats"]["uz"]), callback_data="punishment_stats")],
            [InlineKeyboardButton(text=texts["back"].get(language, texts["back"]["uz"]), callback_data="back_to_main")]
        ]
    )
    return keyboard

def focus_reminder_keyboard(task_id: int, session_id: int, language: str = "uz"):
    """Focus eslatmasi uchun klaviatura"""
    texts = {
        "start": {"uz": "✅ Boshlash", "ru": "✅ Начать", "en": "✅ Start"},
        "snooze": {"uz": "⏰ 5 daqiqa kechiktirish", "ru": "⏰ Отложить на 5 минут", "en": "⏰ Snooze 5 minutes"},
        "skip": {"uz": "❌ Bekor qilish", "ru": "❌ Пропустить", "en": "❌ Skip"}
    }
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts["start"].get(language, texts["start"]["uz"]), callback_data=f"start_focus_{session_id}")],
            [InlineKeyboardButton(text=texts["snooze"].get(language, texts["snooze"]["uz"]), callback_data=f"snooze_focus_{task_id}")],
            [InlineKeyboardButton(text=texts["skip"].get(language, texts["skip"]["uz"]), callback_data=f"skip_focus_{task_id}")]
        ]
    )
    return keyboard

def break_time_keyboard(language: str = "uz"):
    """Tanaffus vaqti klaviaturasi"""
    texts = {
        "tea": {"uz": "☕️ Choy ichyapman", "ru": "☕️ Пью чай", "en": "☕️ Having tea"},
        "walk": {"uz": "🚶‍♂️ Sayr qilyapman", "ru": "🚶‍♂️ Гуляю", "en": "🚶‍♂️ Walking"},
        "water": {"uz": "💧 Suv ichyapman", "ru": "💧 Пью воду", "en": "💧 Drinking water"},
        "rest": {"uz": "🧘‍♂️ Dam olyapman", "ru": "🧘‍♂️ Отдыхаю", "en": "🧘‍♂️ Resting"}
    }
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts["tea"].get(language, texts["tea"]["uz"]), callback_data="break_tea")],
            [InlineKeyboardButton(text=texts["walk"].get(language, texts["walk"]["uz"]), callback_data="break_walk")],
            [InlineKeyboardButton(text=texts["water"].get(language, texts["water"]["uz"]), callback_data="break_water")],
            [InlineKeyboardButton(text=texts["rest"].get(language, texts["rest"]["uz"]), callback_data="break_rest")]
        ]
    )
    return keyboard

def completion_verification_keyboard(task_id: int, language: str = "uz"):
    """Bajarish tasdiqlovchi klaviatura"""
    texts = {
        "photo": {"uz": "📸 Rasm yuborish", "ru": "📸 Отправить фото", "en": "📸 Send photo"},
        "notes": {"uz": "📝 Izoh qo'shish", "ru": "📝 Добавить заметку", "en": "📝 Add notes"},
        "done": {"uz": "✅ Tayyor", "ru": "✅ Готово", "en": "✅ Done"}
    }
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=texts["photo"].get(language, texts["photo"]["uz"]), callback_data=f"submit_photo_{task_id}")],
            [InlineKeyboardButton(text=texts["notes"].get(language, texts["notes"]["uz"]), callback_data=f"add_notes_{task_id}")],
            [InlineKeyboardButton(text=texts["done"].get(language, texts["done"]["uz"]), callback_data=f"verify_complete_{task_id}")]
        ]
    )
    return keyboard


