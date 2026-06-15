"""
AI Helper - Hugging Face Inference API (100% BEPUL, yosh chegarasi yo'q!)
"""
import os
import requests
import base64
from typing import List, Dict, Optional
import json
import logging
from PIL import Image

logger = logging.getLogger(__name__)

client = None
HF_API_URL = "https://api-inference.huggingface.co/models/"
HF_API_KEY = None

def init_ai():
    """AI clientni boshlash - Hugging Face"""
    global client, HF_API_KEY
    HF_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    
    if not HF_API_KEY:
        logger.error("❌ HUGGINGFACE_API_KEY not found!")
        return False
    
    try:
        # Test request
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        response = requests.get("https://huggingface.co/api/whoami-v2", headers=headers, timeout=5)
        
        if response.status_code == 200:
            client = True
            logger.info("✅ Hugging Face API initialized successfully!")
            return True
        else:
            logger.error(f"❌ Hugging Face API error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to initialize Hugging Face: {e}")
        return False

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Rasmni base64 ga o'girish"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Image encoding error: {e}")
        return None

async def analyze_task_photo(photo_path: str, task_id: int, user_id: int, language: str = "uz") -> dict:
    """
    Vazifa rasmini Hugging Face Vision bilan tahlil qilish va tasdiqlash
    
    Uses: Salesforce/blip-image-captioning-large + vikhyatk/moondream2
    
    Args:
        photo_path: Rasm fayl yo'li
        task_id: Vazifa ID
        user_id: Foydalanuvchi ID
        language: Til kodi (uz/ru/en)
    
    Returns:
        dict: {
            "is_valid": bool,  # Rasm vazifaga mos ekanligini ko'rsatadi
            "message": str,    # Foydalanuvchiga ko'rsatiladigan xabar
            "confidence": float  # Ishonch darajasi (0-1)
        }
    """
    logger.info(f"🤖 AI analysis started: photo={photo_path}, task_id={task_id}, user_id={user_id}, lang={language}")
    
    # Translations import
    from utils.translations import get_text
    
    # HUGGINGFACE_API_KEY tekshirish
    if not HF_API_KEY or HF_API_KEY == 'your_huggingface_api_key_here':
        logger.warning("⚠️ HUGGINGFACE_API_KEY not configured - skipping AI analysis")
        
        # Vazifa ma'lumotlarini olish
        from utils.database import get_task_by_id
        task_info = None
        task_name = 'vazifa'
        category = ''
        
        try:
            task_info = await get_task_by_id(task_id, user_id) if task_id else None
            if task_info:
                task_name = task_info.get('task_name', 'vazifa')
                category = task_info.get('category', '')
        except Exception as e:
            logger.warning(f"⚠️ Could not get task info: {e}")
        
        # API key bo'lmasa, oddiy success message
        simple_message = {
            "uz": f"📸 Rasm qabul qilindi!\n\n⭐️ Baho: 8/10\n\n💡 \"{task_name}\" vazifasi bo'yicha ajoyib! Davom eting! 💪\n\n✅ Fokusda qoling va muvaffaqiyatga erishing!",
            "ru": f"📸 Фото принято!\n\n⭐️ Оценка: 8/10\n\n💡 Отлично по задаче \"{task_name}\"! Продолжайте! 💪\n\n✅ Оставайтесь в фокусе и достигайте успеха!",
            "en": f"📸 Photo accepted!\n\n⭐️ Rating: 8/10\n\n💡 Great work on \"{task_name}\"! Keep going! 💪\n\n✅ Stay focused and achieve success!"
        }
        
        return {
            "is_valid": True,
            "message": simple_message.get(language, simple_message["uz"]),
            "confidence": 0.8
        }
    
    if not client:
        logger.error("❌ AI client not initialized!")
        return {
            "is_valid": True,  # Xatolik bo'lsa, rasm qabul qilamiz
            "message": get_text("ai_technical_error", language),
            "confidence": 0.5
        }
    
    try:
        # Vazifa ma'lumotlarini olish
        from utils.database import get_task_by_id
        task_info = None
        task_name = 'vazifa'
        category = ''
        
        try:
            task_info = await get_task_by_id(task_id, user_id) if task_id else None
            if task_info:
                task_name = task_info.get('task_name', 'vazifa')
                category = task_info.get('category', '')
            logger.info(f"📋 Task info: name='{task_name}', category='{category}'")
        except Exception as e:
            logger.warning(f"⚠️ Could not get task info: {e}")
        
        # Rasmni yuklash
        logger.info(f"📷 Loading image: {photo_path}")
        
        try:
            with open(photo_path, "rb") as f:
                image_data = f.read()
            logger.info(f"✅ Image loaded: {len(image_data)} bytes")
        except Exception as e:
            logger.error(f"❌ Image loading failed: {e}")
            return {
                "is_valid": True,
                "message": get_text("ai_technical_error", language),
                "confidence": 0.5
            }
        
        # STEP 1: Image Captioning - rasmda nima borligini aniqlash
        API_URL_CAPTION = HF_API_URL + "Salesforce/blip-image-captioning-large"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        
        logger.info("🚀 Step 1: Calling Image Captioning API...")
        
        caption = ""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.post(API_URL_CAPTION, headers=headers, data=image_data, timeout=30)
            )
            
            logger.info(f"📡 API Response: status={response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Caption ni olish
                if isinstance(result, list) and len(result) > 0:
                    caption = result[0].get('generated_text', '').lower()
                else:
                    caption = result.get('generated_text', '').lower()
                
                logger.info(f"✅ Image caption: {caption}")
            elif response.status_code == 503:
                logger.warning(f"⚠️ Model loading (503) - accepting photo by default")
                return {
                    "is_valid": True,
                    "message": _format_success_message(task_name, category, "model loading", language),
                    "confidence": 0.6
                }
            else:
                logger.warning(f"⚠️ Captioning failed: {response.status_code}, response: {response.text[:200]}")
                # Captioning ishlamasa, rasmni qabul qilamiz
                return {
                    "is_valid": True,
                    "message": _format_success_message(task_name, category, caption, language),
                    "confidence": 0.6
                }
        except Exception as e:
            logger.error(f"❌ Captioning error: {e}", exc_info=True)
            return {
                "is_valid": True,
                "message": get_text("ai_technical_error", language),
                "confidence": 0.5
            }
        
        # STEP 2: Task relevance check - vazifaga mos ekanligini tekshirish
        logger.info("🔍 Step 2: Checking task relevance...")
        
        is_valid, confidence = _check_task_relevance(caption, task_name, category)
        
        logger.info(f"📊 Validation result: is_valid={is_valid}, confidence={confidence:.2f}")
        
        if not is_valid:
            # Rasm vazifaga mos emas
            logger.warning(f"❌ Photo rejected: caption='{caption}', task='{task_name}', category='{category}'")
            return {
                "is_valid": False,
                "message": get_text("photo_not_task_related", language),
                "confidence": confidence
            }
        else:
            # Rasm qabul qilindi
            logger.info(f"✅ Photo accepted: caption='{caption}'")
            return {
                "is_valid": True,
                "message": _format_success_message(task_name, category, caption, language),
                "confidence": confidence
            }
        
    except Exception as e:
        logger.error(f"❌ AI photo analysis error: {e}", exc_info=True)
        
        # Xatolik bo'lsa, rasmni qabul qilamiz (false negative oldini olish uchun)
        return {
            "is_valid": True,
            "message": get_text("ai_technical_error", language),
            "confidence": 0.5
        }

def _check_task_relevance(caption: str, task_name: str, category: str) -> tuple:
    """
    Rasmning vazifaga mos ekanligini tekshirish
    
    Args:
        caption: AI tomonidan yaratilgan rasm tavsifi
        task_name: Vazifa nomi
        category: Vazifa kategoriyasi
    
    Returns:
        tuple: (is_valid: bool, confidence: float)
    """
    # Vazifaga mos kalit so'zlar
    task_related_keywords = {
        "SAT": ["book", "notebook", "paper", "writing", "study", "desk", "computer", "screen", "math", "test", "exam", "reading"],
        "IELTS": ["book", "notebook", "paper", "writing", "study", "desk", "computer", "screen", "speaking", "listening", "reading"],
        "Python": ["computer", "screen", "laptop", "code", "programming", "keyboard", "monitor", "desk", "notebook", "terminal"],
        "Startup": ["computer", "screen", "laptop", "desk", "notebook", "paper", "meeting", "presentation", "whiteboard"],
        "Gym": ["gym", "exercise", "workout", "fitness", "training", "dumbbell", "barbell", "machine", "equipment"],
        "Kitob": ["book", "reading", "page", "desk", "notebook", "paper"],
        "Book": ["book", "reading", "page", "desk", "notebook", "paper"]
    }
    
    # Vazifaga mos bo'lmagan kalit so'zlar (selfie, food, etc.)
    non_task_keywords = [
        "selfie", "face", "person", "people", "man", "woman", "boy", "girl",
        "food", "meal", "eating", "drink", "coffee", "tea",
        "outdoor", "nature", "tree", "sky", "cloud", "sunset",
        "car", "vehicle", "road", "street",
        "pet", "dog", "cat", "animal",
        "building", "architecture",
        "phone", "smartphone", "mobile"  # Telefon rasmlar (agar faqat telefon ko'rinsa)
    ]
    
    caption_lower = caption.lower()
    
    # 1. Avval non-task keywords tekshirish
    non_task_count = sum(1 for keyword in non_task_keywords if keyword in caption_lower)
    
    if non_task_count >= 2:
        # Agar 2 yoki ko'proq non-task keyword bo'lsa, rad etamiz
        logger.info(f"❌ Rejected: {non_task_count} non-task keywords found")
        return False, 0.8
    
    # 2. Kategoriyaga mos keywords tekshirish
    category_keywords = task_related_keywords.get(category, [])
    
    # Default keywords (agar kategoriya topilmasa)
    if not category_keywords:
        category_keywords = ["book", "notebook", "paper", "study", "desk", "computer", "screen", "writing"]
    
    # Keywords topish
    found_keywords = [kw for kw in category_keywords if kw in caption_lower]
    
    if len(found_keywords) >= 1:
        # Kamida 1 ta task-related keyword bor
        confidence = min(0.6 + (len(found_keywords) * 0.1), 0.95)
        logger.info(f"✅ Accepted: Found keywords: {found_keywords}")
        return True, confidence
    
    # 3. Task name bilan mos kelish tekshirish
    task_words = task_name.lower().split()
    task_match = any(word in caption_lower for word in task_words if len(word) > 3)
    
    if task_match:
        logger.info(f"✅ Accepted: Task name match")
        return True, 0.7
    
    # 4. Agar hech narsa topilmasa
    # Lekin non-task keywords ham yo'q bo'lsa, qabul qilamiz (false negative oldini olish)
    if non_task_count == 0:
        logger.info(f"⚠️ Cautiously accepted: No clear indicators")
        return True, 0.5
    
    # 5. Aks holda rad etamiz
    logger.info(f"❌ Rejected: No task-related keywords found")
    return False, 0.6

def _format_success_message(task_name: str, category: str, caption: str, language: str) -> str:
    """
    Muvaffaqiyatli tahlil xabarini formatlash
    
    Args:
        task_name: Vazifa nomi
        category: Kategoriya
        caption: AI caption
        language: Til kodi
    
    Returns:
        Formatlangan xabar
    """
    # Caption ni o'zbek/rus/inglizga tarjima qilish (soddalashtirilgan)
    caption_display = caption[:100] if caption else "Vazifa rasmi"
    
    # Til bo'yicha xabarlar
    if language == "uz":
        return f"""📸 **Nima ko'rsatilgan:** {caption_display}

⭐️ **Baho:** 9/10 - Ajoyib!

💡 **Tavsiya:** "{task_name}" vazifasi bo'yicha zo'r ish! Davom eting, siz juda yaxshi ishlayapsiz! 💪

✅ Fokusda qoling va muvaffaqiyatga erishing!"""
    elif language == "ru":
        return f"""📸 **Что показано:** {caption_display}

⭐️ **Оценка:** 9/10 - Отлично!

💡 **Рекомендация:** Отличная работа по задаче "{task_name}"! Продолжайте, вы очень хорошо работаете! 💪

✅ Оставайтесь в фокусе и достигайте успеха!"""
    else:  # en
        return f"""📸 **What's shown:** {caption_display}

⭐️ **Rating:** 9/10 - Excellent!

💡 **Recommendation:** Great work on task "{task_name}"! Keep going, you're doing very well! 💪

✅ Stay focused and achieve success!"""


async def generate_schedule(tasks: List[Dict], constraints: Dict) -> Dict:
    """
    AI yordamida jadval tuzish - Hugging Face text model
    
    Args:
        tasks: Vazifalar ro'yxati
        constraints: Cheklovlar
    
    Returns:
        Jadval: {"monday": [...], "tuesday": [...], ...}
    """
    if not client or not HF_API_KEY:
        return generate_simple_schedule(tasks, constraints)
    
    try:
        # Hugging Face text generation model
        API_URL = HF_API_URL + "microsoft/Phi-3-mini-4k-instruct"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        
        work_start = constraints.get('work_start_time', '08:00')
        work_end = constraints.get('work_end_time', '16:00')
        task_count = len(tasks)
        
        task_details = ""
        for task in tasks:
            duration_hours = task.get('duration_minutes', 60) / 60
            priority_text = {3: "Muhim", 2: "O'rtacha", 1: "Past"}.get(task.get('priority', 1), "Past")
            task_details += f"\n- {task['task_name']} ({task['category']}) - {duration_hours}h - {priority_text}"
        
        prompt = f"""Create weekly schedule JSON.

Tasks ({task_count}):
{task_details}

Rules:
- Work hours: {work_start}-{work_end} (don't schedule)
- Free time: after {work_end} until 22:00
- Schedule as many tasks as fit until 22:00 each day
- Add 15 min break between tasks
- Don't exceed 22:00
- Balance tasks by priority each day: 2-3 High, 1-2 Medium, 0-1 Low
- Mix categories each day (don't schedule same category consecutively)
- Distribute tasks randomly across days

JSON format:
{{"monday": [{{"time": "17:00-18:30", "task": "Task name", "task_id": 1}}], ...}}

Return ONLY JSON, no text!"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            text = result[0]['generated_text'] if isinstance(result, list) else result.get('generated_text', '')
            
            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            schedule = json.loads(text)
            return schedule
        else:
            logger.error(f"Schedule generation error: {response.status_code}")
            return generate_simple_schedule(tasks, constraints)
            
    except Exception as e:
        logger.error(f"AI schedule generation error: {e}")
        return generate_simple_schedule(tasks, constraints)

def generate_simple_schedule(tasks: List[Dict], constraints: Dict) -> Dict:
    """
    Aqlli algoritm bilan jadval tuzish (AI ishlamasa)
    Har kunga 22:00 gacha qancha vazifa sig'sa shuncha taqsimlaydi
    Vazifalarni kategoriya va prioritet bo'yicha balanslangan tarzda taqsimlaydi
    """
    import random
    
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
    
    # Vazifalarni prioritet bo'yicha guruhlash
    high_priority_tasks = [t for t in tasks if t.get('priority', 1) == 3]
    medium_priority_tasks = [t for t in tasks if t.get('priority', 1) == 2]
    low_priority_tasks = [t for t in tasks if t.get('priority', 1) == 1]
    
    # Har bir prioritet guruhini kategoriya bo'yicha guruhlash
    def group_by_category(task_list):
        categories = {}
        for task in task_list:
            cat = task.get('category', 'Other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(task)
        return categories
    
    high_by_cat = group_by_category(high_priority_tasks)
    medium_by_cat = group_by_category(medium_priority_tasks)
    low_by_cat = group_by_category(low_priority_tasks)
    
    logger.info(f"📊 Tasks grouped: High={len(high_priority_tasks)}, Medium={len(medium_priority_tasks)}, Low={len(low_priority_tasks)}")
    logger.info(f"📊 Categories: High={list(high_by_cat.keys())}, Medium={list(medium_by_cat.keys())}, Low={list(low_by_cat.keys())}")
    
    # Haftaning kunlari
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    
    # Ish vaqtidan keyin boshlanish vaqtini hisoblash
    work_end = constraints.get('work_end_time', '16:00')
    work_end_hour = int(work_end.split(':')[0])
    
    # Mavjud vaqt oralig'i (ishdan keyin)
    start_hour = work_end_hour + 1  # 1 soat dam olish
    
    # 22:00 ga qadar ishlash
    end_hour_limit = 22
    
    # Har bir vazifa qancha marta schedule qilinganini kuzatish
    task_assignments = {task['id']: 0 for task in tasks}
    
    # Har bir vazifa uchun haftalik necha marta schedule qilish kerak
    task_frequency = {}
    for task in tasks:
        priority = task.get('priority', 1)
        if priority == 3:
            task_frequency[task['id']] = 5  # Haftada 5 marta
        elif priority == 2:
            task_frequency[task['id']] = 3  # Haftada 3 marta
        else:
            task_frequency[task['id']] = 2  # Haftada 2 marta
    
    # Har bir kun uchun jadval tuzish
    for day_idx, day in enumerate(weekdays):
        current_hour = start_hour
        current_minute = 0
        
        # Bugungi kun uchun qo'shilgan kategoriyalar va vazifalar
        daily_categories_used = []
        daily_priority_count = {3: 0, 2: 0, 1: 0}  # Har bir prioritetdan qancha qo'shilgan
        
        logger.info(f"\n📅 Planning {day}...")
        
        # 22:00 gacha qancha vazifa sig'sa shuncha qo'yamiz
        while current_hour < end_hour_limit:
            # Ushbu kun uchun eng mos vazifani tanlash
            best_task = None
            
            # Strategiya: Prioritetlarni balansli taqsimlash
            # 1. Avval high priority vazifalarni qo'shamiz (agar kam bo'lsa)
            # 2. Keyin medium priority
            # 3. So'ngra low priority
            
            # Qaysi prioritet guruhidan vazifa tanlashni aniqlash
            candidate_tasks = []
            
            # High priority vazifalar (eng ko'p 2-3 ta kuniga)
            if daily_priority_count[3] < 3:
                for cat, cat_tasks in high_by_cat.items():
                    # Kategoriya takrorlanmasin (yoki kam takrorlansa)
                    if daily_categories_used.count(cat) < 2:
                        for task in cat_tasks:
                            if task_assignments[task['id']] < task_frequency[task['id']]:
                                candidate_tasks.append((task, 3, cat))  # (task, priority, category)
            
            # Medium priority vazifalar (kuniga 1-2 ta)
            if daily_priority_count[2] < 2:
                for cat, cat_tasks in medium_by_cat.items():
                    if daily_categories_used.count(cat) < 2:
                        for task in cat_tasks:
                            if task_assignments[task['id']] < task_frequency[task['id']]:
                                candidate_tasks.append((task, 2, cat))
            
            # Low priority vazifalar (kuniga 0-1 ta)
            if daily_priority_count[1] < 1:
                for cat, cat_tasks in low_by_cat.items():
                    if daily_categories_used.count(cat) < 1:
                        for task in cat_tasks:
                            if task_assignments[task['id']] < task_frequency[task['id']]:
                                candidate_tasks.append((task, 1, cat))
            
            # Agar kandidat vazifalar bo'lmasa, boshqa strategiyani sinab ko'ramiz
            if not candidate_tasks:
                # Barcha vazifalardan eng kam qo'shilganini topamiz
                for task in tasks:
                    if task_assignments[task['id']] < task_frequency[task['id']]:
                        # Bugungi oxirgi vazifa bilan bir xil bo'lmasin
                        if not schedule[day] or schedule[day][-1]['task_id'] != task['id']:
                            candidate_tasks.append((task, task.get('priority', 1), task.get('category', 'Other')))
            
            # Kandidatlar ichidan random tanlash (diversity uchun)
            if candidate_tasks:
                # Prioritet bo'yicha saralash (yuqori prioritetni afzal ko'ramiz)
                candidate_tasks.sort(key=lambda x: (x[1], task_frequency[x[0]['id']] - task_assignments[x[0]['id']]), reverse=True)
                
                # Top 3 kandidatdan random birini tanlaymiz (diversity)
                top_candidates = candidate_tasks[:min(3, len(candidate_tasks))]
                best_task, priority, category = random.choice(top_candidates)
                
                # Vazifaning davomiyligini olish (daqiqalarda)
                duration_minutes = best_task.get('duration_minutes', 60)
                
                # Boshlanish vaqti
                start_time_str = f"{current_hour:02d}:{current_minute:02d}"
                
                # Tugash vaqtini hisoblash
                total_end_minutes = current_hour * 60 + current_minute + duration_minutes
                end_hour = (total_end_minutes // 60) % 24
                end_minute = total_end_minutes % 60
                end_time_str = f"{end_hour:02d}:{end_minute:02d}"
                
                # Agar vazifa tugash vaqti 22:00 dan oshib ketsa, qo'shmaymiz
                if end_hour > end_hour_limit or (end_hour == end_hour_limit and end_minute > 0):
                    logger.info(f"⏰ Stopped scheduling for {day}: Would end at {end_time_str}, limit is {end_hour_limit}:00")
                    break
                
                time_slot = f"{start_time_str}-{end_time_str}"
                
                schedule[day].append({
                    "time": time_slot,
                    "task": best_task['task_name'],
                    "task_id": best_task['id'],
                    "category": category,
                    "priority": priority
                })
                task_assignments[best_task['id']] += 1
                daily_categories_used.append(category)
                daily_priority_count[priority] += 1
                
                logger.info(f"✅ {day}: {best_task['task_name']} ({category}, P{priority}) at {time_slot}")
                
                # Keyingi vazifa uchun vaqtni yangilash (15 daqiqa tanaffus)
                next_total_minutes = total_end_minutes + 15
                current_hour = (next_total_minutes // 60) % 24
                current_minute = next_total_minutes % 60
                
                # Agar 22:00 ga yaqinlashsak, to'xtatamiz
                if current_hour >= end_hour_limit:
                    logger.info(f"⏰ Reached time limit for {day}: {current_hour}:00")
                    break
            else:
                # Boshqa vazifa yo'q yoki barcha vazifalar o'z frequency'ga yetdi
                logger.info(f"✅ All tasks scheduled for {day}")
                break
        
        # Kunlik statistika
        logger.info(f"📊 {day} summary: High={daily_priority_count[3]}, Medium={daily_priority_count[2]}, Low={daily_priority_count[1]}")
    
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
