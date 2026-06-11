"""
APScheduler - avtomatik eslatmalar
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from aiogram import Bot
import logging

from utils.database import get_schedule
from utils.keyboards import task_action_keyboard

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_and_send_reminders(bot: Bot):
    """
    Har 15 daqiqada bir marta barcha foydalanuvchilarning 
    jadvalini tekshirish va eslatma yuborish
    """
    try:
        current_time = datetime.now()
        current_day = current_time.weekday()
        current_hour_minute = current_time.strftime("%H:%M")
        
        # TODO: Barcha aktiv foydalanuvchilarni olish
        # Hozircha database'dan foydalanuvchilar ro'yxatini olish kerak
        
        logger.info(f"Checking reminders for {current_hour_minute}")
        
    except Exception as e:
        logger.error(f"Reminder check error: {e}")

async def send_task_reminder(bot: Bot, user_id: int, task_id: int, task_name: str, start_time: str):
    """
    Vazifa eslatmasini yuborish
    """
    try:
        message = (
            f"⏰ **Vazifa vaqti!**\n\n"
            f"🎯 {task_name}\n"
            f"🕐 Boshlanish: {start_time}\n\n"
            f"Vazifani bajaring va natijani yuboring! 💪"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=task_action_keyboard(task_id)
        )
        
        logger.info(f"Reminder sent to user {user_id} for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error sending reminder to {user_id}: {e}")

async def send_motivational_message(bot: Bot, user_id: int):
    """
    Kunlik motivatsiya xabari
    """
    try:
        messages = [
            "☀️ Xayrli tong! Bugun ajoyib kun bo'ladi! 🌟",
            "💪 Har bir kichik qadam katta muvaffaqiyatga olib boradi!",
            "🎯 Bugungi vazifalaringizni bajaring, ertaga o'zingizga rahmat aytasiz!",
            "🔥 Siz qila olasiz! Men sizga ishonaman!",
            "✨ Har bir yangi kun - yangi imkoniyat!"
        ]
        
        import random
        message = random.choice(messages)
        
        await bot.send_message(
            chat_id=user_id,
            text=message
        )
        
        logger.info(f"Motivational message sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending motivation to {user_id}: {e}")

async def send_weekly_test_reminder(bot: Bot, user_id: int):
    """
    Haftalik test eslatmasi (Shanba)
    """
    try:
        message = (
            "📚 **Haftalik test vaqti!**\n\n"
            "Siz bu hafta nima o'rgandingiz?\n"
            "Bilimlaringizni sinab ko'ring! 🎓\n\n"
            "/test buyrug'ini kiriting yoki "
            "'📊 Statistika' tugmasidan testni boshlang."
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"Weekly test reminder sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending test reminder to {user_id}: {e}")

async def send_weekly_report(bot: Bot, user_id: int):
    """
    Haftalik hisobot (Yakshanba)
    """
    try:
        from utils.database import get_weekly_stats
        from utils.ai_helper import analyze_weekly_progress
        
        # Statistikani olish
        stats = await get_weekly_stats(user_id)
        
        # AI tahlili
        analysis = await analyze_weekly_progress(stats, [])
        
        message = (
            "📊 **HAFTALIK HISOBOT**\n\n"
            f"{analysis}\n\n"
            "Keyingi haftaga tayyormisiz? 💪"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"Weekly report sent to {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending weekly report to {user_id}: {e}")

def init_scheduler(bot: Bot):
    """
    Schedulerni ishga tushirish
    """
    # Har 15 daqiqada eslatmalarni tekshirish
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(minute="*/15"),
        args=[bot],
        id="check_reminders",
        replace_existing=True
    )
    
    # Ertalabki motivatsiya (har kuni 07:00)
    # TODO: Barcha userlar ro'yxatini olish va har biriga yuborish
    # Hozircha o'chirilgan
    # scheduler.add_job(
    #     send_motivational_message,
    #     trigger=CronTrigger(hour=7, minute=0),
    #     args=[bot],
    #     id="morning_motivation",
    #     replace_existing=True
    # )
    
    # Shanba kuni test eslatmasi (14:00)
    # TODO: Barcha userlar ro'yxatini olish
    # Hozircha o'chirilgan
    # scheduler.add_job(
    #     send_weekly_test_reminder,
    #     trigger=CronTrigger(day_of_week='sat', hour=14, minute=0),
    #     args=[bot],
    #     id="weekly_test_reminder",
    #     replace_existing=True
    # )
    
    # Yakshanba kuni haftalik hisobot (18:00)
    # TODO: Barcha userlar ro'yxatini olish
    # Hozircha o'chirilgan
    # scheduler.add_job(
    #     send_weekly_report,
    #     trigger=CronTrigger(day_of_week='sun', hour=18, minute=0),
    #     args=[bot],
    #     id="weekly_report",
    #     replace_existing=True
    # )
    
    scheduler.start()
    logger.info("Scheduler started successfully!")

def stop_scheduler():
    """Schedulerni to'xtatish"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
