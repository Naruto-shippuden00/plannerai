"""
Focus Keeper - Vazifalarni bajarish vaqtida to'liq nazorat
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
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
    get_user_tasks
)
from utils.keyboards import (
    focus_action_keyboard,
    main_menu_keyboard,
    camera_permission_keyboard
)

router = Router()
logger = logging.getLogger(__name__)

# Aktiv bildirishnomalar uchun tracking
active_notifications = {}  # {user_id: {'task': asyncio.Task, 'session_id': int, 'count': int}}

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
    Har 5 minutda bir marta bildirishnoma
    """
    count = 0
    max_notifications = 100  # Xavfsizlik uchun maksimal limit
    
    logger.info(f"Starting continuous notifications for user {user_id}, session {session_id}")
    
    try:
        while count < max_notifications:
            # Agar user rasm yuborgan bo'lsa, to'xtatamiz
            if user_id not in active_notifications:
                logger.info(f"Notifications stopped for user {user_id} - photo submitted")
                break
            
            count += 1
            
            # Bildirishnoma turli-tuman bo'lishi uchun
            messages = [
                f"⏰ **VAZIFA VAQTI!** ({count}-eslatma)\n\n"
                f"🎯 {task_name}\n"
                f"🕐 {start_time} - {end_time}\n\n"
                f"❗️ DIQQAT: Bildirishnoma to'xtatish uchun vazifa RASMINI yuboring!\n\n"
                f"📸 Rasm turlaridan biri:\n"
                f"• Dars jarayoningiz\n"
                f"• Bajarayotgan vazifangiz\n"
                f"• Mashq daftaringiz\n"
                f"• Ish statingiz\n\n"
                f"⚠️ Rasm yubormasangiz, bildirishnomalar davom etadi!",
                
                f"🔔 **{count}-CHI ESLATMA!**\n\n"
                f"🎯 Vazifa: {task_name}\n\n"
                f"Sizdan hali ham rasm kutilmoqda! 📸\n\n"
                f"Agar hozir ishlamayotgan bo'lsangiz, bu vazifani bajarmagangiz hisoblanadi!\n\n"
                f"❌ Natija: Jazo olasiz!\n\n"
                f"✅ Tezroq rasm yuboring va fokusga kiring!",
                
                f"🚨 **MUHIM OGOHLANTIRISH!** ({count}/∞)\n\n"
                f"🎯 {task_name}\n\n"
                f"Siz hali ham ishlamayapsizmi?\n\n"
                f"⏰ Vaqt o'tyapti!\n"
                f"📸 Tezroq rasm yuboring!\n\n"
                f"Bu bildirishnomalar RASM yuborguningizgacha davom etadi!\n\n"
                f"💪 Boshladingizmi? Rasmni yuboring!",
            ]
            
            # Xabar turini tanlash (3 dan boshlab random)
            if count <= 3:
                message = messages[0]
            elif count <= 10:
                message = messages[1]
            else:
                import random
                message = random.choice(messages)
            
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown"
                )
                logger.info(f"Notification #{count} sent to user {user_id}")
            except Exception as e:
                logger.error(f"Error sending notification to {user_id}: {e}")
            
            # 5 daqiqa kutish
            await asyncio.sleep(300)  # 300 sekund = 5 daqiqa
            
    except asyncio.CancelledError:
        logger.info(f"Notification task cancelled for user {user_id}")
    except Exception as e:
        logger.error(f"Error in continuous notifications for user {user_id}: {e}")
    finally:
        # Tozalash
        if user_id in active_notifications:
            del active_notifications[user_id]

async def start_continuous_notifications(bot, user_id: int, session_id: int, task_name: str, start_time: str, end_time: str):
    """Cheksiz bildirishnomalarni boshlash"""
    # Agar avvalgi bildirishnomalar bo'lsa, to'xtatamiz
    if user_id in active_notifications:
        active_notifications[user_id]['task'].cancel()
    
    # Yangi task yaratish
    task = asyncio.create_task(
        continuous_notification_sender(bot, user_id, session_id, task_name, start_time, end_time)
    )
    
    active_notifications[user_id] = {
        'task': task,
        'session_id': session_id,
        'count': 0
    }
    
    logger.info(f"Continuous notifications started for user {user_id}, session {session_id}")

async def stop_continuous_notifications(user_id: int):
    """Bildirishnomalarni to'xtatish"""
    if user_id in active_notifications:
        active_notifications[user_id]['task'].cancel()
        del active_notifications[user_id]
        logger.info(f"Continuous notifications stopped for user {user_id}")

