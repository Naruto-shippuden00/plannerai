# 🤖 AI Vision Setup Guide

## Groq AI Vision ishlatish

Planner AI bot rasmlarni tahlil qilish uchun **Groq Vision API** ishlatadi.

### ✅ Groq AI haqida:

- **Model:** `llama-3.2-90b-vision-preview`
- **Narx:** 100% BEPUL! 🎉
- **Limit:** Kuniga 14,400 request (daqiqada 10 ta)
- **Format:** JPG, PNG, WebP, GIF
- **Max size:** 20MB

### 🔑 API Key olish:

1. **Groq.com ga o'ting:**
   - https://console.groq.com/

2. **Sign Up qiling:**
   - GitHub yoki Google bilan kirish

3. **API Key yarating:**
   - Dashboard → API Keys
   - "Create API Key" tugmasini bosing
   - Key nomini kiriting (masalan: "Planner AI")
   - **Key ni ko'chirib oling va saqlab qo'ying!**

4. **Railway'ga qo'shing:**
   ```
   GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 📸 Rasm formatlari:

Bot quyidagi formatlarni qabul qiladi:
- ✅ JPG/JPEG
- ✅ PNG  
- ✅ WebP
- ✅ GIF

**Telegram'dan yuborilgan rasmlar** avtomatik JPG formatida saqlanadi.

### 🧪 AI Vision test qilish:

```bash
# 1. API key tekshirish
import os
from groq import Groq

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
print("✅ Groq client initialized!")

# 2. Simple test
response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": "Salom!"}]
)
print(response.choices[0].message.content)
```

### 🔍 Xatoliklarni hal qilish:

#### 1. "AI xizmat mavjud emas"
**Sabab:** GROQ_API_KEY o'rnatilmagan

**Yechim:**
```bash
# .env faylda:
GROQ_API_KEY=your_actual_key_here

# Railway'da:
Settings → Variables → Add:
GROQ_API_KEY=your_actual_key_here
```

#### 2. "Rate limit exceeded"
**Sabab:** Juda ko'p request yuborilgan

**Yechim:**
- Daqiqada maksimal 10 ta request
- Biroz kuting (1-2 daqiqa)

#### 3. "Image encoding failed"
**Sabab:** Rasm o'qilmayapti

**Yechim:**
- Rasm fayli mavjudligini tekshiring
- File permissions tekshiring
- Rasm formatini tekshiring (JPG recommended)

#### 4. "Timeout"
**Sabab:** API juda sekin javob bermoqda

**Yechim:**
- Internet connection tekshiring
- Timeout'ni oshiring (30-60 sekund)
- Qayta urinib ko'ring

### 📊 AI Vision workflow:

```
Foydalanuvchi rasm yuboradi
   ↓
Telegram rasm yuklaydi (JPG)
   ↓
Bot rasmni saqlaydi (data/focus_photos/)
   ↓
AI helper rasm encode qiladi (base64)
   ↓
Groq Vision API'ga yuboriladi
   ↓
AI tahlil qiladi (5-15 sekund)
   ↓
O'zbek tilida natija qaytaradi
   ↓
Foydalanuvchiga yuboriladi
```

### 💡 AI tahlil natijasi format:

```
📸 [Nima ko'rsatilgan: SAT Math mashqlar]
⭐️ Baho: 8/10
💡 Tavsiya: Ajoyib! Davom eting!
```

### ⚙️ Sozlamalar:

**ai_helper.py** faylida:

```python
# Model
model="llama-3.2-90b-vision-preview"

# Timeout
timeout=30.0  # 30 sekund

# Max tokens
max_tokens=500  # ~400 so'z

# Temperature
temperature=0.7  # Creativity darajasi
```

### 🚀 Alternativ - Agar Groq ishlamasa:

#### 1. **OpenAI Vision** (Pullik)
```python
# Narx: $0.01 / 1000 tokens
model="gpt-4-vision-preview"
```

#### 2. **Google Gemini Vision** (Bepul)
```python
# Narx: Bepul (limit bor)
model="gemini-pro-vision"
```

#### 3. **Anthropic Claude Vision** (Pullik)
```python
# Narx: $0.008 / 1000 tokens
model="claude-3-opus-20240229"
```

### 📝 Bot loglarini tekshirish:

Railway'da deploy bo'lgach:
```bash
# Dashboard → Deployments → View Logs

# Qidiruv:
"AI analysis started"  # AI boshlanish
"Image encoded"        # Rasm encode bo'ldi
"Calling Groq Vision API"  # API chaqirilmoqda
"AI analysis completed"  # Muvaffaqiyatli tugadi
"AI photo analysis error"  # Xatolik
```

### ✅ Success markers:

```
✅ AI client initialized!
✅ Image encoded: 12345 bytes
✅ AI analysis completed: 150 chars
```

### ❌ Error markers:

```
❌ AI client not initialized!
❌ Image encoding failed!
❌ AI photo analysis error: [xato]
```

### 🎯 Best practices:

1. **Rasm sifati:** Yorqin va aniq rasmlar yuboring
2. **Rasm hajmi:** 1-5 MB optimal
3. **Rasm mazmuni:** Vazifaga oid bo'lsin
4. **Kutish vaqti:** 10-15 sekund kutish normal

### 💰 Narxlar (2024):

| Service | Model | Price | Limit |
|---------|-------|-------|-------|
| Groq | llama-3.2-vision | **FREE** | 14,400/day |
| OpenAI | gpt-4-vision | $0.01/1k | Unlimited |
| Google | gemini-pro-vision | **FREE** | 60/min |
| Anthropic | claude-3-opus | $0.008/1k | Unlimited |

**Tavsiya:** Groq bepul va juda tez! 🚀

---

## Support

Savollar yoki muammolar:
- Loglarni tekshiring
- API key'ni tasdiqlang
- Internet connection tekshiring
- Groq status: https://status.groq.com/

✅ **Bot tayyor! AI Vision ishlayapti!** 🎉
