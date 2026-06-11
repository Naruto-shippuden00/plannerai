"""
Statistika va progress tracking
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import os

from utils.database import get_weekly_stats, get_user_tasks
from utils.keyboards import main_menu_keyboard

router = Router()

@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    """Statistikani ko'rsatish"""
    user_id = message.from_user.id
    
    # Haftalik statistika
    stats = await get_weekly_stats(user_id)
    
    if stats['total_scheduled'] == 0:
        await message.answer(
            "❌ **Statistika yo'q**\n\n"
            "Avval vazifalar qo'shing va jadval tuzing!\n\n"
            "1️⃣ ➕ Vazifa qo'shish\n"
            "2️⃣ 🤖 AI Jadval",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # Matn statistika
    completion_rate = stats['completion_rate']
    completed = stats['completed']
    total = stats['total_scheduled']
    
    # Progress bar
    progress_bar = create_progress_bar(completion_rate)
    
    # Emoji mood
    if completion_rate >= 80:
        mood = "🔥 AJOYIB!"
        message_text = "Siz ajoyib natijaga erishdingiz!"
    elif completion_rate >= 60:
        mood = "👍 YAXSHI!"
        message_text = "Yaxshi ish qilyapsiz, davom eting!"
    elif completion_rate >= 40:
        mood = "💪 YAXSHILANYAPTI"
        message_text = "Yaxshi yo'ldasiz, yana biroz harakat!"
    else:
        mood = "📈 BOSHLADINGIZ"
        message_text = "Har bir qadam muhim, taslim bo'lmang!"
    
    text = f"""
📊 **HAFTALIK STATISTIKA**

{mood}
{message_text}

━━━━━━━━━━━━━━━━━━━━
📈 **Umumiy natijalar:**

✅ Bajarildi: {completed} / {total} ta
{progress_bar} {completion_rate:.1f}%

━━━━━━━━━━━━━━━━━━━━
📂 **Kategoriyalar bo'yicha:**
"""
    
    # Kategoriya bo'yicha
    category_emoji = {
        "SAT": "📚",
        "IELTS": "🗣",
        "Python": "🐍",
        "Startup": "💡",
        "Gym": "💪",
        "Kitob": "📖",
        "Boshqa": "📌"
    }
    
    if stats['by_category']:
        for category, count in stats['by_category'].items():
            emoji = category_emoji.get(category, "📌")
            text += f"\n{emoji} {category}: {count} ta"
    else:
        text += "\n\n_Hali hech narsa bajarilmagan_"
    
    text += "\n\n━━━━━━━━━━━━━━━━━━━━"
    text += "\n\n💡 **Maslahat:**\n"
    
    if completion_rate < 50:
        text += "Kunlik maqsadlarni kichikroq qiling. Har kuni kamida 1 ta vazifani bajaring!"
    elif completion_rate < 80:
        text += "Yaxshi ish! Eslatmalarni o'chirmang va doimiy bo'ling!"
    else:
        text += "Siz champion! Davom eting va boshqalarga ilhom bering! 🌟"
    
    await message.answer(text, parse_mode="Markdown")
    
    # Grafik yaratish
    if stats['by_category']:
        chart_path = await create_stats_chart(user_id, stats)
        if chart_path and os.path.exists(chart_path):
            photo = FSInputFile(chart_path)
            await message.answer_photo(
                photo=photo,
                caption="📊 Kategoriyalar bo'yicha grafik"
            )
            # Faylni o'chirish
            try:
                os.remove(chart_path)
            except:
                pass

def create_progress_bar(percentage: float, length: int = 10) -> str:
    """Progress bar yaratish"""
    filled = int(length * percentage / 100)
    empty = length - filled
    return "█" * filled + "░" * empty

async def create_stats_chart(user_id: int, stats: dict) -> str:
    """Statistika grafigi yaratish"""
    try:
        by_category = stats['by_category']
        
        if not by_category:
            return None
        
        # Ma'lumotlarni tayyorlash
        categories = list(by_category.keys())
        counts = list(by_category.values())
        
        # Rangli emoji uchun
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
        
        # Grafik yaratish
        plt.figure(figsize=(10, 6))
        bars = plt.bar(categories, counts, color=colors[:len(categories)])
        
        plt.xlabel('Kategoriyalar', fontsize=12, fontweight='bold')
        plt.ylabel('Bajarilgan vazifalar soni', fontsize=12, fontweight='bold')
        plt.title('Haftalik natijalar kategoriyalar bo\'yicha', fontsize=14, fontweight='bold')
        
        # Y o'qidagi qiymatlar
        plt.yticks(range(0, max(counts) + 2))
        
        # Grid
        plt.grid(axis='y', alpha=0.3)
        
        # Har bir bar ustiga qiymat yozish
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Saqlash
        chart_dir = "data/charts"
        os.makedirs(chart_dir, exist_ok=True)
        chart_path = os.path.join(chart_dir, f"stats_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return chart_path
        
    except Exception as e:
        print(f"Chart creation error: {e}")
        return None

@router.message(F.text.startswith("/stats"))
async def cmd_stats(message: Message):
    """Statistika buyrug'i"""
    await show_statistics(message)

@router.message(F.text == "🏆 Yutuqlarim")
async def show_achievements(message: Message):
    """Yutuqlarni ko'rsatish"""
    user_id = message.from_user.id
    stats = await get_weekly_stats(user_id)
    
    completed = stats['completed']
    
    achievements = []
    
    # Yutuqlar ro'yxati
    if completed >= 1:
        achievements.append("🌱 Birinchi qadam - 1 ta vazifa bajarildi")
    if completed >= 5:
        achievements.append("🔥 Qiziyapti - 5 ta vazifa bajarildi")
    if completed >= 10:
        achievements.append("💪 Kuchli boshlanish - 10 ta vazifa")
    if completed >= 20:
        achievements.append("🚀 Momentum - 20 ta vazifa")
    if completed >= 50:
        achievements.append("⭐ Yulduz - 50 ta vazifa")
    if completed >= 100:
        achievements.append("🏆 Champion - 100 ta vazifa!")
    
    if stats['completion_rate'] >= 80:
        achievements.append("🎯 Aniqlik - 80%+ bajarish")
    
    if not achievements:
        text = "🏆 **Yutuqlar**\n\nHali yutuqlaringiz yo'q.\nVazifalarni bajaring va yutuqlarga erishing! 💪"
    else:
        text = "🏆 **Sizning yutuqlaringiz:**\n\n"
        for ach in achievements:
            text += f"✅ {ach}\n"
        
        text += f"\n\n📊 Jami: {len(achievements)} ta yutuq!"
    
    await message.answer(text, parse_mode="Markdown")
