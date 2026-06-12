"""
Jadval bilan ishlash
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from utils.database import (
    get_user_tasks, 
    get_schedule, 
    add_schedule_item,
    clear_schedule,
    get_user_settings
)
from utils.ai_helper import generate_schedule
from utils.keyboards import (
    confirm_schedule_keyboard,
    day_navigation_keyboard,
    main_menu_keyboard
)

router = Router()

# Temp storage for generated schedule
user_schedules = {}

@router.message(F.text == "🤖 AI Jadval")
async def generate_ai_schedule(message: Message):
    """AI bilan jadval tuzish"""
    user_id = message.from_user.id
    tasks = await get_user_tasks(user_id)
    
    if not tasks:
        await message.answer(
            "❌ Jadval tuzish uchun avval vazifalar qo'shing!\n\n"
            "➕ Vazifa qo'shish tugmasini bosing.",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # Foydalanuvchi sozlamalarini olish
    settings = await get_user_settings(user_id)
    work_start = settings.get('work_start_time', '08:00')
    work_end = settings.get('work_end_time', '16:00')
    
    # Loading message
    loading_msg = await message.answer(
        "🤖 AI jadval tuzmoqda...\n\n"
        "⏳ Bir oz kuting, sizning vazifalaringizni tahlil qilyapman va "
        "optimal jadval yaratyapman..."
    )
    
    # AI bilan jadval generatsiya
    # Vaqtni soat va daqiqaga ajratish
    work_start_hour = int(work_start.split(':')[0])
    work_end_hour = int(work_end.split(':')[0])
    
    constraints = {
        "work_hours": [work_start_hour, work_end_hour],
        "work_start_time": work_start,
        "work_end_time": work_end,
        "work_days": [0, 1, 2, 3, 4, 5],  # Dushanba-Shanba
        "sleep_hours": [23, 6],
        "priority_focused": True
    }
    
    try:
        schedule = await generate_schedule(tasks, constraints)
        user_schedules[user_id] = schedule
        
        # Jadvalni formatlash
        schedule_text = format_schedule_preview(schedule)
        
        await loading_msg.edit_text(
            f"✅ **Jadval tayyor!**\n\n{schedule_text}\n\n"
            f"Bu jadval sizning prioritetlaringiz va ish vaqtingizni "
            f"({work_start}-{work_end}) hisobga olgan holda tuzildi.\n\n"
            "**Tasdiqlaysizmi?**",
            parse_mode="Markdown",
            reply_markup=confirm_schedule_keyboard()
        )
        
    except Exception as e:
        await loading_msg.edit_text(
            f"❌ Xatolik yuz berdi: {str(e)}\n\n"
            "Qaytadan urinib ko'ring yoki /help buyrug'ini kiriting."
        )

def format_schedule_preview(schedule: dict) -> str:
    """Jadvalni formatlash - statistika bilan"""
    day_names = {
        "monday": "Dushanba",
        "tuesday": "Seshanba", 
        "wednesday": "Chorshanba",
        "thursday": "Payshanba",
        "friday": "Juma",
        "saturday": "Shanba",
        "sunday": "Yakshanba"
    }
    
    # Statistika hisoblash
    total_sessions = 0
    task_frequency = {}
    
    for day_eng, items in schedule.items():
        if day_eng == "sunday":
            continue  # Yakshanba review kuni
        for item in items:
            total_sessions += 1
            task_name = item.get('task', 'N/A')
            task_frequency[task_name] = task_frequency.get(task_name, 0) + 1
    
    # Haftalik statistika
    text = "📊 **HAFTALIK JADVAL STATISTIKASI:**\n\n"
    text += f"📚 Jami sessionlar: {total_sessions}\n"
    text += f"📝 Har bir vazifa:\n"
    for task, count in sorted(task_frequency.items(), key=lambda x: x[1], reverse=True):
        text += f"   • {task}: {count}x haftada\n"
    text += f"\n{'='*30}\n\n"
    
    # Kunlik jadval
    for day_eng, day_uz in day_names.items():
        if day_eng in schedule and schedule[day_eng]:
            emoji = "📍" if day_eng == datetime.now().strftime("%A").lower() else "📅"
            text += f"\n{emoji} **{day_uz}**\n"
            for item in schedule[day_eng]:
                time = item.get('time', 'N/A')
                task = item.get('task', 'N/A')
                text += f"  • {time} - {task}\n"
    
    return text

@router.callback_query(F.data == "confirm_schedule")
async def confirm_schedule_handler(callback: CallbackQuery):
    """Jadvalni tasdiqlash"""
    user_id = callback.from_user.id
    
    if user_id not in user_schedules:
        await callback.answer("Jadval topilmadi. Qaytadan tuzing.")
        return
    
    schedule = user_schedules[user_id]
    
    # Eski jadvalni tozalash
    await clear_schedule(user_id)
    
    # Yangi jadvalni saqlash
    day_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2,
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }
    
    saved_count = 0
    for day_eng, day_num in day_map.items():
        if day_eng in schedule:
            for item in schedule[day_eng]:
                task_id = item.get('task_id')
                time_range = item.get('time', '').split('-')
                
                if len(time_range) == 2 and task_id:
                    start_time = time_range[0].strip()
                    end_time = time_range[1].strip()
                    
                    await add_schedule_item(
                        user_id=user_id,
                        task_id=task_id,
                        day_of_week=day_num,
                        start_time=start_time,
                        end_time=end_time
                    )
                    saved_count += 1
    
    del user_schedules[user_id]
    
    await callback.message.edit_text(
        f"✅ **JADVAL TASDIQLANDI!**\n\n"
        f"📊 {saved_count} ta vazifa jadvalga qo'shildi.\n\n"
        f"═══════════════════════\n\n"
        f"🎯 **ENDI AVTOMATIK ISHLAYDI:**\n\n"
        f"1️⃣ **Vazifa vaqti** - Aniq bildirishnoma\n"
        f"2️⃣ **Cheksiz eslatmalar** - Har 5 daqiqada\n"
        f"3️⃣ **Rasm yuboring** - Bildirishnomalar to'xtaydi\n"
        f"4️⃣ **Pomodoro timer** - To'liq fokus\n"
        f"5️⃣ **Nazorat** - Har 15 daqiqada\n"
        f"6️⃣ **Tanaffus** - 10 daqiqa dam olish\n"
        f"7️⃣ **Keyingi vazifa** - Avtomatik davom\n\n"
        f"⏰ **SIZ FAQAT:**\n"
        f"• Vazifa vaqtida rasm yuboring\n"
        f"• Fokusda ishlang\n\n"
        f"🤖 Qolganini men qilaman!\n\n"
        f"📅 Jadvalingizni ko'rish: '📅 Jadval' tugmasi",
        parse_mode="Markdown"
    )
    
    await callback.message.answer(
        "Omad! 💪",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer("Jadval saqlandi!")

@router.callback_query(F.data == "regenerate_schedule")
async def regenerate_schedule_handler(callback: CallbackQuery):
    """Jadvalni qayta tuzish"""
    await callback.message.edit_text("🔄 Jadval qayta tuzilmoqda...")
    await callback.answer()
    
    # Qayta generate qilish
    await generate_ai_schedule(callback.message)

@router.callback_query(F.data == "cancel_schedule")
async def cancel_schedule_handler(callback: CallbackQuery):
    """Jadvalni bekor qilish"""
    user_id = callback.from_user.id
    if user_id in user_schedules:
        del user_schedules[user_id]
    
    await callback.message.edit_text(
        "❌ Jadval bekor qilindi.\n\n"
        "Qaytadan tuzish uchun '🤖 AI Jadval' tugmasini bosing."
    )
    await callback.answer()

@router.message(F.text == "📅 Jadval")
async def show_schedule(message: Message):
    """Jadvalni ko'rsatish"""
    today = datetime.now().weekday()
    await show_day_schedule(message, today)

