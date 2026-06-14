# 📝 CHANGELOG

## Version 1.0.1 (2026-06-12) - TIMEZONE FIX 🌍

### 🐛 Muhim Tuzatishlar

#### ⏰ Vaqt Zonasi Muammosi Hal Qilindi
- **MUAMMO**: Bot UTC vaqtida ishlayotgan edi, Tashkent vaqti emas
- **NATIJA**: Noto'g'ri vaqtda bildirishnomalar kelayotgan edi
- **HAL**: Barcha datetime operatsiyalari uchun `Asia/Tashkent` timezone qo'shildi

#### 📅 Kun Hisoblash Xatosi Tuzatildi
- **MUAMMO**: Shanba kuni juma deb ko'rsatilayotgan edi
- **SABAB**: Server vaqti va Tashkent vaqti farqi tufayli
- **HAL**: `datetime.now(TASHKENT_TZ)` ishlatilmoqda

#### 🔧 Tuzatilgan Fayllar
```python
utils/scheduler.py
- datetime.now() → datetime.now(TASHKENT_TZ)
- Hafta kunlari nomlari logga qo'shildi

utils/database.py  
- Barcha datetime.now() → datetime.now(TASHKENT_TZ)
- zoneinfo.ZoneInfo import qilindi

handlers/schedule.py
- Bugungi kunni to'g'ri aniqlash
- Jadval ko'rsatishda "BUGUN" belgisi

handlers/reminders.py
- Rasm fayl nomlari uchun Tashkent vaqti
- Completion vaqtlari to'g'rilandi
```

#### 📦 Yangi Dependencies
- `tzdata>=2024.1` - Timezone ma'lumotlari (Python 3.9+)

#### ✅ Test Script
- `test_timezone.py` - Vaqt zonasi tekshirish skripti
- Server va Tashkent vaqtini solishtirish
- Debug uchun kun nomlarini ko'rsatish

### 🎯 Endi Ishlaydi
- ✅ Vazifalar aniq vaqtida boshlanadi (Tashkent vaqti)
- ✅ Kun to'g'ri ko'rsatiladi (shanba shanba deb ko'rsatiladi)
- ✅ Bildirishnomalar to'g'ri vaqtda keladi
- ✅ Juma kuni vazifalar juma kuni boshlanadi, kechqurun emas!

### 📝 Qo'shimcha Ma'lumotlar
**MUHIM**: Agar sizning serveringiz boshqa vaqt zonasida bo'lsa (masalan, AWS US-East), endi bot to'g'ri Tashkent vaqtida ishlaydi!

**Misol**:
- Juma 17:00 da vazifa rejalashtirilgan
- Bot 17:00 (Tashkent) da aniq bildirishnoma yuboradi
- Juma kuni 17:00-19:30 oralig'ida vazifalar bor
- Kechqurun 21:00, 22:00, 23:00 da EMAS!

---

## Version 1.0.0 (2026-06-11)

### ✨ Yangi xususiyatlar

#### 🤖 AI Planner
- Groq AI integratsiyasi (bepul!)
- Vazifalar asosida optimal jadval tuzish
- Prioritet va davomiylik hisobga olish
- Texnikum/ish vaqti avtomatik hisoblanadi
- Fallback algorithm (AI ishlamasa)

#### ⏰ Smart Reminders
- APScheduler bilan avtomatik eslatmalar
- Har 15 daqiqada jadval tekshirish
- Vazifa vaqtida bildrishnoma
- Rasm yuborish va tekshirish
- 30 daqiqaga kechiktrish
- Ertalabki motivatsiya (har kuni 07:00)

#### 📊 Progress Tracking
- Haftalik statistika
- Kategoriyalar bo'yicha tahlil
- Matplotlib bilan grafiklar
- Progress bar va foiz ko'rsatkichlari
- Yutuqlar tizimi
- Completion rate tracking

#### ✅ Weekly Assessment
- Shanba kuni avtomatik test eslatmasi
- AI tomonidan test savollari generatsiyasi
- Ko'p variantli savollar
- Avtomatik tekshirish va baholash
- Yakshanba kuni haftalik hisobot
- AI tahlil va tavsiyalar

#### 📱 Telegram Interface
- Intuitive keyboard menu
- Inline keyboards
- FSM (Finite State Machine)
- Callback handlers
- Photo upload va saqlash

### 🗄️ Database
- SQLite database
- Asinxron operations (aiosqlite)
- Tables: users, tasks, schedule, completions, weekly_tests
- Efficient queries va indexing

