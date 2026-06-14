"""
Focus Keeper - Vazifalarni bajarish vaqtida to'liq nazorat (OPTIMIZED)
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio
import os
import logging

from utils.database import (
    create_focus_session,
    get_active_focus_session,
    end_focus_session,
    add_focus_photo,
    get_camera_permission,
    set_camera_permission,
    add_punishment,
    mark_task_as_completed,
    get_user_tasks,
    add_achievement,
    update_user_statistics
)
from utils.keyboards import (
    focus_action_keyboard,
    main_menu_keyboard,
    camera_permission_keyboard,
    break_time_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

# Tashkent timezone
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")

# Aktiv bildirishnomalar uchun tracking
active_notifications = {}  # {user_id: {'task': asyncio.Task, 'session_id': int, 'count': int, 'started_at': datetime}}

# Aktiv Pomodoro sessiyalar
active_pomodoro = {}  # {user_id: {'task': asyncio.Task, 'session_id': int, 'started_at': datetime}}

class FocusState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_notes = State()
    camera_verification = State()

@router.message(F.text == "🎯 Focus Mode")
async def start_focus_mode_menu(message: Message):
    """Focus mode menyu"""
    active_session = await get_active_focus_session(message.from_user.id)
    
    if active_session:
        elapsed = datetime.now() - datetime.fromisoformat(active_session['session_start'])
        elapsed_minutes = int(elapsed.total_seconds() / 60)
        remaining = active_session['planned_duration'] - elapsed_minutes
        
        await message.answer(
            f"🔥 **AKTIV FOCUS SESSION**\n\n"
            f"📝 Vazifa: **{active_session['task_name']}**\n"
            f"📂 Kategoriya: {active_session['category']}\n"
            f"⏱ O'tgan vaqt: {elapsed_minutes} daqiqa\n"
            f"⏳ Qolgan: {remaining} daqiqa\n"
            f"📸 Rasmlar: {active_session['photos_submitted']} ta\n\n"
            f"💪 Davom eting! Fokusda qoling!",
            parse_mode="Markdown",
            reply_markup=focus_action_keyboard(active_session['id'])
        )
    else:
        await message.answer(
            "🎯 **FOCUS MODE**\n\n"
            "Focus Mode - bu sizning shaxsiy nazorat tizimingiz!\n\n"
            "**Qanday ishlaydi?**\n"
            "1️⃣ Vazifa vaqti kelganda, har 5 minutda bildirishnoma olasiz\n"
            "2️⃣ Bildirishnomani to'xtatish uchun vazifa rasmi yuboring\n"
            "3️⃣ Rasm yuborilgach, 1 soatlik Pomodoro timer boshlanadi\n"
            "4️⃣ 1 soatdan keyin 10 minut tanaffus\n"
            "5️⃣ Keyingi vazifaga avtomatik o'tadi\n\n"
            "⚠️ **Ogohlantirish:**\n"
            "Agar rasm yubormasangiz, bildirishnomalar davom etadi!\n"
            "Vazifani bajarmagan bo'lsangiz, jazo olasiz!\n\n"
            "📋 Jadvalingiz bo'yicha avtomatik ishga tushadi.",
            parse_mode="Markdown"
        )

async def continuous_notification_sender(bot, user_id: int, session_id: int, task_name: str, start_time: str, end_time: str):
    """
    Cheksiz bildirishnoma yuborish - faqat rasm yuborilganda to'xtaydi
    Har 5 minutda bir marta bildirishnoma (test rejimda 30 soniya)
    
    OPTIMIZED VERSION - better tracking and error handling + TEST MODE support
    """
    # TEST MODE ni import qilish
    from handlers.admin import get_notification_interval
    
    count = 0
    max_notifications = 100  # Xavfsizlik uchun maksimal limit
    notification_interval = get_notification_interval(user_id)  # Test mode support
    
    started_at = datetime.now(TASHKENT_TZ)
    
    logger.info(
        f"🔔 Starting continuous notifications: user={user_id}, session={session_id}, "
        f"task='{task_name}', interval={notification_interval}s"
    )
    
    try:
        while count < max_notifications:
            # Agar user rasm yuborgan bo'lsa, to'xtatamiz
            if user_id not in active_notifications:
                logger.info(f"✅ Notifications stopped for user {user_id} - photo submitted or manually stopped")
                break
            
            count += 1
            elapsed_minutes = int((datetime.now(TASHKENT_TZ) - started_at).total_seconds() / 60)
            
            # Bildirishnoma turli-tuman bo'lishi uchun
            if count == 1:
                message = (
                    f"⏰ **VAZIFA VAQTI!** (1-eslatma)\n\n"
                    f"🎯 {task_name}\n"
                    f"🕐 {start_time} - {end_time}\n\n"
                    f"❗️ DIQQAT: Bildirishnomani to'xtatish uchun vazifa RASMINI yuboring!\n\n"
                    f"📸 Rasm turlaridan biri:\n"
                    f"• Dars jarayoningiz\n"
                    f"• Bajarayotgan vazifangiz\n"
                    f"• Mashq daftaringiz\n"
                    f"• Ish statingiz\n\n"
                    f"⚠️ Rasm yubormasangiz, bildirishnomalar davom etadi!"
                )
            elif count <= 3:
                message = (
                    f"🔔 **{count}-CHI ESLATMA!**\n\n"
                    f"🎯 Vazifa: {task_name}\n"
                    f"⏱ O'tgan vaqt: {elapsed_minutes} daqiqa\n\n"
                    f"Sizdan hali ham rasm kutilmoqda! 📸\n\n"
                    f"Agar hozir ishlamayotgan bo'lsangiz, bu vazifani bajarmagangiz hisoblanadi!\n\n"
                    f"❌ Natija: Jazo olasiz!\n\n"
                    f"✅ Tezroq rasm yuboring va fokusga kiring!"
                )
            elif count <= 6:
                message = (
                    f"🚨 **MUHIM OGOHLANTIRISH!** ({count}/∞)\n\n"
                    f"🎯 {task_name}\n"
                    f"⏱ {elapsed_minutes} daqiqa o'tdi!\n\n"
                    f"Siz hali ham ishlamayapsizmi?\n\n"
                    f"📸 TEZROQ rasm yuboring!\n\n"
                    f"Bu bildirishnomalar RASM yuborguningizgacha davom etadi!\n\n"
                    f"💪 Boshladingizmi? Rasmni yuboring!"
                )
            else:
                # 6 dan keyin random messages
                messages = [
                    f"⚠️ **ESLATMA #{count}**\n\n🎯 {task_name}\n⏱ {elapsed_minutes} min\n\n📸 Rasm yuboring!",
                    f"🔥 **FOKUSGA KIRING!** ({count})\n\n{task_name}\n\n📸 Vazifa rasmini yuboring!",
                    f"💪 **HARAKATGA O'TING!** (#{count})\n\n⏱ {elapsed_minutes} daqiqa!\n📸 Rasm kerak!"
                ]
                import random
                message = random.choice(messages)
            
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown"
                )
                logger.info(f"📨 Notification #{count} sent to user {user_id} (elapsed: {elapsed_minutes}m)")
            except Exception as e:
                logger.error(f"❌ Error sending notification #{count} to user {user_id}: {e}")
                # Agar xabar yuborishda xatolik bo'lsa, user block qilgan bo'lishi mumkin
                if "bot was blocked" in str(e).lower() or "user is deactivated" in str(e).lower():
                    logger.warning(f"⚠️ User {user_id} has blocked the bot. Stopping notifications.")
                    break
            
            # Keyingi bildirishnomaga kutish
            await asyncio.sleep(notification_interval)
            
    except asyncio.CancelledError:
        logger.info(f"🛑 Notification task cancelled for user {user_id} (session {session_id})")
        raise
    except Exception as e:
        logger.error(f"❌ Error in continuous notifications for user {user_id}: {e}", exc_info=True)
    finally:
        # Tozalash
        if user_id in active_notifications:
            del active_notifications[user_id]
            logger.info(f"🧹 Cleaned up notification tracking for user {user_id}")

async def start_continuous_notifications(bot, user_id: int, session_id: int, task_name: str, start_time: str, end_time: str):
    """
    Cheksiz bildirishnomalarni boshlash
    
    OPTIMIZED VERSION
    """
    # Agar avvalgi bildirishnomalar bo'lsa, to'xtatamiz
    if user_id in active_notifications:
        logger.info(f"⚠️ Stopping previous notifications for user {user_id}")
        active_notifications[user_id]['task'].cancel()
        # Bir oz kutamiz cancel bo'lishi uchun
        await asyncio.sleep(0.1)
    
    # Yangi task yaratish
    try:
        task = asyncio.create_task(
            continuous_notification_sender(bot, user_id, session_id, task_name, start_time, end_time)
        )
        
        active_notifications[user_id] = {
            'task': task,
            'session_id': session_id,
            'count': 0,
            'started_at': datetime.now(TASHKENT_TZ)
        }
        
        logger.info(f"✅ Continuous notifications started: user={user_id}, session={session_id}")
    except Exception as e:
        logger.error(f"❌ Error starting notifications for user {user_id}: {e}", exc_info=True)

async def stop_continuous_notifications(user_id: int):
    """
    Bildirishnomalarni to'xtatish
    
    OPTIMIZED VERSION
    """
    if user_id in active_notifications:
        try:
            active_notifications[user_id]['task'].cancel()
            # Task cancel bo'lishini kutamiz
            try:
                await asyncio.wait_for(active_notifications[user_id]['task'], timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            
            del active_notifications[user_id]
            logger.info(f"✅ Notifications stopped for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error stopping notifications for user {user_id}: {e}")
    else:
        logger.debug(f"ℹ️ No active notifications for user {user_id}")

@router.message(FocusState.waiting_for_photo, F.photo)
async def receive_focus_photo(message: Message, state: FSMContext):
    """
    Focus vaqtida rasm qabul qilish - bildirishnomalarni to'xtatadi
    
    FIX: Task name va ma'lumotlarni to'g'ri olish
    """
    user_id = message.from_user.id
    
    logger.info(f"📸 Photo received from user {user_id}")
    
    # Aktiv sessionni olish
    active_session = await get_active_focus_session(user_id)
    
    if not active_session:
        logger.warning(f"⚠️ No active session for user {user_id}")
        await message.answer(
            "⚠️ Aktiv focus session topilmadi!\n\n"
            "📋 Jadvalingizdan vazifa boshlang.",
            reply_markup=main_menu_keyboard()
        )
        await state.clear()
        return
    
    session_id = active_session['id']
    task_id = active_session.get('task_id', 0)
    planned_duration = active_session.get('planned_duration', 60)
    
    # Task ma'lumotlarini to'g'ri olish
    from utils.database import get_task_by_id
    task_info = await get_task_by_id(task_id) if task_id else None
    task_name = task_info.get('task_name', 'Unknown Task') if task_info else 'Unknown Task'
    
    logger.info(f"📋 Task info: task_id={task_id}, name='{task_name}'")
    
    # Rasmni saqlash
    photo = message.photo[-1]
    photo_dir = "data/focus_photos"
    
    try:
        os.makedirs(photo_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating photo directory: {e}")
    
    file_name = f"{user_id}_{session_id}_{datetime.now(TASHKENT_TZ).strftime('%Y%m%d_%H%M%S')}.jpg"
    photo_path = os.path.join(photo_dir, file_name)
    
    try:
        # Rasmni yuklab olish
        file = await message.bot.get_file(photo.file_id)
        await message.bot.download_file(file.file_path, photo_path)
        
        logger.info(f"📥 Photo saved: {photo_path}")
        
        # Rasmni bazaga saqlash
        await add_focus_photo(session_id, photo_path)
        
        # MUHIM: Bildirishnomalarni to'xtatish
        await stop_continuous_notifications(user_id)
        logger.info(f"🔕 Notifications stopped for user {user_id}")
        
        # Photo count
        from utils.database import get_focus_session_photos
        photos = await get_focus_session_photos(session_id)
        photo_count = len(photos)
        
        # Achievement check - birinchi rasm
        if photo_count == 1:
            try:
                await add_achievement(user_id, "first_photo", "Birinchi vazifa rasmi")
            except Exception as e:
                logger.warning(f"Could not add achievement: {e}")
        
        # AI TAHLIL QILISH
        try:
            from utils.ai_helper import analyze_task_photo
            
            # AI tahlil xabari
            await message.answer(
                "🤖 **AI TAHLIL QILINMOQDA...**\n\n"
                "📸 Rasmingizni tahlil qilyapman...\n"
                "⏳ Bir necha soniya kuting...",
                parse_mode="Markdown"
            )
            
            # AI tahlil
            analysis_result = await analyze_task_photo(photo_path, task_id, user_id)
            
            # AI natijasini yuborish
            await message.answer(
                f"🤖 **AI TAHLIL NATIJASI**\n\n"
                f"{analysis_result}\n\n"
                f"✅ Tahlil yakunlandi!",
                parse_mode="Markdown"
            )
            
            logger.info(f"✅ AI analysis completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed for user {user_id}: {e}", exc_info=True)
            await message.answer(
                "⚠️ AI tahlil qilishda xatolik yuz berdi.\n\n"
                "Lekin davom etamiz! Timer boshlanadi...",
                parse_mode="Markdown"
            )
        
        # Pomodoro timer start xabari
        await message.answer(
            f"✅ **RASM QABUL QILINDI!** ({photo_count}-rasm)\n\n"
            f"🎉 Ajoyib! Bildirishnomalar to'xtatildi!\n\n"
            f"⏱ Endi **POMODORO TIMER** boshlanadi!\n\n"
            f"📊 Sizda {planned_duration} daqiqalik fokus sessiya bor.\n"
            f"🔥 Men sizni nazorat qilib turaman!\n\n"
            f"💪 Fokusda qoling va muvaffaqiyatga erishing!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        
        # Session data'ni to'ldirish Pomodoro uchun
        session_with_task = {
            'id': session_id,
            'task_id': task_id,
            'task_name': task_name,
            'planned_duration': planned_duration
        }
        
        logger.info(f"🚀 Starting Pomodoro timer for user {user_id}: session_id={session_id}, task='{task_name}', duration={planned_duration}")
        
        # Pomodoro timerni boshlash
        try:
            await start_pomodoro_session(message.bot, user_id, session_with_task)
            logger.info(f"✅ Pomodoro session started successfully for user {user_id}")
        except Exception as pomodoro_error:
            logger.error(f"❌ CRITICAL: Pomodoro failed to start for user {user_id}: {pomodoro_error}", exc_info=True)
            await message.answer(
                "⚠️ Timerda xatolik yuz berdi!\n\n"
                "Iltimos, /start dan qayta boshlang yoki admin bilan bog'laning.",
                parse_mode="Markdown"
            )
        
        # State tozalash
        await state.clear()
        
        logger.info(f"✅ Photo processed successfully for user {user_id}, session {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Error saving focus photo for user {user_id}: {e}", exc_info=True)
        await message.answer(
            "❌ Rasmni saqlashda xatolik!\n\n"
            "Iltimos, qayta urinib ko'ring.",
            reply_markup=main_menu_keyboard()
        )

@router.message(F.photo)
async def handle_any_photo(message: Message, state: FSMContext):
    """
    Har qanday rasm qabul qilish - STATE qat'iy nazar
    Bu handler birinchi o'rinda turishi kerak!
    """
    user_id = message.from_user.id
    
    logger.info(f"📸 PHOTO RECEIVED from user {user_id} - checking state...")
    
    # Hozirgi state'ni tekshirish
    current_state = await state.get_state()
    logger.info(f"📊 Current FSM state: {current_state}")
    
    # Aktiv session borligini tekshirish
    active_session = await get_active_focus_session(user_id)
    
    if not active_session:
        logger.info("ℹ️ No active session, informing user")
        await message.answer(
            "📸 Rasm qabul qilindi!\n\n"
            "❓ Lekin hozirda aktiv vazifa yo'q.\n\n"
            "Vazifa boshlash uchun:\n"
            "1️⃣ /test_reminder - Test bildirishnoma\n"
            "2️⃣ Yoki jadvalingizdan vazifa boshlang\n\n"
            "💡 Rasm yuborish faqat vazifa davomida kerak.",
            parse_mode="Markdown"
        )
        return
    
    # AKTIV SESSION BOR - RASMNI QABUL QILAMIZ!
    logger.info(f"✅ Active session found: {active_session['id']}, processing photo...")
    
    session_id = active_session['id']
    task_id = active_session.get('task_id', 0)
    planned_duration = active_session.get('planned_duration', 60)
    
    # Task ma'lumotlarini olish
    from utils.database import get_task_by_id
    task_info = await get_task_by_id(task_id) if task_id else None
    task_name = task_info.get('task_name', 'Unknown Task') if task_info else 'Unknown Task'
    
    logger.info(f"📋 Task: '{task_name}', duration: {planned_duration}min")
    
    # Rasmni saqlash
    photo = message.photo[-1]
    photo_dir = "data/focus_photos"
    
    try:
        os.makedirs(photo_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating photo directory: {e}")
    
    file_name = f"{user_id}_{session_id}_{datetime.now(TASHKENT_TZ).strftime('%Y%m%d_%H%M%S')}.jpg"
    photo_path = os.path.join(photo_dir, file_name)
    
    try:
        # Rasmni yuklab olish
        file = await message.bot.get_file(photo.file_id)
        await message.bot.download_file(file.file_path, photo_path)
        
        logger.info(f"✅ Photo saved: {photo_path}")
        
        # Rasmni bazaga saqlash
        await add_focus_photo(session_id, photo_path)
        
        # 🔥 MUHIM: Bildirishnomalarni TO'XTATISH
        logger.info(f"🛑 STOPPING notifications for user {user_id}...")
        await stop_continuous_notifications(user_id)
        logger.info(f"✅ Notifications STOPPED for user {user_id}")
        
        # Photo count
        from utils.database import get_focus_session_photos
        photos = await get_focus_session_photos(session_id)
        photo_count = len(photos)
        
        # Achievement
        if photo_count == 1:
            try:
                await add_achievement(user_id, "first_photo", "Birinchi vazifa rasmi")
            except Exception as e:
                logger.warning(f"Could not add achievement: {e}")
        
        # AI TAHLIL QILISH
        try:
            from utils.ai_helper import analyze_task_photo
            
            await message.answer(
                "🤖 **AI TAHLIL QILINMOQDA...**\n\n"
                "📸 Rasmingizni tahlil qilyapman...\n"
                "⏳ Bir necha soniya kuting...",
                parse_mode="Markdown"
            )
            
            logger.info(f"🤖 Starting AI analysis...")
            analysis_result = await analyze_task_photo(photo_path, task_id, user_id)
            logger.info(f"✅ AI analysis done: {len(analysis_result)} chars")
            
            await message.answer(
                f"🤖 **AI TAHLIL NATIJASI**\n\n"
                f"{analysis_result}\n\n"
                f"✅ Tahlil yakunlandi!",
                parse_mode="Markdown"
            )
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}", exc_info=True)
            await message.answer(
                "⚠️ AI tahlil qilishda xatolik yuz berdi.\n\n"
                "Lekin davom etamiz! Timer boshlanadi...",
                parse_mode="Markdown"
            )
        
        # Pomodoro timer start xabari
        await message.answer(
            f"✅ **RASM QABUL QILINDI!** ({photo_count}-rasm)\n\n"
            f"🎉 Ajoyib! Bildirishnomalar to'xtatildi!\n\n"
            f"⏱ Endi **POMODORO TIMER** boshlanadi!\n\n"
            f"📊 Sizda {planned_duration} daqiqalik fokus sessiya bor.\n"
            f"🔥 Men sizni nazorat qilib turaman!\n\n"
            f"💪 Fokusda qoling va muvaffaqiyatga erishing!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        
        # Session data
        session_with_task = {
            'id': session_id,
            'task_id': task_id,
            'task_name': task_name,
            'planned_duration': planned_duration
        }
        
        logger.info(f"🚀 Starting Pomodoro timer...")
        
        # Pomodoro timerni boshlash
        try:
            await start_pomodoro_session(message.bot, user_id, session_with_task)
            logger.info(f"✅ Pomodoro started successfully")
        except Exception as pomodoro_error:
            logger.error(f"❌ Pomodoro failed: {pomodoro_error}", exc_info=True)
            await message.answer(
                "⚠️ Timerda xatolik yuz berdi!\n\n"
                "Iltimos, /start dan qayta boshlang.",
                parse_mode="Markdown"
            )
        
        # State tozalash
        await state.clear()
        
        logger.info(f"✅ COMPLETE: Photo processed for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR processing photo: {e}", exc_info=True)
        await message.answer(
            "❌ Rasmni saqlashda xatolik!\n\n"
            "Iltimos, qayta urinib ko'ring.",
            reply_markup=main_menu_keyboard()
        )

@router.message(FocusState.waiting_for_photo)
async def wrong_content_during_focus(message: Message):
    """Rasm o'rniga boshqa narsa yuborilsa"""
    await message.answer(
        "❌ **RASM KERAK!**\n\n"
        "Bildirishnomani to'xtatish uchun faqat RASM yuboring! 📸\n\n"
        "Matn yoki boshqa narsalar qabul qilinmaydi!\n\n"
        "📸 Vazifangizni bajarayotganingizni tasdiqlovchi rasm yuboring!"
    )