@router.message(FocusState.waiting_for_photo, F.photo)
async def receive_focus_photo(message: Message, state: FSMContext):
    """
    Focus vaqtida rasm qabul qilish - bildirishnomalarni to'xtatadi
    """
    user_id = message.from_user.id
    
    # Aktiv sessionni olish
    active_session = await get_active_focus_session(user_id)
    
    if not active_session:
        await message.answer(
            "⚠️ Aktiv focus session topilmadi!\n\n"
            "📋 Jadvalingizdan vazifa boshlang.",
            reply_markup=main_menu_keyboard()
        )
        await state.clear()
        return
    
    # Rasmni saqlash
    photo = message.photo[-1]
    photo_dir = "data/focus_photos"
    os.makedirs(photo_dir, exist_ok=True)
    
    file_name = f"{user_id}_{active_session['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    photo_path = os.path.join(photo_dir, file_name)
    
    try:
        await message.bot.download(photo.file_id, photo_path)
        
        # Rasmni bazaga saqlash
        await add_focus_photo(active_session['id'], photo_path)
        
        # MUHIM: Bildirishnomalarni to'xtatish
        await stop_continuous_notifications(user_id)
        
        await message.answer(
            "✅ **RASM QABUL QILINDI!**\n\n"
            "🎉 Ajoyib! Bildirishnomalar to'xtatildi!\n\n"
            "⏱ Endi **POMODORO TIMER** boshlanadi!\n\n"
            "📊 Sizda 1 soatlik fokus sessiya bor.\n"
            "🔥 Men sizni nazorat qilib turaman!\n\n"
            "💪 Fokusda qoling va muvaffaqiyatga erishing!",
            parse_mode="Markdown"
        )
        
        # Pomodoro timerni boshlash
        await start_pomodoro_session(message.bot, user_id, active_session)
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error saving focus photo: {e}")
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
    Pomodoro timer - 1 soat focus + har 15 daqiqada nazorat
    """
    session_id = session_data['id']
    task_name = session_data['task_name']
    planned_duration = session_data['planned_duration']
    
    logger.info(f"Starting Pomodoro session for user {user_id}, session {session_id}, duration {planned_duration} min")
    
    # Darhol xabar yuborish
    await bot.send_message(
        user_id,
        f"🍅 **POMODORO TIMER BOSHLANDI!**\n\n"
        f"🎯 Vazifa: {task_name}\n"
        f"⏱ Davomiyligi: {planned_duration} daqiqa\n\n"
        f"📱 Telefon: Silent mode\n"
        f"🔕 Notificationlar: O'chirilgan\n"
        f"💻 Faqat vazifa: Fokus 100%\n\n"
        f"🚀 Boshlang! Men sizni nazorat qilaman!",
        parse_mode="Markdown"
    )
    
    # Har 15 daqiqada focus keeper xabarlari
    # Lekin faqat planned_duration ichida
    check_intervals = []
    for interval in range(15, planned_duration, 15):
        check_intervals.append(interval)
    
    # Har bir intervalda nazorat qilish
    for interval in check_intervals:
        asyncio.create_task(
            send_pomodoro_check(bot, user_id, task_name, interval, session_id)
        )
    
    # Asosiy timer - vazifa tugaganda
    asyncio.create_task(
        finish_pomodoro_session(bot, user_id, session_id, task_name, planned_duration)
    )

async def send_pomodoro_check(bot, user_id: int, task_name: str, after_minutes: int, session_id: int):
    """Pomodoro davomida tekshirish xabarlari - har 15 daqiqada"""
    await asyncio.sleep(after_minutes * 60)  # Kutish
    
    # Session hali ham aktiv ekanligini tekshirish
    active = await get_active_focus_session(user_id)
    if not active or active['id'] != session_id:
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
        else:
            await bot.send_message(user_id, message, parse_mode="Markdown")
        
        logger.info(f"Pomodoro check sent at {after_minutes} min for user {user_id}")
    except Exception as e:
        logger.error(f"Error sending Pomodoro check to {user_id}: {e}")

async def finish_pomodoro_session(bot, user_id: int, session_id: int, task_name: str, duration_minutes: int):
    """Pomodoro sessionni yakunlash va tanaffus berish"""
    # Duration minutes davom etish
    await asyncio.sleep(duration_minutes * 60)
    
    # Session tugallash
    await end_focus_session(session_id, completed=True)
    
    try:
        await bot.send_message(
            user_id,
            f"🎉 **VAZIFA TUGADI!**\n\n"
            f"🎯 {task_name}\n"
            f"⏱ {duration_minutes} daqiqa\n\n"
            f"✅ Ajoyib ish qildingiz!\n\n"
            f"🧘‍♂️ Endi 10 daqiqa TANAFFUS!\n\n"
            f"☕️ Choy iching\n"
            f"🚶‍♂️ Biroz yuring\n"
            f"💧 Suv iching\n\n"
            f"⏰ 10 daqiqadan keyin keyingi vazifaga o'tamiz!",
            parse_mode="Markdown"
        )
        
        # 10 daqiqa tanaffus
        await asyncio.sleep(600)  # 10 minut
        
        # Tanaffus tugadi
        await bot.send_message(
            user_id,
            f"⏰ **TANAFFUS TUGADI!**\n\n"
            f"💪 Keyingi vazifaga tayyormisiz?\n\n"
            f"📋 Jadvalingizga qarang!\n\n"
            f"🚀 Davom etamiz!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error finishing Pomodoro session for {user_id}: {e}")

@router.callback_query(F.data.startswith("end_focus_"))
async def end_focus_early(callback: CallbackQuery):
    """Focus sessionni erta tugatish"""
    session_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    # Bildirishnomalarni to'xtatish
    await stop_continuous_notifications(user_id)
    
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
        "🔴 Jazo: 1 ball kamaytrildi\n\n"
        "📊 Statistikangizga ta'sir qiladi!\n\n"
        "💪 Keyingi safar to'liq bajaring!",
        parse_mode="Markdown"
    )
    await callback.answer()

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

# Eksport qilish uchun
__all__ = ['router', 'start_continuous_notifications', 'stop_continuous_notifications']
