# 🧪 TEST QILISH BO'YICHA YO'RIQNOMA

## Botni to'liq test qilish uchun qadamma-qadam yo'riqnoma

---

## ⚙️ BO'SHLIQDAN BOSHLASH

### 1. O'rnatish va sozlash

```bash
# 1. Loyihani ochish
cd plannerai

# 2. Virtual environment (ixtiyoriy)
python3 -m venv venv
source venv/bin/activate

# 3. Kutubxonalar
pip install -r requirements.txt

# 4. .env faylini sozlash
cp .env.example .env
nano .env
```

**.env fayl:**
```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz123456789
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ADMIN_USER_ID=your_telegram_id
```

### 2. Botni ishga tushirish

```bash
python bot.py
```

**Kutilgan natija:**
```
INFO - Database ready!
INFO - AI ready!
INFO - Scheduler started successfully!
✅ Reminder checker started - running every 1 minute
🚀 Scheduler started successfully!
INFO - Bot starting...
```

---

## 📱 TELEGRAM'DA TEST QILISH

### 1️⃣ START VA REGISTRATSIYA

```
Telegram'da botni toping
/start yuboring
```

**Kutilgan natija:**
- Xush kelibsiz xabari
- Asosiy menyu klaviaturasi
- Foydalanuvchi database'ga qo'shildi

---

### 2️⃣ VAZIFA QO'SHISH

#### Test 1: SAT Math vazifasi

```
➕ Vazifa qo'shish tugmasini bosing

1. Nom: SAT Math practice
2. Kategoriya: 📚 SAT
3. Prioritet: 🔴 Juda muhim (3)
4. Davomiylik: 1 soat
```

**Kutilgan natija:**
- "✅ Vazifa muvaffaqiyatli qo'shildi!" xabari
- Vazifa haqida to'liq ma'lumot ko'rsatiladi

#### Test 2: Python vazifasi

```
➕ Vazifa qo'shish

1. Nom: Python loops o'rganish
2. Kategoriya: 🐍 Python
3. Prioritet: 🟡 O'rtacha (2)
4. Davomiylik: 1.5 soat (90 min)
```

#### Test 3: Kitob o'qish

```
➕ Vazifa qo'shish

1. Nom: Atomic Habits kitobini o'qish
2. Kategoriya: 📖 Kitob
3. Prioritet: 🟢 Past (1)
4. Davomiylik: 30 min
```

**Jami:** 3 ta vazifa qo'shilishi kerak

---

### 3️⃣ VAZIFALARNI KO'RISH

```
📋 Vazifalarim tugmasini bosing
```

**Kutilgan natija:**
- 3 ta vazifa ko'rsatiladi
- Kategoriya bo'yicha guruhlangan
- Har bir vazifa uchun boshqaruv tugmalari:
  - ✅ Bajarildi
  - ⏰ Keyinroq
  - 🗑 O'chirish

---

### 4️⃣ AI JADVAL TUZISH

```
🤖 AI Jadval tugmasini bosing
```

**Kutilgan natija:**
1. "🤖 AI jadval tuzmoqda..." loading message
2. Haftalik jadval statistikasi:
   - Jami sessionlar
   - Har bir vazifa uchun haftalik soni
3. Kunlik jadval:
   - Dushanba, Seshanba, Chorshanba...
   - Har bir kun uchun vaqt va vazifa
4. Tasdiqlash tugmalari:
   - ✅ Tasdiqlash
   - 🔄 Qayta tuzish
   - ❌ Bekor qilish

**"✅ Tasdiqlash" ni bosing**

**Kutilgan natija:**
- "✅ Jadval tasdiqlandi!"
- Nechtа vazifa jadvalga qo'shilgani
- "⏰ Endi men sizga har bir vazifa vaqtida eslatma yuboraman!"

---

### 5️⃣ JADVALNI KO'RISH

```
📅 Jadval tugmasini bosing
```

**Kutilgan natija:**
- Bugungi kun uchun jadval
- Har bir vazifa uchun:
  - Emoji (📚 SAT, 🐍 Python, 📖 Kitob)
  - Vaqt (17:00 - 18:00)
  - Vazifa nomi
- Kunlar bo'yicha navigatsiya tugmalari

**Boshqa kunlarni ko'rish:**
- Tugmalardan boshqa kunni tanlang
- Har bir kun uchun jadval ko'rsatiladi

---

## 🔥 FOCUS MODE VA BILDIRISHNOMA TIZIMI

### 6️⃣ BILDIRISHNOMA TESTINI SOZLASH