async def show_day_schedule(message: Message, day: int):
    """Kun bo'yicha jadval"""
    user_id = message.from_user.id
    schedule = await get_schedule(user_id, day)
    
    day_names = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", 
                 "Juma", "Shanba", "Yakshanba"]
    
    if not schedule:
        text = f"📅 **{day_names[day]}**\n\n❌ Bu kun uchun jadval yo'q."
    else:
        text = f"📅 **{day_names[day]}**\n\n"
        for item in schedule:
            emoji = "📚" if item['category'] == "SAT" else \
                    "🐍" if item['category'] == "Python" else \
                    "📖" if item['category'] == "Kitob" else "📌"
            
            text += f"{emoji} **{item['start_time']} - {item['end_time']}**\n"
            text += f"   {item['task_name']}\n\n"
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=day_navigation_keyboard(day)
    )

@router.callback_query(F.data.startswith("day_"))
async def navigate_day(callback: CallbackQuery):
    """Kunlar orasida navigatsiya"""
    day = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    schedule = await get_schedule(user_id, day)
    
    day_names = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", 
                 "Juma", "Shanba", "Yakshanba"]
    
    if not schedule:
        text = f"📅 **{day_names[day]}**\n\n❌ Bu kun uchun jadval yo'q."
    else:
        text = f"📅 **{day_names[day]}**\n\n"
        for item in schedule:
            emoji = "📚" if item['category'] == "SAT" else \
                    "🐍" if item['category'] == "Python" else \
                    "📖" if item['category'] == "Kitob" else "📌"
            
            text += f"{emoji} **{item['start_time']} - {item['end_time']}**\n"
            text += f"   {item['task_name']}\n\n"
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=day_navigation_keyboard(day)
    )
    await callback.answer()

@router.message(F.text.startswith("/schedule"))
async def cmd_schedule(message: Message):
    """Bugungi jadval"""
    await show_schedule(message)
