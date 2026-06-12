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
        constraints: Cheklovlar {"work_hours": [8, 16], "work_start_time": "08:00", "work_end_time": "16:00", ...}
    
    Returns:
        Jadval: {"monday": [...], "tuesday": [...], ...}
    """
    if not client:
        # Agar AI ishlamasa, oddiy algoritm
        return generate_simple_schedule(tasks, constraints)
    
    # Vaqtlarni olish
    work_start = constraints.get('work_start_time', '08:00')
    work_end = constraints.get('work_end_time', '16:00')
    
    try:
        # Vazifalar sonini hisoblash
        task_count = len(tasks)
        
        # Har bir vazifaning ma'lumotlarini tayyorlash
        task_details = ""
        for task in tasks:
            duration_hours = task.get('duration_minutes', 60) / 60
            priority_text = {3: "🔴 Juda muhim", 2: "🟡 O'rtacha", 1: "🟢 Past"}.get(task.get('priority', 1), "🟢 Past")
            task_details += f"\n- {task['task_name']} ({task['category']}) - {duration_hours}h - {priority_text}"
        
        prompt = f"""
Siz professional time management AI assistant. Sizning vazifangiz - optimal, muvozanatli haftalik jadval tuzish.

📋 VAZIFALAR ({task_count} ta):
{task_details}

⚙️ CHEKLOVLAR:
- Ish/Texnikum: Dushanba-Shanba, {work_start}-{work_end} ❌ (band qilmang!)
- Bo'sh vaqt: {work_end} dan keyin va yakshanba kuni
- Uyqu: 23:00-06:00 (MUHIM!)
- Optimal ish vaqti: Har kuni 3-4 soat o'qish/mashq

🎯 MAQSAD: Har bir vazifaga HAFTADA 3-5 marta vaqt ajrating!

⚠️ MUHIM QOIDALAR:

1. **HAR KUNGA XILMA-XILLIK:**
   - Bir kunga BARCHA vazifalarni joylashtirmang!
   - Har kuni 2-3 xil vazifa bo'lishi kerak
   - Misol: Dushanba → SAT, Python | Seshanba → IELTS, Kitob | ...

2. **OPTIMAL TAQSIMLASH:**
   - Yuqori prioritetli vazifalar: haftada 4-5 marta
   - O'rtacha prioritet: haftada 3-4 marta  
   - Past prioritet: haftada 2-3 marta

3. **VAQT ORALIG'I:**
   - {work_end} dan keyin 1 soat dam olish
   - Asosiy vazifalar: {work_end}+1 soat dan 22:00 gacha
   - Har bir session: 1-2 soat
   - Sessionlar orasida 15-30 daqiqa tanaffus

4. **PRIORITET HISOBGA OLING:**
   - Priority 3 (🔴): Eng yaxshi vaqtda (ertalab yoki kechqurun birinchi)
   - Priority 2 (🟡): O'rtacha vaqt
   - Priority 1 (🟢): Qolgan vaqt

5. **KATEGORIYA BO'YICHA:**
   - SAT/IELTS: Ertalab yoki kechqurun birinchi
   - Python/Programming: Miya yangi bo'lganda
   - Kitob: Kechqurun dam olish uchun
   - Gym: Energiya kerak bo'lganda

6. **MUVOZANAT:**
   - Qiyin vazifadan keyin oson vazifa
   - Mental ishdan keyin physical ish
   - Bir xil vazifani ketma-ket 2 kunga joylashtirmang

7. **YAKSHANBA:**
   - Haftalik review: 10:00-12:00
   - Yengil o'qish/takrorlash: 14:00-16:00
   - Keyingi hafta plani: 17:00-18:00

📊 JSON FORMAT:
{{
    "monday": [
        {{"time": "17:00-18:30", "task": "SAT Math", "task_id": 1}},
        {{"time": "19:00-20:30", "task": "Python Basics", "task_id": 2}}
    ],
    "tuesday": [
        {{"time": "17:00-18:30", "task": "IELTS Speaking", "task_id": 3}},
        {{"time": "19:00-20:00", "task": "Kitob", "task_id": 4}}
    ],
    ...
}}

⚡️ ESLATMA: 
- Har bir vazifani HAFTADA KO'P MARTA takrorlang
- Bir kunga hammani yig'mang, xilma-xillik yarating!
- Faqat {work_end} dan keyingi vaqtga joylashtiring

FAQAT JSON javob bering, boshqa TEXT YO'Q!
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
    Aqlli algoritm bilan jadval tuzish (AI ishlamasa)
    Har kunga har xil vazifalarni taqsimlaydi
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
    
    if not tasks:
        return schedule
    
    # Prioritet bo'yicha saralash
    sorted_tasks = sorted(tasks, key=lambda x: x.get('priority', 1), reverse=True)
    
    # Haftaning kunlari
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    
    # Ish vaqtidan keyin boshlanish vaqtini hisoblash
    work_end = constraints.get('work_end_time', '16:00')
    work_end_hour = int(work_end.split(':')[0])
    
    # Mavjud vaqt oralig'i (ishdan keyin)
    start_hour = work_end_hour + 1  # 1 soat dam olish
    
    # Har bir vazifa uchun haftalik necha marta schedule qilish kerak
    task_frequency = {}
    for task in sorted_tasks:
        priority = task.get('priority', 1)
        if priority == 3:
            task_frequency[task['id']] = 5  # Haftada 5 marta
        elif priority == 2:
            task_frequency[task['id']] = 3  # Haftada 3 marta
        else:
            task_frequency[task['id']] = 2  # Haftada 2 marta
    
    # Har bir kun uchun 2-3 ta slot
    daily_slots = [
        f"{start_hour:02d}:00-{start_hour+1:02d}:30",
        f"{start_hour+2:02d}:00-{start_hour+3:02d}:30",
    ]
    
    # Round-robin usulida taqsimlash
    task_assignments = {task['id']: 0 for task in sorted_tasks}  # Har bir vazifa necha marta qo'shilgani
    
    for day_idx, day in enumerate(weekdays):
        # Har kuni 2 ta vazifa
        daily_task_count = 0
        
        for slot in daily_slots:
            if daily_task_count >= 2:
                break
            
            # Eng kam qo'shilgan va frequency'ga yetmagan vazifani topish
            best_task = None
            min_assignments = float('inf')
            
            for task in sorted_tasks:
                task_id = task['id']
                current_assignments = task_assignments[task_id]
                target_frequency = task_frequency[task_id]
                
                # Agar bu vazifa hali target frequency'ga yetmagan bo'lsa
                if current_assignments < target_frequency:
                    # Va eng kam qo'shilgan vazifa bo'lsa
                    if current_assignments < min_assignments:
                        # Va bu vazifa bugungi kundagi birinchi vazifa bilan bir xil bo'lmasa
                        if not schedule[day] or schedule[day][0]['task_id'] != task_id:
                            best_task = task
                            min_assignments = current_assignments
            
            if best_task:
                schedule[day].append({
                    "time": slot,
                    "task": best_task['task_name'],
                    "task_id": best_task['id']
                })
                task_assignments[best_task['id']] += 1
                daily_task_count += 1
    
    # Yakshanba - review va test kuni
    schedule["sunday"] = [
        {"time": "10:00-12:00", "task": "📚 Haftalik Review", "task_id": None},
        {"time": "14:00-16:00", "task": "📖 Yengil o'qish", "task_id": None},
        {"time": "17:00-18:00", "task": "📝 Keyingi hafta plani", "task_id": None}
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
