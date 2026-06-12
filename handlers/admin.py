"""
Admin panel - Faqat admin foydalana oladi
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta
import os
import asyncio

from utils.database import (
    get_all_users,
    get_user_stats,
    get_system_stats
)
from utils.keyboards import main_menu_keyboard

router = Router()

def is_admin(user_id: int) -> bool:
    """Admin tekshirish"""
    admin_id = os.getenv('ADMIN_USER_ID')
    if not admin_id:
        return False
    # String'ni integer'ga o'tkazamiz va taqqoslaymiz
    try:
        return int(user_id) == int(admin_id.strip())
    except (ValueError, AttributeError):
        return False

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat admin uchun!")
        return
    
    admin_id = message.from_user.id
    
    text = f"""👨‍💼 **ADMIN PANEL**

Quyidagi komandalar mavjud:

📊 /stats_all - Tizim statistikasi
👥 /users - Barcha foydalanuvchilar
🔍 /check - Bot holatini tekshirish
🧪 /test_reminder - Test bildirishnoma yuborish

📌 Sizning admin ID: `{admin_id}`
"""
    
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("stats_all"))
async def system_stats(message: Message):
    """Tizim statistikasi"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat admin uchun!")
        return
    
    await message.answer("📊 Statistika yuklanmoqda...")
    
    stats = await get_system_stats()
    
    text = f"""
📊 **TIZIM STATISTIKASI**

👥 **Foydalanuvchilar:**
━━━━━━━━━━━━━━━━━━━━
Jami: {stats['total_users']} ta

📋 **Vazifalar:**
━━━━━━━━━━━━━━━━━━━━
Jami vazifalar: {stats['total_tasks']} ta
Bajarilgan: {stats['total_completions']} ta

🔥 **Eng mashhur:**
━━━━━━━━━━━━━━━━━━━━
Kategoriya: {stats['top_category']['category']}
Vazifalar: {stats['top_category']['count']} ta

📅 **Vaqt:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("users"))
async def list_users(message: Message):
    """Barcha foydalanuvchilar ro'yxati"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat admin uchun!")
        return
    
    await message.answer("👥 Foydalanuvchilar yuklanmoqda...")
    
    users = await get_all_users()
    
    if not users:
        await message.answer("👥 Hali foydalanuvchilar yo'q.")
        return
    
    text = f"👥 **FOYDALANUVCHILAR** ({len(users)} ta)\n\n"
    
    for i, user in enumerate(users, 1):
        username = f"@{user['username']}" if user['username'] else "Username yo'q"
        created = user['created_at'][:10] if user['created_at'] else "N/A"
        
        # User statistikasi
        user_stat = await get_user_stats(user['user_id'])
        
        text += f"{i}. **{user['full_name']}**\n"
        text += f"   ID: `{user['user_id']}`\n"
        text += f"   Username: {username}\n"
        text += f"   Ro'yxat: {created}\n"
        text += f"   Vazifalar: {user_stat['total_tasks']} ta\n"
        text += f"   Bajarildi: {user_stat['completed']} ta\n\n"
    
    # Telegram 4096 belgi limitini hisobga olamiz
    if len(text) > 4000:
        chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for chunk in chunks:
            await message.answer(chunk, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

@router.message(Command("check"))
async def check_bot_status(message: Message):
    """Bot holatini tekshirish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat admin uchun!")
        return
    
    from utils.scheduler import scheduler
    from handlers.focus_keeper import active_notifications
    
    bot_token = os.getenv('BOT_TOKEN')
    groq_key = os.getenv('GROQ_API_KEY')
    admin_id = os.getenv('ADMIN_USER_ID')
    
    # Bot ma'lumotlarini olish
    bot_info = await message.bot.get_me()
    bot_status_token = '✅ Mavjud' if bot_token else '❌ Yoq'
    bot_status_groq = '✅ Mavjud' if groq_key else '❌ Yoq'
    bot_status_admin = f'✅ {admin_id}' if admin_id else '❌ Yoq'
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Scheduler info
    jobs = scheduler.get_jobs()
    scheduler_status = '✅ Aktiv' if scheduler.running else '❌ Toxtagan'
    
    text = f"""
🔍 **BOT HOLATI**

🤖 **Bot:**
━━━━━━━━━━━━━━━━━━━━
Status: ✅ Ishlayapti
Bot ID: `{message.bot.id}`
Username: @{bot_info.username}

🔑 **Konfiguratsiya:**
━━━━━━━━━━━━━━━━━━━━
BOT_TOKEN: {bot_status_token}
GROQ_API_KEY: {bot_status_groq}
ADMIN_USER_ID: {bot_status_admin}

⏰ **Scheduler:**
━━━━━━━━━━━━━━━━━━━━
Status: {scheduler_status}
Jobs: {len(jobs)} ta
Aktiv bildirishnomalar: {len(active_notifications)} ta

📅 **Vaqt:** {current_time}
🌍 **Platform:** Railway.app
"""
    
    if active_notifications:
        text += "\n\n🔔 **Aktiv bildirishnomalar:**\n"
        for user_id, data in active_notifications.items():
            text += f"• User {user_id}: Session {data['session_id']}\n"
    
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("test_reminder"))
async def test_reminder_command(message: Message):
    """TEST - Hozir bildirishnoma yuborish"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Bu komanda faqat admin uchun!")
        return
    
    from utils.scheduler import send_task_reminder
    from utils.database import get_user_tasks
    
    user_id = message.from_user.id
    
    # Foydalanuvchining birinchi vazifasini olish
    tasks = await get_user_tasks(user_id)
    
    if not tasks:
        await message.answer("❌ Sizda vazifalar yo'q! Avval vazifa qo'shing.")
        return
    
    task = tasks[0]
    
    await message.answer(
        f"🧪 **TEST REJIMI**\n\n"
        f"Hozir sizga test bildirishnoma yuboriladi:\n\n"
        f"🎯 Vazifa: {task['task_name']}\n"
        f"📂 Kategoriya: {task['category']}\n\n"
        f"⏱ 3 soniyadan keyin...",
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(3)
    
    # Test reminder yuborish
    bot = message.bot
    await send_task_reminder(
        bot=bot,
        user_id=user_id,
        task_id=task['id'],
        task_name=task['task_name'],
        start_time=f"{datetime.now().strftime('%H:%M')}-{(datetime.now() + timedelta(hours=1)).strftime('%H:%M')}"
    )
    
    await message.answer(
        "✅ Test bildirishnoma yuborildi!\n\n"
        "Endi rasm yuboring va tizim qanday ishlashini ko'ring! 📸",
        parse_mode="Markdown"
    )

