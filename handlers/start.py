"""
Start va asosiy komandalar
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.database import add_user, get_user_language, set_user_language
from utils.keyboards import main_menu_keyboard, language_selection_keyboard
from utils.translations import get_text

router = Router()

class UserState(StatesGroup):
    """Foydalanuvchi holatlari"""
    waiting_for_task_name = State()
    waiting_for_duration = State()
    waiting_for_photo = State()
    waiting_for_test_answer = State()
    selecting_language = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasi - Har doim til tanlashni ko'rsatish"""
    user = message.from_user
    await add_user(user.id, user.username or "", user.full_name or "")
    
    # Har doim til tanlashni ko'rsatish (yangi yoki mavjud foydalanuvchi)
    await show_language_selection(message)

async def show_language_selection(message: Message):
    """Til tanlash menyusini ko'rsatish"""
    keyboard = language_selection_keyboard()
    
    await message.answer(
        "🌍 **Select your language / Выберите язык / Tilni tanlang**\n\n"
        "Choose your preferred language for the bot interface:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

async def show_welcome_message(message: Message, language: str):
    """Welcome xabarini ko'rsatish"""
    user = message.from_user
    welcome_text = get_text("welcome", language, name=user.first_name)
    
    await message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(language),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery):
    """Til tanlash callback"""
    language = callback.data.split("_")[1]  # lang_uz -> uz
    user_id = callback.from_user.id
    
    # Tilni saqlash
    await set_user_language(user_id, language)
    
    # Eski xabarni o'chirish
    await callback.message.delete()
    
    # Til o'zgartirilganini ko'rsatish
    lang_names = {
        "uz": "O'zbek",
        "ru": "Русский", 
        "en": "English"
    }
    
    selected_lang_name = lang_names.get(language, lang_names["uz"])
    
    change_texts = {
        "uz": f"✅ Til o'zgartirildi: {selected_lang_name}",
        "ru": f"✅ Язык изменён: {selected_lang_name}",
        "en": f"✅ Language changed: {selected_lang_name}"
    }
    
    await callback.answer(change_texts.get(language, change_texts["uz"]), show_alert=True)
    
    # Welcome xabarini ko'rsatish
    welcome_text = get_text("welcome", language, name=callback.from_user.first_name)
    
    await callback.message.answer(
        welcome_text,
        reply_markup=main_menu_keyboard(language),
        parse_mode="Markdown"
    )

@router.message(Command("language"))
async def cmd_language(message: Message):
    """Tilni o'zgartirish komandasi"""
    await show_language_selection(message)

@router.message(Command("help"))
@router.message(F.text.in_(["❓ Yordam", "❓ Помощь", "❓ Help"]))
async def cmd_help(message: Message):
    """Yordam komandasi"""
    user_lang = await get_user_language(message.from_user.id)
    help_text = get_text("help_text", user_lang)
    
    await message.answer(help_text, parse_mode="Markdown")

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

@router.message(F.text.in_(["🏠 Bosh menyu", "🏠 Главное меню", "🏠 Main Menu"]))
async def back_to_main(message: Message, state: FSMContext):
    """Bosh menyuga qaytish"""
    await state.clear()  # Barcha state'larni tozalash
    user_lang = await get_user_language(message.from_user.id)
    
    back_text = {
        "uz": "🏠 Bosh menyu\n\nQuyidagi tugmalardan birini tanlang:",
        "ru": "🏠 Главное меню\n\nВыберите одну из кнопок ниже:",
        "en": "🏠 Main Menu\n\nSelect one of the buttons below:"
    }
    
    await message.answer(
        back_text.get(user_lang, back_text["uz"]),
        reply_markup=main_menu_keyboard(user_lang)
    )

