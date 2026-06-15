"""
APScheduler - avtomatik eslatmalar (OPTIMIZED)
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from aiogram import Bot
import logging
import asyncio

from utils.database import get_schedule

# Tashkent vaqt zonasi
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

async def get_all_users():
    """Scheduler uchun import"""
    from utils.database import get_all_users as db_get_all_users
    return await db_get_all_users()

from utils.keyboards import task_action_keyboard, focus_reminder_keyboard
from handlers.focus_keeper import start_continuous_notifications
from handlers.punishments import auto_apply_punishment

logger = logging.getLogger(__name__)

# Scheduler konfiguratsiyasi
scheduler = AsyncIOScheduler(
    timezone=TASHKENT_TZ,
    job_defaults={
        'coalesce': True,  # Bir xil joblarni birlashtirish
        'max_instances': 3,  # Maksimal parallel instances
        'misfire_grace_time': 60  # 60 sekund grace time
    }
)

async def check_and_send_reminders(bot: Bot):
    """
    Har 1 daqiqada barcha foydalanuvchilarning 
    jadvalini tekshirish va eslatma yuborish
    
    OPTIMIZED VERSION - Tashkent vaqti bilan to'g'ri ishlaydi
    """
    try:
        from utils.database import get_all_users, get_user_schedule_for_today
        
        # TASHKENT VAQTI bilan ishlash (timezone-aware)
        current_time = datetime.now(TASHKENT_TZ)
        current_day = current_time.weekday()  # 0=Monday, 6=Sunday
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Hafta kunlari nomlari debug uchun
        day_names = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
        
        logger.info(
            f"⏰ Reminder Check: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')} | "
            f"Day: {current_day} ({day_names[current_day]}) | "
            f"Time: {current_hour:02d}:{current_minute:02d}"
        )
        
        # Barcha foydalanuvchilarni olish
        users = await get_all_users()
        if not users:
            logger.info("👥 No users found")
            return
        
        logger.info(f"👥 Checking {len(users)} users")
        
        reminders_sent = 0
        
        for user in users:
            try:
                user_id = user['user_id']
                
                # Foydalanuvchining bugungi jadvalini olish
                schedule = await get_user_schedule_for_today(user_id, current_day)
                
                if not schedule:
                    continue
                
                logger.debug(f"👤 User {user_id}: {len(schedule)} tasks for {day_names[current_day]}")
                
                for item in schedule:
                    start_time = item.get('start_time', '')
                    end_time = item.get('end_time', 'N/A')
                    task_name = item.get('task_name', 'Unknown')
                    task_id = item.get('task_id')
                    schedule_id = item.get('id')
                    
                    if not task_id or not start_time:
                        logger.warning(f"⚠️ Invalid schedule item: {item}")
                        continue
                    
                    # Vaqtni parse qilish
                    try:
                        # start_time faqat boshlanish vaqti (masalan "17:00")
                        time_parts = start_time.strip().split(':')
                        if len(time_parts) != 2:
                            logger.error(f"Invalid time format: {start_time}")
                            continue
                        
                        item_hour = int(time_parts[0])
                        item_minute = int(time_parts[1])
                        
                        # ANIQ VAQT TEKSHIRUVI - 0 daqiqa tolerance
                        if item_hour == current_hour and item_minute == current_minute:
                            logger.info(
                                f"🔔 MATCH! User {user_id} | Task '{task_name}' | "
                                f"Scheduled: {start_time} | Current: {current_hour:02d}:{current_minute:02d}"
                            )
                            
                            # start_time va end_time ni birlashtirgan holda yuboramiz
                            time_range = f"{start_time}-{end_time}" if end_time != 'N/A' else start_time
                            
                            await send_task_reminder(
                                bot=bot,
                                user_id=user_id,
                                task_id=task_id,
                                task_name=task_name,
                                start_time=time_range,
                                schedule_id=schedule_id
                            )
                            
                            reminders_sent += 1
                        
                    except ValueError as e:
                        logger.error(f"Error parsing time '{start_time}': {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing schedule item: {e}", exc_info=True)
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing user {user.get('user_id', 'unknown')}: {e}", exc_info=True)
                continue
        
        if reminders_sent > 0:
            logger.info(f"✅ Sent {reminders_sent} reminders")
        
    except Exception as e:
        logger.error(f"❌ Critical error in reminder check: {e}", exc_info=True)

async def send_task_reminder(bot: Bot, user_id: int, task_id: int, task_name: str, start_time: str, schedule_id: int = 0):
    """
    Vazifa eslatmasini yuborish va focus sessionni boshlash
    
    OPTIMIZED VERSION - to'liq error handling va logging
    """
    try:
        from utils.database import create_focus_session, get_task_by_id
        from handlers.focus_keeper import FocusState
        
        logger.info(f"📤 Sending reminder: user={user_id}, task={task_id}, name='{task_name}'")
        
        # Task ma'lumotlarini olish
        task = await get_task_by_id(task_id)
        if not task:
            logger.error(f"❌ Task {task_id} not found in database")
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
                if duration_minutes < 0:
                    duration_minutes += 24 * 60  # Next day
            except Exception as e:
                logger.warning(f"Could not calculate duration: {e}")
        else:
            start_time_only = start_time
            # Vazifa davomiyligidan end_time ni hisoblash
            try:
                start_h, start_m = map(int, start_time_only.split(':'))
                end_minutes = start_h * 60 + start_m + duration_minutes
                end_h = (end_minutes // 60) % 24
                end_m = end_minutes % 60
                end_time = f"{end_h:02d}:{end_m:02d}"
            except Exception as e:
                logger.warning(f"Could not calculate end time: {e}")
                end_time = "N/A"
        
        # Focus session yaratish
        try:
            session_id = await create_focus_session(
                user_id=user_id,
                task_id=task_id,
                schedule_id=schedule_id,
                planned_duration=duration_minutes
            )
            logger.info(f"✅ Focus session created: session_id={session_id}")
        except Exception as e:
            logger.error(f"❌ Error creating focus session: {e}", exc_info=True)
            return
        
        # FSM state o'rnatish - OPTIMIZED va ISHONCHLI
        try:
            import sys
            dp = None
            
            # 1-usul: handlers modulidan topish (eng ishonchli)
            try:
                import handlers as handlers_module
                if hasattr(handlers_module, 'dp') and handlers_module.dp is not None:
                    dp = handlers_module.dp
                    logger.info("✅ Dispatcher found in handlers module")
            except Exception as e:
                logger.debug(f"Could not import from handlers: {e}")
            
            # 2-usul: bot modulidan topish
            if not dp and 'bot' in sys.modules:
                bot_module = sys.modules['bot']
                if hasattr(bot_module, 'dp') and bot_module.dp is not None:
                    dp = bot_module.dp
                    logger.info("✅ Dispatcher found in bot module")
            
            if dp:
                from aiogram.fsm.context import FSMContext
                from aiogram.fsm.storage.base import StorageKey
                
                storage_key = StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
                state = FSMContext(storage=dp.storage, key=storage_key)
                
                # State o'rnatish
                await state.set_state(FocusState.waiting_for_photo)
                await state.update_data(
                    session_id=session_id, 
                    task_id=task_id, 
                    task_name=task_name,
                    start_time=start_time_only,
                    end_time=end_time,
                    scheduler_triggered=True  # Bu scheduler tomonidan qo'shilganligini bildiradi
                )
                logger.info(f"✅ FSM state set successfully: user={user_id}, session={session_id}, state=FocusState.waiting_for_photo")
            else:
                logger.error("❌ CRITICAL: Dispatcher not found!")
                logger.error("❌ Photo handler will not work properly!")
                logger.error("❌ User will not be able to stop notifications by sending photo!")
        except Exception as e:
            logger.error(f"❌ Error setting FSM state: {e}", exc_info=True)
        
        # Xabar yuborish
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
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="Markdown",
                reply_markup=focus_reminder_keyboard(task_id, session_id)
            )
            logger.info(f"✅ Reminder message sent to user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error sending message to user {user_id}: {e}", exc_info=True)
            return
        
        # CHEKSIZ BILDIRISHNOMALARNI BOSHLASH
        try:
            await start_continuous_notifications(
                bot=bot,
                user_id=user_id,
                session_id=session_id,
                task_name=task_name,
                start_time=start_time_only,
                end_time=end_time
            )
            logger.info(f"✅ Continuous notifications started for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error starting notifications: {e}", exc_info=True)
        
        # Vazifa tugashi vaqtini hisoblash va completion reminder qo'shish
        try:
            if end_time != "N/A":
                end_hour, end_min = map(int, end_time.split(':'))
                
                # TASHKENT VAQTI bilan ishlash
                today = datetime.now(TASHKENT_TZ)
                end_datetime = today.replace(
                    hour=end_hour, 
                    minute=end_min, 
                    second=0, 
                    microsecond=0
                )
                
                # Agar vaqt o'tib ketgan bo'lsa, ertaga qo'shamiz
                if end_datetime <= datetime.now(TASHKENT_TZ):
                    end_datetime += timedelta(days=1)
                
                # Vazifa tugaganda rasm so'rash va jazo berish
                job_id = f"completion_{user_id}_{task_id}_{session_id}_{int(datetime.now(TASHKENT_TZ).timestamp())}"
                
                scheduler.add_job(
                    check_task_completion,
                    trigger=DateTrigger(run_date=end_datetime, timezone=TASHKENT_TZ),
                    args=[bot, user_id, task_id, session_id, task_name],
                    id=job_id,
                    replace_existing=False
                )
                
                logger.info(
                    f"📅 Completion check scheduled: "
                    f"time={end_datetime.strftime('%H:%M')} | job_id={job_id}"
                )
        except Exception as e:
            logger.error(f"❌ Error scheduling completion reminder: {e}", exc_info=True)
        
    except Exception as e:
        logger.error(f"❌ Critical error in send_task_reminder for user {user_id}: {e}", exc_info=True)

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
    
    OPTIMIZED VERSION - Tashkent timezone bilan to'g'ri ishlaydi
    """
    
    logger.info("🚀 Initializing scheduler with Tashkent timezone...")
    
    # Har 1 daqiqada eslatmalarni tekshirish (aniq vaqtni ushlab olish uchun)
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(
            minute="*",  # Har bir daqiqada
            timezone=TASHKENT_TZ
        ),
        args=[bot],
        id="check_reminders",
        replace_existing=True,
        name="Reminder Checker"
    )
    
    logger.info("✅ Reminder checker configured - runs every 1 minute (Tashkent time)")
    
    # Ertalabki motivatsiya (har kuni 07:00 Tashkent vaqti)
    async def send_morning_to_all(bot):
        try:
            users = await get_all_users()
            logger.info(f"📧 Sending morning motivation to {len(users)} users")
            sent = 0
            for user in users:
                try:
                    await send_motivational_message(bot, user['user_id'])
                    sent += 1
                except Exception as e:
                    logger.error(f"Error sending morning message to {user['user_id']}: {e}")
            logger.info(f"✅ Morning motivation sent to {sent} users")
        except Exception as e:
            logger.error(f"Error in morning motivation batch: {e}", exc_info=True)
    
    # Hozircha commented - agar kerak bo'lsa uncomment qiling
    scheduler.add_job(
        send_morning_to_all,
        trigger=CronTrigger(
            hour=7, 
            minute=0,
            timezone=TASHKENT_TZ
        ),
        args=[bot],
        id="morning_motivation",
        replace_existing=True,
        name="Morning Motivation"
    )
    
    logger.info("✅ Morning motivation configured - 07:00 daily (Tashkent time)")
    
    # Shanba kuni test eslatmasi (14:00 Tashkent vaqti)
    async def send_test_to_all(bot):
        try:
            users = await get_all_users()
            logger.info(f"📝 Sending test reminders to {len(users)} users")
            sent = 0
            for user in users:
                try:
                    await send_weekly_test_reminder(bot, user['user_id'])
                    sent += 1
                except Exception as e:
                    logger.error(f"Error sending test reminder to {user['user_id']}: {e}")
            logger.info(f"✅ Test reminders sent to {sent} users")
        except Exception as e:
            logger.error(f"Error in test reminder batch: {e}", exc_info=True)
    
    scheduler.add_job(
        send_test_to_all,
        trigger=CronTrigger(
            day_of_week='sat', 
            hour=14, 
            minute=0,
            timezone=TASHKENT_TZ
        ),
        args=[bot],
        id="weekly_test_reminder",
        replace_existing=True,
        name="Weekly Test Reminder"
    )
    
    logger.info("✅ Weekly test reminder configured - Saturday 14:00 (Tashkent time)")
    
    # Yakshanba kuni haftalik hisobot (18:00 Tashkent vaqti)
    async def send_report_to_all(bot):
        try:
            users = await get_all_users()
            logger.info(f"📊 Sending weekly reports to {len(users)} users")
            sent = 0
            for user in users:
                try:
                    await send_weekly_report(bot, user['user_id'])
                    sent += 1
                except Exception as e:
                    logger.error(f"Error sending weekly report to {user['user_id']}: {e}")
            logger.info(f"✅ Weekly reports sent to {sent} users")
        except Exception as e:
            logger.error(f"Error in weekly report batch: {e}", exc_info=True)
    
    scheduler.add_job(
        send_report_to_all,
        trigger=CronTrigger(
            day_of_week='sun', 
            hour=18, 
            minute=0,
            timezone=TASHKENT_TZ
        ),
        args=[bot],
        id="weekly_report",
        replace_existing=True,
        name="Weekly Report"
    )
    
    logger.info("✅ Weekly report configured - Sunday 18:00 (Tashkent time)")
    
    # Schedulerni ishga tushirish
    try:
        scheduler.start()
        logger.info("🎉 Scheduler started successfully!")
        logger.info(f"📍 Timezone: {TASHKENT_TZ}")
        logger.info(f"📅 Current time: {datetime.now(TASHKENT_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # Barcha joblarni log qilish
        jobs = scheduler.get_jobs()
        logger.info(f"📋 Total scheduled jobs: {len(jobs)}")
        for job in jobs:
            logger.info(f"   - {job.name} (ID: {job.id}) | Next run: {job.next_run_time}")
            
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}", exc_info=True)
        raise

