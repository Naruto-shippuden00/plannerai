"""
Vazifalar bilan ishlash
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from utils.database import (
    add_task, 
    get_user_tasks, 
    delete_task, 
    delete_task_by_name,
    get_task_by_name,
    mark_task_as_completed,
    unmark_task_completion,
    get_completed_tasks
)
from utils.keyboards import (
    task_category_keyboard, 
    priority_keyboard, 
    duration_keyboard,
    main_menu_keyboard,
    task_action_keyboard,
    task_management_keyboard
)

router = Router()

class AddTaskState(StatesGroup):
    waiting_for_name = State()
    waiting_for_category = State()
    waiting_for_priority = State()
    waiting_for_duration = State()

@router.message(F.text == "➕ Vazifa qo'shish")
async def add_task_start(message: Message, state: FSMContext):
    """Vazifa qo'shish boshlash"""
    await state.set_state(AddTaskState.waiting_for_name)
    await message.answer(
        "📝 **Yangi vazifa qo'shish**\n\n"
        "Vazifa nomini kiriting:\n\n"
        "Misol: SAT Math practice\n"
        "Misol: Python dasturlash o'rganish\n"
        "Misol: Kitob o'qish - 'Atomic Habits'",
        parse_mode="Markdown"
    )

@router.message(AddTaskState.waiting_for_name)
async def add_task_name(message: Message, state: FSMContext):
    """Vazifa nomi"""
    await state.update_data(task_name=message.text)
    await state.set_state(AddTaskState.waiting_for_category)
    
    await message.answer(
        f"✅ Vazifa: **{message.text}**\n\n"
        "Kategoriyani tanlang:",
        parse_mode="Markdown",
        reply_markup=task_category_keyboard()
    )

@router.callback_query(F.data.startswith("cat_"))
async def add_task_category(callback: CallbackQuery, state: FSMContext):
    """Kategoriya tanlash"""
    category_map = {
        "cat_sat": "SAT",
        "cat_ielts": "IELTS",
        "cat_python": "Python",
        "cat_startup": "Startup",
        "cat_gym": "Gym",
        "cat_book": "Kitob",
        "cat_other": "Boshqa"
    }
    
    category = category_map.get(callback.data, "Boshqa")
    await state.update_data(category=category)
    await state.set_state(AddTaskState.waiting_for_priority)
    
    await callback.message.edit_text(
        f"📂 Kategoriya: **{category}**\n\n"
        "Prioritetni tanlang:",
        parse_mode="Markdown",
        reply_markup=priority_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("priority_"))
async def add_task_priority(callback: CallbackQuery, state: FSMContext):
    """Prioritet tanlash"""
    priority = int(callback.data.split("_")[1])
    await state.update_data(priority=priority)
    await state.set_state(AddTaskState.waiting_for_duration)
    
    priority_text = {3: "🔴 Juda muhim", 2: "🟡 O'rtacha", 1: "🟢 Past"}
    
    await callback.message.edit_text(
        f"⭐ Prioritet: **{priority_text[priority]}**\n\n"
        "Davomiylikni tanlang:",
        parse_mode="Markdown",
        reply_markup=duration_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("dur_"))
