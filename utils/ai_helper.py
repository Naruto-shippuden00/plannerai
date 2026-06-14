"""
AI Helper - Google Gemini API (100% BEPUL va TEZKOR!)
"""
import os
import google.generativeai as genai
from typing import List, Dict, Optional
import json
import logging
from PIL import Image

logger = logging.getLogger(__name__)

client = None
vision_model = None

def init_ai():
    """AI clientni boshlash - Google Gemini"""
    global client, vision_model
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not found!")
        return False
    
    try:
        genai.configure(api_key=api_key)
        vision_model = genai.GenerativeModel('gemini-1.5-flash')
        client = True
        logger.info("✅ Google Gemini initialized successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini: {e}")
        return False

async def analyze_task_photo(photo_path: str, task_id: int, user_id: int) -> str:
    """
    Vazifa rasmini Google Gemini bilan tahlil qilish
    
    Args:
        photo_path: Rasm fayl yo'li
        task_id: Vazifa ID
        user_id: Foydalanuvchi ID
    
    Returns:
        Tahlil matni
    """
    logger.info(f"🤖 AI analysis started: photo={photo_path}, task_id={task_id}, user_id={user_id}")
    
    if not client or not vision_model:
        logger.error("❌ AI client not initialized!")
        return "⚠️ AI xizmat hozirda mavjud emas.\n\n✅ Rasm qabul qilindi, davom eting!"
    
    try:
        # Vazifa ma'lumotlarini olish
        from utils.database import get_task_by_id
        task_info = None
        task_name = 'vazifa'
        category = ''
        
        try:
            task_info = await get_task_by_id(task_id) if task_id else None
            if task_info:
                task_name = task_info.get('task_name', 'vazifa')
                category = task_info.get('category', '')
            logger.info(f"📋 Task info: name='{task_name}', category='{category}'")
        except Exception as e:
            logger.warning(f"⚠️ Could not get task info: {e}")
        
        # Rasmni yuklash
        logger.info(f"📷 Loading image: {photo_path}")
        
        try:
            img = Image.open(photo_path)
            logger.info(f"✅ Image loaded: size={img.size}, mode={img.mode}")
        except Exception as e:
            logger.error(f"❌ Image loading failed: {e}")
            return "⚠️ Rasmni o'qishda xatolik yuz berdi.\n\n✅ Lekin rasm qabul qilindi, davom eting!"
        
        prompt = f"""
Siz o'quvchilarni motivatsiya qiluvchi AI yordamchisisiz. 

Vazifa: {task_name}
Kategoriya: {category}

Rasmni tahlil qilib, quyidagilarni baholang:

1. **Nima qilindi?** (qisqacha, 1-2 jumla)
2. **Sifat darajasi** (1-10 ball)
3. **Qisqa tavsiya** (1 jumla, ijobiy)

MUHIM:
- O'zbek tilida yozing
- Juda qisqa va aniq bo'ling (maksimal 4 jumla)
- Motivatsiya bering, tanqid qilmang
- Agar rasm vazifaga mos bo'lmasa ham ijobiy yozing

Format:
📸 [Nima ko'rsatilgan]
⭐️ Baho: [X/10]
💡 [Qisqa tavsiya]
"""
        
        logger.info("🚀 Calling Google Gemini Vision API...")
        
        # Gemini API chaqirish
        response = vision_model.generate_content([prompt, img])
        
        if not response or not response.text:
            logger.error("❌ Empty response from Gemini")
            return "⚠️ AI javob bermadi.\n\n✅ Rasm qabul qilindi, davom eting!"
        
        analysis = response.text.strip()
        logger.info(f"✅ AI analysis completed: {len(analysis)} chars")
        logger.info(f"📝 Analysis result: {analysis[:100]}...")
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ AI photo analysis error: {e}", exc_info=True)
        
        # Fallback - oddiy javob
        return f"""📸 Rasm qabul qilindi!
⭐️ Baho: 7/10
💡 Ajoyib! Davom eting, siz zo'r ishlayapsiz! 💪

⚠️ AI tahlil: Texnik xatolik
✅ Rasm saqlandi, fokusda qoling!"""


