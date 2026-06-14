"""
Foydalanuvchi sozlamalari
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from utils.database import get_user_settings, update_work_hours
from utils.keyboards import settings_keyboard, back_to_main_keyboard

router = Router()

class SettingsStates(StatesGroup):
    """Sozlamalar uchun state'lar"""
    waiting_for_start_time = State()
    waiting_for_end_time = State()

@router.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: Message):
    """Sozlamalar menyusini ko'rsatish"""
    user_id = message.from_user.id
    settings = await get_user_settings(user_id)
    
    text = (
        "⚙️ **Sozlamalar**\n\n"
        f"🕐 **Ish vaqti:**\n"
        f"   Boshlanish: {settings['work_start_time']}\n"
        f"   Tugash: {settings['work_end_time']}\n\n"
        f"🌍 **Vaqt mintaqasi:** {settings['timezone']}\n\n"
        "Nimani o'zgartirmoqchisiz?"
    )
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=settings_keyboard()
    )

@router.callback_query(F.data == "change_work_hours")
async def change_work_hours(callback: CallbackQuery, state: FSMContext):
    """Ish vaqtini o'zgartirish"""
    await callback.message.edit_text(
        "🕐 **Ish vaqtini sozlash**\n\n"
        "Bu vaqt oralig'ida siz band bo'lasiz (masalan, texnikum, ish, maktab).\n"
        "AI jadval tuzayotganda bu vaqtni bo'sh qoldiradi.\n\n"
        "**Boshlanish vaqtini kiriting:**\n"
        "Format: HH:MM (masalan, 08:00 yoki 09:30)\n\n"
        "❌ Bekor qilish uchun /cancel",
        parse_mode="Markdown"
    )
    await state.set_state(SettingsStates.waiting_for_start_time)
    await callback.answer()

@router.message(SettingsStates.waiting_for_start_time)
async def process_start_time(message: Message, state: FSMContext):
    """Boshlanish vaqtini qabul qilish"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=back_to_main_keyboard()
        )
        return
    
    # Vaqt formatini tekshirish
    time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    if not re.match(time_pattern, message.text):
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "Iltimos, HH:MM formatida kiriting.\n"
            "Masalan: 08:00, 09:30, 14:00\n\n"
            "Qaytadan kiriting yoki /cancel"
        )
        return
    
    # State'ga saqlash
    await state.update_data(start_time=message.text)
    
    await message.answer(
        f"✅ Boshlanish vaqti: {message.text}\n\n"
        "**Endi tugash vaqtini kiriting:**\n"
        "Format: HH:MM (masalan, 16:00 yoki 17:30)\n\n"
        "❌ Bekor qilish uchun /cancel"
    )
    await state.set_state(SettingsStates.waiting_for_end_time)

@router.message(SettingsStates.waiting_for_end_time)
async def process_end_time(message: Message, state: FSMContext):
    """Tugash vaqtini qabul qilish va saqlash"""
    if message.text == "/cancel":
        await state.clear()
        await message.answer(
            "❌ Bekor qilindi.",
            reply_markup=back_to_main_keyboard()
        )
        return
    
    # Vaqt formatini tekshirish
    time_pattern = r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$'
    if not re.match(time_pattern, message.text):
        await message.answer(
            "❌ Noto'g'ri format!\n\n"
            "Iltimos, HH:MM formatida kiriting.\n"
            "Masalan: 16:00, 17:30, 20:00\n\n"
            "Qaytadan kiriting yoki /cancel"
        )
        return
    
    # State'dan boshlanish vaqtini olish
    data = await state.get_data()
    start_time = data.get('start_time')
    end_time = message.text
    
    # Vaqtlarni solishtirish
    start_hour, start_min = map(int, start_time.split(':'))
    end_hour, end_min = map(int, end_time.split(':'))
    
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min
    
    if end_minutes <= start_minutes:
        await message.answer(
            "❌ Tugash vaqti boshlanish vaqtidan kech bo'lishi kerak!\n\n"
            f"Siz kiritgan:\n"
            f"Boshlanish: {start_time}\n"
            f"Tugash: {end_time}\n\n"
            "Tugash vaqtini qaytadan kiriting yoki /cancel"
        )
        return
    
    # Database'ga saqlash
    user_id = message.from_user.id
    await update_work_hours(user_id, start_time, end_time)
    await state.clear()
    
    duration_hours = (end_minutes - start_minutes) / 60
    
    await message.answer(
        f"✅ **Ish vaqti saqlandi!**\n\n"
        f"🕐 Boshlanish: {start_time}\n"
        f"🕐 Tugash: {end_time}\n"
        f"⏱ Davomiyligi: {duration_hours:.1f} soat\n\n"
        f"AI jadval tuzayotganda bu vaqtni hisobga oladi.\n"
        f"Agarda jadvalingiz mavjud bo'lsa, yangi jadval yaratish uchun "
        f"'🤖 AI Jadval' tugmasini bosing.",
        parse_mode="Markdown",
        reply_markup=back_to_main_keyboard()
    )

@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    """Sozlamalarga qaytish"""
    user_id = callback.from_user.id
    settings = await get_user_settings(user_id)
    
    text = (
        "⚙️ **Sozlamalar**\n\n"
        f"🕐 **Ish vaqti:**\n"
        f"   Boshlanish: {settings['work_start_time']}\n"
        f"   Tugash: {settings['work_end_time']}\n\n"
        f"🌍 **Vaqt mintaqasi:** {settings['timezone']}\n\n"
        "Nimani o'zgartirmoqchisiz?"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=settings_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Asosiy menyu",
        reply_markup=back_to_main_keyboard()
    )
    await callback.answer()

# ============== VAQT MINTAQASI ==============

@router.callback_query(F.data == "change_timezone")
async def change_timezone_menu(callback: CallbackQuery):
    """Vaqt mintaqasini o'zgartirish menyusi"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇿 Toshkent (UTC+5)", callback_data="tz_tashkent")],
            [InlineKeyboardButton(text="🇷🇺 Moskva (UTC+3)", callback_data="tz_moscow")],
            [InlineKeyboardButton(text="🇹🇷 Istanbul (UTC+3)", callback_data="tz_istanbul")],
            [InlineKeyboardButton(text="🇦🇪 Dubai (UTC+4)", callback_data="tz_dubai")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_settings")]
        ]
    )
    
    await callback.message.edit_text(
        "🌍 **Vaqt mintaqasini tanlang:**\n\n"
        "Bu jadval va eslatmalar uchun ishlatiladi.\n"
        "Hozirda: Toshkent (UTC+5) standart",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("tz_"))
