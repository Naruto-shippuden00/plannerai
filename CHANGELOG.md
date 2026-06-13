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
