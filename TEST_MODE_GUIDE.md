# 🧪 TEST MODE QO'LLANMA

## Umumiy ma'lumot

Test rejimi - bu Planner AI botni tezroq sinab ko'rish va barcha funksiyalarni tekshirish uchun maxsus rejim.

**Normal rejim:**
- ⏰ Bildirishnoma intervali: 5 daqiqa
- ⏱ Pomodoro davomiyligi: Jadval bo'yicha (15-120 daqiqa)
- 🔔 Tanaffus: 10 daqiqa

**Test rejimi:**
- ⏰ Bildirishnoma intervali: 30 soniya
- ⏱ Pomodoro davomiyligi: 2 daqiqa
- 🔔 Tanaffus: 30 soniya

## Test rejimini yoqish

### 1. Admin sifatida tizimga kirish
```
BOT_TOKEN=sizning_tokeningiz
ADMIN_USER_ID=sizning_telegram_id
```

### 2. Test rejimini yoqish
```
/testmode
```

✅ Bot sizga test rejimi yoqilganligini bildirib, quyidagi xabar yuboradi:

```
🟢 TEST REJIMI YOQILDI

✅ Tizim tezlashtirilgan rejimda ishlaydi:

⏰ Bildirishnoma intervali: 30 soniya (5 daqiqa o'rniga)
⏱ Pomodoro davomiyligi: 2 daqiqa (test uchun)
🔔 Tanaffus: 30 soniya (10 daqiqa o'rniga)

🧪 TEST JARAYONI:

1️⃣ /test_reminder - Bildirishnoma yuborish
2️⃣ Har 30 soniyada yangi bildirishnoma keladi
3️⃣ 📸 Rasm yuboring - bildirishnoma to'xtaydi
4️⃣ 🤖 AI rasm tahlil qiladi
5️⃣ ⏱ Avtomatik 2 daqiqalik timer boshlanadi
6️⃣ ⏰ 2 daqiqadan keyin tanaffus (30 soniya)
7️⃣ 🔁 Keyingi vazifa (agar mavjud bo'lsa)

⚠️ Test rejimini o'chirish: /testmode

💡 MUHIM: Testdan keyin albatta o'chiring!
```

## Test jarayoni

### 1-qadam: Vazifa qo'shish

Avval kamida bitta vazifa qo'shing:

```
➕ Vazifa qo'shish → Vazifa nomini kiriting → Kategoriya → Prioritet → Davomiylik
```

### 2-qadam: Test bildirishnoma yuborish

```
/test_reminder
```

Bot sizning birinchi vazifangiz uchun bildirishnoma yuboradi.

### 3-qadam: Bildirishnomalarni kuzatish

✅ Har **30 soniyada** yangi bildirishnoma keladi:

```
⏰ VAZIFA VAQTI! (1-eslatma)

🎯 SAT Math Practice
🕐 17:00 - 18:00

❗️ DIQQAT: Bildirishnomani to'xtatish uchun vazifa RASMINI yuboring!

📸 Rasm turlaridan biri:
• Dars jarayoningiz
• Bajarayotgan vazifangiz
• Mashq daftaringiz
• Ish statingiz

⚠️ Rasm yubormasangiz, bildirishnomalar davom etadi!
```

### 4-qadam: Rasm yuborish

📸 Istalgan rasmni yuboring (test uchun - har qanday rasm)

✅ Bot quyidagilarni bajaradi:

1. **Bildirishnomalarni darhol to'xtatadi**
2. **AI rasm tahlil qiladi** (Groq Vision API)
3. **Tahlil natijasini yuboradi**

```
✅ RASM QABUL QILINDI! (1-rasm)

🎉 Ajoyib! Bildirishnomalar to'xtatildi!

⏱ Endi POMODORO TIMER boshlanadi!

📊 Sizda 2 daqiqalik fokus sessiya bor.
🔥 Men sizni nazorat qilib turaman!

💪 Fokusda qoling va muvaffaqiyatga erishing!
```

### 5-qadam: Pomodoro timer

⏱ **2 daqiqalik** fokus timer boshlanadi:

```
🍅 POMODORO TIMER BOSHLANDI! [TEST MODE]

🎯 Vazifa: SAT Math Practice
⏱ Davomiyligi: 2 daqiqa

📱 Telefon: Silent mode
🔕 Notificationlar: O'chirilgan
💻 Faqat vazifa: Fokus 100%

🚀 Boshlang! Men sizni nazorat qilaman!
```

### 6-qadam: Timer tugashi

⏰ **2 daqiqadan keyin:**

```
🎉 VAZIFA TUGADI! [TEST MODE]

🎯 SAT Math Practice
⏱ 2 daqiqa

✅ Ajoyib ish qildingiz!

🧘‍♂️ Endi 0 daqiqa TANAFFUS!

☕️ Choy iching
🚶‍♂️ Biroz yuring
💧 Suv iching
👀 Ko'zingizni dam oldiring

⏰ 0 daqiqadan keyin keyingi vazifaga o'tamiz!
```

### 7-qadam: Tanaffus