### 🛠️ Technical Stack
- Python 3.8+
- aiogram 3.4+ (Telegram Bot API)
- Groq API (LLM)
- APScheduler (task scheduling)
- Matplotlib (data visualization)
- SQLite (database)

### 📚 Documentation
- README.md (English + Uzbek)
- QOLLANMA_UZ.md (Quick Start Uzbek)
- CHANGELOG.md
- Inline comments
- Docstrings

### 🎨 Features
- O'zbek tili support
- Emoji va vizual elementlar
- User-friendly interface
- Error handling
- Logging

---

## Kelajak rejalar (v2.0.0)

### Rejalashtirilgan xususiyatlar:
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Export to PDF/Excel
- [ ] Multiple users support
- [ ] Team collaboration
- [ ] Pomodoro timer integration
- [ ] Voice commands
- [ ] More AI models (local LLM)
- [ ] Mobile app
- [ ] Backup/restore
- [ ] Cloud sync

### Yaxshilanishlar:
- [ ] Better error messages
- [ ] More test coverage
- [ ] Performance optimization
- [ ] Advanced analytics
- [ ] Custom themes
- [ ] Notification sounds

---

## Bug Fixes

### v1.0.0
- Barcha asosiy xususiyatlar ishlaydi
- Known issues yo'q
- Beta testing muvaffaqiyatli

---

## Migration Notes

### v1.0.0
- Initial release
- Migration kerak emas

---

**Keyingi versiya:** v1.1.0 (TBD)



---

## Version 2.0.0 (2026-06-14) - MULTI-LANGUAGE & AI VISION 🌐🤖

### 🌍 Ko'p Tillilik / Multi-Language Support

#### ✨ Yangi Imkoniyatlar
- **3 ta til qo'llab-quvvatlanadi:**
  - 🇺🇿 O'zbek (Uzbek)
  - 🇷🇺 Русский (Russian)
  - 🇬🇧 English (English)

#### 📁 Yangi Fayllar
- `utils/translations.py` - Barcha matnlarning tarjimalari
- `LANGUAGE_AND_AI_VISION_UPDATE.md` - To'liq dokumentatsiya

#### 🔧 O'zgartirilgan Fayllar
```python
handlers/start.py
- Birinchi /start da til tanlash
- language_selection_keyboard() qo'shildi
- /language buyrug'i qo'shildi
- Barcha xabarlar translations orqali

utils/keyboards.py
- Barcha keyboard funksiyalari language parametri qo'shildi
- language_selection_keyboard() yaratildi
- Tugmalar tarjimaga bog'landi

utils/database.py
- get_user_language() funksiya
- set_user_language() funksiya
- update_user_timezone() funksiya
- get_notification_settings() funksiya
- update_notification_settings() funksiya

handlers/settings.py
- Til o'zgartirish sozlamasi qo'shildi
- change_language callback handler
- Bildirishnoma sozlamalari
```

#### 🎨 Til Tanlash Oqimi
1. Foydalanuvchi /start bosadi
2. Til tanlash tugmalari ko'rsatiladi
3. Til tanlanadi va saqlana di
4. Barcha xabarlar o'sha tilda

---

### 🤖 AI Vision Rasm Tahlili

#### ✨ Yangi Imkoniyatlar
- **Rasmlarni Tekshirish va Tasdiqlash:**
  - ✅ AI rasm vazifaga mos ekanligini tekshiradi
  - ❌ Vazifaga mos bo'lmagan rasmlar rad etiladi
  - 🔄 Rad etilganda bildirishnomalar qayta boshlanadi

#### 🔍 AI Tahlil Mexanizmi
```python
# Image Captioning
Model: Salesforce/blip-image-captioning-large
Vazifa: Rasmda nima borligini aniqlash

# Task Relevance Check
Kategoriya bo'yicha kalit so'zlar tekshiriladi
Ishonch darajasi (confidence) hisoblanadi
is_valid: True/False qaytariladi
```

#### 📊 Qabul Qilinadigan Rasmlar
- 📚 Dars jarayoni (book, notebook, paper, study)
- 💻 Kompyuter ekrani (computer, screen, laptop)
- 📝 Yozish (writing, desk)
- 🏋️ Gym (exercise, workout, fitness)

#### ❌ Rad Etiladigan Rasmlar
- 🤳 Selfie (face, person, people)
- 🍔 Ovqat (food, meal, eating)
- 🌳 Tabiat (outdoor, nature, tree)
- 🚗 Transport (car, vehicle)
- 🐕 Hayvonlar (pet, dog, cat)

