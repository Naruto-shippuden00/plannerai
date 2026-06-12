"""
APScheduler - avtomatik eslatmalar
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from aiogram import Bot
import logging

from utils.database import get_schedule

async def get_all_users():
    """Scheduler uchun import"""
    from utils.database import get_all_users as db_get_all_users
    return await db_get_all_users()
from utils.keyboards import task_action_keyboard

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_and_send_reminders(bot: Bot):
    """
    Har 15 daqiqada bir marta barcha foydalanuvchilarning 
    jadvalini tekshirish va eslatma yuborish
    """
    try:
        from utils.database import get_all_users, get_user_schedule_for_today
        
        current_time = datetime.now()
        current_day = current_time.weekday()  # 0=Monday, 6=Sunday
        current_hour_minute = current_time.strftime("%H:%M")
        
        logger.info(f"Checking reminders for {current_hour_minute}, day={current_day}")
        
        # Barcha foydalanuvchilarni olish
        users = await get_all_users()
        
        for user in users:
            user_id = user['user_id']
            
            # Foydalanuvchining bugungi jadvalini olish
            schedule = await get_user_schedule_for_today(user_id, current_day)
            
            for item in schedule:
                start_time = item['start_time']
                task_name = item['task_name']
                task_id = item['task_id']
                
                # Vaqt tekshiruvi (15 daqiqalik oyna ichida)
                # Masalan: jadvalda 17:00 bo'lsa, 16:55-17:10 oralig'ida eslatma yuboriladi
                item_time = datetime.strptime(start_time, "%H:%M").time()
                current = current_time.time()
                
                # 5 daqiqa oldin eslatma
                reminder_time = (datetime.combine(datetime.today(), item_time) - timedelta(minutes=5)).time()
                
                # Agar hozir eslatma vaqti bo'lsa
                if reminder_time.hour == current.hour and abs(reminder_time.minute - current.minute) < 3:
                    await send_task_reminder(bot, user_id, task_id, task_name, start_time)
        
    except Exception as e:
        logger.error(f"Reminder check error: {e}", exc_info=True)

async def send_task_reminder(bot: Bot, user_id: int, task_id: int, task_name: str, start_time: str):
    """
    Vazifa eslatmasini yuborish
    """
    try:
        message = (
            f"⏰ **VAZIFA VAQTI!**\n\n"
            f"🎯 **{task_name}**\n"
            f"🕐 Boshlanish: {start_time}\n\n"
            f"🎧 Telefonni silent modega qo'ying\n"
            f"🔕 Notificationlarni o'chiring\n"
            f"💪 Fokusda qoling!\n\n"
            f"Vazifani bajargach, rasm va izoh yuboring! 📸"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=task_action_keyboard(task_id)
        )
        
        logger.info(f"Reminder sent to user {user_id} for task {task_id}")
        
        # Focus keeper'ni 10 daqiqaga rejalashtiramiz
        from apscheduler.triggers.date import DateTrigger
        run_time = datetime.now() + timedelta(minutes=10)
        
        scheduler.add_job(
            send_focus_keeper,
            trigger=DateTrigger(run_date=run_time),
            args=[bot, user_id, task_name],
            id=f"focus_{user_id}_{task_id}_{int(datetime.now().timestamp())}",
            replace_existing=False
        )
        
        # Vazifa tugashi vaqtini hisoblash va completion reminder qo'shish
        # Misol: 17:00-19:00 bo'lsa, 19:00 da rasm so'raymiz
        try:
            # start_time formatida: "HH:MM" yoki "HH:MM-HH:MM"
            if '-' in start_time:
                end_time_str = start_time.split('-')[1]
                end_hour, end_min = map(int, end_time_str.split(':'))
                
                today = datetime.now()
                end_datetime = today.replace(hour=end_hour, minute=end_min, second=0)
                
                # Agar vaqt o'tib ketgan bo'lsa, ertaga qo'shamiz
                if end_datetime < datetime.now():
                    end_datetime += timedelta(days=1)
                
                # Vazifa tugaganda rasm so'rash
                scheduler.add_job(
                    ask_for_completion,
                    trigger=DateTrigger(run_date=end_datetime),
                    args=[bot, user_id, task_id, task_name],
                    id=f"completion_{user_id}_{task_id}_{int(datetime.now().timestamp())}",
                    replace_existing=False
                )
                
                logger.info(f"Completion reminder scheduled for {end_datetime}")
        except Exception as e:
            logger.error(f"Error scheduling completion reminder: {e}")
        
    except Exception as e:
        logger.error(f"Error sending reminder to {user_id}: {e}")

async def send_focus_keeper(bot: Bot, user_id: int, task_name: str):
    """
    Focus keeper - vazifa davomida fokusda qolishga yordam beradi
    """
    try:
        messages = [
            f"💪 **FOCUS KEEPER**\n\n🎯 **{task_name}** davom etmoqdami?\n\nChalg'itmang, maqsadga intiling! 🔥",
            f"🔥 **Ajoyib!**\n\n🎯 **{task_name}** ga fokus qiling!\n\nHar bir daqiqa muhim! ⏰",
            f"⚡️ **Davom eting!**\n\n🎯 **{task_name}**\n\nSiz zo'rsiz! Oxirigacha boring! 💯",
            f"🎯 **Fokusda qoling!**\n\n📚 **{task_name}**\n\nSiz buni qila olasiz! 💪"
        ]
        
        import random
        message = random.choice(messages)
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"Focus keeper sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error sending focus keeper to {user_id}: {e}")

async def ask_for_completion(bot: Bot, user_id: int, task_id: int, task_name: str):
    """
    Vazifa tugaganda rasm va completion so'rash
    """
    try:
        message = (
            f"✅ **VAZIFA TUGADI!**\n\n"
            f"🎯 **{task_name}**\n\n"
            f"Ajoyib! Vazifani bajardingizmi?\n\n"
            f"📸 Iltimos natija rasmini yuboring!\n"
            f"📝 Va qisqa izoh bering.\n\n"
            f"Bu sizning progressingizni tasdiqlaydi! 💪"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown",
            reply_markup=task_action_keyboard(task_id)
        )
        
        logger.info(f"Completion request sent to user {user_id} for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error asking for completion from {user_id}: {e}")

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
    # Har 5 daqiqada eslatmalarni tekshirish (tezroq ishlashi uchun)
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(minute="*/5"),  # 5 daqiqada bir
        args=[bot],
        id="check_reminders",
        replace_existing=True
    )
    
    # Ertalabki motivatsiya (har kuni 07:00)
    async def send_morning_to_all(bot):
        users = await get_all_users()
        for user in users:
            try:
                await send_motivational_message(bot, user['user_id'])
            except Exception as e:
                logger.error(f"Error sending morning message to {user['user_id']}: {e}")
    
    # Hozircha commented - agar kerak bo'lsa uncomment qiling
    # scheduler.add_job(
    #     send_morning_to_all,
    #     trigger=CronTrigger(hour=7, minute=0),
    #     args=[bot],
    #     id="morning_motivation",
    #     replace_existing=True
    # )
    
    # Shanba kuni test eslatmasi (14:00)
    async def send_test_to_all(bot):
        users = await get_all_users()
        for user in users:
            try:
                await send_weekly_test_reminder(bot, user['user_id'])
            except Exception as e:
                logger.error(f"Error sending test reminder to {user['user_id']}: {e}")
    
    scheduler.add_job(
        send_test_to_all,
        trigger=CronTrigger(day_of_week='sat', hour=14, minute=0),
        args=[bot],
        id="weekly_test_reminder",
        replace_existing=True
    )
    
    # Yakshanba kuni haftalik hisobot (18:00)
    async def send_report_to_all(bot):
        users = await get_all_users()
        for user in users:
            try:
                await send_weekly_report(bot, user['user_id'])
            except Exception as e:
                logger.error(f"Error sending weekly report to {user['user_id']}: {e}")
    
    scheduler.add_job(
        send_report_to_all,
        trigger=CronTrigger(day_of_week='sun', hour=18, minute=0),
        args=[bot],
        id="weekly_report",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started successfully!")

def stop_scheduler():
    """Schedulerni to'xtatish"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
