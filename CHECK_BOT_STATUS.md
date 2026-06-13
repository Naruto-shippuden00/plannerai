# ⚠️ BILDIRISHNOMA KELMAYAPTI? TEKSHIRISH

## 1. Bot ishlab turibdimi?

**ANIQ SABAB:** Bot o'chiq bo'lsa, bildirishnoma KELMAYDI!

### Tekshirish:
```bash
# Terminal ochiq bo'lishi kerak
python bot.py
```

### Loglarni kuzating:
```
⏰ Checking reminders at HH:MM, day=X (Kun nomi)
👥 Total users: N
```

Agar bu xabarlar HAR DAQIQADA kelmasa - BOT ISHLAMAYAPTI!

## 2. Jadval bormi?

### Tekshirish:
1. Botda: `/start`
2. `📅 Jadval` tugmasini bosing
3. Bugungi kunni ko'ring

Agar JADVAL YO'Q bo'lsa:
1. `➕ Vazifa qo'shish` - Vazifa qo'shing
2. `🤖 AI Jadval` - Jadval tuzing
3. Tasdiqlang

## 3. Vaqt to'g'rimi?

### Misol:
- Hozirgi vaqt: **14:30**
- Jadvaldagi vaqt: **14:30**
- Natija: **14:30:00** da bildirishnoma keladi

⚠️ **MUHIM:** Bot faqat ANIQ vaqtda tekshiradi!
- 14:29 - kelmaydi
- 14:30 - keladi ✅
- 14:31 - o'tib ketgan

## 4. Bot doim ishlashi kerak!

### 3 ta variant:

#### A. Kompyuterda (Test uchun)
```bash
cd plannerai
python bot.py
# Terminal ochiq qolsin!
```

#### B. Serverda (Tavsiya etiladi)
- Railway.app (BEPUL)
- Heroku (BEPUL tier)
- DigitalOcean VPS

#### C. Kompyuterda Background (Linux/Mac)
```bash
nohup python bot.py > bot.log 2>&1 &
```

## 5. Test qilish

### 1-qadam: Bot ishga tushiring
```bash
python bot.py
```

### 2-qadam: Jadval qo'shing
Masalan, hozir 14:29 bo'lsa:
- Vazifa: Test Task
- Jadval: 14:30-15:00
- Bugun

### 3-qadam: Kuting
- 14:30:00 da bildirishnoma kelishi kerak
- Logda: `🔔 MATCH!` ko'rinishi kerak

## 6. Muammo bo'lsa?

### Log tekshirish:
```bash
# Bot loglarida qidiring
grep "Checking reminders" bot.log
grep "MATCH" bot.log
```

### Database tekshirish:
```bash
sqlite3 data/productivity.db
.tables
SELECT * FROM schedule;
SELECT * FROM tasks WHERE active=1;
```

## ✅ XULOSA

Bildirishnoma kelmasligi sabablari:
1. ❌ Bot o'chiq
2. ❌ Jadval yo'q
3. ❌ Vaqt o'tmay ketgan
4. ❌ Timezone noto'g'ri

**YEChIM:** Botni doim ishlatib turing! 🚀