async def set_timezone(callback: CallbackQuery):
    """Vaqt mintaqasini o'rnatish"""
    from utils.database import update_user_timezone
    
    timezone_map = {
        "tz_tashkent": ("Asia/Tashkent", "🇺🇿 Toshkent (UTC+5)"),
        "tz_moscow": ("Europe/Moscow", "🇷🇺 Moskva (UTC+3)"),
        "tz_istanbul": ("Europe/Istanbul", "🇹🇷 Istanbul (UTC+3)"),
        "tz_dubai": ("Asia/Dubai", "🇦🇪 Dubai (UTC+4)")
    }
    
    tz_key = callback.data
    if tz_key in timezone_map:
        tz_id, tz_name = timezone_map[tz_key]
        
        user_id = callback.from_user.id
        await update_user_timezone(user_id, tz_id)
        
        await callback.message.edit_text(
            f"✅ **Vaqt mintaqasi o'zgartirildi!**\n\n"
            f"Yangi mintaqa: {tz_name}\n\n"
            f"Barcha jadval va eslatmalar endi bu vaqt bo'yicha yuboriladi.",
            parse_mode="Markdown"
        )
        
        # 2 soniyadan keyin settings'ga qaytish
        import asyncio
        await asyncio.sleep(2)
        await back_to_settings(callback)
    
    await callback.answer()

# ============== KAMERA SOZLAMALARI ==============

@router.callback_query(F.data == "camera_settings")
async def camera_settings_menu(callback: CallbackQuery):
    """Kamera sozlamalari menyusi"""
    from utils.database import get_camera_permission
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    user_id = callback.from_user.id
    has_permission = await get_camera_permission(user_id)
    
    if has_permission:
        text = (
            "📸 **KAMERA RUXSATI BERILGAN**\n\n"
            "✅ Focus sessiya davomida men sizdan tasodifiy suratlar so'rayman.\n\n"
            "**Nima uchun kerak?**\n"
            "• Sizning chindan ham ishlayotganingizni tasdiqlaydi\n"
            "• Chalg'itishlardan saqlaydi\n"
            "• Natijalarni yaxshilaydi\n\n"
            "**Maxfiylik:**\n"
            "• Rasmlar faqat sizning progressingiz uchun\n"
            "• Hech kim bilan baham ko'rilmaydi\n"
            "• Istalgan vaqt o'chirib qo'yishingiz mumkin"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Ruxsatni bekor qilish", callback_data="camera_revoke")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_settings")]
            ]
        )
    else:
        text = (
            "📸 **KAMERA RUXSATI**\n\n"
            "Bot focus sessiya vaqtida tasodifiy ravishda sizdan suratlar so'rashi mumkin.\n\n"
            "**Nima uchun kerak?**\n"
            "• Sizning chindan ham ishlayotganingizni tasdiqlaydi\n"
            "• Chalg'itishlardan saqlaydi\n"
            "• Natijalarni yaxshilaydi\n\n"
            "**Maxfiylik:**\n"
            "• Rasmlar faqat sizning progressingiz uchun saqlanadi\n"
            "• Hech kim bilan baham ko'rilmaydi\n"
            "• Istalgan vaqt o'chirib qo'yishingiz mumkin\n\n"
            "Ruxsat berasizmi?"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Ruxsat berish", callback_data="camera_grant")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_settings")]
            ]
        )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "camera_grant")
