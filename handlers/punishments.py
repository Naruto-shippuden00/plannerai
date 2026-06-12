"""
Jazo tizimi - vazifani bajarmagan o'quvchilar uchun
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from datetime import datetime, timedelta
import random

from utils.database import (
    get_user_punishments,
    mark_punishment_completed,
    add_punishment,
    get_user_tasks
)
from utils.keyboards import (
    punishment_keyboard,
    main_menu_keyboard
)

router = Router()

# Jazo turlari va tavsiflari
PUNISHMENT_TYPES = {
    "missed_task": {
        "name": "Vazifani o'tkazib yuborish",
        "penalty": "30 daqiqalik qo'shimcha vazifa",
        "points": -5
    },
    "no_photo": {
        "name": "Rasm yubormaslik",
        "penalty": "Vazifani qayta bajarish",
        "points": -3
    },
    "early_exit": {
        "name": "Vazifani erta to'xtatish",
        "penalty": "15 daqiqalik qo'shimcha o'qish",
        "points": -2
    },
    "late_start": {
        "name": "Vazifani kech boshlash (10+ min)",
        "penalty": "Ogohlantirish va 10 min qo'shimcha",
        "points": -1
    },
    "no_break": {
        "name": "Tanaffusni to'g'ri oldirmaslik",
        "penalty": "Keyingi tanaffus bekor",
        "points": -1
    }
}

# Motivatsion jazolar (ijobiy ta'sir)
MOTIVATIONAL_PUNISHMENTS = [
    {
        "task": "10 ta pushup qiling",
        "icon": "💪",
        "benefit": "Qon aylanishini yaxshilaydi"
    },
    {
        "task": "5 daqiqa meditatsiya qiling",
        "icon": "🧘‍♂️",
        "benefit": "Fokusni oshiradi"
    },
    {
        "task": "20 ta jumping jack",
        "icon": "🤸",
        "benefit": "Energiya beradi"
    },
    {
        "task": "3 daqiqa chuqur nafas oling",
        "icon": "🫁",
        "benefit": "Stressni kamaytiradi"
    },
    {
        "task": "1 stakan suv iching",
        "icon": "💧",
        "benefit": "Gidratsiya"
    },
    {
        "task": "Ko'zlaringizni 2 daqiqa dam oldiring",
        "icon": "👀",
        "benefit": "Ko'z toliqishini kamaytiradi"
    },
    {
        "task": "5 daqiqa yuring",
        "icon": "🚶",
        "benefit": "Tana faoliyati"
    }
]

@router.message(F.text == "⚠️ Jazolarim")
async def show_punishments(message: Message):
    """Foydalanuvchi jazolarini ko'rsatish"""
    active_punishments = await get_user_punishments(message.from_user.id, completed=False)
    completed_punishments = await get_user_punishments(message.from_user.id, completed=True)
    
    text = "⚠️ **JAZOLARIM**\n\n"
    
    if not active_punishments and not completed_punishments:
        text += "✅ **Sizda jazolar yo'q!**\n\n"
        text += "🎉 Ajoyib! Barcha vazifalarni o'z vaqtida bajaryapsiz!\n\n"
        text += "💪 Davom eting!"
    else:
        if active_punishments:
            text += "🔴 **FAOL JAZOLAR:**\n\n"
            for p in active_punishments:
                punishment_info = PUNISHMENT_TYPES.get(p['punishment_type'], {
                    "name": p['punishment_type'],
                    "penalty": "Noma'lum",
                    "points": 0
                })
                
                text += f"❌ **{punishment_info['name']}**\n"
                text += f"   📝 Sabab: {p['reason']}\n"
                text += f"   ⚠️ Jazo: {punishment_info['penalty']}\n"
                text += f"   📉 Ball: {punishment_info['points']}\n"
                
                if p['task_name']:
                    text += f"   🎯 Vazifa: {p['task_name']}\n"
                
                applied_date = datetime.fromisoformat(p['applied_at'])
                text += f"   📅 {applied_date.strftime('%d.%m.%Y %H:%M')}\n"
                text += f"   ✅ Bajarish: /complete_punishment_{p['id']}\n\n"
        
        if completed_punishments:
            text += f"\n✅ **BAJARILGAN:** {len(completed_punishments)} ta\n"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

@router.message(F.text.startswith("/complete_punishment_"))
async def complete_punishment(message: Message):
    """Jazoni bajarish"""
    try:
        punishment_id = int(message.text.split("_")[2])
        
        # Tasodifiy motivatsion jazo tanlash
        mot_punishment = random.choice(MOTIVATIONAL_PUNISHMENTS)
        
        await message.answer(
            f"{mot_punishment['icon']} **JAZO VAZIFASI**\n\n"
            f"**Vazifa:** {mot_punishment['task']}\n\n"
            f"💡 **Foyda:** {mot_punishment['benefit']}\n\n"
            f"Bajargandan keyin, tasdiqlash uchun:\n"
            f"`/confirm_punishment_{punishment_id}`",
            parse_mode="Markdown"
        )
        
    except (IndexError, ValueError):
        await message.answer(
            "❌ **Xatolik!**\n\n"
            "Noto'g'ri buyruq formati.",
            reply_markup=main_menu_keyboard()
        )