**MUHIM:** Bildirishnomani test qilish uchun, jadvalda vazifani **5 daqiqa o'tgach** boshlashga sozlang.

#### Qadamlar:

1. **Hozirgi vaqtni bilib oling:**
   ```
   Telegram'da /time yuboring yoki soatga qarang
   Misol: 17:23
   ```

2. **5 daqiqadan keyingi vaqtni hisoblang:**
   ```
   17:23 + 5 min = 17:28
   ```

3. **Jadvalda vaqtni o'zgartirish:**
   ```bash
   # Database'ni ochish
   sqlite3 data/productivity.db
   
   # Birinchi vazifani bugun, 5 daqiqadan keyinga o'rnatish
   UPDATE schedule 
   SET day_of_week = 4,    -- Bugungi kun (0=Dush, 1=Sesh, 2=Chor, 3=Pay, 4=Juma, 5=Shan, 6=Yak)
       start_time = '17:28', 
       end_time = '18:28'
   WHERE id = 1;
   
   # Tekshirish
   SELECT * FROM schedule WHERE id = 1;
   
   # Chiqish
   .exit
   ```

**Yoki Python orqali:**

```python
# test_reminder.py
import sqlite3
from datetime import datetime, timedelta

# 5 daqiqadan keyingi vaqt
now = datetime.now()
start_time = (now + timedelta(minutes=5)).strftime("%H:%M")
end_time = (now + timedelta(minutes=65)).strftime("%H:%M")  # +1 soat
day_of_week = now.weekday()

# Database'ni yangilash
conn = sqlite3.connect('data/productivity.db')
cursor = conn.cursor()

cursor.execute("""
    UPDATE schedule 
    SET day_of_week = ?,
        start_time = ?,
        end_time = ?
    WHERE id = 1
""", (day_of_week, start_time, end_time))

conn.commit()
conn.close()

print(f"✅ Vazifa {start_time} ga sozlandi!")
print(f"⏰ {start_time} da bildirishnoma keladi!")
print(f"⏳ {5} daqiqa kutish...")
```

Ishga tushiring:
```bash
python test_reminder.py
```

---

### 7️⃣ BILDIRISHNOMA KUTISH (5 DAQIQA)

**5 daqiqa kutasiz...**

**ANIQ 17:28 DA (yoki sizning vaqtingizda) quyidagi bo'ladi:**

#### BIRINCHI BILDIRISHNOMA:

```
⏰ VAZIFA VAQTI KELDI!

🎯 SAT Math practice
📂 Kategoriya: SAT
🕐 Boshlanish: 17:28
⏰ Tugash: 18:28
⏱ Davomiyligi: 60 daqiqa

🔔 CHEKSIZ BILDIRISHNOMALAR BOSHLANDI!

❗️ HAR 5 DAQIQADA ESLATMA YUBORILADI!

🛑 TO'XTATISH UCHUN:
📸 Vazifani bajarayotganingizni tasdiqlovchi RASM yuboring!

**Rasm misollari:**
• Dars jarayoni (SAT, IELTS)
• Kod yozayotgan ekran (Python)
• Mashq daftari (Study)
• O'qiyotgan kitob sahifasi
• Gym mashqi jarayoni

⚠️ Rasm yubormasangiz, bildirishnomalar DAVOM ETADI!

💪 Fokusga kiring va muvaffaqiyatga erishing!
```

---

### 8️⃣ CHEKSIZ BILDIRISHNOMALAR (RASM YUBORMASANGIZ)

**Agar rasm yubormasangiz, har 5 daqiqada kelaveradigan bildirishnomalar:**

#### 5 daqiqadan keyin (17:33):

```
⏰ VAZIFA VAQTI! (1-eslatma)

🎯 SAT Math practice
🕐 17:28 - 18:28

❗️ DIQQAT: Bildirishnoma to'xtatish uchun vazifa RASMINI yuboring!

📸 Rasm turlaridan biri:
• Dars jarayoningiz
• Bajarayotgan vazifangiz
• Mashq daftaringiz
• Ish statingiz

⚠️ Rasm yubormasangiz, bildirishnomalar davom etadi!
```

#### 10 daqiqadan keyin (17:38):

```
🔔 2-CHI ESLATMA!

🎯 Vazifa: SAT Math practice

Sizdan hali ham rasm kutilmoqda! 📸

Agar hozir ishlamayotgan bo'lsangiz, bu vazifani bajarmagangiz hisoblanadi!

❌ Natija: Jazo olasiz!

✅ Tezroq rasm yuboring va fokusga kiring!
```