async def grant_camera_permission(callback: CallbackQuery):
    """Kamera ruxsatini berish"""
    from utils.database import set_camera_permission
    
    user_id = callback.from_user.id
    await set_camera_permission(user_id, True)
    
    await callback.message.edit_text(
        "✅ **RUXSAT BERILDI!**\n\n"
        "📸 Endi focus vaqtida men sizdan tasodifiy suratlar so'rayman.\n\n"
        "Bu sizning natijalaringizni yaxshilashga yordam beradi!\n\n"
        "💪 Muvaffaqiyat yo'lida birgamiz!",
        parse_mode="Markdown"
    )
    
    # 2 soniyadan keyin settings'ga qaytish
    import asyncio
    await asyncio.sleep(2)
    await camera_settings_menu(callback)

@router.callback_query(F.data == "camera_revoke")
async def revoke_camera_permission(callback: CallbackQuery):
    """Kamera ruxsatini bekor qilish"""
    from utils.database import set_camera_permission
    
    user_id = callback.from_user.id
    await set_camera_permission(user_id, False)
    
    await callback.message.edit_text(
        "❌ **RUXSAT BEKOR QILINDI**\n\n"
        "📸 Endi men sizdan suratlar so'ramayman.\n\n"
        "⚠️ Lekin progress tracking kamroq samarali bo'ladi.",
        parse_mode="Markdown"
    )
    
    # 2 soniyadan keyin settings'ga qaytish
    import asyncio
    await asyncio.sleep(2)
    await camera_settings_menu(callback)

# ============== BILDIRISHNOMA SOZLAMALARI ==============

@router.callback_query(F.data == "notification_settings")
async def notification_settings_menu(callback: CallbackQuery):
    """Bildirishnoma sozlamalari menyusi"""
    from utils.database import get_notification_settings, update_notification_settings
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    user_id = callback.from_user.id
    settings = await get_notification_settings(user_id)
    
    # Default settings agar yo'q bo'lsa
    task_reminders = settings.get('task_reminders', True) if settings else True
    morning_motivation = settings.get('morning_motivation', True) if settings else True
    weekly_reports = settings.get('weekly_reports', True) if settings else True
    
    task_status = "✅ Yoqilgan" if task_reminders else "❌ O'chirilgan"
    morning_status = "✅ Yoqilgan" if morning_motivation else "❌ O'chirilgan"
    weekly_status = "✅ Yoqilgan" if weekly_reports else "❌ O'chirilgan"
    
    text = (
        "🔔 **BILDIRISHNOMA SOZLAMALARI**\n\n"
        f"📋 Vazifa eslatmalari: {task_status}\n"
        f"☀️ Ertalabki motivatsiya: {morning_status}\n"
        f"📊 Haftalik hisobotlar: {weekly_status}\n\n"
        "Qaysi birini o'zgartirmoqchisiz?"
    )
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"📋 Vazifa eslatmalari: {'✅' if task_reminders else '❌'}",
                callback_data="toggle_task_reminders"
            )],
            [InlineKeyboardButton(
                text=f"☀️ Ertalabki motivatsiya: {'✅' if morning_motivation else '❌'}",
                callback_data="toggle_morning_motivation"
            )],
            [InlineKeyboardButton(
                text=f"📊 Haftalik hisobotlar: {'✅' if weekly_reports else '❌'}",
                callback_data="toggle_weekly_reports"
            )],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_settings")]
        ]
    )
    
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_notification(callback: CallbackQuery):
    """Bildirishnomani yoqish/o'chirish"""
    from utils.database import get_notification_settings, update_notification_settings
    
    user_id = callback.from_user.id
    setting_type = callback.data.replace("toggle_", "")
    
    # Hozirgi sozlamalarni olish
    settings = await get_notification_settings(user_id)
    if not settings:
        settings = {
            'task_reminders': True,
            'morning_motivation': True,
            'weekly_reports': True
        }
    
    # Toggle qilish
    if setting_type in settings:
        settings[setting_type] = not settings[setting_type]
        await update_notification_settings(user_id, settings)
        
        status = "yoqildi ✅" if settings[setting_type] else "o'chirildi ❌"
        
        setting_names = {
            'task_reminders': 'Vazifa eslatmalari',
            'morning_motivation': 'Ertalabki motivatsiya',
            'weekly_reports': 'Haftalik hisobotlar'
        }
        
        await callback.answer(
            f"{setting_names[setting_type]} {status}",
            show_alert=True
        )
        
        # Menyuni yangilash
        await notification_settings_menu(callback)
    else:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)

@router.message(F.text == "/settings")
async def cmd_settings(message: Message):
    """Sozlamalar buyrug'i"""
    await show_settings(message)