#### 🔧 O'zgartirilgan Fayllar
```python
utils/ai_helper.py
- analyze_task_photo() qayta yozildi
- Dict qaytaradi: {is_valid, message, confidence}
- _check_task_relevance() funksiya qo'shildi
- _format_success_message() funksiya qo'shildi
- Ko'p tilli xabarlar

handlers/focus_keeper.py
- AI tahlil natijasiga qarab rasm qabul/rad
- Rad etilganda bildirishnomalar qayta boshlanadi
- Foydalanuvchi tiliga mos xabarlar
- Rad etilgan rasmlar o'chiriladi
```

#### 🎯 AI Vision Oqimi
1. Foydalanuvchi rasm yuboradi
2. AI rasm tahlil qiladi (caption)
3. Vazifaga mosligini tekshiradi
4. Natija:
   - ✅ Qabul: Timer boshlanadi
   - ❌ Rad: Bildirishnomalar davom etadi

---

### 📦 Yangi Dependencies
```txt
# Mavjud paketlar:
aiogram>=3.4.1,<3.10
aiosqlite>=0.19.0
requests>=2.31.0
python-dotenv>=1.0.0

# HUGGINGFACE_API_KEY .env ga qo'shilishi kerak!
```

---

### 🔐 Environment Variables
```env
# .env.example yangilandi:
BOT_TOKEN=your_bot_token_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here  # YANGI!
GROQ_API_KEY=your_groq_api_key_here  # OPTIONAL
ADMIN_USER_ID=your_telegram_id
```

---

### 📊 Database O'zgarishlar

#### Yangi Ustunlar
```sql
-- Users jadvali
ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'uz';

-- Avtomatik migratsiya mavjud foydalanuvchilar uchun
```

---

### ✅ Test Qilingan

#### Til Tanlash
- [x] /start da til tanlash
- [x] Barcha xabarlar to'g'ri tilda
- [x] Tugmalar tarjima qilingan
- [x] /language bilan o'zgartirish
- [x] Sozlamalarda til o'zgartirish

#### AI Vision
- [x] Task-related rasmlar qabul qilinadi
- [x] Non-task rasmlar rad etiladi
- [x] Bildirishnomalar qayta boshlanadi
- [x] Xabarlar foydalanuvchi tilida
- [x] Rad etilgan rasmlar o'chiriladi
- [x] Confidence score hisoblanadi

---

### 🐛 Ma'lum Muammolar

1. **AI Model Loading (503)**
   - Birinchi chaqiriqda model yuklanishi kerak
   - 20-30 soniya kutish kerak
   - Keyingi chaqiriqlar tez

2. **False Positives/Negatives**
   - Ba'zan noto'g'ri qaror qabul qilishi mumkin
   - Xatolikdan foydalanuvchini himoya qilish uchun
   - Kelajakda yaxshilanadi

---

### 📝 Qo'shimcha Dokumentatsiya

To'liq ma'lumot uchun:
- `LANGUAGE_AND_AI_VISION_UPDATE.md` - Batafsil dokumentatsiya
- Til tanlash va AI vision test qilish bo'yicha yo'riqnoma
- Texnik tafsilotlar va API ma'lumotlari

---

### 🎉 Nima Yaxshilandi?

#### Foydalanuvchi Tajribasi
- ✅ Har kim o'z tilida ishlata oladi
- ✅ AI rasmlarni tekshiradi (haqiqiy task ekanligini)
- ✅ Xatolar kamaydi (noto'g'ri rasmlar rad etiladi)
- ✅ Focus session samaraliroq

#### Developer Experience
- ✅ Oson tarjima tizimi (translations.py)
- ✅ Yaxshi strukturalangan kod
- ✅ Yangi tillar qo'shish oson
- ✅ AI tahlil kengaytirilishi mumkin

---

### 🚀 Keyingi Versiya Rejalari (v2.1.0)

1. **Ko'proq Tillar:**
   - 🇹🇷 Turkcha
   - 🇩🇪 Nemischa
   - 🇫🇷 Frantsuzcha

2. **AI Vision Yaxshilash:**
   - Yanada aniqroq model
   - Video tahlil
   - Real-time monitoring

3. **Ko'proq Tarjimalar:**
   - Barcha handlers
   - Error xabarlar
   - Statistika sahifalari

---

**🎊 Version 2.0.0 - Katta Yangilanish!** 🌐🤖