#### 15 daqiqadan keyin (17:43):

```
🚨 MUHIM OGOHLANTIRISH! (3/∞)

🎯 SAT Math practice

Siz hali ham ishlamayapsizmi?

⏰ Vaqt o'tyapti!
📸 Tezroq rasm yuboring!

Bu bildirishnomalar RASM yuborguningizgacha davom etadi!

💪 Boshladingizmi? Rasmni yuboring!
```

**...va har 5 daqiqada davom etadi!**

---

### 9️⃣ RASM YUBORISH (BILDIRISHNOMANI TO'XTATISH)

**RASM YUBORING:**

1. Telegram'da botga rasm yuboring
   - Har qanday rasm (mashq daftari, kitob, ekran va h.k.)
   - Caption kerak emas, faqat rasm

**INSTANT NATIJA:**

```
✅ RASM QABUL QILINDI!

🎉 Ajoyib! Bildirishnomalar to'xtatildi!

⏱ Endi POMODORO TIMER boshlanadi!

📊 Sizda 1 soatlik fokus sessiya bor.
🔥 Men sizni nazorat qilib turaman!

💪 Fokusda qoling va muvaffaqiyatga erishing!
```

**Bildirishnomalar DARHOL to'xtaydi! ✅**

---

### 🔟 POMODORO TIMER (1 SOAT FOKUS)

#### Darhol boshlanganda:

```
🍅 POMODORO TIMER BOSHLANDI!

🎯 Vazifa: SAT Math practice
⏱ Davomiyligi: 60 daqiqa

📱 Telefon: Silent mode
🔕 Notificationlar: O'chirilgan
💻 Faqat vazifa: Fokus 100%

🚀 Boshlang! Men sizni nazorat qilaman!
```

#### 15 daqiqadan keyin:

```
💪 15 DAQIQA O'TDI!

🎯 SAT Math practice

Zo'r ishlamoqdasiz! Davom eting!
Fokusda qoling! 🔥
```

#### 30 daqiqadan keyin:

```
🔥 YARIM SOAT!

🎯 SAT Math practice

Ajoyib! Siz juda yaxshi ishlayapsiz!
Yana 30 daqiqa! 💪

📸 Iltimos, hozirgi holatni tasdiqlovchi rasm yuboring!
(Agar kamera ruxsati berilgan bo'lsa)
```

#### 45 daqiqadan keyin:

```
⚡️ 45 DAQIQA!

🎯 SAT Math practice

Zo'r! Deyarli tugadik!
Oxirgi 15 daqiqa! Qani endi! 🚀
```

#### 60 daqiqa (1 soat) tugaganda:

```
🎉 VAZIFA TUGADI!

🎯 SAT Math practice
⏱ 60 daqiqa

✅ Ajoyib ish qildingiz!

🧘‍♂️ Endi 10 daqiqa TANAFFUS!

☕️ Choy iching
🚶‍♂️ Biroz yuring
💧 Suv iching

⏰ 10 daqiqadan keyin keyingi vazifaga o'tamiz!
```

---

### 1️⃣1️⃣ TANAFFUS (10 DAQIQA)

**10 daqiqa tanaffus avtomatik...**

**10 daqiqadan keyin:**

```
⏰ TANAFFUS TUGADI!

💪 Keyingi vazifaga tayyormisiz?

📋 Jadvalingizga qarang!

🚀 Davom etamiz!
```

---

## ⚠️ JAZO TIZIMI

### 1️⃣2️⃣ RASM YUBORMASANGIZ

**Agar vazifa tugaganda hali rasm yubormagan bo'lsangiz:**

```
❌ VAZIFA BAJARILMADI!

🎯 Vazifa: SAT Math practice

⚠️ Siz hech qanday rasm yubormagansiz!

🔴 JAZO BERILDI!

Bu vazifani qayta bajarishingiz kerak.

Jazolaringizni ko'rish: '⚠️ Jazolarim' tugmasi
```

### 1️⃣3️⃣ JAZOLARNI KO'RISH

```
⚠️ Jazolarim tugmasini bosing
```

**Kutilgan natija:**
- Faol jazolar ro'yxati
- Har bir jazo uchun:
  - Vazifa nomi
  - Jazo turi
  - Sabab
  - Sana
- "✅ Jazoni bajarish" tugmalari

---

## 📊 STATISTIKA

### 1️⃣4️⃣ STATISTIKANI KO'RISH

