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
    await show_settings(callback.message)
    await callback.answer()

@router.message(F.text == "/settings")
async def cmd_settings(message: Message):
    """Sozlamalar buyrug'i"""
    await show_settings(message)
