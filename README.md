# Birzumda Taqdimot boti

Talabalar va ustozlardan buyurtma qabul qiluvchi Telegram bot. Binafsha–qora dizayn, Mini ilova, rangli tugmalar.

## Bot nima qiladi

**Mijoz uchun:**
- 🛒 **Buyurtma berish:** Talaba / Ustoz → xizmat → paket → mavzu → qo'shimcha talablar → fayllar → muddat → tasdiqlash
- 💳 Karta raqamini ko'rsatadi, mijoz **chek rasmini** yuboradi
- 💰 **Narxlar**, 🎨 **Namunalar** (`samples/` papkasidagi fayllar), 📦 **Buyurtmalarim**, 📞 **Aloqa**

**Admin (siz) uchun:**
- Yangi buyurtma va chek darhol sizga keladi
- Tugmalar: **✅ To'lov tasdiqlandi** / **❌ Rad etish**
- **📤 Tayyor ishni yuborish** → faylni tashlaysiz → `/done` — mijozga avtomatik boradi
- `/orders` — oxirgi 15 ta buyurtma
- `/myid` — Telegram ID raqamingizni bilish

Shoshilinch buyurtma avtomatik **+50%** hisoblanadi.

## Ishga tushirish

### 1. Bot ochish
@BotFather → `/newbot` → nom va username bering → **token**ni nusxalang.

### 2. GitHub'ga yuklash
Shu papkadagi hamma faylni yangi repoga yuklang (masalan `taqdimot-bot`).

### 3. Railway
1. **New Project → Deploy from GitHub repo** → reponi tanlang
2. **Variables** bo'limiga qo'shing:

| O'zgaruvchi | Qiymat |
|---|---|
| `BOT_TOKEN` | BotFather bergan token |
| `ADMIN_ID` | Telegram ID raqamingiz |
| `CARD_NUMBER` | `8600 xxxx xxxx xxxx` |
| `CARD_OWNER` | Karta egasining ismi |
| `CONTACT` | `@Abdulazizov_prince` |
| `DB_PATH` | `/data/orders.db` |
| `WEBAPP_URL` | Railway domeni, masalan `https://birzumda-taqdimot.up.railway.app` |
| `EMOJI_IDS` | ixtiyoriy, pastga qarang |

3. **Settings → Networking → Generate Domain** bosing. Chiqqan manzilni `WEBAPP_URL` ga yozing — shunda **✨ Mini ilova** tugmasi paydo bo'ladi.
4. **Volume** qo'shing va uni `/data` ga ulang. Shunda qayta deploy qilganda buyurtmalar o'chib ketmaydi.
5. Deploy tugagach, botga `/start` yozing.

**ADMIN_ID ni bilish:** avval `ADMIN_ID` ga vaqtincha `0` qo'yib ishga tushiring. Keyin botga `/myid` yozing, chiqqan raqamni `ADMIN_ID` ga qo'ying.

## Narxlarni o'zgartirish
`bot.py` ichidagi `CATALOG` bo'limida. `"s"` — talabalar, `"t"` — ustozlar.

## Kompyuterda sinab ko'rish
```
pip install -r requirements.txt
set BOT_TOKEN=...      (Linux/Mac: export BOT_TOKEN=...)
set ADMIN_ID=...
python bot.py
```

## ✨ Mini ilova
`webapp/index.html` — bot ichida ochiladigan animatsiyali sayt: bosh sahifa, narxlar (Talabalar/Ustozlar),
namunalar (video + animatsiyali maketlar) va buyurtma formasi. Buyurtma Mini ilovadan to'g'ridan-to'g'ri botga keladi.
Narxlar `bot.py` dagi `CATALOG` dan avtomatik olinadi.

## 🎨 Rangli tugmalar
Telegram faqat 3 rangga ruxsat beradi: `primary` (ko'k), `success` (yashil), `danger` (qizil). Binafsha rang yo'q.
Tugma ranglari `bot.py` da `kbtn(...)` va `ikb(...)` ichida o'zgartiriladi.

## 💎 Premium emoji
Faqat **bot egasining akkauntida Telegram Premium** bo'lsa ishlaydi (yoki botga Fragment'dan qo'shimcha username olingan bo'lsa).
1. Botga `/emoji` yozing, keyin premium emojili xabar yuboring — bot ID'larini qaytaradi.
2. Railway'da `EMOJI_IDS` ga JSON yozing, masalan:
```
{"hi":"5285430309720966085","star":"...","student":"...","teacher":"...","order":"...","prices":"...","samples":"...","app":"...","ok":"...","money":"...","check":"...","down":"..."}
```
ID qo'yilmagan joyda oddiy emoji chiqadi — bot baribir ishlayveradi.

## 🔒 Maxfiylik siyosati
Sahifa: `WEBAPP_URL/privacy` (masalan `https://birzumda-taqdimot.up.railway.app/privacy`).
BotFather → Edit Privacy Policy → shu havolani yuboring. Botda `/privacy` buyrug'i ham shu havolani beradi.
