# ⚡️ TEZKOR BOSHLASH - 5 DAQIQADA!

## 🎯 Botni 5 daqiqada ishga tushiring!

---

## 1️⃣ O'RNATISH (2 daqiqa)

```bash
# Klonlash (agar kerak bo'lsa)
git clone https://github.com/Naruto-shippuden00/plannerai.git
cd plannerai

# Kutubxonalar
pip install -r requirements.txt
```

---

## 2️⃣ SOZLASH (2 daqiqa)

### .env fayli yaratish:

```bash
cp .env.example .env
nano .env
```

### To'ldirish:

```env
# Telegram Bot Token (BotFather'dan oling)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Groq AI API (groq.com'dan bepul oling)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxx

# Telegram User ID (botdan bilib olasiz)
ADMIN_USER_ID=
```

**BotFather'dan token olish:**
1. Telegram'da @BotFather ni toping
2. `/newbot` → Bot nomi → Username → TOKEN olasiz

**Groq API key olish:**
1. [groq.com](https://groq.com) → Sign Up → API Keys → Create

---

## 3️⃣ ISHGA TUSHIRISH (1 daqiqa)

```bash
python bot.py
```

**Ko'rinishi kerak:**
```
✅ Database ready!
✅ AI ready!
✅ Reminder checker started - running every 1 minute
🚀 Scheduler started successfully!
Bot starting...
```

---

## 4️⃣ TELEGRAM'DA BOSHLASH (30 soniya)

1. Botingizni Telegram'da toping (@your_bot_username)
2. `/start` yuboring
3. `/id` yuboring - User ID'ngizni oling
4. User ID'ni `.env` fayliga qo'shing (ADMIN_USER_ID=...)
5. Botni restart qiling (Ctrl+C, keyin `python bot.py`)

---

## 5️⃣ BIRINCHI VAZIFA (30 soniya)

```
➕ Vazifa qo'shish

Nom: SAT Math practice
Kategoriya: 📚 SAT
Prioritet: 🔴 Juda muhim (3)
Davomiylik: 1 soat

✅ Qo'shildi!
```

---

## 6️⃣ JADVAL TUZISH (30 soniya)

```
🤖 AI Jadval → Tasdiqlash → ✅

Tayyor! Endi eslatmalar avtomatik keladi! 🎉
```

---

## ✅ TAYYOR!

Bot ishlayapti! Endi:

1. ⏰ Vazifa vaqtida bildirishnoma keladi
2. 📸 Rasm yuborasiz
3. 🍅 Pomodoro timer boshlanadi
4. 💪 Fokusda ishlaysiz
5. 📊 Statistikani ko'rasiz

---

## 🚀 KEYINGI QADAMLAR

- 📖 [README.md](README.md) - To'liq yo'riqnoma
- 🧪 [TEST_GUIDE.md](TEST_GUIDE.md) - Test qilish
- 📋 [TUZATISHLAR.md](TUZATISHLAR.md) - O'zgarishlar

---

## 💡 MASLAHATLAR

### Bildirishnomani test qilish:

Jadvalda vazifani **5 daqiqadan keyin** boshlanishiga sozlang:

```bash
python test_reminder.py
```

Bu script avtomatik ravishda vazifani 5 daqiqadan keyinga o'rnatadi.

### Muammolar?

1. **Bot ishlamayapti** - `pip install -r requirements.txt --upgrade`
2. **Bildirishnoma yo'q** - Bot restart qiling
3. **AI ishlamayapti** - GROQ_API_KEY'ni tekshiring
4. **Database xatosi** - `rm data/productivity.db` va restart

---

## 📞 YORDAM

- 📖 [README.md](README.md) - Batafsil dokumentatsiya
- 🐛 [GitHub Issues](https://github.com/Naruto-shippuden00/plannerai/issues)
- 💬 Telegram: @yourhandle

---

## 🎉 OMAD!

**Bot 100% ishlaydi!** 💪🚀

Savollар bo'lsa - so'rang! 😊

---

**Yaratildi:** 2026-06-12  
**Versiya:** 2.0  
**Muallif:** Productivity Bot Team