async def add_task_duration(callback: CallbackQuery, state: FSMContext):
    """Davomiylik tanlash"""
    if callback.data == "dur_custom":
        await callback.message.edit_text(
            "⏱ Davomiylikni daqiqalarda kiriting:\n\n"
            "Masalan: 45 yoki 90"
        )
        return
    
    duration = int(callback.data.split("_")[1])
    data = await state.get_data()
    
    # Vazifani saqlash
    task_id = await add_task(
        user_id=callback.from_user.id,
        task_name=data['task_name'],
        category=data['category'],
        priority=data['priority'],
        duration=duration
    )
    
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ **Vazifa muvaffaqiyatli qo'shildi!**\n\n"
        f"📝 Nomi: {data['task_name']}\n"
        f"📂 Kategoriya: {data['category']}\n"
        f"⭐ Prioritet: {data['priority']}/3\n"
        f"⏱ Davomiyligi: {duration} daqiqa\n\n"
        f"🤖 Endi 'AI Jadval' tugmasini bosing va men sizga optimal jadval tuzaman!",
        parse_mode="Markdown"
    )
    
    await callback.message.answer(
        "Yana vazifa qo'shasizmi yoki jadval tuzamizmi?",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@router.message(F.text == "📋 Vazifalarim")
async def show_tasks(message: Message):
    """Vazifalarni ko'rsatish"""
    tasks = await get_user_tasks(message.from_user.id)
    
    if not tasks:
        await message.answer(
            "📋 **Sizda hali vazifalar yo'q**\n\n"
            "➕ Vazifa qo'shish tugmasini bosing!",
            parse_mode="Markdown"
        )
        return
    
    text = "📋 **Sizning vazifalaringiz:**\n\n"
    
    # Kategoriya bo'yicha guruplash
    by_category = {}
    for task in tasks:
        cat = task['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(task)
    
    category_emoji = {
        "SAT": "📚",
        "IELTS": "🗣",
        "Python": "🐍",
        "Startup": "💡",
        "Gym": "💪",
        "Kitob": "📖",
        "Boshqa": "📌"
    }
    
    for category, cat_tasks in by_category.items():
        emoji = category_emoji.get(category, "📌")
        text += f"\n{emoji} **{category}**\n"
        
        for task in cat_tasks:
            priority_emoji = "🔴" if task['priority'] == 3 else "🟡" if task['priority'] == 2 else "🟢"
            text += f"  {priority_emoji} {task['task_name']} ({task['duration_minutes']} min)\n"
    
    text += f"\n\n📊 Jami: {len(tasks)} ta vazifa"
    text += "\n\n💡 Vazifani boshqarish uchun quyidagi tugmalarni bosing:"
    
    await message.answer(text, parse_mode="Markdown")
    
    # Har bir vazifa uchun alohida boshqaruv tugmalari
    for task in tasks:
        task_text = f"📝 **{task['task_name']}**\n"
        task_text += f"📂 {task['category']} | ⏱ {task['duration_minutes']} min\n"
        priority_text = "🔴 Juda muhim" if task['priority'] == 3 else "🟡 O'rtacha" if task['priority'] == 2 else "🟢 Past"
        task_text += f"⭐ Prioritet: {priority_text}"
        
        await message.answer(
            task_text,
            parse_mode="Markdown",
            reply_markup=task_action_keyboard(task['id'])
        )

@router.callback_query(F.data.startswith("delete_"))
async def delete_task_handler(callback: CallbackQuery):
    """Vazifani o'chirish"""
    task_id = int(callback.data.split("_")[1])
    await delete_task(task_id)
    
    await callback.message.edit_text(
        "🗑 **Vazifa o'chirildi!**\n\n"
        "Vazifa muvaffaqiyatli o'chirildi.\n"
        "📋 Vazifalarim tugmasini bosib yangilangan ro'yxatni ko'ring.",
        parse_mode="Markdown"
    )
    await callback.answer("✅ Vazifa o'chirildi", show_alert=True)

@router.callback_query(F.data.startswith("complete_"))
async def complete_task_handler(callback: CallbackQuery):
    """Vazifani bajarilgan deb belgilash (o'chirmasdan)"""
    task_id = int(callback.data.split("_")[1])
    
    # Vazifani bajarilgan deb belgilash
    await mark_task_as_completed(task_id)
    
    await callback.message.edit_text(
        "✅ **Ajoyib! Vazifa bajarildi!**\n\n"
        "🎉 Tabriklaymiz! Siz yana bir maqsadga erishdingiz!\n"
        "📊 Vazifa bajarilgan deb belgilandi va ro'yxatda qoladi.\n\n"
        "💡 Qayta faollashtirish uchun '📋 Vazifalarim' bo'limiga o'ting.",
        parse_mode="Markdown"
    )
    await callback.answer("🎉 Barakalla!", show_alert=True)

@router.callback_query(F.data.startswith("snooze_"))
async def snooze_task_handler(callback: CallbackQuery):
    """Vazifani keyinroqqa qoldirish"""
    task_id = int(callback.data.split("_")[1])
    
    await callback.message.edit_text(
        "⏰ **Vazifa keyinroqqa qoldirildi**\n\n"
        "Bu vazifa uchun keyinroq eslatma yuboramiz.\n"
        "⚙️ Sozlamalarda eslatma vaqtlarini sozlashingiz mumkin.",
        parse_mode="Markdown"
    )
    await callback.answer("⏰ Keyinroqqa qoldirildi")

# ============== VAZIFANI O'CHIRISH TIZIMI ==============

@router.message(F.text.startswith("/remove_"))
async def remove_task_by_command(message: Message):
    """
    Vazifani buyruq orqali o'chirish
    Misol: /remove_SAT Math yoki /remove_Kitob o'qish
    """
    # Buyruqdan vazifa nomini ajratish
    command_text = message.text[8:]  # "/remove_" dan keyingi qism
    
    if not command_text or len(command_text.strip()) < 2:
        await message.answer(
            "❌ **Noto'g'ri format!**\n\n"
            "Vazifa nomini kiriting:\n\n"
            "Misol:\n"
            "• `/remove_SAT Math`\n"
            "• `/remove_Kitob o'qish`\n"
            "• `/remove_Python`\n\n"
            "Yoki '🗑 Vazifalarni boshqarish' tugmasini bosing.",
            parse_mode="Markdown"
        )
        return
    
    task_name = command_text.strip()
    
    # Vazifani topish
    task = await get_task_by_name(message.from_user.id, task_name)
    
    if not task:
        await message.answer(
            f"❌ **Vazifa topilmadi!**\n\n"
            f"🔍 Qidirildi: `{task_name}`\n\n"
            f"💡 Vazifaning to'g'ri nomini kiriting yoki\n"
            f"'📋 Vazifalarim' bo'limidan ko'ring.",
            parse_mode="Markdown"
        )
        return
    
    # Tasdiqlash
    await message.answer(
        f"⚠️ **Vazifani o'chirmoqchimisiz?**\n\n"
        f"📝 Vazifa: **{task['task_name']}**\n"
        f"📂 Kategoriya: {task['category']}\n"
        f"⏱ Davomiyligi: {task['duration_minutes']} daqiqa\n\n"
        f"❗️ Bu amalni bekor qilib bo'lmaydi!\n\n"
        f"Tasdiqlash uchun buyruqni qayta kiriting:\n"
        f"`/confirm_remove_{task['id']}`",
        parse_mode="Markdown"
    )

@router.message(F.text.startswith("/confirm_remove_"))
async def confirm_remove_task(message: Message):
    """Vazifani o'chirishni tasdiqlash"""
    try:
        task_id = int(message.text.split("_")[2])
        
        # O'chirish
        await delete_task(task_id)
        
        await message.answer(
            "✅ **Vazifa o'chirildi!**\n\n"
            "🗑 Vazifa tizimdan butunlay o'chirildi.\n\n"
            "📋 Yangilangan ro'yxatni ko'rish uchun '📋 Vazifalarim' tugmasini bosing.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        
    except (IndexError, ValueError):
        await message.answer(
            "❌ **Xatolik!**\n\n"
            "Noto'g'ri tasdiqlash buyrug'i.\n"
            "Iltimos, qaytadan urinib ko'ring.",
            reply_markup=main_menu_keyboard()
        )

@router.message(F.text == "🗑 Vazifalarni boshqarish")
async def manage_tasks_menu(message: Message):
    """Vazifalarni boshqarish menyusi"""
    tasks = await get_user_tasks(message.from_user.id)
    completed_tasks = await get_completed_tasks(message.from_user.id)
    
    if not tasks and not completed_tasks:
        await message.answer(
            "📋 **Sizda vazifalar yo'q**\n\n"
            "Avval vazifa qo'shing!",
            reply_markup=main_menu_keyboard()
        )
        return
    
    await message.answer(
        "🗑 **VAZIFALARNI BOSHQARISH**\n\n"
        "Bu yerda barcha vazifalaringizni ko'rishingiz va boshqarishingiz mumkin:\n\n"
        "• ✅ Bajarilganlar\n"
        "• 📝 Faol vazifalar\n"
        "• 🗑 O'chirish\n"
        "• 🔄 Qayta faollashtirish\n\n"
        "Quyidagi bo'limlarni tanlang:",
        parse_mode="Markdown",
        reply_markup=task_management_keyboard()
    )

@router.callback_query(F.data == "show_active_tasks")
async def show_active_tasks(callback: CallbackQuery):
    """Faol vazifalarni ko'rsatish"""
    tasks = await get_user_tasks(callback.from_user.id)
    
    if not tasks:
        await callback.message.edit_text(
            "📋 **Faol vazifalar yo'q**\n\n"
            "Barcha vazifalar bajarilgan yoki o'chirilgan.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    text = "📝 **FAOL VAZIFALAR**\n\n"
    
    for task in tasks:
        priority_emoji = "🔴" if task['priority'] == 3 else "🟡" if task['priority'] == 2 else "🟢"
        text += f"{priority_emoji} **{task['task_name']}**\n"
        text += f"   📂 {task['category']} | ⏱ {task['duration_minutes']} min\n"
        text += f"   ID: `{task['id']}`\n\n"
    
    text += "\n💡 O'chirish: `/remove_vazifa_nomi`"
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data == "show_completed_tasks")
async def show_completed_tasks_cb(callback: CallbackQuery):
    """Bajarilgan vazifalarni ko'rsatish"""
    tasks = await get_completed_tasks(callback.from_user.id)
    
    if not tasks:
        await callback.message.edit_text(
            "✅ **Bajarilgan vazifalar yo'q**\n\n"
            "Hali hech qanday vazifa bajarilmagan.",
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    text = "✅ **BAJARILGAN VAZIFALAR**\n\n"
    
    for task in tasks:
        text += f"✔️ **{task['task_name']}**\n"
        text += f"   📂 {task['category']} | ⏱ {task['duration_minutes']} min\n"
        
        if task['completed_at']:
            completed_date = datetime.fromisoformat(task['completed_at'])
            text += f"   📅 {completed_date.strftime('%d.%m.%Y %H:%M')}\n"
        
        text += f"   🔄 Qayta faollashtirish: `/reactivate_{task['id']}`\n\n"
    
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

@router.message(F.text.startswith("/reactivate_"))
async def reactivate_task(message: Message):
    """Bajarilgan vazifani qayta faollashtirish"""
    try:
        task_id = int(message.text.split("_")[1])
        
        # Vazifani qayta faollashtirish
        await unmark_task_completion(task_id)
        
        await message.answer(
            "🔄 **Vazifa qayta faollashtirildi!**\n\n"
            "✅ Vazifa yana faol vazifalar ro'yxatiga qo'shildi.\n\n"
            "📋 Jadvalni qayta tuzishingiz kerak bo'lishi mumkin.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        
    except (IndexError, ValueError):
        await message.answer(
            "❌ **Xatolik!**\n\n"
            "Noto'g'ri buyruq formati.",
            reply_markup=main_menu_keyboard()
        )

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await callback.message.edit_text(
        "🏠 Asosiy menyuga qaytdingiz.",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()