⏰ **30 soniyadan keyin:**

```
⏰ TANAFFUS TUGADI! [TEST MODE]

💪 Keyingi vazifaga tayyormisiz?

📋 Jadvalingizga qarang!

🚀 Davom etamiz!
```

## Test rejimi holatini tekshirish

```
/teststatus
```

✅ Natija:

```
🟢 TEST REJIMI YOQILGAN

📅 Boshlangan: 2026-06-14 17:30:15
⏱ Davomiyligi: 0s 15d

⚙️ Sozlamalar:
• Bildirishnoma: 30 soniya
• Pomodoro: 2 daqiqa
• Tanaffus: 30 soniya

O'chirish: /testmode
```

## Test rejimini o'chirish

### Ommaga taqdim qilishdan oldin:

```
/testmode
```

✅ Bot xabar beradi:

```
🔴 TEST REJIMI O'CHIRILDI

✅ Bot endi normal rejimda ishlaydi:

⏰ Bildirishnoma intervali: 5 daqiqa
⏱ Pomodoro davomiyligi: Jadval bo'yicha
🔔 Tanaffus: 10 daqiqa

🚀 Bot endi ommaga taqdim qilish uchun tayyor!
```

## Test uchun senarilar

### Senariy 1: To'liq sikl testi

1. `/testmode` - Test rejimini yoqish
2. Vazifa qo'shish
3. `/test_reminder` - Bildirishnoma yuborish
4. 30 soniya kutish → 2-bildirishnoma
5. 30 soniya kutish → 3-bildirishnoma
6. Rasm yuborish → Bildirishnomalar to'xtaydi
7. AI tahlilini kutish
8. 2 daqiqa kutish → Pomodoro tugaydi
9. 30 soniya kutish → Tanaffus tugaydi
10. `/testmode` - Test rejimini o'chirish

**Umumiy vaqt:** ~5 daqiqa

### Senariy 2: AI vision testi

1. Test rejimini yoqish
2. `/test_reminder`
3. Turli rasmlar yuborish:
   - Dars jarayoni
   - Kod screenshot
   - Kitob sahifasi
   - Mashq daftari
4. AI tahlillarini solishtrish

### Senariy 3: Chidamlilik testi

1. Test rejimini yoqish
2. `/test_reminder`
3. Rasm **YUBORMASDAN** 5 daqiqa kutish
4. Bildirishnomalar davom etishini tekshirish (~10 ta bildirishnoma)
5. Rasm yuborish → To'xtatish

## Admin komandalar

| Komanda | Tavsif |
|---------|--------|
| `/admin` | Admin panel |
| `/testmode` | Test rejimini yoqish/o'chirish |
| `/teststatus` | Test rejimi holati |
| `/test_reminder` | Test bildirishnoma yuborish |
| `/stats_all` | Tizim statistikasi |
| `/users` | Foydalanuvchilar ro'yxati |
| `/check` | Bot holatini tekshirish |

## Muhim eslatmalar

⚠️ **DIQQAT:**

1. Test rejimini faqat **siz (admin)** ishlata olasiz
2. Test rejimi **faqat sizning akkountingizda** ishlaydi
3. Boshqa foydalanuvchilarga ta'sir qilmaydi
4. **Ommaga taqdim qilishdan oldin ALBATTA o'chiring!**
5. Test rejimi faqat development uchun

## Xatoliklarni aniqlash

### Agar bildirishnomalar kelmasa:

1. Bot ishlab turganini tekshiring: `/check`
2. Scheduler holatini tekshiring: `/check` → Scheduler status
3. Vazifalaringizni tekshiring: `📋 Vazifalarim`

### Agar rasm tahlil qilinmasa:

1. `.env` faylida `GROQ_API_KEY` borligini tekshiring
2. `/check` → AI status
3. Rasm formatini tekshiring (JPG, PNG)

### Agar test rejimi ishlamasa:

1. `/teststatus` - Holatni tekshiring
2. `/testmode` - Qayta yoqib ko'ring
3. Bot loglarini tekshiring

## Muvaffaqiyatli test natijalari

✅ **Barcha funksiyalar ishlaydi:**

1. ✅ Bildirishnomalar har 30 soniyada keladi
2. ✅ Rasm yuborilganda bildirishnomalar to'xtaydi
3. ✅ AI rasm tahlil qiladi
4. ✅ Pomodoro 2 daqiqa davom etadi
5. ✅ Tanaffus 30 soniya davom etadi
6. ✅ Keyingi vazifaga avtomatik o'tadi

## Keyingi qadamlar

Test tugagandan keyin:

1. **Test rejimini o'chiring:** `/testmode`
2. **Final tekshirish:** `/check` → Hammasi normal rejimda
3. **Ommaga taqdim qiling:** Bot tayyor! 🚀

---

**Savollar yoki muammolar bo'lsa:**
- Loglarni tekshiring
- `/check` komandasi bilan holatni ko'ring
- Admin sifatida barcha funksiyalardan foydalaning

🎉 **Muvaffaqiyatli testlar!**
