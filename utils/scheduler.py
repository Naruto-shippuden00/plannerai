"""
APScheduler - avtomatik eslatmalar
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram import Bot
import logging

from utils.database import get_schedule

# Tashkent vaqt zonasi
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

async def get_all_users():
    """Scheduler uchun import"""
    from utils.database import get_all_users as db_get_all_users
    return await db_get_all_users()

from utils.keyboards import task_action_keyboard
from handlers.focus_keeper import start_continuous_notifications
from handlers.punishments import auto_apply_punishment

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_and_send_reminders(bot: Bot):
    """
    Har 1 daqiqada barcha foydalanuvchilarning 
    jadvalini tekshirish va eslatma yuborish
    """
    try:
        from utils.database import get_all_users, get_user_schedule_for_today, get_task_by_id
        
        # TASHKENT VAQTI bilan ishlash
        current_time = datetime.now(TASHKENT_TZ)
        current_day = current_time.weekday()  # 0=Monday, 6=Sunday
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Hafta kunlari nomlari debug uchun
        day_names = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        logger.info(f"⏰ Checking reminders at {current_hour:02d}:{current_minute:02d}, day={current_day} ({day_names[current_day]})")
        
        # Barcha foydalanuvchilarni olish
        users = await get_all_users()
        logger.info(f"👥 Total users: {len(users)}")
        
        for user in users:
            user_id = user['user_id']
            
            # Foydalanuvchining bugungi jadvalini olish
            schedule = await get_user_schedule_for_today(user_id, current_day)
            
            if schedule:
                logger.info(f"👤 User {user_id}: {len(schedule)} tasks scheduled for {day_names[current_day]}")
            
            for item in schedule:
                start_time = item['start_time']
                end_time = item.get('end_time', 'N/A')
                task_name = item.get('task_name', 'Unknown')
                task_id = item.get('task_id')
                
                if not task_id:
                    logger.warning(f"⚠️ Schedule item without task_id: {item}")
                    continue
                
                # Vazifa aktiv ekanligini tekshirish
                task = await get_task_by_id(task_id)
                if not task or task.get('active') != 1:
                    logger.info(f"⏭️ Task {task_id} is not active, skipping")
                    continue
                
                # Vaqtni parse qilish
                try:
                    # start_time faqat boshlanish vaqti (masalan "17:00")
                    item_time_str = start_time.strip()
                    item_hour, item_minute = map(int, item_time_str.split(':'))
                    
                    # ANIQ VAQT TEKSHIRUVI - ± 0 daqiqa
                    if item_hour == current_hour and item_minute == current_minute:
                        logger.info(f"🔔 MATCH! Sending reminder to user {user_id} for task '{task_name}' at {item_time_str}")
                        # start_time va end_time ni birlashtirgan holda yuboramiz
                        time_range = f"{start_time}-{end_time}" if end_time != 'N/A' else start_time
                        await send_task_reminder(bot, user_id, task_id, task_name, time_range)
                    
                except Exception as e:
                    logger.error(f"Error parsing time '{start_time}' for task {task_id}: {e}")
                    continue
        
    except Exception as e:
        logger.error(f"Reminder check error: {e}", exc_info=True)

async def send_task_reminder(bot: Bot, user_id: int, task_id: int, task_name: str, start_time: str):
    """
    Vazifa eslatmasini yuborish va focus sessionni boshlash
    """
    try:
        from utils.database import create_focus_session, get_task_by_id
        from handlers.focus_keeper import FocusState
        
        # Task ma'lumotlarini olish
        task = await get_task_by_id(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        # Task aktiv ekanligini qayta tekshirish
        if task.get('active') != 1:
            logger.info(f"Task {task_id} is not active, skipping reminder")
            return
        
        # Start_time formatidan end_time ni olish
        end_time = "N/A"
        duration_minutes = task.get('duration_minutes', 60)
        
        if '-' in start_time:
            time_parts = start_time.split('-')
            start_time_only = time_parts[0].strip()
            end_time = time_parts[1].strip()
            
            # Duration'ni hisoblash
            try:
                start_h, start_m = map(int, start_time_only.split(':'))
                end_h, end_m = map(int, end_time.split(':'))
                duration_minutes = (end_h * 60 + end_m) - (start_h * 60 + start_m)
            except:
                pass
        else:
            start_time_only = start_time
            # Vazifa davomiyligidan end_time ni hisoblash
            try:
                start_h, start_m = map(int, start_time_only.split(':'))
                end_minutes = start_h * 60 + start_m + duration_minutes
                end_h = (end_minutes // 60) % 24
                end_m = end_minutes % 60
                end_time = f"{end_h:02d}:{end_m:02d}"
            except:
                end_time = "N/A"
        
        # Focus session yaratish
        session_id = await create_focus_session(
            user_id=user_id,
            task_id=task_id,
            schedule_id=0,
            planned_duration=duration_minutes
        )
        
        # FSM state o'rnatish
        try:
            # Bot modulidan dispatcher ni import qilish
            import sys
            if 'bot' in sys.modules:
                bot_module = sys.modules['bot']
                if hasattr(bot_module, 'dp'):
                    from aiogram.fsm.context import FSMContext
                    from aiogram.fsm.storage.base import StorageKey
                    
                    storage_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
                    state = FSMContext(storage=bot_module.dp.storage, key=storage_key)
                    await state.set_state(FocusState.waiting_for_photo)
                    await state.update_data(session_id=session_id, task_id=task_id, task_name=task_name)
                    logger.info(f"FSM state set for user {user_id}, session {session_id}")
                else:
                    logger.warning("Dispatcher not found in bot module")
            else:
                logger.warning("Bot module not loaded yet")
        except Exception as e:
            logger.error(f"Error setting FSM state: {e}")
        
        message = (
            f"⏰ **VAZIFA VAQTI KELDI!**\n\n"
            f"🎯 **{task_name}**\n"
            f"📂 Kategoriya: {task.get('category', 'N/A')}\n"
            f"🕐 Boshlanish: {start_time_only}\n"
            f"⏰ Tugash: {end_time}\n"
            f"⏱ Davomiyligi: {duration_minutes} daqiqa\n\n"
            f"🔔 **CHEKSIZ BILDIRISHNOMALAR BOSHLANDI!**\n\n"
            f"❗️ HAR 5 DAQIQADA ESLATMA YUBORILADI!\n\n"
            f"🛑 **TO'XTATISH UCHUN:**\n"
            f"📸 Vazifani bajarayotganingizni tasdiqlovchi RASM yuboring!\n\n"
            f"**Rasm misollari:**\n"
            f"• Dars jarayoni (SAT, IELTS)\n"
            f"• Kod yozayotgan ekran (Python)\n"
            f"• Mashq daftari (Study)\n"
            f"• O'qiyotgan kitob sahifasi\n"
            f"• Gym mashqi jarayoni\n\n"
            f"⚠️ Rasm yubormasangiz, bildirishnomalar DAVOM ETADI!\n\n"
            f"💪 Fokusga kiring va muvaffaqiyatga erishing!"
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="Markdown"
        )
        
        logger.info(f"✅ Task reminder sent to user {user_id} for task {task_id}, session {session_id}")
        
        # CHEKSIZ BILDIRISHNOMALARNI BOSHLASH
        await start_continuous_notifications(
            bot=bot,
            user_id=user_id,
            session_id=session_id,
            task_name=task_name,
            start_time=start_time_only,
            end_time=end_time
        )
        
        # Vazifa tugashi vaqtini hisoblash va completion reminder qo'shish
        try:
            if end_time != "N/A":
                end_hour, end_min = map(int, end_time.split(':'))
                
                # TASHKENT VAQTI bilan ishlash
                today = datetime.now(TASHKENT_TZ)
                end_datetime = today.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
                
                # Agar vaqt o'tib ketgan bo'lsa, ertaga qo'shamiz
                if end_datetime < datetime.now(TASHKENT_TZ):
                    end_datetime += timedelta(days=1)
                
                # Vazifa tugaganda rasm so'rash va jazo berish
                scheduler.add_job(
                    check_task_completion,
                    trigger=DateTrigger(run_date=end_datetime),
                    args=[bot, user_id, task_id, session_id, task_name],
                    id=f"completion_{user_id}_{task_id}_{int(datetime.now(TASHKENT_TZ).timestamp())}",
                    replace_existing=False
                )
                
                logger.info(f"📅 Completion check scheduled for {end_datetime}")
        except Exception as e:
            logger.error(f"Error scheduling completion reminder: {e}")
        
    except Exception as e:
        logger.error(f"❌ Error sending reminder to {user_id}: {e}", exc_info=True)

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
    # Har 1 daqiqada eslatmalarni tekshirish (aniq vaqtni ushlab olish uchun)
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(minute="*"),  # Har bir daqiqada
        args=[bot],
        id="check_reminders",
        replace_existing=True
    )
    
    logger.info("✅ Reminder checker started - running every 1 minute")
    
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
    logger.info("🚀 Scheduler started successfully!")

def stop_scheduler():
    """Schedulerni to'xtatish"""
    scheduler.shutdown()
    logger.info("Scheduler stopped")



