"""
Vazifalar bilan ishlash
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.database import add_task, get_user_tasks, delete_task
from utils.keyboards import (
    task_category_keyboard, 
    priority_keyboard, 
    duration_keyboard,
    main_menu_keyboard,
    task_action_keyboard
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
    
    await message.answer(text, parse_mode="Markdown")

@router.callback_query(F.data.startswith("delete_"))
async def delete_task_handler(callback: CallbackQuery):
    """Vazifani o'chirish"""
    task_id = int(callback.data.split("_")[1])
    await delete_task(task_id)
    
    await callback.message.edit_text("🗑 Vazifa o'chirildi!")
    await callback.answer("Vazifa o'chirildi")
