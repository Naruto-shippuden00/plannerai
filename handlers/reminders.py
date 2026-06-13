"""
Eslatmalar va vazifalarni bajarish
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from zoneinfo import ZoneInfo
import os

from utils.database import mark_task_completed, get_schedule
from utils.keyboards import task_action_keyboard, main_menu_keyboard

# Tashkent vaqt zonasi
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

router = Router()

class CompletionState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_notes = State()

# Vazifa completion tracking
pending_completions = {}

@router.callback_query(F.data.startswith("complete_"))
async def start_completion(callback: CallbackQuery, state: FSMContext):
    """Vazifani bajarish jarayonini boshlash"""
    task_id = int(callback.data.split("_")[1])
    
    await state.update_data(
        task_id=task_id,
        scheduled_time=datetime.now(TASHKENT_TZ).isoformat()
    )
    await state.set_state(CompletionState.waiting_for_photo)
    
    await callback.message.edit_text(
        "📸 **Ajoyib!**\n\n"
        "Endi vazifani bajarganingizni tasdiqlovchi **rasm yuboring**:\n\n"
        "Misol:\n"
        "• SAT uchun: mashq daftari yoki test natijasi\n"
        "• Python uchun: kod screenshot\n"
        "• Kitob uchun: o'qiyotgan sahifa\n"
        "• Gym uchun: mashq jarayoni\n\n"
        "⏭ Rasm yo'q bo'lsa /skip yozing",
        parse_mode="Markdown"
    )
    await callback.answer()

@router.message(CompletionState.waiting_for_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext):
    """Rasm qabul qilish"""
    data = await state.get_data()
    
    # Rasmni saqlash
    photo = message.photo[-1]  # Eng katta o'lcham
    photo_dir = "data/photos"
    os.makedirs(photo_dir, exist_ok=True)
    
    file_name = f"{message.from_user.id}_{datetime.now(TASHKENT_TZ).strftime('%Y%m%d_%H%M%S')}.jpg"
    photo_path = os.path.join(photo_dir, file_name)
    
    # Rasmni yuklab olish
    await message.bot.download(photo.file_id, photo_path)
    
    await state.update_data(photo_path=photo_path)
    await state.set_state(CompletionState.waiting_for_notes)
    
    await message.answer(
        "✅ Rasm qabul qilindi!\n\n"
        "📝 Endi qisqacha izoh yozing:\n\n"
        "Misol:\n"
        "• 'SAT Math 20 ta savol bajardim'\n"
        "• 'Python da loop mavzusini o'rgandim'\n"
        "• '25 sahifa o'qidim'\n\n"
        "⏭ Izoh qo'shmasangiz /skip yozing",
        reply_markup=main_menu_keyboard()
    )

@router.message(CompletionState.waiting_for_photo, F.text == "/skip")
async def skip_photo(message: Message, state: FSMContext):
    """Rasmni o'tkazib yuborish"""
    await state.update_data(photo_path=None)
    await state.set_state(CompletionState.waiting_for_notes)
    
    await message.answer(
        "📝 Qisqacha izoh yozing yoki /skip yozing:",
        reply_markup=main_menu_keyboard()
    )

@router.message(CompletionState.waiting_for_notes, F.text)
async def receive_notes(message: Message, state: FSMContext):
    """Izohni qabul qilish va yakunlash"""
    data = await state.get_data()
    
    notes = None if message.text == "/skip" else message.text
    
    # Ma'lumotlar bazasiga saqlash
    await mark_task_completed(
        user_id=message.from_user.id,
        task_id=data['task_id'],
        scheduled_time=data['scheduled_time'],
        photo_path=data.get('photo_path'),
        notes=notes
    )
    
    await state.clear()
    
    # Congratulations message
    await message.answer(
        "🎉 **Ajoyib ish qildingiz!**\n\n"
        "✅ Vazifa bajarilgan deb belgilandi!\n"
        "📊 Statistikangiz yangilandi.\n\n"
        "Davom eting! Siz zo'rsiz! 💪",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(F.data.startswith("snooze_"))
async def snooze_task(callback: CallbackQuery):
    """Vazifani kechiktrish"""
    task_id = int(callback.data.split("_")[1])
    
    await callback.message.edit_text(
        "⏰ **Vazifa kechiktirildi**\n\n"
        "30 daqiqadan keyin yana eslataman! ⏳",
        parse_mode="Markdown"
    )
    
    # TODO: Scheduler bilan kechiktrish
    await callback.answer("30 daqiqa kechiktirildi")

@router.message(F.text == "✅ Bajarilganlar")
async def show_completions(message: Message):
    """Bajarilgan vazifalarni ko'rsatish"""
    # Bu qismni keyinroq statistika bilan birga qo'shamiz
    await message.answer(
        "📊 Bajarilgan vazifalarni ko'rish uchun '📊 Statistika' tugmasini bosing!",
        reply_markup=main_menu_keyboard()
    )
