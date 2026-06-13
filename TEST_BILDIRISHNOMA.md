# 🔍 Bildirishnoma Kelmayapti - Tekshirish

## 📋 Muammo
Bildirishnoma kelmayapti yoki AI vision qo'shilgandan keyin bildirishnoma to'xtagan.

## ✅ Tekshirish Bosqichlari

### 1️⃣ Bot Ishlab Turibdimi?

**Railway.app da:**
```bash
# Deployment loglarini ko'ring
# Settings → Deployments → Latest Deployment → Logs
```

**Local da:**
```bash
cd plannerai
python bot.py
```

**Kutilayotgan log:**
```
✅ Database ready!
✅ AI ready!
✅ Scheduler started!
📋 Total scheduled jobs: 4
   - Reminder Checker (ID: check_reminders) | Next run: ...
   - Morning Motivation (ID: morning_motivation) | Next run: ...
🎉 Scheduler started successfully!
```

### 2️⃣ Database Holatini Tekshirish

```bash
python test_scheduler_debug.py
```

**Ko'rish kerak:**
- ✅ Foydalanuvchilar soni: X ta
- ✅ Vazifalar soni: X ta
- ✅ Jadval soni: X ta
- ✅ Bugungi jadval: ...

### 3️⃣ Jadval Bormi?

Botda:
```
/schedule - Jadval tuzish
```

Yoki:
```
📅 Jadval → 🤖 AI bilan tuzish
```

**Muhim:** Jadval bo'lmasa, bildirishnoma bo'lmaydi!

### 4️⃣ Vaqt To'g'rimi?

**Toshkent vaqti bilan tekshiring:**
```python
from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo("Asia/Tashkent"))
print(f"Hozir: {now.strftime('%H:%M')} ({now.strftime('%A')})")
```

**Jadvalda vaqt:**
```
17:00 - SAT Math
```

**Bildirishnoma keladi:** 17:00 da (aniq)

### 5️⃣ Loglarni Ko'rish

**Bot ishlab turgan terminalda quyidagi log bo'lishi kerak:**

```
⏰ Reminder Check: 2026-06-13 17:00:00 +05 | Day: 4 (Juma) | Time: 17:00
👥 Checking 1 users
👤 User 123456: 2 tasks for Juma
🔔 MATCH! User 123456 | Task 'SAT Math' | Scheduled: 17:00 | Current: 17:00
📤 Sending reminder: user=123456, task=1, name='SAT Math'
✅ Reminder message sent to user 123456
```

**Agar bu log bo'lmasa:**
- ❌ Jadval yo'q
- ❌ Vaqt mos kelmayapti
- ❌ Bot to'xtab qolgan

## 🛠️ Umumiy Muammolar va Yechimlar

### ❌ Muammo: "No users found"
**Yechim:** Botda `/start` buyrug'ini yuboring

### ❌ Muammo: "Bugun uchun jadval yo'q"
**Yechim:** `/schedule` orqali jadval tuzing

### ❌ Muammo: "Scheduler ishlamayapti"
**Yechim:** 
```bash
# Botni qaytadan ishga tushiring
python bot.py
```

### ❌ Muammo: AI vision qo'shilgandan keyin to'xtadi
**Yechim:** Bu muammo emas, kod to'g'ri ishlaydi. Jadval tekshiring.

### ❌ Muammo: Railway.app da ishlayapti lekin bildirishnoma yo'q
**Yechim:**
1. Railway loglarini tekshiring
2. `GROQ_API_KEY` qo'shilganmi?
3. Jadval to'g'ri tuzilganmi?

## 🧪 Test Qilish

### Manual Test (Tezkor)

1. **Hozirgi vaqtni oling:**
   ```
   Hozir: 14:35
   ```

2. **Jadvalga 1-2 daqiqadan keyingi vaqt qo'shing:**
   ```
   14:37 - Test Task
   ```

3. **2 daqiqa kuting**

4. **Bildirishnoma kelishi kerak!**

## 📊 Status Tekshirish Skript

```bash
python test_scheduler_debug.py
```

**Natija:**
```
🔍 SCHEDULER DEBUG
⏰ Hozirgi vaqt (Toshkent): 2026-06-13 14:35:42
📆 Kun: 4 (Juma)

💾 Database:
   👥 Foydalanuvchilar: 1 ta
   📋 Vazifalar: 5 ta
   📅 Jadval: 12 ta

📅 Bugungi jadval (Day of week = 4):
   🔔 User 123456: 17:00-18:30 | SAT Math (Education)
   🔔 User 123456: 19:00-20:00 | Python Basics (Programming)

🤖 Bot holati:
   ✅ Scheduler ishlayapti
   📋 Joblar soni: 4

⏰ Keyingi bildirishnoma:
   🔔 17:00 - SAT Math (User: 123456)
```

## ✅ Hammasi Ishlasa

Agar barcha tekshiruvlar to'g'ri bo'lsa:
- ✅ Bot ishlab turibdi
- ✅ Scheduler active
- ✅ Jadval mavjud
- ✅ Vaqt to'g'ri

**Unda bildirishnoma keladi! Vaqt kelishini kuting.** ⏰

## 🆘 Yordam

Agar hali ham ishlamasa, quyidagi ma'lumotlarni yuboring:

1. `test_scheduler_debug.py` natijasi
2. Bot loglarining oxirgi 50 qatori
3. Screenshot: `/schedule` buyrug'i natijasi

Men tezkor yordam beraman! 😊