async def check_task_completion(bot: Bot, user_id: int, task_id: int, session_id: int, task_name: str):
    """
    Vazifa tugaganda tekshirish - agar rasm yuborilmagan bo'lsa jazo berish
    """
    try:
        from utils.database import get_active_focus_session, get_focus_session_photos
        from handlers.focus_keeper import stop_continuous_notifications
        
        # Session holatini tekshirish
        active_session = await get_active_focus_session(user_id)
        
        # Bildirishnomalarni to'xtatish (agar hali to'xtatilmagan bo'lsa)
        await stop_continuous_notifications(user_id)
        
        if active_session and active_session['id'] == session_id:
            # Rasmlar tekshiruvi
            photos = await get_focus_session_photos(session_id)
            
            if len(photos) == 0:
                # RASM YO'Q - JAZO!
                await auto_apply_punishment(
                    bot=bot,
                    user_id=user_id,
                    task_id=task_id,
                    punishment_type="no_photo",
                    reason=f"Vazifa '{task_name}' uchun hech qanday rasm yuborilmadi"
                )
                
                await bot.send_message(
                    user_id,
                    f"❌ **VAZIFA BAJARILMADI!**\n\n"
                    f"🎯 Vazifa: {task_name}\n\n"
                    f"⚠️ Siz hech qanday rasm yubormagansiz!\n\n"
                    f"🔴 **JAZO BERILDI!**\n\n"
                    f"Bu vazifani qayta bajarishingiz kerak.\n\n"
                    f"Jazolaringizni ko'rish: '⚠️ Jazolarim' tugmasi",
                    parse_mode="Markdown"
                )
            else:
                # RASM BOR - AJOYIB!
                from utils.database import end_focus_session
                await end_focus_session(session_id, completed=True)
                
                await bot.send_message(
                    user_id,
                    f"✅ **VAZIFA TUGADI!**\n\n"
                    f"🎯 {task_name}\n\n"
                    f"🎉 Ajoyib ish qildingiz!\n"
                    f"📸 Rasmlar yuborildi: {len(photos)} ta\n\n"
                    f"💪 Davom eting! Siz zo'rsiz!",
                    parse_mode="Markdown"
                )
        
        logger.info(f"Task completion checked for user {user_id}, task {task_id}")
        
    except Exception as e:
        logger.error(f"Error checking task completion for {user_id}: {e}")