async def generate_schedule(tasks: List[Dict], constraints: Dict) -> Dict:
    """
    AI yordamida jadval tuzish - Google Gemini
    
    Args:
        tasks: Vazifalar ro'yxati [{"name": "SAT", "duration": 120, "priority": 3, ...}]
        constraints: Cheklovlar {"work_hours": [8, 16], "work_start_time": "08:00", "work_end_time": "16:00", ...}
    
    Returns:
        Jadval: {"monday": [...], "tuesday": [...], ...}
    """
    if not client:
        # Agar AI ishlamasa, oddiy algoritm
        return generate_simple_schedule(tasks, constraints)
    
    try:
        # Gemini text model
        text_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Vaqtlarni olish
        work_start = constraints.get('work_start_time', '08:00')
        work_end = constraints.get('work_end_time', '16:00')
        
        # Vazifalar sonini hisoblash
        task_count = len(tasks)
        
        # Har bir vazifaning ma'lumotlarini tayyorlash
        task_details = ""
        for task in tasks:
            duration_hours = task.get('duration_minutes', 60) / 60
            priority_text = {3: "🔴 Juda muhim", 2: "🟡 O'rtacha", 1: "🟢 Past"}.get(task.get('priority', 1), "🟢 Past")
            task_details += f"\n- {task['task_name']} ({task['category']}) - {duration_hours}h - {priority_text}"
        
        prompt = f"""
Professional time management AI assistant. Sizning vazifangiz - optimal haftalik jadval tuzish.

📋 VAZIFALAR ({task_count} ta):
{task_details}

⚙️ CHEKLOVLAR:
- Ish/Texnikum: {work_start}-{work_end} ❌ (band qilmang!)
- Bo'sh vaqt: {work_end} dan keyin
- Har kunga 2-3 ta vazifa

JSON format:
{{
    "monday": [{{"time": "17:00-18:30", "task": "SAT Math", "task_id": 1}}],
    "tuesday": [...],
    ...
}}

FAQAT JSON javob bering!
"""
        
        response = text_model.generate_content(prompt)
        result = response.text.strip()
        
        # JSON ni extract qilish
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        schedule = json.loads(result)
        return schedule
        
    except Exception as e:
        logger.error(f"AI schedule generation error: {e}")
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
    
    # Har bir kun uchun 2-3 ta slot - DINAMIK HISOBLASH
    # Round-robin usulida taqsimlash
    task_assignments = {task['id']: 0 for task in sorted_tasks}  # Har bir vazifa necha marta qo'shilgani
    
    for day_idx, day in enumerate(weekdays):
        # Har kuni 2 ta vazifa
        daily_task_count = 0
        
        # Har kun uchun boshlanish vaqti
        current_hour = start_hour
        current_minute = 0
        
        while daily_task_count < 2:
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
                # Vazifaning davomiyligini olish (daqiqalarda)
                duration_minutes = best_task.get('duration_minutes', 60)
                
                # Boshlanish vaqti
                start_time_str = f"{current_hour:02d}:{current_minute:02d}"
                
                # Tugash vaqtini hisoblash
                total_end_minutes = current_hour * 60 + current_minute + duration_minutes
                end_hour = (total_end_minutes // 60) % 24
                end_minute = total_end_minutes % 60
                end_time_str = f"{end_hour:02d}:{end_minute:02d}"
                
                time_slot = f"{start_time_str}-{end_time_str}"
                
                schedule[day].append({
                    "time": time_slot,
                    "task": best_task['task_name'],
                    "task_id": best_task['id']
                })
                task_assignments[best_task['id']] += 1
                daily_task_count += 1
                
                # Keyingi vazifa uchun vaqtni yangilash (15 daqiqa tanaffus)
                next_total_minutes = total_end_minutes + 15
                current_hour = (next_total_minutes // 60) % 24
                current_minute = next_total_minutes % 60
                
                # Agar 22:00 dan keyin bo'lsa, to'xtatamiz
                if current_hour >= 22:
                    break
            else:
                break  # Boshqa vazifa yo'q
    
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
