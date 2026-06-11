# 🚀 TEZKOR BOSHLASH - O'zbek tilida

## 1️⃣ Kerakli narsalar

- Python 3.8+ o'rnatilgan kompyuter
- Telegram akkaunti
- Internet

## 2️⃣ O'rnatish (5 daqiqa)

### A) Python kutubxonalarini o'rnatish

```bash
cd productivity-bot
pip install -r requirements.txt
```

### B) Telegram Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` yuboring
3. Bot nomini kiriting
4. Bot username'ini kiriting
5. **TOKEN**ni ko'chirib oling

Misol token:
```
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### C) Groq AI Key olish (BEPUL!)

1. [groq.com](https://groq.com) ga kiring
2. GitHub/Google bilan ro'yxatdan o'ting
3. "API Keys" → "Create API Key"
4. **KEY**ni ko'chirib oling

Misol key:
```
gsk_xxxxxxxxxxxxxxxxxxxxxxxxx
```

### D) .env fayli yaratish

Loyiha papkasida `.env` fayli yarating va quyidagilarni yozing:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_USER_ID=
```

**DIQQAT:** O'z tokenlaringizni yozing!

## 3️⃣ Ishga tushirish

```bash
python bot.py
```

Agar muvaffaqiyatli bo'lsa:
```
✓ Database ready!
✓ AI ready!
✓ Scheduler started!
✓ Bot starting...
```

## 4️⃣ Telegram'da ochish

1. Telegram'ni oching
2. Botingizni qidiring (username)
3. **START** bosing
4. `/id` yuboring - ID'ingizni oling
5. ID ni `.env` ga yozing (`ADMIN_USER_ID`)
6. Botni qaytadan ishga tushiring

## 5️⃣ Foydalanish

### Vazifa qo'shish
1. ➕ Vazifa qo'shish
2. Nom kiriting: "SAT Math"
3. Kategoriya: SAT
4. Prioritet: 🔴 Juda muhim
5. Davomiylik: 2 soat

### Jadval tuzish
1. 🤖 AI Jadval
2. Kutamiz... (AI tahlil qilmoqda)
3. ✅ Tasdiqlash
4. TAYYOR! ⏰

### Vazifa bajarish
1. Bot eslatadi ⏰
2. Vazifani bajaring 💪
3. ✅ Bajarildi tugmasini bosing
4. Rasm yuboring 📸
5. Izoh yozing ✏️

### Statistika
📊 Statistika tugmasi → Haftalik natijalar + grafik

### Test
📝 Shanba kuni test → Yakshanba natijalar

---

## 🆘 Muammolar

**Bot ishlamayapti?**
```bash
pip install -r requirements.txt --upgrade
python bot.py
```

**Token xatosi?**
- `.env` fayli borligini tekshiring
- Token to'g'ri ko'chirilganini tekshiring

**AI ishlamayapti?**
- Groq API key to'g'ri kiritilganligini tekshiring
- Internet borligini tekshiring
- AI ishlamasa ham bot oddiy algoritm bilan ishlaydi!

---

## 💡 Maslahatlar

✅ Har kuni bir xil vaqtda ishlang  
✅ Rasmlar yuborishni unutmang  
✅ Haftalik testlarni o'tkazmang  
✅ Statistikani har kuni ko'ring  
✅ Doimiy bo'ling!  

---

## 📞 Yordam

1. `README.md` ni o'qing (batafsil)
2. Bot ichida `/help`
3. Loglarni tekshiring

---

## 🎯 Asosiy Buyruqlar

- `/start` - Botni boshlash
- `/help` - Yordam
- `/id` - User ID
- `/stats` - Statistika
- `/schedule` - Bugungi jadval
- `/test` - Test boshlash

---

**OMAD! SIZ QILA OLASIZ! 💪🔥**

Savol bo'lsa yozing!
