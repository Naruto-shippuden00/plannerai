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

@router.message(F.text.in_(["➕ Vazifa qo'shish", "➕ Добавить задачу", "➕ Add Task"]))
async def add_task_start(message: Message, state: FSMContext):
    """Vazifa qo'shish boshlash"""
    from utils.database import get_user_language
    user_lang = await get_user_language(message.from_user.id)
    
    texts = {
        "uz": "📝 **Yangi vazifa qo'shish**\n\nVazifa nomini kiriting:\n\nMisol: SAT Math practice\nMisol: Python dasturlash o'rganish\nMisol: Kitob o'qish - 'Atomic Habits'",
        "ru": "📝 **Добавить новую задачу**\n\nВведите название задачи:\n\nПример: SAT Math practice\nПример: Изучение Python\nПример: Чтение книги - 'Atomic Habits'",
        "en": "📝 **Add New Task**\n\nEnter task name:\n\nExample: SAT Math practice\nExample: Learn Python programming\nExample: Read book - 'Atomic Habits'"
    }
    
    await state.set_state(AddTaskState.waiting_for_name)
    await message.answer(texts.get(user_lang, texts["uz"]), parse_mode="Markdown")

@router.message(AddTaskState.waiting_for_name)
async def add_task_name(message: Message, state: FSMContext):
    """Vazifa nomi"""
    from utils.database import get_user_language
    user_lang = await get_user_language(message.from_user.id)
    
    await state.update_data(task_name=message.text)
    await state.set_state(AddTaskState.waiting_for_category)
    
    prompts = {
        "uz": f"✅ Vazifa: **{message.text}**\n\nKategoriyani tanlang:",
        "ru": f"✅ Задача: **{message.text}**\n\nВыберите категорию:",
        "en": f"✅ Task: **{message.text}**\n\nSelect category:"
    }
    
    await message.answer(
        prompts.get(user_lang, prompts["uz"]),
        parse_mode="Markdown",
        reply_markup=task_category_keyboard(user_lang)
    )

