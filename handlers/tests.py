"""
Haftalik test tizimi
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from utils.ai_helper import generate_weekly_test, analyze_weekly_progress
from utils.database import get_weekly_stats
from utils.keyboards import (
    weekly_test_keyboard,
    test_answer_keyboard,
    main_menu_keyboard
)

router = Router()

class TestState(StatesGroup):
    taking_test = State()
    answering_question = State()

# Test ma'lumotlarini saqlash
active_tests = {}

@router.message(F.text.startswith("/test"))
@router.message(F.text == "📝 Test")
async def start_test_menu(message: Message):
    """Test menyusi"""
    await message.answer(
        "📚 **HAFTALIK TEST**\n\n"
        "Qaysi kategoriya bo'yicha test topshirmoqchisiz?\n\n"
        "Bu test o'tgan hafta o'rganganlaringizni tekshiradi va "
        "qaysi mavzularga e'tibor berish kerakligini ko'rsatadi.",
        parse_mode="Markdown",
        reply_markup=weekly_test_keyboard()
    )

@router.callback_query(F.data.startswith("test_"))
async def generate_test(callback: CallbackQuery, state: FSMContext):
    """Test generatsiya qilish"""
    category = callback.data.split("_")[1].upper()
    
    await callback.message.edit_text(
        f"🤖 {category} bo'yicha test tayyorlanmoqda...\n\n"
        "⏳ Bir oz kuting..."
    )
    
    # Test savollari generatsiya
    topics = ["Asosiy tushunchalar", "Amaliy mashqlar", "Murakkab mavzular"]
    test_data = await generate_weekly_test(category, topics)
    
    if not test_data or 'questions' not in test_data:
        await callback.message.edit_text(
            "❌ Test yaratishda xatolik yuz berdi.\n"
            "Keyinroq qayta urinib ko'ring."
        )
        return
    
    questions = test_data['questions']
    
    # Test ma'lumotlarini saqlash
    test_id = f"{callback.from_user.id}_{datetime.now().timestamp()}"
    active_tests[test_id] = {
        'category': category,
        'questions': questions,
        'current_question': 0,
        'answers': [],
        'score': 0
    }
    
    await state.update_data(test_id=test_id)
    await state.set_state(TestState.taking_test)
    
    # Birinchi savolni yuborish
    await send_question(callback.message, test_id, 0)
    await callback.answer()

async def send_question(message: Message, test_id: str, question_num: int):
    """Savolni yuborish"""
    test = active_tests.get(test_id)
    if not test:
        await message.answer("❌ Test topilmadi")
        return
    
    questions = test['questions']
    if question_num >= len(questions):
        # Test tugadi
        await finish_test(message, test_id)
        return
    
    question = questions[question_num]
    total_questions = len(questions)
    
    text = f"📝 **Savol {question_num + 1}/{total_questions}**\n\n"
    text += f"{question['question']}\n\n"
    
    if 'options' in question:
        for i, option in enumerate(question['options']):
            text += f"{chr(65+i)}) {option}\n"
    
    await message.answer(
        text,
        parse_mode="Markdown",
        reply_markup=test_answer_keyboard(question_num)
    )

@router.callback_query(F.data.startswith("ans_"))
async def answer_question(callback: CallbackQuery, state: FSMContext):
    """Javobni qabul qilish"""
    data = await state.get_data()
    test_id = data.get('test_id')
    
    if not test_id or test_id not in active_tests:
        await callback.answer("Test topilmadi")
        return
    
    # Javobni parse qilish
    parts = callback.data.split("_")
    question_num = int(parts[1])
    answer = int(parts[2])
    
    test = active_tests[test_id]
    question = test['questions'][question_num]
    
    # Javobni saqlash
    test['answers'].append(answer)
    
    # To'g'riligini tekshirish
    correct = question.get('correct', -1)
    is_correct = (answer == correct) if correct >= 0 else None
    
    if is_correct is True:
        test['score'] += 1
        response = "✅ To'g'ri!"
    elif is_correct is False:
        correct_letter = chr(65 + correct)
        response = f"❌ Noto'g'ri. To'g'ri javob: {correct_letter}"
    else:
        response = "📝 Javob qabul qilindi"
    
    # Tushuntirish
    if 'explanation' in question:
        response += f"\n\n💡 {question['explanation']}"
    
    await callback.message.edit_text(response, parse_mode="Markdown")
    await callback.answer()
    
    # Keyingi savol
    test['current_question'] = question_num + 1
    
    # Bir oz kutish
    import asyncio
    await asyncio.sleep(2)
    
    await send_question(callback.message, test_id, test['current_question'])

async def finish_test(message: Message, test_id: str):
    """Testni yakunlash"""
    test = active_tests.get(test_id)
    if not test:
        return
    
    total = len(test['questions'])
    score = test['score']
    percentage = (score / total * 100) if total > 0 else 0
    
    # Grade
    if percentage >= 90:
        grade = "A"
        emoji = "🏆"
        comment = "Ajoyib natija! Siz bu mavzuni juda yaxshi bilasiz!"
    elif percentage >= 80:
        grade = "B"
        emoji = "🌟"
        comment = "Yaxshi natija! Davom eting!"
    elif percentage >= 70:
        grade = "C"
        emoji = "👍"
        comment = "Yaxshi, lekin yana biroz ishlash kerak."
    elif percentage >= 60:
        grade = "D"
        emoji = "📚"
        comment = "O'rtacha natija. Bu mavzuga ko'proq e'tibor bering."
    else:
        grade = "F"
        emoji = "💪"
        comment = "Taslim bo'lmang! Bu mavzuni qayta o'rganing."
    
    text = f"""
{emoji} **TEST YAKUNLANDI!**

📊 **Natijalar:**

✅ To'g'ri javoblar: {score}/{total}
📈 Foiz: {percentage:.1f}%
🎯 Baho: {grade}

💬 **Izoh:**
{comment}

━━━━━━━━━━━━━━━━━━━━

📚 Qaysi mavzularga e'tibor berish kerak:
• Asosiy tushunchalarni mustahkamlang
• Amaliy mashqlar qiling
• Har kuni kamida 30 daqiqa mashq qiling

Keyingi test: Kelasi shanba 📅
"""
    
    await message.answer(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    
    # Testni o'chirish
    del active_tests[test_id]

@router.message(F.text == "📊 Haftalik hisobot")
async def weekly_report(message: Message):
    """Haftalik hisobot"""
    user_id = message.from_user.id
    
    loading = await message.answer("📊 Hisobot tayyorlanmoqda...")
    
    # Statistikani olish
    stats = await get_weekly_stats(user_id)
    
    # AI tahlili
    analysis = await analyze_weekly_progress(stats, [])
    
    text = f"""
📊 **HAFTALIK HISOBOT**

📅 **Hafta:** {datetime.now().strftime('%d.%m.%Y')}

━━━━━━━━━━━━━━━━━━━━

{analysis}

━━━━━━━━━━━━━━━━━━━━

🎯 **Keyingi hafta rejasi:**
• Doimiy bo'ling
• Kichik maqsadlar qo'ying
• Har kuni progress qiling

Yangi haftaga tayyormisiz? 💪
"""
    
    await loading.edit_text(text, parse_mode="Markdown")