```
📊 Statistika tugmasini bosing
```

**Kutilgan natija:**
- Haftalik statistika
- Jami vazifalar
- Bajarilgan vazifalar
- Completion rate (%)
- Kategoriyalar bo'yicha grafik
- Eng faol kategoriya
- Progressni grafik

---

## 🔧 QOSHIMCHA TESTLAR

### 1️⃣5️⃣ Vazifani O'chirish

#### Usul 1: Buyruq

```
/remove_Python
```

**Kutilgan natija:**
- Tasdiqlash so'raladi
- `/confirm_remove_ID` buyrug'i beriladi

#### Usul 2: Boshqaruv paneli

```
🗑 Vazifalarni boshqarish
📝 Faol vazifalar
```

**Kutilgan natija:**
- Barcha faol vazifalar ro'yxati
- Har biri uchun ID
- O'chirish instruksiyalari

---

### 1️⃣6️⃣ Bajarilganlar

```
🗑 Vazifalarni boshqarish
✅ Bajarilganlar
```

**Kutilgan natija:**
- Bajarilgan vazifalar ro'yxati
- Bajarilgan sana
- Qayta faollashtirish tugmalari

---

### 1️⃣7️⃣ Kamera Ruxsati

```
⚙️ Sozlamalar
📸 Kamera sozlamalari
```

**Test 1: Ruxsat berish**
```
✅ Ruxsat berish tugmasini bosing
```

**Kutilgan natija:**
- "✅ RUXSAT BERILDI!"
- Izoh: focus vaqtida tasodifiy suratlar so'raladi

**Test 2: Ruxsatni bekor qilish**
```
❌ Ruxsatni bekor qilish
```

**Kutilgan natija:**
- "❌ RUXSAT BEKOR QILINDI"
- Izoh: endi suratlar so'ralmaydi

---

## ✅ TO'LIQ TEST NATIJALARI

### Barcha testlar o'tgandan keyin:

- [x] Bot ishga tushdi
- [x] Foydalanuvchi registratsiya qilindi
- [x] 3 ta vazifa qo'shildi
- [x] AI jadval tuzildi va tasdiqlandi
- [x] Jadval ko'rsatildi
- [x] Bildirishnoma keldi (aniq vaqtda)
- [x] Cheksiz bildirishnomalar (5 daqiqada bir)
- [x] Rasm yuborildi - bildirishnomalar to'xtadi
- [x] Pomodoro timer boshlandi
- [x] Har 15 daqiqada nazorat xabarlari
- [x] Kamera ruxsati (30 daqiqada)
- [x] 1 soat tugaganda tanaffus
- [x] 10 daqiqadan keyin keyingi vazifa
- [x] Jazo tizimi (rasm yo'q bo'lsa)
- [x] Jazolarni ko'rish va bajarish
- [x] Statistika to'g'ri ko'rsatildi
- [x] Vazifalarni o'chirish ishlaydi
- [x] Bajarilganlarni boshqarish ishlaydi
- [x] Kamera ruxsati ishlaydi

---

## 🐛 MUAMMO ANIQLASH

### Agar bildirishnoma kelmasa:

1. **Scheduler loglarini tekshiring:**
   ```bash
   # Terminal'da bot.py ishga tushirilgan joyda:
   # Har 1 daqiqada "⏰ Checking reminders..." ko'rinishi kerak
   ```

2. **Database'ni tekshiring:**
   ```bash
   sqlite3 data/productivity.db
   SELECT * FROM schedule WHERE user_id = YOUR_ID;
   .exit
   ```

3. **Bot qayta ishga tushiring:**
   ```bash
   # Ctrl+C
   python bot.py
   ```

### Agar rasm yuborilmasa:

1. **State'ni tekshiring:**
   - Bot log'ida "FSM State avtomatik o'rnatish" xabari bo'lishi kerak

2. **Rasmni qayta yuboring:**
   - Caption qo'shmang, faqat rasm

3. **Bot qayta ishga tushiring:**

---

## 🎉 OMAD!

Barcha testlar muvaffaqiyatli o'tsa, bot **100% ISHLAYDI!** 🚀

Savollar bo'lsa:
- `TUZATISHLAR.md` faylini o'qing
- `README.md` faylini o'qing
- GitHub Issues'da savol bering

---

**Test qiluvchi:** _______________________
**Sana:** _______________________
**Natija:** ☐ Muvaffaqiyatli ☐ Muammolar bor

**Izohlar:**
________________________________________________
________________________________________________
________________________________________________
