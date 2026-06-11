"""
AI Helper - Groq API (bepul) ishlatadi
"""
import os
from groq import Groq
from typing import List, Dict
import json

client = None

def init_ai():
    """AI clientni boshlash"""
    global client
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        client = Groq(api_key=api_key)
    return client is not None

async def generate_schedule(tasks: List[Dict], constraints: Dict) -> Dict:
    """
    AI yordamida jadval tuzish
    
    Args:
        tasks: Vazifalar ro'yxati [{"name": "SAT", "duration": 120, "priority": 3, ...}]
        constraints: Cheklovlar {"work_hours": [8, 16], "work_days": [0,1,2,3,4,5], ...}
    
    Returns:
        Jadval: {"monday": [...], "tuesday": [...], ...}
    """
    if not client:
        # Agar AI ishlamasa, oddiy algoritm
        return generate_simple_schedule(tasks, constraints)
    
    try:
        prompt = f"""
Siz professional time management assistant sizga vazifalar va cheklovlar berilgan. 
Optimal haftalik jadval tuzing.

VAZIFALAR:
{json.dumps(tasks, ensure_ascii=False, indent=2)}

CHEKLOVLAR:
- Texnikum: Dushanba-Shanba, 08:00-16:00
- Uyquga kamida 7-8 soat ajrating
- Har bir vazifa uchun optimal vaqtni tanlang
- Prioritet muhim: 3 (eng muhim), 2 (o'rta), 1 (past)
- Dam olish vaqtini unutmang

QOIDALAR:
1. Ertalab 6:00-8:00: Morning routine, breakfast, preparation
2. 08:00-16:00: Texnikum (bu vaqtni band qilmang)
3. 16:00-17:00: Dam olish, kechki ovqat
4. 17:00-22:00: Asosiy vazifalar (SAT, Python, Kitob)
5. 22:00-23:00: Review, keyingi kun tayyorligi
6. 23:00-06:00: Uyqu
7. Yakshanba: Haftalik review va yangi hafta plani

Jadval quyidagi JSON formatida bo'lsin:
{{
    "monday": [
        {{"time": "17:00-19:00", "task": "SAT Practice", "task_id": 1}},
        {{"time": "19:30-21:00", "task": "Python Learning", "task_id": 2}}
    ],
    ...
}}

Faqat JSON javob bering, boshqa hech narsa yo'q.
"""
        
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Groq'ning eng yaxshi bepul modeli
            messages=[
                {"role": "system", "content": "Siz professional time management assistant. Faqat JSON formatida javob bering."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        
        # JSON ni extract qilish
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        schedule = json.loads(result)
        return schedule
        
    except Exception as e:
        print(f"AI schedule generation error: {e}")
        return generate_simple_schedule(tasks, constraints)

def generate_simple_schedule(tasks: List[Dict], constraints: Dict) -> Dict:
    """
    Oddiy algoritm bilan jadval tuzish (AI ishlamasa)
    """
    schedule = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    }
    
    # Prioritet bo'yicha saralash
    sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 1), reverse=True)
    
    # Haftaning kunlari
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    
    # Mavjud vaqt oralig'i (texnikumdan keyin)
    time_slots = [
        "17:00-18:30",
        "18:30-20:00",
        "20:00-21:30"
    ]
    
    # Vazifalarni taqsimlash
    task_idx = 0
    for day in weekdays:
        for time_slot in time_slots:
            if task_idx >= len(sorted_tasks):
                task_idx = 0  # Qaytadan boshla
            
            task = sorted_tasks[task_idx]
            schedule[day].append({
                "time": time_slot,
                "task": task['task_name'],
                "task_id": task['id']
            })
            task_idx += 1
    
    # Yakshanba - review va test kuni
    schedule["sunday"] = [
        {"time": "10:00-12:00", "task": "📚 Haftalik Review", "task_id": None},
        {"time": "14:00-16:00", "task": "✅ Weekly Test", "task_id": None},
        {"time": "16:30-18:00", "task": "📝 Keyingi hafta plani", "task_id": None}
    ]
    
    return schedule

async def generate_weekly_test(category: str, topics: List[str]) -> Dict:
    """
    Haftalik test savollari generatsiya qilish
    """
    if not client:
        return generate_simple_test(category, topics)
    
    try:
        prompt = f"""
Quyidagi mavzu bo'yicha 10 ta test savoli yarating:
Kategoriya: {category}
Mavzular: {', '.join(topics)}

Har bir savol quyidagi formatda bo'lsin:
{{
    "question": "Savol matni",
    "options": ["A) variant", "B) variant", "C) variant", "D) variant"],
    "correct": 0,
    "explanation": "Qisqacha tushuntirish"
}}

Faqat JSON array qaytaring, boshqa hech narsa yo'q.
"""
        
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Siz test savollari yaratuvchi assistant. Faqat JSON formatida javob bering."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        questions = json.loads(result)
        return {"questions": questions}
        
    except Exception as e:
        print(f"AI test generation error: {e}")
        return generate_simple_test(category, topics)

def generate_simple_test(category: str, topics: List[str]) -> Dict:
    """Oddiy test (AI ishlamasa)"""
    # Bu yerda oldindan tayyorlangan savollar bo'lishi mumkin
    return {
        "questions": [
            {
                "question": f"{category} bo'yicha asosiy bilimingizni baholang",
                "options": ["A) Juda yaxshi", "B) Yaxshi", "C) O'rtacha", "D) Yaxshilashim kerak"],
                "correct": -1,  # Self-assessment
                "explanation": "Bu o'z-o'zini baholash savoli"
            }
        ]
    }

async def analyze_weekly_progress(stats: Dict, completions: List[Dict]) -> str:
    """
    Haftalik progress tahlili
    """
    if not client:
        return generate_simple_analysis(stats)
    
    try:
        prompt = f"""
Foydalanuvchining haftalik natijalarini tahlil qiling va motivatsiya bering:

STATISTIKA:
{json.dumps(stats, ensure_ascii=False, indent=2)}

Quyidagilarni qo'shing:
1. Nima yaxshi bo'lgan (yutuqlar)
2. Nimani yaxshilash kerak
3. Keyingi hafta uchun tavsiyalar
4. Motivatsiya xabari

O'zbek tilida, samimiy va motivatsiya beruvchi yozing. 200-300 so'z.
"""
        
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "Siz motivatsiya beruvchi coach. O'zbek tilida yozing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"AI analysis error: {e}")
        return generate_simple_analysis(stats)

def generate_simple_analysis(stats: Dict) -> str:
    """Oddiy tahlil"""
    completion_rate = stats.get('completion_rate', 0)
    
    if completion_rate >= 80:
        mood = "🔥 AJOYIB!"
        message = "Siz bu haftada ajoyib ish qildingiz! Davom eting!"
    elif completion_rate >= 60:
        mood = "👍 Yaxshi!"
        message = "Yaxshi natija! Yana biroz harakat qiling."
    else:
        mood = "💪 Harakat qiling!"
        message = "Bu hafta qiyin bo'ldi, lekin taslim bo'lmang! Keyingi hafta yaxshiroq bo'ladi."
    
    return f"""
{mood}

Haftalik natijalar:
✅ Bajarilgan: {stats.get('completed', 0)} ta vazifa
📊 Foiz: {completion_rate:.1f}%

{message}

Keyingi hafta uchun tavsiyalar:
- Kunlik maqsadlarni kichikroq qiling
- Har kuni kamida bitta vazifani bajaring
- Eslatmalarni o'chirmang, javob bering!

Siz qila olasiz! 💪
"""