@router.callback_query(F.data.startswith("cat_"))
async def add_task_category(callback: CallbackQuery, state: FSMContext):
    """Kategoriya tanlash"""
    from utils.database import get_user_language
    user_lang = await get_user_language(callback.from_user.id)
    
    category_map = {
        "cat_sat": "SAT",
        "cat_ielts": "IELTS",
        "cat_python": "Python",
        "cat_startup": "Startup",
        "cat_gym": "Gym",
        "cat_book": {"uz": "Kitob", "ru": "Книга", "en": "Book"},
        "cat_other": {"uz": "Boshqa", "ru": "Другое", "en": "Other"}
    }
    
    category_raw = category_map.get(callback.data, "Boshqa")
    if isinstance(category_raw, dict):
        category = category_raw.get(user_lang, category_raw["uz"])
    else:
        category = category_raw
        
    await state.update_data(category=category)
    await state.set_state(AddTaskState.waiting_for_priority)
    
    texts = {
        "uz": f"📂 Kategoriya: **{category}**\n\nPrioritetni tanlang:",
        "ru": f"📂 Категория: **{category}**\n\nВыберите приоритет:",
        "en": f"📂 Category: **{category}**\n\nSelect priority:"
    }
    
    await callback.message.edit_text(
        texts.get(user_lang, texts["uz"]),
        parse_mode="Markdown",
        reply_markup=priority_keyboard(user_lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("priority_"))
async def add_task_priority(callback: CallbackQuery, state: FSMContext):
    """Prioritet tanlash"""
    from utils.database import get_user_language
    user_lang = await get_user_language(callback.from_user.id)
    
    priority = int(callback.data.split("_")[1])
    await state.update_data(priority=priority)
    await state.set_state(AddTaskState.waiting_for_duration)
    
    priority_texts = {
        "uz": {3: "🔴 Juda muhim", 2: "🟡 O'rtacha", 1: "🟢 Past"},
        "ru": {3: "🔴 Очень важно", 2: "🟡 Средне", 1: "🟢 Низкий"},
        "en": {3: "🔴 Very important", 2: "🟡 Medium", 1: "🟢 Low"}
    }
    
    duration_prompt = {
        "uz": "⏱ Davomiylikni tanlang:",
        "ru": "⏱ Выберите продолжительность:",
        "en": "⏱ Select duration:"
    }
    
    priority_text = priority_texts.get(user_lang, priority_texts["uz"])[priority]
    
    await callback.message.edit_text(
        f"⭐ {priority_text}\n\n{duration_prompt.get(user_lang, duration_prompt['uz'])}",
        parse_mode="Markdown",
        reply_markup=duration_keyboard(user_lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("dur_"))
async def add_task_duration(callback: CallbackQuery, state: FSMContext):
    """Davomiylik tanlash"""
    from utils.database import get_user_language
    user_lang = await get_user_language(callback.from_user.id)
    
    if callback.data == "dur_custom":
        # Custom duration uchun state'ni saqlash
        await state.set_state(AddTaskState.waiting_for_duration)
        
        prompts = {
            "uz": "⏱ **Davomiylikni daqiqalarda kiriting:**\n\nMasalan:\n• 15 (15 daqiqa)\n• 45 (45 daqiqa)\n• 90 (1 soat 30 daqiqa)\n• 120 (2 soat)\n\nFaqat RAQAM kiriting!",
            "ru": "⏱ **Введите продолжительность в минутах:**\n\nНапример:\n• 15 (15 минут)\n• 45 (45 минут)\n• 90 (1 час 30 минут)\n• 120 (2 часа)\n\nВводите только ЧИСЛО!",
            "en": "⏱ **Enter duration in minutes:**\n\nFor example:\n• 15 (15 minutes)\n• 45 (45 minutes)\n• 90 (1 hour 30 minutes)\n• 120 (2 hours)\n\nEnter NUMBER only!"
        }
        
        await callback.message.edit_text(
            prompts.get(user_lang, prompts["uz"]),
            parse_mode="Markdown"
        )
        await callback.answer()
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
    
    success_texts = {
        "uz": f"✅ **VAZIFA MUVAFFAQIYATLI QO'SHILDI!**\n\n📝 Nomi: **{data['task_name']}**\n📂 Kategoriya: {data['category']}\n⭐ Prioritet: {data['priority']}/3\n⏱ Davomiyligi: {duration} daqiqa\n\n═══════════════════════\n\n🎯 **KEYINGI QADAMLAR:**\n\n1️⃣ Yana vazifa qo'shing (ixtiyoriy)\n2️⃣ **'🤖 AI Jadval'** tugmasini bosing\n3️⃣ AI optimal jadval tuzadi\n4️⃣ Jadvalni tasdiqlang\n\n⏰ **KEYIN AVTOMATIK:**\n• Vazifa vaqti kelganda bildirishnoma\n• Har 5 daqiqada eslatma (rasm yuborguningizcha)\n• Rasm yuborish → Pomodoro timer\n• {duration} daqiqa fokusda ishlash\n• 10 daqiqa tanaffus\n• Keyingi vazifa avtomatik boshlanadi\n\n💪 **100% avtomatik nazorat!**",
        "ru": f"✅ **ЗАДАЧА УСПЕШНО ДОБАВЛЕНА!**\n\n📝 Название: **{data['task_name']}**\n📂 Категория: {data['category']}\n⭐ Приоритет: {data['priority']}/3\n⏱ Продолжительность: {duration} минут\n\n═══════════════════════\n\n🎯 **СЛЕДУЮЩИЕ ШАГИ:**\n\n1️⃣ Добавьте еще задачи (опционально)\n2️⃣ Нажмите **'🤖 AI Расписание'**\n3️⃣ AI создаст оптимальное расписание\n4️⃣ Подтвердите расписание\n\n⏰ **ЗАТЕМ АВТОМАТИЧЕСКИ:**\n• Уведомление при наступлении времени\n• Напоминания каждые 5 минут (пока не отправите фото)\n• Отправка фото → Pomodoro таймер\n• {duration} минут в фокусе\n• 10 минут перерыв\n• Следующая задача запускается автоматически\n\n💪 **100% автоматический контроль!**",
        "en": f"✅ **TASK SUCCESSFULLY ADDED!**\n\n📝 Name: **{data['task_name']}**\n📂 Category: {data['category']}\n⭐ Priority: {data['priority']}/3\n⏱ Duration: {duration} minutes\n\n═══════════════════════\n\n🎯 **NEXT STEPS:**\n\n1️⃣ Add more tasks (optional)\n2️⃣ Click **'🤖 AI Schedule'** button\n3️⃣ AI creates optimal schedule\n4️⃣ Confirm schedule\n\n⏰ **THEN AUTOMATICALLY:**\n• Notification when task time comes\n• Reminders every 5 minutes (until you send photo)\n• Send photo → Pomodoro timer\n• {duration} minutes in focus\n• 10 minute break\n• Next task starts automatically\n\n💪 **100% automatic control!**"
    }
    
    next_prompts = {
        "uz": "🎯 Yana vazifa qo'shasizmi yoki jadvalni tuzamizmi?",
        "ru": "🎯 Добавить еще задачу или создать расписание?",
        "en": "🎯 Add another task or create schedule?"
    }
    
    await callback.message.edit_text(
        success_texts.get(user_lang, success_texts["uz"]),
        parse_mode="Markdown"
    )
    
    await callback.message.answer(
        next_prompts.get(user_lang, next_prompts["uz"]),
        reply_markup=main_menu_keyboard(user_lang)
    )
    await callback.answer("✅ Vazifa qo'shildi!" if user_lang == "uz" else "✅ Задача добавлена!" if user_lang == "ru" else "✅ Task added!", show_alert=False)

# Custom duration handler
@router.message(AddTaskState.waiting_for_duration, F.text)
async def add_task_custom_duration(message: Message, state: FSMContext):
    """Custom davomiylikni qabul qilish"""
    try:
        # Faqat raqam tekshirish
        duration = int(message.text.strip())
        
        if duration < 5 or duration > 480:  # 5 daqiqadan 8 soatgacha
            await message.answer(
                "❌ **Noto'g'ri qiymat!**\n\n"
                "Davomiylik 5 dan 480 daqiqagacha bo'lishi kerak.\n\n"
                "Qaytadan kiriting:",
                parse_mode="Markdown"
            )
            return
        
        data = await state.get_data()
        
        # Vazifani saqlash
        task_id = await add_task(
            user_id=message.from_user.id,
            task_name=data['task_name'],
            category=data['category'],
            priority=data['priority'],
            duration=duration
        )
        
        await state.clear()
        
        from utils.database import get_user_language
        user_lang = await get_user_language(message.from_user.id)
        
        await message.answer(
            f"✅ **VAZIFA MUVAFFAQIYATLI QO'SHILDI!**\n\n"
            f"📝 Nomi: **{data['task_name']}**\n"
            f"📂 Kategoriya: {data['category']}\n"
            f"⭐ Prioritet: {data['priority']}/3\n"
            f"⏱ Davomiyligi: {duration} daqiqa\n\n"
            f"═══════════════════════\n\n"
            f"🎯 **KEYINGI QADAMLAR:**\n\n"
            f"1️⃣ Yana vazifa qo'shing (ixtiyoriy)\n"
            f"2️⃣ **'🤖 AI Jadval'** tugmasini bosing\n"
            f"3️⃣ AI optimal jadval tuzadi\n"
            f"4️⃣ Jadvalni tasdiqlang\n\n"
            f"💪 **100% avtomatik nazorat!**",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(user_lang)
        )
        
    except ValueError:
        await message.answer(
            "❌ **Xato!**\n\n"
            "Faqat RAQAM kiriting!\n\n"
            "Misol: 45 yoki 90\n\n"
            "Qaytadan kiriting:",
            parse_mode="Markdown"
        )

@router.message(F.text.in_(["📋 Vazifalarim", "📋 Мои задачи", "📋 My Tasks"]))
async def show_tasks(message: Message):
    """Vazifalarni ko'rsatish"""
    from utils.database import get_user_language
    user_lang = await get_user_language(message.from_user.id)
    
    tasks = await get_user_tasks(message.from_user.id)
    
    if not tasks:
        texts = {
            "uz": "📋 **Sizda hali vazifalar yo'q**\n\n➕ Vazifa qo'shish tugmasini bosing!",
            "ru": "📋 **У вас пока нет задач**\n\n➕ Нажмите кнопку Добавить задачу!",
            "en": "📋 **You have no tasks yet**\n\n➕ Click Add Task button!"
        }
        await message.answer(texts.get(user_lang, texts["uz"]), parse_mode="Markdown")
        return
    
    title_texts = {
        "uz": "📋 **Sizning vazifalaringiz:**\n\n",
        "ru": "📋 **Ваши задачи:**\n\n",
        "en": "📋 **Your tasks:**\n\n"
    }
    text = title_texts.get(user_lang, title_texts["uz"])
    
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
        "Книга": "📖",
        "Book": "📖",
        "Boshqa": "📌",
        "Другое": "📌",
        "Other": "📌"
    }
    
    for category, cat_tasks in by_category.items():
        emoji = category_emoji.get(category, "📌")
        text += f"\n{emoji} **{category}**\n"
        
        for task in cat_tasks:
            priority_emoji = "🔴" if task['priority'] == 3 else "🟡" if task['priority'] == 2 else "🟢"
            text += f"  {priority_emoji} {task['task_name']} ({task['duration_minutes']} min)\n"
    
    footer_texts = {
        "uz": f"\n\n📊 Jami: {len(tasks)} ta vazifa\n\n💡 Vazifani boshqarish uchun quyidagi tugmalarni bosing:",
        "ru": f"\n\n📊 Всего: {len(tasks)} задач\n\n💡 Для управления задачами нажмите кнопки ниже:",
        "en": f"\n\n📊 Total: {len(tasks)} tasks\n\n💡 Click buttons below to manage tasks:"
    }
    text += footer_texts.get(user_lang, footer_texts["uz"])
    
    await message.answer(text, parse_mode="Markdown")
    
    # Har bir vazifa uchun alohida boshqaruv tugmalari
    for task in tasks:
        task_text = f"📝 **{task['task_name']}**\n"
        task_text += f"📂 {task['category']} | ⏱ {task['duration_minutes']} min\n"
        
        priority_texts = {
            "uz": {"3": "🔴 Juda muhim", "2": "🟡 O'rtacha", "1": "🟢 Past"},
            "ru": {"3": "🔴 Очень важно", "2": "🟡 Средне", "1": "🟢 Низкий"},
            "en": {"3": "🔴 Very important", "2": "🟡 Medium", "1": "🟢 Low"}
        }
        priority_text = priority_texts.get(user_lang, priority_texts["uz"])[str(task['priority'])]
        task_text += f"⭐ {priority_text}"
        
        await message.answer(
            task_text,
            parse_mode="Markdown",
            reply_markup=task_action_keyboard(task['id'], user_lang)
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

@router.message(F.text.in_(["🗑 Vazifalarni boshqarish", "🗑 Управление задачами", "🗑 Manage Tasks"]))
async def manage_tasks_menu(message: Message):
    """Vazifalarni boshqarish menyusi"""
    from utils.database import get_user_language
    user_lang = await get_user_language(message.from_user.id)
    
    tasks = await get_user_tasks(message.from_user.id)
    completed_tasks = await get_completed_tasks(message.from_user.id)
    
    if not tasks and not completed_tasks:
        texts = {
            "uz": "📋 **Sizda vazifalar yo'q**\n\nAvval vazifa qo'shing!",
            "ru": "📋 **У вас нет задач**\n\nСначала добавьте задачу!",
            "en": "📋 **You have no tasks**\n\nAdd task first!"
        }
        await message.answer(
            texts.get(user_lang, texts["uz"]),
            reply_markup=main_menu_keyboard(user_lang)
        )
        return
    
    title_texts = {
        "uz": "🗑 **VAZIFALARNI BOSHQARISH**\n\nBu yerda barcha vazifalaringizni ko'rishingiz va boshqarishingiz mumkin:\n\n• ✅ Bajarilganlar\n• 📝 Faol vazifalar\n• 🗑 O'chirish\n• 🔄 Qayta faollashtirish\n\nQuyidagi bo'limlarni tanlang:",
        "ru": "🗑 **УПРАВЛЕНИЕ ЗАДАЧАМИ**\n\nЗдесь вы можете просматривать и управлять всеми задачами:\n\n• ✅ Выполненные\n• 📝 Активные задачи\n• 🗑 Удалить\n• 🔄 Реактивировать\n\nВыберите раздел ниже:",
        "en": "🗑 **TASK MANAGEMENT**\n\nHere you can view and manage all your tasks:\n\n• ✅ Completed\n• 📝 Active tasks\n• 🗑 Delete\n• 🔄 Reactivate\n\nSelect section below:"
    }
    
    await message.answer(
        title_texts.get(user_lang, title_texts["uz"]),
        parse_mode="Markdown",
        reply_markup=task_management_keyboard(user_lang)
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
