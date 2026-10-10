# 🧮 Aqlli Telegram Kalkulyator Boti (Python / aiogram 3)

Ushbu bot zamonaviy **Python** dasturlash tili va **aiogram 3.x** kutubxonasida yaratilgan yuqori darajadagi interaktiv **Telegram Kalkulyator Boti** hisoblanadi.

Bot foydalanuvchilar kiritgan barcha turdagi matematik ifodalarni bir zumda hisoblaydi, vizual ekranga ega va qulay tugmalar (ham doimiy **Reply**, ham interaktiv dinamik **Inline**) bilan jihozlangan.

---

## ✨ Asosiy Imkoniyatlar va Qulayliklar

1. **📱 Telegram Mini App (Web App) Kalkulyator:**
   - Telegram Bot API ning eng so'nggi **Mini Apps** texnologiyasiga asoslangan.
   - To'liq grafikli, zamonaviy **Glassmorphism Dark** dizayn.
   - **Haptic Feedback:** Har bir tugma bosilganda telefonda tebranish hissi (vibratsiya).
   - **Real vaqtdagi hisoblash:** Ifodani kiritayotgandayoq natijani pastda jonli ko'rsatib boradi.
   - **DEG / RAD** burchak o'lchovlarini almashtirish imkoniyati.
   - **✈️ Chatga yuborish:** Birgina tugma orqali hisoblangan natijani to'g'ridan-to'g'ri Telegram chatiga uzatadi.