async def start_pomodoro_session(bot, user_id: int, session_data: dict):
    """
    Pomodoro timer - planned_duration focus + har 15 daqiqada nazorat
    
    OPTIMIZED VERSION - dynamic duration, better tracking + TEST MODE support
    """
    # TEST MODE ni import qilish
    from handlers.admin import get_pomodoro_duration, is_test_mode
    
    session_id = session_data['id']
    task_name = session_data['task_name']
    planned_duration_original = session_data['planned_duration']
    
    # TEST MODE tekshirish
    planned_duration = get_pomodoro_duration(user_id, planned_duration_original)
    
    test_mode_indicator = " [TEST MODE]" if is_test_mode(user_id) else ""
    
    logger.info(
        f"🍅 Starting Pomodoro session: user={user_id}, session={session_id}, "
        f"task='{task_name}', duration={planned_duration}min{test_mode_indicator}"
    )
    
    # Avvalgi Pomodoro sessiyani to'xtatish
    if user_id in active_pomodoro:
        logger.warning(f"⚠️ Stopping previous Pomodoro for user {user_id}")
        active_pomodoro[user_id]['task'].cancel()
        await asyncio.sleep(0.1)
    
    # Darhol xabar yuborish
    try:
        await bot.send_message(
            user_id,
            f"🍅 **POMODORO TIMER BOSHLANDI!**{test_mode_indicator}\n\n"
            f"🎯 Vazifa: {task_name}\n"
            f"⏱ Davomiyligi: {planned_duration} daqiqa\n\n"
            f"📱 Telefon: Silent mode\n"
            f"🔕 Notificationlar: O'chirilgan\n"
            f"💻 Faqat vazifa: Fokus 100%\n\n"
            f"🚀 Boshlang! Men sizni nazorat qilaman!",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error sending Pomodoro start message: {e}")
    
    # Har 15 daqiqada focus keeper xabarlari
    # Lekin faqat planned_duration ichida
    check_intervals = []
    for interval in range(15, planned_duration, 15):
        check_intervals.append(interval)
    
    logger.info(f"📋 Scheduled {len(check_intervals)} check intervals: {check_intervals}")
    
    # Har bir intervalda nazorat qilish
    for interval in check_intervals:
        asyncio.create_task(
            send_pomodoro_check(bot, user_id, task_name, interval, session_id)
        )
    
    # Asosiy Pomodoro timer task
    pomodoro_task = asyncio.create_task(
        finish_pomodoro_session(bot, user_id, session_id, task_name, planned_duration)
    )
    
    # Tracking
    active_pomodoro[user_id] = {
        'task': pomodoro_task,
        'session_id': session_id,
        'started_at': datetime.now(TASHKENT_TZ)
    }
    
    logger.info(f"✅ Pomodoro session fully initialized for user {user_id}")

async def send_pomodoro_check(bot, user_id: int, task_name: str, after_minutes: int, session_id: int):
    """
    Pomodoro davomida tekshirish xabarlari - har 15 daqiqada
    
    OPTIMIZED VERSION
    """
    await asyncio.sleep(after_minutes * 60)  # Kutish
    
    logger.info(f"📊 Pomodoro check at {after_minutes}min for user {user_id}, session {session_id}")
    
    # Session hali ham aktiv ekanligini tekshirish
    try:
        active = await get_active_focus_session(user_id)
        if not active or active['id'] != session_id:
            logger.info(f"ℹ️ Session {session_id} no longer active. Skipping check.")
            return
    except Exception as e:
        logger.error(f"Error checking active session: {e}")
        return
    
    # Har bir 15 daqiqa uchun turli xabarlar
    message_variants = [
        f"💪 **{after_minutes} DAQIQA O'TDI!**\n\n"
        f"🎯 {task_name}\n\n"
        f"Zo'r ishlamoqdasiz! Davom eting!\n"
        f"Fokusda qoling! 🔥",
        
        f"🔥 **{after_minutes} MIN!**\n\n"
        f"🎯 {task_name}\n\n"
        f"Ajoyib! Siz juda yaxshi ishlayapsiz!\n"
        f"💪 Intiling!",
        
        f"⚡️ **{after_minutes} DAQIQA!**\n\n"
        f"🎯 {task_name}\n\n"
        f"Zo'r! Keep going!\n"
        f"Maqsadga yetib boramiz! 🚀"
    ]
    
    import random
    message = random.choice(message_variants)
    
    try:
        # Kamera tekshiruvi (agar ruxsat bo'lsa va 30 daqiqada bir)
        has_camera = await get_camera_permission(user_id)
        if has_camera and after_minutes % 30 == 0:
            await bot.send_message(
                user_id,
                f"{message}\n\n"
                f"📸 Iltimos, hozirgi holatni tasdiqlovchi rasm yuboring!",
                parse_mode="Markdown"
            )
            logger.info(f"📸 Camera check requested at {after_minutes}min")
        else:
            await bot.send_message(user_id, message, parse_mode="Markdown")
        
        logger.info(f"✅ Pomodoro check sent at {after_minutes}min for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Error sending Pomodoro check to user {user_id}: {e}")

async def finish_pomodoro_session(bot, user_id: int, session_id: int, task_name: str, duration_minutes: int):
    """
    Pomodoro sessionni yakunlash va tanaffus berish
    
    OPTIMIZED VERSION - achievements, statistics + TEST MODE support
    """
    # TEST MODE ni import qilish
    from handlers.admin import get_break_duration, is_test_mode
    
    logger.info(f"⏱ Waiting {duration_minutes}min for session {session_id} to complete...")
    
    # Duration minutes davom etish
    await asyncio.sleep(duration_minutes * 60)
    
    # Break duration
    break_seconds = get_break_duration(user_id)
    break_minutes = break_seconds // 60 if break_seconds >= 60 else 1
    
    test_mode_indicator = " [TEST MODE]" if is_test_mode(user_id) else ""
    
    logger.info(f"🏁 Pomodoro session completed: user={user_id}, session={session_id}")
    
    # Session tugallash
    try:
        await end_focus_session(session_id, completed=True)
        
        # Statistikani yangilash
        await update_user_statistics(user_id)
        
        # Achievement check
        await add_achievement(user_id, "completed_focus", f"Fokus sessiya tugallandi: {task_name}")
        
    except Exception as e:
        logger.error(f"Error ending focus session: {e}")
    
    # Tracking tozalash
    if user_id in active_pomodoro:
        del active_pomodoro[user_id]
    
    try:
        # Tugallanganlik xabari
        await bot.send_message(
            user_id,
            f"🎉 **VAZIFA TUGADI!**{test_mode_indicator}\n\n"
            f"🎯 {task_name}\n"
            f"⏱ {duration_minutes} daqiqa\n\n"
            f"✅ Ajoyib ish qildingiz!\n\n"
            f"🧘‍♂️ Endi {break_minutes} daqiqa TANAFFUS!\n\n"
            f"☕️ Choy iching\n"
            f"🚶‍♂️ Biroz yuring\n"
            f"💧 Suv iching\n"
            f"👀 Ko'zingizni dam oldiring\n\n"
            f"⏰ {break_minutes} daqiqadan keyin keyingi vazifaga o'tamiz!",
            parse_mode="Markdown",
            reply_markup=break_time_keyboard()
        )
        
        logger.info(f"✅ Completion message sent to user {user_id}")
        
        # Tanaffus
        await asyncio.sleep(break_seconds)
        
        # Tanaffus tugadi
        await bot.send_message(
            user_id,
            f"⏰ **TANAFFUS TUGADI!**{test_mode_indicator}\n\n"
            f"💪 Keyingi vazifaga tayyormisiz?\n\n"
            f"📋 Jadvalingizga qarang!\n\n"
            f"🚀 Davom etamiz!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        
        logger.info(f"✅ Break finished message sent to user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Error finishing Pomodoro session for user {user_id}: {e}", exc_info=True)

@router.callback_query(F.data.startswith("end_focus_"))
async def end_focus_early(callback: CallbackQuery):
    """
    Focus sessionni erta tugatish
    
    OPTIMIZED VERSION
    """
    try:
        session_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        logger.info(f"⏹ User {user_id} requesting early end of session {session_id}")
        
        # Bildirishnomalarni to'xtatish
        await stop_continuous_notifications(user_id)
        
        # Pomodoro'ni to'xtatish
        if user_id in active_pomodoro:
            active_pomodoro[user_id]['task'].cancel()
            del active_pomodoro[user_id]
        
        # Sessionni tugatish
        await end_focus_session(session_id, completed=False)
        
        # Jazo berish
        active_session = await get_active_focus_session(user_id)
        if active_session:
            await add_punishment(
                user_id,
                active_session['task_id'],
                session_id,
                "early_exit",
                "Vazifani vaqtidan oldin to'xtatdi"
            )
        
        await callback.message.edit_text(
            "⚠️ **FOCUS SESSION TO'XTATILDI!**\n\n"
            "❌ Siz vazifani to'liq bajarmadingiz.\n\n"
            "🔴 Jazo: Vazifani qayta bajarish kerak\n\n"
            "📊 Statistikangizga ta'sir qiladi!\n\n"
            "💪 Keyingi safar to'liq bajaring!",
            parse_mode="Markdown"
        )
        await callback.answer("Session to'xtatildi")
        
        logger.info(f"✅ Session {session_id} terminated early by user {user_id}")
        
    except Exception as e:
        logger.error(f"Error ending focus session early: {e}", exc_info=True)
        await callback.answer("Xatolik yuz berdi!", show_alert=True)

@router.message(F.text == "📸 Kamera Ruxsati")
async def camera_permission_request(message: Message):
    """Kamera ruxsatini so'rash"""
    has_permission = await get_camera_permission(message.from_user.id)
    
    if has_permission:
        await message.answer(
            "✅ **KAMERA RUXSATI BERILGAN**\n\n"
            "📸 Men focus vaqtida tasodifiy suratlar so'rayman.\n\n"
            "Bu sizning chindan ham ishlayotganingizni tasdiqlaydi!\n\n"
            "⚙️ Ruxsatni bekor qilishingiz mumkin.",
            reply_markup=camera_permission_keyboard(True)
        )
    else:
        await message.answer(
            "📸 **KAMERA RUXSATI**\n\n"
            "Bot focus sessiya vaqtida tasodifiy ravishda sizdan suratlar so'rashi mumkin.\n\n"
            "**Nima uchun kerak?**\n"
            "• Sizning chindan ham ishlayotganingizni tasdiqlaydi\n"
            "• Chalg'itishlardan saqlaydi\n"
            "• Natijalarni yaxshilaydi\n\n"
            "⚠️ **Maxfiylik:**\n"
            "• Rasmlar faqat sizning progressingiz uchun saqlanadi\n"
            "• Hech kim bilan baham ko'rilmaydi\n"
            "• Istalgan vaqt o'chirib qo'yishingiz mumkin\n\n"
            "Ruxsat berasizmi?",
            parse_mode="Markdown",
            reply_markup=camera_permission_keyboard(False)
        )

@router.callback_query(F.data.startswith("camera_"))
async def handle_camera_permission(callback: CallbackQuery):
    """Kamera ruxsatini boshqarish"""
    action = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    if action == "grant":
        await set_camera_permission(user_id, True)
        await callback.message.edit_text(
            "✅ **RUXSAT BERILDI!**\n\n"
            "📸 Endi focus vaqtida men sizdan tasodifiy suratlar so'rayman.\n\n"
            "Bu sizning natijalaringizni yaxshilashga yordam beradi!\n\n"
            "💪 Muvaffaqiyat yo'lida birgamiz!",
            parse_mode="Markdown"
        )
    elif action == "revoke":
        await set_camera_permission(user_id, False)
        await callback.message.edit_text(
            "❌ **RUXSAT BEKOR QILINDI**\n\n"
            "📸 Endi men sizdan suratlar so'ramayman.\n\n"
            "⚠️ Lekin progress tracking kamroq samarali bo'ladi.",
            parse_mode="Markdown"
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("break_"))
async def handle_break_activity(callback: CallbackQuery):
    """Tanaffus vaqtidagi faoliyatlarni tracking"""
    activity = callback.data.split("_")[1]
    
    activity_messages = {
        "tea": "☕️ Choydan bahramand bo'ling!",
        "walk": "🚶‍♂️ Yaxshi sayr qiling!",
        "water": "💧 Suv ichish juda foydali!",
        "rest": "🧘‍♂️ Yaxshi dam oling!"
    }
    
    message = activity_messages.get(activity, "Dam oling!")
    
    await callback.answer(message, show_alert=True)
    logger.info(f"Break activity logged: user={callback.from_user.id}, activity={activity}")

# Eksport qilish uchun
__all__ = [
    'router', 
    'start_continuous_notifications', 
    'stop_continuous_notifications',
    'FocusState'
]