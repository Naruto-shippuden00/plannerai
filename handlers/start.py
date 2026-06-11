"""
Start va asosiy komandalar
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.database import add_user
from utils.keyboards import main_menu_keyboard

router = Router()

class UserState(StatesGroup):
    """Foydalanuvchi holatlari"""
    waiting_for_task_name = State()
    waiting_for_duration = State()
    waiting_for_photo = State()
    waiting_for_test_answer = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start komandasi"""
    user = message.from_user
    await add_user(user.id, user.username or "", user.full_name or "")
    
    welcome_text = f"""
👋 Assalomu alaykum, {user.first_name}!

Men sizning shaxsiy **Productivity Assistant** botingizman! 🚀

📌 **Nima qila olaman:**

🤖 **AI Planner** - Sizning vazifalaringizni olib, optimal haftalik jadval tuzaman

⏰ **Smart Reminders** - Har bir vazifa vaqtida eslatma beraman va tekshirish uchun rasm so'rayman

📊 **Progress Tracking** - Kunlik va haftalik progressingizni kuzataman

✅ **Weekly Tests** - Har shanba kuni o'rganganlaringiz bo'yicha test, yakshanba kuni natijalar

💪 **Motivation** - Sizni doimo motivatsiya qilaman va qo'llab-quvvatlayman!

---

🎯 **Hozir nima qilish kerak:**

1️⃣ Vazifalaringizni qo'shing (➕ Vazifa qo'shish)
2️⃣ AI bilan jadval tuzing (🤖 AI Jadval)
3️⃣ Jadvalingizga amal qiling!

Men sizga eslatmalar yuboraman va natijalarni kuzataman. 

**Tayyor bo'lsangiz, pastdagi tugmalardan foydalaning!** 👇
"""
    
    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

@router.message(Command("help"))
@router.message(F.text == "❓ Yordam")
async def cmd_help(message: Message):
    """Yordam komandasi"""
    help_text = """
📚 **Bot qanday ishlaydi:**

**1. Vazifalar qo'shish:**
- "➕ Vazifa qo'shish" tugmasini bosing
- Vazifa nomini kiriting (masalan: "SAT Math practice")
- Kategoriyani tanlang (SAT, Python, Kitob va h.k.)
- Prioritet va davomiylikni belgilang

**2. AI Jadval tuzish:**
- "🤖 AI Jadval" tugmasini bosing
- AI sizning vazifalaringizni tahlil qilib, optimal jadval tuzadi
- Texnikum vaqtingiz (8:00-16:00) avtomatik hisobga olinadi
- Jadvalni tasdiqlang

**3. Eslatmalar:**
- Vazifa vaqti kelganda sizga eslatma yuboriladi
- Vazifani bajargandan keyin rasm yuboring
- Rasm sizning progressingizni tasdiqlaydi

**4. Statistika:**
- Kunlik va haftalik progressingizni ko'ring
- Qaysi vazifalarni ko'proq bajaryapsiz
- O'z-o'zingizni taqqoslang

**5. Haftalik test:**
- Shanba kuni: o'rganganlaringiz bo'yicha test
- Yakshanba kuni: haftalik natijalar va tahlil

**Qo'shimcha buyruqlar:**
/stats - Statistika
/schedule - Bugungi jadval
/reset - Jadvalni qayta tuzish

❓ Savollar bo'lsa, bemalol yozing!
"""
    
    await message.answer(help_text)

@router.message(Command("id"))
async def cmd_id(message: Message):
    """User ID ni ko'rsatish"""
    await message.answer(
        f"Sizning Telegram ID: `{message.from_user.id}`\n\n"
        f"Buni .env fayliga ADMIN_USER_ID sifatida yozing.",
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Asosiy menyuga qaytish"""
    await callback.message.edit_text(
        "Asosiy menyu 👇",
        reply_markup=None
    )
    await callback.message.answer(
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()