2. **🔘 Interaktiv Inline Kalkulyator (Ekranli):**
   - Telegram xabari ichida to'laqonli kalkulyator ekrani va tugmalari.
   - Har bir bosilgan tugma xabarni dinamik tahrirlaydi (xabar ko'payib ketmaydi).
   - O'chirish (`⌫`), tozalash (`C`), tenglik (`=`) va qavslar bilan ishlash.
   - **🔬 Ilmiy rejim (Scientific mode):** Ildiz ($\sqrt{x}$), daraja ($x^y, x^2$), faktorial ($n!$), $\sin, \cos, \tan$, $\log_{10}$, $\pi$, $e$, modul ($|x|$).

3. **✍️ To'g'ridan-to'g'ri Matnli Ifodalarni Hisoblash:**
   - Foydalanuvchi xabarga oddiy matn ko'rinishida yozsa ham avtomatik hisoblaydi:
     - `25 * 4 + 100` ➔ `200`
     - `1 000 000 + 500 000` (raqamlar orasidagi bo'shliqlarni tushunadi) ➔ `1 500 000`
     - `sqrt(144) + 2^8` ➔ `268`
     - `sin(30) + cos(60)` ➔ `1`

4. **📊 Foizlar bilan Aqlli Ishlash:**
   - Hayotiy amallar:
     - `200 + 15%` ➔ `230`
     - `500 - 20%` ➔ `400`
     - `1000 * 12%` ➔ `120`

5. **🛡 Xavfsizlik (Security):**
   - Hech qanday xavfli `eval()` ishlatilmagan!
   - Python **AST (Abstract Syntax Tree)** orqali xavfsiz matematik tahlil qiluvchi dvigatel yaratilgan. Tizim xavfsizligi 100% kafolatlangan (kod inyeksiyalari va DoS hujumlardan himoyalangan).

6. **📜 Hisoblashlar Tarixi va Inline Rejim:**
   - Oxirgi hisoblash natijalari vaqt bilan saqlanadi.
   - Istalgan guruh yoki chatda `@bot_nomi 25*4` deb yozib, tezkor hisob-kitob qilish mumkin.

---

## 📁 Loyiha Fayllari Tuzilishi

```text
bot/
├── main.py            # Botni ishga tushiruvchi asosiy fayl
├── server.py          # Mini App statik veb-serveri
├── config.py          # Sozlamalar va muhit o'zgaruvchilari (Token, WebApp URL)
├── calculator.py      # Xavfsiz AST matematik hisoblash dvigateli
├── keyboards.py       # Inline, Reply va WebApp tugmalari
├── handlers.py        # Buyruqlar, matnlar, WebApp ma'lumotlari handlerlari
├── test_bot.py        # Avtomatlashtirilgan unit-testlar
├── requirements.txt   # Kerakli Python kutubxonalari
├── .env.example       # Token va URL namunasi
├── .env               # Shaxsiy sozlamalar saqlanadigan fayl
├── webapp/            # Telegram Mini App fayllari
│   ├── index.html     # Mini App interfeysi
│   ├── style.css      # Glassmorphism dizayn va stillar
│   └── app.js         # Telegram WebApp SDK va kalkulyator mantiqi
└── README.md          # To'liq qo'llanma
```

---

## 🚀 O'rnatish va Ishga Tushirish

### 1-qadam: Kutubxonalarni o'rnatish

Terminalda loyiha papkasiga kiring va kerakli paketlarni o'rnating:

```bash
pip install -r requirements.txt
```

*(Kutubxonalar: `aiogram>=3.14.0`, `python-dotenv>=1.0.0`)*

---

### 2-qadam: Bot Tokenini olish

1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botga nom va username bering (masalan, `MyCalcUzBot`).
4. `@BotFather` sizga bergan **API Token**ni nusxalab oling.

---

### 3-qadam: Tokenni `.env` fayliga yozish

Loyiha papkasidagi `.env` faylini oching va tokenni joylashtiring:

```env
BOT_TOKEN=1234567890:AAHabcdefghijKLMNopqrstuvwxyz123456
```

---

### 4-qadam: Testlarni tekshirish

Barcha matematik funksiyalar va tugmalar to'g'ri ishlashini tekshirish uchun:

```bash
python3 test_bot.py
```

---

### 5-qadam: Botni ishga tushirish!

```bash
python3 main.py
```

Terminalda quyidagi yozuv paydo bo'ladi:
```text
Bot muvaffaqiyatli ishga tushdi! @SizningBotUsername (ID: ...)
```

Tabriklaymiz! Endi Telegramda botingizga `/start` buyrug'ini yuborib bemalol foydalanishingiz mumkin. 🎉

---

## ☁️ Railway orqali 24/7 Serverga Joylash (Deployment)

Ushbu bot va Telegram Mini App Railway platformasida 24/7 uzluksiz ishlash uchun to'liq moslashtirilgan (`Procfile`, `railway.json`, `runtime.txt` tayyor).

Railway bir vaqtning o'zida ham **Telegram botingizni 24/7 yurgizadi**, ham **Mini Appingiz uchun bepul HTTPS domen** taqdim etadi!

### Qadamlar:

1. [railway.app](https://railway.app) saytiga kiring va **GitHub orqali kiring (Login with GitHub)**.
2. **«+ New Project»** tugmasini bosing.
3. **«Deploy from GitHub repo»** bandini tanlang.
4. Ushbu repositoryni tanlang: **`telegram-calculator-bot`**.
5. Loyiha ochilgach, **«Variables»** (Muhit o'zgaruvchilari) bo'limiga o'ting va quyidagi qiymatlarni qo'shing:
   - `BOT_TOKEN` = `@BotFather`dan olingan bot tokeningiz
   - `WEBAPP_URL` = (Buni 6-qadamda olasiz)
6. **«Settings»** bo'limiga o'ting va **«Networking» -> «Generate Domain»** tugmasini bosing. Railway sizga shaxsiy HTTPS domen beradi (masalan: `https://telegram-calculator-bot-production.up.railway.app`).
7. Olingan domenni **«Variables»** dagi `WEBAPP_URL` ga joylashtiring.
8. **Bo'ldi!** Railway avtomatik ravishda botni qayta ishga tushiradi va botingiz butun umr 24/7 uzluksiz ishlaydi. 🚀
