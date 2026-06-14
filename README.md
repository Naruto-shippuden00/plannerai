# 🤖 Productivity Bot - AI Shaxsiy Yordamchi

> Telegram bot - vazifalaringizni boshqarish, AI bilan jadval tuzish, avtomatik eslatmalar va haftalik tahlil!

## 📋 Mundarija

- [Xususiyatlar](#-xususiyatlar)
- [O'rnatish](#-ornatish)
- [Sozlash](#-sozlash)
- [Ishga tushirish](#-ishga-tushirish)
- [Foydalanish](#-foydalanish)
- [Tuzilma](#-tuzilma)
- [Muammolarni hal qilish](#-muammolarni-hal-qilish)

---

## ✨ Xususiyatlar

### 🤖 AI Planner
- Vazifalaringizni tahlil qilib optimal haftalik jadval tuzadi
- Texnikum/ish vaqtingizni avtomatik hisobga oladi
- Prioritet va davomiylikni e'tiborga oladi
- Bepul Groq AI ishlatadi

### 🎯 Focus Mode (YANGI!)
- **Cheksiz bildirishnomalar**: Vazifa vaqti kelganda har 5 minutda eslatma
- **Rasm orqali tasdiqlash**: Faqat rasm yuborish bilan bildirishnoma to'xtaydi
- **🤖 AI Vision Integration**: Yuborilgan rasmlarni avtomatik tahlil qilish
  - Groq Vision API bilan powered
  - Vazifa mos kelishini tekshirish
  - Sifat darajasini baholash (1-10)
  - O'zbek tilida konstruktiv tavsiyalar
- **Pomodoro Timer**: Rasm yuborilgandan keyin AVTOMATIK timer boshlanadi
- **Smart Duration**: Jadval bo'yicha fokus + 10 daqiqa tanaffus + avtomatik davom etish
- **Nazorat tizimi**: Har 15 daqiqada fokus tekshiruvi
- **Kamera integratsiyasi**: Foydalanuvchi ruxsati bilan tasodifiy rasm so'rash

### ⚠️ Jazo Tizimi (YANGI!)
- **Avtomatik jazolar**: Vazifa bajarilmasa yoki rasm yuborilmasa
- **Motivatsion jazolar**: Pushup, meditatsiya, yurish va boshqalar
- **Statistika**: Qaysi xatolar ko'proq takrorlanayotganini ko'rish
- **Tiklash**: Jazolarni bajarish orqali ballingizni tiklash
- **Progressni kuzatish**: Jazo tarixi va natijalar

### 🗑 Vazifalarni Boshqarish (YANGI!)
- **Vazifani o'chirish**: `/remove_vazifa_nomi` buyrug'i bilan
- **Bajarilganlar ro'yxati**: Vazifalar o'chirilmasdan, bajarilgan deb belgilanadi
- **Qayta faollashtirish**: Bajarilgan vazifalarni qayta ishlatish mumkin
- **Boshqaruv paneli**: Barcha vazifalarni bir joydan ko'rish va boshqarish

### ⏰ Smart Reminders
- Har bir vazifa vaqtida avtomatik eslatma
- Focus session avtomatik boshlanadi
- Vazifa tugaganda avtomatik tekshirish
- 30 daqiqaga kechiktirish imkoniyati
- Ertalabki motivatsiya xabarlari

### 📊 Progress Tracking
- Kunlik va haftalik statistika
- Kategoriyalar bo'yicha tahlil
- Grafik va vizual ko'rsatkichlar
- Yutuqlar tizimi

### ✅ Weekly Assessment
- Shanba kuni: o'rganganlar bo'yicha test
- Yakshanba kuni: haftalik hisobot va tahlil
- AI tomonidan maxsus tavsiyalar
- Qaysi mavzularga e'tibor berish kerakligi

---

## 🚀 O'rnatish

### 1. Talablar

- Python 3.8 yoki yuqori
- pip (Python package manager)
- Telegram akkaunti

### 2. Loyihani yuklab olish

```bash
cd productivity-bot
```

### 3. Virtual environment yaratish (ixtiyoriy, lekin tavsiya etiladi)

```bash
python3 -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

---

## 🔧 Sozlash

### 1. Telegram Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ni toping
2. `/newbot` buyrug'ini yuboring
3. Bot uchun ism kiriting (masalan: "My Productivity Bot")
4. Bot uchun username kiriting (masalan: "my_productivity_bot")
5. BotFather sizga **BOT TOKEN** beradi. Buni saqlab qo'ying!

Misol:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789
```

### 2. Groq AI API Key olish (BEPUL! 💰)

1. [groq.com](https://groq.com) saytiga kiring
2. "Sign Up" tugmasini bosing (GitHub yoki Google bilan kiring)
3. Dashboard'ga o'ting
4. "API Keys" bo'limiga o'ting
5. "Create API Key" tugmasini bosing
6. Key nomini kiriting va yarating
7. **API KEY**ni ko'chirib oling va saqlab qo'ying!

### 3. .env fayli yaratish

Loyiha papkasida `.env` fayli yarating:

```bash
cp .env.example .env
```

Keyin `.env` faylini ochib quyidagilarni kiriting:

```env
# Telegram Bot Token (BotFather'dan olgan)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789

# Groq AI API Key (groq.com'dan olgan)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Sizning Telegram User ID (botdan bilib olasiz)
ADMIN_USER_ID=your_telegram_id
```

**DIQQAT:** 
- `BOT_TOKEN` va `GROQ_API_KEY` ni haqiqiy qiymatlar bilan almashtiring!
- `ADMIN_USER_ID` ni hozircha bo'sh qoldiring, keyinroq to'ldiramiz

---

## 🎯 Ishga tushirish

### 1. Botni ishga tushirish

```bash
python bot.py
```

Muvaffaqiyatli ishga tushsa, quyidagi xabarni ko'rasiz:

```
INFO - Database ready!
INFO - AI ready!
INFO - Scheduler started successfully!
INFO - Bot starting...
```

### 2. Telegram'da botni topish

1. Telegram'ni oching
2. Qidiruv qatorida botning username'ini yozing (masalan: @my_productivity_bot)
3. "START" tugmasini bosing yoki `/start` yuboring

### 3. User ID ni olish

Botga `/id` buyrug'ini yuboring. Bot sizga Telegram ID'ingizni ko'rsatadi:

```
Sizning Telegram ID: 123456789

Buni .env fayliga ADMIN_USER_ID sifatida yozing.
```

Bu ID ni `.env` faylidagi `ADMIN_USER_ID` ga yozing va botni qaytadan ishga tushiring:

```bash
# Ctrl+C bilan to'xtating
# .env ni yangilang
# Qayta ishga tushiring
python bot.py
```

---

## 💡 Foydalanish

### Asosiy qadamlar

#### 1. Vazifalar qo'shish

1. "➕ Vazifa qo'shish" tugmasini bosing
2. Vazifa nomini kiriting (masalan: "SAT Math practice")
3. Kategoriyani tanlang (SAT, Python, Kitob va h.k.)
4. Prioritetni belgilang (1-3)
5. Davomiylikni tanlang (30 min, 1 soat va h.k.)

**Maslahat:** Avval barcha vazifalaringizni qo'shing, keyin jadval tuzing!

#### 2. AI bilan jadval tuzish

1. "🤖 AI Jadval" tugmasini bosing
2. AI sizning vazifalaringizni tahlil qiladi
3. Optimal jadval taklif qiladi
4. "✅ Tasdiqlash" tugmasini bosing
5. Tayyor! Endi eslatmalar keladi!

#### 3. Vazifalarni bajarish (Focus Mode)

1. Vazifa vaqti kelganda bot eslatadi
2. **CHEKSIZ BILDIRISHNOMALAR BOSHLANADI!** (har 5 minutda)
3. Bildirishnomani to'xtatish uchun:
   - 📸 Vazifa rasmini yuboring (kitob, dars, mashq daftari va h.k.)
   - 🤖 **AI RASM TAHLIL QILADI**:
     - Nima ko'rsatilgan
     - Vazifaga mos kelishi
     - Sifat darajasi (1-10 ball)
     - Tavsiyalar va motivatsiya
   - ✅ Rasm tasdiqlangandan keyin bildirishnomalar to'xtaydi
4. **⏱ POMODORO TIMER AVTOMATIK BOSHLANDI!**
   - Jadval bo'yicha fokusda ishlaysiz (masalan, 60 daqiqa)
   - Har 15 daqiqada motivatsiya xabarlari
   - Kamera ruxsati bo'lsa, tasodifiy rasm so'raladi
5. Timer tugagandan keyin 10 daqiqa tanaffus
6. Keyingi vazifaga avtomatik o'tish

**MUHIM:** Agar rasm yubormasangiz, bildirishnomalar to'xtamaydi va jazo olasiz!

**AI VISION MISOL:**
```
📸 Nima ko'rsatilgan: SAT Math mashq daftari, algebraik tenglamalar
⭐️ Baho: 8/10
💡 Tavsiya: Ajoyib! Yozuv aniq va tartibli. Davom eting!
```

#### 4. Jazolarni boshqarish

1. "⚠️ Jazolarim" tugmasini bosing
2. Faol jazolaringizni ko'ring
3. Jazoni bajarish uchun `/complete_punishment_ID` yuboring
4. Motivatsion vazifa (pushup, meditatsiya) beriladi
5. Bajargandan keyin `/confirm_punishment_ID` yuboring
6. Ballingiz tiklanadi!

**Jazo turlari:**
- ❌ Vazifani o'tkazib yuborish: 30 min qo'shimcha
- ❌ Rasm yubormaslik: Vazifani qayta bajarish
- ❌ Vazifani erta to'xtatish: 15 min qo'shimcha
- ❌ Kech boshlash: Ogohlantirish

#### 5. Vazifalarni o'chirish

**Usul 1: Buyruq orqali**
```
/remove_SAT Math
/remove_Kitob o'qish  
/remove_Python
```

**Usul 2: Boshqaruv paneli**
1. "🗑 Vazifalarni boshqarish" tugmasini bosing
2. "📝 Faol vazifalar" tanlang
3. Vazifa ID'sini ko'ring
4. `/confirm_remove_ID` buyrug'i bilan tasdiqlang

#### 6. Kamera ruxsati

1. "⚙️ Sozlamalar" > "📸 Kamera sozlamalari"
2. "✅ Ruxsat berish" tugmasini bosing
3. Endi focus vaqtida tasodifiy rasm so'raladi
4. Bu sizning chindan ham ishlayotganingizni tasdiqlaydi
5. Istalgan vaqt "❌ Ruxsatni bekor qilish" mumkin

**Maxfiylik:**
- Rasmlar faqat sizning progressingiz uchun
- Hech kim bilan baham ko'rilmaydi
- Istalgan vaqt o'chirib qo'yishingiz mumkin

#### 4. Statistikani ko'rish

1. "📊 Statistika" tugmasini bosing
2. Haftalik natijalaringizni ko'ring
3. Kategoriyalar bo'yicha grafik
4. Completion rate va yutuqlar

#### 5. Haftalik test

1. Shanba kuni bot test eslatmasini yuboradi
2. Kategoriya tanlang (SAT, Python, Kitob)
3. Savollarga javob bering
4. Natijalaringizni ko'ring va tavsiyalar oling

#### 6. Yakshanba hisobot

1. Yakshanba kuni bot avtomatik hisobot yuboradi
2. Haftalik natijalar va tahlil
3. AI tavsiyalari
4. Keyingi hafta rejasi

---

## 📂 Tuzilma

```
productivity-bot/
├── bot.py                 # Asosiy bot fayli
├── requirements.txt       # Python kutubxonalar
├── .env                   # Konfiguratsiya (maxfiy!)
├── .env.example          # Konfiguratsiya namunasi
├── .gitignore            # Git ignore
├── README.md             # Bu fayl
│
├── handlers/             # Bot handlerlari
│   ├── __init__.py
│   ├── start.py         # Start va yordam
│   ├── tasks.py         # Vazifalar boshqaruvi
│   ├── schedule.py      # Jadval va AI planner
│   ├── reminders.py     # Eslatmalar va completion
│   ├── focus_keeper.py  # Focus mode va Pomodoro (YANGI!)
│   ├── punishments.py   # Jazo tizimi (YANGI!)
│   ├── stats.py         # Statistika va grafik
│   └── tests.py         # Haftalik test tizimi
│
├── utils/               # Yordamchi funksiyalar
│   ├── __init__.py
│   ├── database.py      # SQLite database
│   ├── ai_helper.py     # Groq AI integratsiya
│   ├── scheduler.py     # APScheduler (eslatmalar)
│   └── keyboards.py     # Telegram klaviaturalar
│
└── data/                # Ma'lumotlar
    ├── productivity.db  # Database (avtomatik yaratiladi)
    ├── photos/          # Yuklangan rasmlar (completion)
    ├── focus_photos/    # Focus session rasmlari (YANGI!)
    └── charts/          # Statistika grafiklari
```

---

## 🛠 Muammolarni hal qilish

### Bot ishlamayapti

**Muammo:** Bot ishga tushmayapti

**Yechim:**
```bash
# Kutubxonalarni qayta o'rnatish
pip install -r requirements.txt --upgrade

# Python versiyasini tekshirish
python --version  # 3.8 yoki yuqori bo'lishi kerak
```

### BOT_TOKEN xatosi

**Muammo:** `BOT_TOKEN topilmadi!`

**Yechim:**
1. `.env` fayli loyiha papkasida borligini tekshiring
2. `.env` ichida `BOT_TOKEN=...` to'g'ri yozilganini tekshiring
3. Token BotFather'dan to'g'ri ko'chirilganini tekshiring

### AI ishlamayapti

**Muammo:** AI jadval yoki test ishlamayapti

**Yechim:**
1. `.env` da `GROQ_API_KEY` to'g'ri kiritilganini tekshiring
2. [groq.com](https://groq.com) da API key active ekanini tekshiring
3. Internet connection borligini tekshiring

**Eslatma:** AI ishlamasa ham, bot oddiy algoritm bilan ishlaydi!

### Eslatmalar kelmayapti

**Muammo:** Vazifa vaqti bo'ldi, lekin eslatma yo'q

**Yechim:**
1. Jadval to'g'ri tuzilganini tekshiring ("📅 Jadval")
2. Botni qaytadan ishga tushiring
3. Scheduler loglarini tekshiring

### Database xatosi

**Muammo:** Database bilan bog'liq xatolar

**Yechim:**
```bash
# Database'ni qayta yaratish (DIQQAT: barcha ma'lumotlar o'chadi!)
rm data/productivity.db
python bot.py
```

---

## 🎯 Maslahatlar

### Samarali foydalanish

1. **Har kuni bir xil vaqtda vazifalarni bajaring**
   - Uyquga yotishdan oldin ertangi kunni rejalashtiring
   - Bitta vazifani bajarib bo'lib, darhol belgilang

2. **Prioritetlarni to'g'ri belgilang**
   - 🔴 Juda muhim (3): SAT, IELTS, asosiy vazifalar
   - 🟡 O'rtacha (2): Python, Startup
   - 🟢 Past (1): Qo'shimcha mashg'ulotlar

3. **Rasmlar yuboring!**
   - Bu sizni masʼuliyatli qiladi
   - Keyinchalik qarab chiqish uchun foydali
   - Progress ko'rinadi

4. **Haftalik testlarni o'tkazmang**
   - Bu sizning bilimingizni baholaydi
   - Qaysi mavzularga e'tibor berish kerakligini ko'rsatadi

5. **Motivatsiya xabarlarini o'qing**
   - Bot har kuni motivatsiya beradi
   - Taslim bo'lmang!

---

## 📞 Yordam

Savollar yoki muammolar bo'lsa:

1. README.md ni qaytadan o'qing
2. "Muammolarni hal qilish" bo'limini ko'ring
3. Bot ichida `/help` buyrug'ini kiriting

---

## 🧪 Test Mode (Admin)

Botni tezroq sinash uchun test rejimi:

```bash
# Test rejimini yoqish (faqat admin)
/testmode

# Test bildirishnoma yuborish
/test_reminder

# Rasm yuborish va tizimni kuzatish
# (30 soniya interval, 2 daqiqa timer, 30 soniya tanaffus)

# Test rejimini o'chirish
/testmode
```

**Test Mode sozlamalari:**
- ⏰ Bildirishnoma: 30 soniya (normal: 5 daqiqa)
- ⏱ Pomodoro: 2 daqiqa (normal: jadval bo'yicha)
- 🔔 Tanaffus: 30 soniya (normal: 10 daqiqa)

📄 To'liq qo'llanma: [TEST_MODE_GUIDE.md](TEST_MODE_GUIDE.md)

---

## 🎉 Qo'shimcha Imkoniyatlar

### ✅ Qo'shilgan funksiyalar:

- [x] ~~Pomodoro timer~~ ✅ Qo'shildi! (v2.0)
- [x] ~~Punishment system~~ ✅ Qo'shildi! (v2.0)
- [x] ~~Camera monitoring~~ ✅ Qo'shildi! (v2.0)
- [x] ~~AI Vision Integration~~ ✅ Qo'shildi! (v2.2)
- [x] ~~Auto notification stop~~ ✅ Qo'shildi! (v2.2)
- [x] ~~Auto Pomodoro timer~~ ✅ Qo'shildi! (v2.2)
- [x] ~~Test Mode~~ ✅ Qo'shildi! (v2.2)

### Kelajakda qo'shilishi mumkin (v2.3+):

- [ ] Web dashboard
- [ ] Mobile ilova (Telegram Mini App)
- [ ] Jamoa uchun shared tasks
- [ ] Habit tracking
- [ ] Voice commands
- [ ] Multiple languages
- [ ] Analytics dashboard
- [ ] Video verification
- [ ] AI progress analysis
- [ ] Social features (progress sharing)

---

## 📄 Litsenziya

Bu loyiha shaxsiy foydalanish uchun bepul.

---

## 🙏 Minnatdorchilik

- **Telegram** - Bot Platform
- **Groq** - Bepul AI API
- **Python aiogram** - Telegram bot library
- **APScheduler** - Task scheduling
- **Matplotlib** - Data visualization

---

## 🚀 Omad tilaymiz!

Endi sizda professional Productivity Bot bor! 

Muvaffaqiyat sari qadam tashlang! 💪

**Unutmang:** 
- Doimiy bo'ling
- Kichik maqsadlar qo'ying  
- Har kuni progress qiling
- Taslim bo'lmang!

---

## 📚 Qo'shimcha Dokumentatsiya

- 📖 [TEST_MODE_GUIDE.md](TEST_MODE_GUIDE.md) - Test rejimi qo'llanma
- 📋 [RELEASE_NOTES_VISION.md](RELEASE_NOTES_VISION.md) - v2.2.0 yangiliklar
- 🚀 [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy qo'llanma
- 🇺🇿 [QOLLANMA_UZ.md](QOLLANMA_UZ.md) - O'zbek tili qo'llanma

---

**Yaratildi:** 2026-06-11  
**Yangilandi:** 2026-06-14 (AI Vision, Auto Timer, Test Mode)  
**Versiya:** 2.2.0  
**Til:** Python 3.9+  
**Platform:** Telegram Bot API 7.0+

🎉 **Muvaffaqiyat sari birgalikda!**