@router.message(F.text.startswith("/confirm_punishment_"))
async def confirm_punishment_completion(message: Message):
    """Jazo bajarilganini tasdiqlash"""
    try:
        punishment_id = int(message.text.split("_")[2])
        
        # Jazoni bajarilgan deb belgilash
        await mark_punishment_completed(punishment_id)
        
        await message.answer(
            "✅ **JAZO BAJARILDI!**\n\n"
            "🎉 Ajoyib! Siz javobgarlilik ko'rsatdingiz!\n\n"
            "💪 Keyingi safar vazifalarni o'z vaqtida bajaring!\n\n"
            "📊 Ballingiz tiklandi.",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        
    except (IndexError, ValueError):
        await message.answer(
            "❌ **Xatolik!**\n\n"
            "Noto'g'ri tasdiqlash buyrug'i.",
            reply_markup=main_menu_keyboard()
        )

@router.message(F.text == "📊 Jazo Statistikasi")
async def punishment_statistics(message: Message):
    """Jazo statistikasi"""
    all_punishments = await get_user_punishments(message.from_user.id)
    active_punishments = await get_user_punishments(message.from_user.id, completed=False)
    completed_punishments = await get_user_punishments(message.from_user.id, completed=True)
    
    # Jazo turlariga ko'ra hisoblash
    by_type = {}
    total_points_lost = 0
    
    for p in all_punishments:
        p_type = p['punishment_type']
        if p_type not in by_type:
            by_type[p_type] = 0
        by_type[p_type] += 1
        
        # Ballni hisoblash
        punishment_info = PUNISHMENT_TYPES.get(p_type, {"points": 0})
        total_points_lost += abs(punishment_info['points'])
    
    text = "📊 **JAZO STATISTIKASI**\n\n"
    text += f"🔴 Faol jazolar: {len(active_punishments)} ta\n"
    text += f"✅ Bajarilgan: {len(completed_punishments)} ta\n"
    text += f"📉 Yo'qotilgan ball: {total_points_lost}\n\n"
    
    if by_type:
        text += "**Jazo turlari bo'yicha:**\n\n"
        for p_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            punishment_info = PUNISHMENT_TYPES.get(p_type, {"name": p_type})
            text += f"• {punishment_info.get('name', p_type)}: {count} ta\n"
    
    text += "\n\n💡 **Maslahat:**\n"
    
    if len(active_punishments) == 0:
        text += "Siz ajoyib ishlayapsiz! Davom eting! 🎉"
    elif len(active_punishments) <= 2:
        text += "Yaxshi natija! Jazolarni kamaytirishda davom eting! 👍"
    else:
        text += "Vazifalarni o'z vaqtida bajarish ustida ishlang! 💪"
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

async def auto_apply_punishment(bot, user_id: int, task_id: int, punishment_type: str, reason: str):
    """
    Avtomatik jazo berish (scheduler tomonidan chaqiriladi)
    """
    # Jazoni bazaga qo'shish
    await add_punishment(user_id, task_id, None, punishment_type, reason)
    
    punishment_info = PUNISHMENT_TYPES.get(punishment_type, {
        "name": punishment_type,
        "penalty": "Vazifa bajarilmadi",
        "points": -5
    })
    
    # Foydalanuvchiga xabar yuborish
    try:
        await bot.send_message(
            user_id,
            f"⚠️ **JAZO BERILDI!**\n\n"
            f"❌ **Sabab:** {punishment_info['name']}\n"
            f"📝 {reason}\n\n"
            f"⚠️ **Jazo:** {punishment_info['penalty']}\n"
            f"📉 **Ball:** {punishment_info['points']}\n\n"
            f"💪 Keyingi safar yaxshiroq bajaring!\n\n"
            f"Jazolaringizni ko'rish: '⚠️ Jazolarim' tugmasi",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Error sending punishment notification to {user_id}: {e}")

# Admin funksiyalar (agar kerak bo'lsa)
@router.message(F.text == "/reset_punishments")
async def reset_punishments_command(message: Message):
    """Jazolarni reset qilish (faqat o'zingiz uchun)"""
    # Bu funksiya faqat test uchun, production da o'chirish kerak
    pass

__all__ = ['router', 'auto_apply_punishment', 'PUNISHMENT_TYPES']