def stop_scheduler():
    """Schedulerni to'xtatish"""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=False)
            logger.info("⏹ Scheduler stopped successfully")
        else:
            logger.info("⏹ Scheduler was not running")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}", exc_info=True)



async def check_task_completion(bot: Bot, user_id: int, task_id: int, session_id: int, task_name: str):
    """
    Vazifa tugaganda tekshirish - agar rasm yuborilmagan bo'lsa jazo berish
    
    OPTIMIZED VERSION - to'liq error handling
    """
    try:
        from utils.database import get_active_focus_session, get_focus_session_photos
        from handlers.focus_keeper import stop_continuous_notifications
        
        logger.info(
            f"🔍 Checking task completion: user={user_id}, task={task_id}, "
            f"session={session_id}, name='{task_name}'"
        )
        
        # Session holatini tekshirish
        active_session = await get_active_focus_session(user_id)
        
        # Bildirishnomalarni to'xtatish (agar hali to'xtatilmagan bo'lsa)
        try:
            await stop_continuous_notifications(user_id)
            logger.info(f"✅ Notifications stopped for user {user_id}")
        except Exception as e:
            logger.warning(f"Could not stop notifications: {e}")
        
        if not active_session or active_session['id'] != session_id:
            logger.info(
                f"ℹ️ Session {session_id} is no longer active for user {user_id}. "
                f"Possibly already completed."
            )
            return
        
        # Rasmlar tekshiruvi
        photos = await get_focus_session_photos(session_id)
        photo_count = len(photos)
        
        logger.info(f"📸 Photos submitted: {photo_count}")
        
        if photo_count == 0:
            # RASM YO'Q - JAZO!
            logger.warning(f"⚠️ No photos submitted for session {session_id}")
            
            await auto_apply_punishment(
                bot=bot,
                user_id=user_id,
                task_id=task_id,
                punishment_type="no_photo",
                reason=f"Vazifa '{task_name}' uchun hech qanday rasm yuborilmadi"
            )
            
            try:
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
                logger.info(f"✅ Punishment notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending punishment notification: {e}")
        else:
            # RASM BOR - AJOYIB!
            logger.info(f"✅ Photos submitted: {photo_count}. Marking as completed.")
            
            from utils.database import end_focus_session
            await end_focus_session(session_id, completed=True)
            
            try:
                await bot.send_message(
                    user_id,
                    f"✅ **VAZIFA TUGADI!**\n\n"
                    f"🎯 {task_name}\n\n"
                    f"🎉 Ajoyib ish qildingiz!\n"
                    f"📸 Rasmlar yuborildi: {photo_count} ta\n\n"
                    f"💪 Davom eting! Siz zo'rsiz!",
                    parse_mode="Markdown"
                )
                logger.info(f"✅ Completion success notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending completion notification: {e}")
        
        logger.info(f"✅ Task completion check finished for session {session_id}")
        
    except Exception as e:
        logger.error(
            f"❌ Error checking task completion: user={user_id}, task={task_id}, "
            f"session={session_id} | Error: {e}",
            exc_info=True
        )
