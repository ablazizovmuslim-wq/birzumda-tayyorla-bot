"""
Birzumda Taqdimot boti — buyurtma qabul qilish, karta orqali to'lov (chek), admin tasdiqlashi
va tayyor ishni mijozga yuborish.

Muhit o'zgaruvchilari (Railway → Variables):
  BOT_TOKEN    — @BotFather bergan token
  ADMIN_ID     — sizning Telegram ID raqamingiz (bir nechta bo'lsa vergul bilan)
  CARD_NUMBER  — to'lov qabul qilinadigan karta raqami
  CARD_OWNER   — karta egasining ismi
  CONTACT      — aloqa uchun username (masalan @Abdulazizov_prince)
  DB_PATH      — ixtiyoriy, baza fayli yo'li (Railway Volume uchun: /data/orders.db)
  WEBAPP_URL   — Mini ilova manzili (Railway domeni, masalan https://xxx.up.railway.app)
  PORT         — Railway o'zi beradi (Mini ilova shu portda ishlaydi)
  EMOJI_IDS    — ixtiyoriy, premium emoji ID'lari JSON ko'rinishida (README'ga qarang)
"""
import asyncio
import html
import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, InputMediaPhoto, KeyboardButton,
                           Message, ReplyKeyboardMarkup, WebAppInfo)

# ------------------------------------------------------------------ sozlamalar
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_ID", "0").replace(" ", "").split(",") if x}
CARD_NUMBER = os.getenv("CARD_NUMBER", "0000 0000 0000 0000")
CARD_OWNER = os.getenv("CARD_OWNER", "Ism Familiya")
CONTACT = os.getenv("CONTACT", "@Abdulazizov_prince")
DB_PATH = os.getenv("DB_PATH", "orders.db")
BASE = Path(__file__).parent
SAMPLES = BASE
ASSETS = BASE
BOT_NAME = os.getenv("BOT_NAME", "Birzumda Taqdimot")
URGENT_EXTRA = 0.5  # shoshilinch: +50%
WEBAPP_URL = os.getenv("WEBAPP_URL", "").rstrip("/")
if WEBAPP_URL and not WEBAPP_URL.startswith("http"):
    WEBAPP_URL = "https://" + WEBAPP_URL
PORT = int(os.getenv("PORT", "8080"))
WEBAPP_DIR = BASE
# Premium emoji: {"kalit": "emoji_id"}. Faqat bot egasida Telegram Premium bo'lsa ishlaydi.
DEFAULT_EMOJI_IDS = {
    "hi": "5215248074498128418", "star": "5211057719720561874", "student": "5373012449597335010",
    "teacher": "5372926953978341366", "order": "5443127283898405358", "prices": "5188208446461188962",
    "samples": "5431456208487716895", "app": "5176998281170911817", "ok": "4956672355876209142",
    "check": "4956672355876209142", "money": "5188208446461188962", "down": "5470177992950946662",
    "orders": "5188311512791393083", "contact": "5933749305155260825", "cancel": "5210952531676504517",
    "globe": "5447410659077661506", "bot": "5244983043621411868", "music": "5213323516832667837",
    "image": "5375074927252621134", "channel": "5370599459661045441", "edit": "5237808360882977239",
    "heart": "5345961113479572537", "fire": "5176998281170911817",
}
try:
    EMOJI_IDS = {**DEFAULT_EMOJI_IDS, **json.loads(os.getenv("EMOJI_IDS", "{}"))}
except json.JSONDecodeError:
    EMOJI_IDS = dict(DEFAULT_EMOJI_IDS)
if os.getenv("PREMIUM_EMOJI", "1") == "0":
    EMOJI_IDS = {}


def pe(key: str, fallback: str) -> str:
    """Matn ichida premium emoji (ID bo'lmasa oddiy emoji)."""
    eid = EMOJI_IDS.get(key)
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>' if eid else fallback

logging.basicConfig(level=logging.INFO)

# ------------------------------------------------------------------ narxlar
# packages: (nomi, narx, tavsif)
CATALOG = {
    "s": {
        "title": "🎓 Talabalar uchun",
        "services": {
            "taqdimot": {"name": "Taqdimot", "packages": {
                "start": ("Start", 40000, "10–12 slayd, zamonaviy dizayn, 1 kun"),
                "pro": ("Professional", 70000, "15–20 slayd, animatsiya, diagrammalar, 1–2 kun"),
                "premium": ("Premium", 95000, "20–25 slayd, Morph, neon dizayn, nutq matni, 2–3 kun"),
            }},
            "mustaqil": {"name": "Mustaqil ish", "price": 60000, "desc": "Word formatda, chiroyli muqova bilan"},
            "kurs": {"name": "Kurs ishi", "price": 95000, "desc": "Reja, boblar, adabiyotlar, rasmiylashtirish"},
            "portfolio": {"name": "Portfolio", "price": 50000, "desc": "Talaba portfoliosi va rezyume"},
        },
    },
    "t": {
        "title": "👩‍🏫 Ustozlar uchun",
        "services": {
            "dars": {"name": "Dars taqdimoti", "packages": {
                "start": ("Start", 60000, "12–15 slayd, ochiq dars uchun"),
                "pro": ("Professional", 110000, "15–20 slayd, animatsiya, diagrammalar"),
                "premium": ("Premium", 180000, "20–25 slayd, Morph, nutq matni, video"),
            }},
            "portfolio": {"name": "Portfolio", "price": 120000, "desc": "Attestatsiya va «Eng yaxshi tyutor» tanlovi"},
            "oum": {"name": "O'quv-uslubiy majmua", "price": 250000, "desc": "Ma'ruza, amaliy mashg'ulot, testlar"},
            "tadbir": {"name": "Tadbir taqdimoti", "price": 80000, "desc": "Konferensiya, tadbir, hisobot"},
        },
    },
}

DEADLINES = {"normal": "Oddiy muddat", "urgent": "⚡ Shoshilinch (+50%)"}

STATUS = {
    "new": "🕐 To'lov kutilmoqda",
    "paid": "🧾 Chek tekshirilmoqda",
    "work": "🛠 Tayyorlanmoqda",
    "done": "✅ Topshirildi",
    "rejected": "❌ Rad etildi",
}


def money(n: int) -> str:
    return f"{n:,}".replace(",", " ") + " so'm"


# ------------------------------------------------------------------ baza
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, username TEXT, full_name TEXT, phone TEXT,
            audience TEXT, service TEXT, package TEXT, price INTEGER,
            topic TEXT, details TEXT, deadline TEXT, files TEXT,
            status TEXT, created_at TEXT)""")


def create_order(data: dict, user) -> int:
    with db() as con:
        cur = con.execute(
            """INSERT INTO orders(user_id, username, full_name, phone, audience, service, package, price,
               topic, details, deadline, files, status, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (user.id, user.username or "", user.full_name, data.get("phone", ""), data["aud"], data["svc"],
             data.get("pkg", ""), data["price"], data["topic"], data.get("details", ""), data["deadline"],
             json.dumps(data.get("files", [])), "new", datetime.now().strftime("%Y-%m-%d %H:%M")))
        return cur.lastrowid


def get_order(oid: int):
    with db() as con:
        return con.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()


def set_status(oid: int, status: str):
    with db() as con:
        con.execute("UPDATE orders SET status=? WHERE id=?", (status, oid))


def user_orders(uid: int):
    with db() as con:
        return con.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10", (uid,)).fetchall()


def last_orders(n=15):
    with db() as con:
        return con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (n,)).fetchall()


def service_label(o) -> str:
    svc = CATALOG[o["audience"]]["services"][o["service"]]
    label = svc["name"]
    if o["package"]:
        label += f" — {svc['packages'][o['package']][0]}"
    return label


def order_text(o, for_admin=False) -> str:
    t = (f"<b>Buyurtma #{o['id']}</b>\n"
         f"📦 {service_label(o)}\n"
         f"📝 Mavzu: {html.escape(o['topic'])}\n")
    if o["details"]:
        t += f"ℹ️ Qo'shimcha: {html.escape(o['details'])}\n"
    t += (f"⏱ Muddat: {DEADLINES.get(o['deadline'], o['deadline'])}\n"
          f"💰 Narx: <b>{money(o['price'])}</b>\n"
          f"Holat: {STATUS.get(o['status'], o['status'])}")
    if for_admin:
        uname = f"@{o['username']}" if o["username"] else "username yo'q"
        t += (f"\n\n👤 {html.escape(o['full_name'])} ({uname})\n🆔 <code>{o['user_id']}</code>"
              + (f"\n📞 {o['phone']}" if o["phone"] else "") + f"\n🕐 {o['created_at']}")
    return t


# ------------------------------------------------------------------ klaviaturalar
def _strip_emoji(text: str) -> str:
    """Premium ikonka qo'yilganda boshidagi oddiy emojini olib tashlaydi."""
    head, _, rest = text.partition(" ")
    return rest if rest and not any(ch.isalnum() for ch in head) else text


def kbtn(text, style=None, icon=None, **kw):
    """Rangli pastki tugma. style: primary (ko'k), success (yashil), danger (qizil)."""
    extra = {}
    if style:
        extra["style"] = style
    if icon and EMOJI_IDS.get(icon):
        extra["icon_custom_emoji_id"] = EMOJI_IDS[icon]
        text = _strip_emoji(text)
    return KeyboardButton(text=text, **extra, **kw)


def main_kb():
    rows = []
    if WEBAPP_URL:
        rows.append([kbtn("✨ Mini ilova", "primary", "app", web_app=WebAppInfo(url=WEBAPP_URL + "/"))])
    rows += [
        [kbtn("🛒 Buyurtma berish", "success", "order")],
        [kbtn("💰 Narxlar", "primary", "prices"), kbtn("🎨 Namunalar", "primary", "samples")],
        [kbtn("📦 Buyurtmalarim", None, "orders"), kbtn("📞 Aloqa", None, "contact")],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=rows)


MAIN_KB = main_kb()


def ibtn(text, data, style=None, icon=None):
    extra = {}
    if style:
        extra["style"] = style
    if icon and EMOJI_IDS.get(icon):
        extra["icon_custom_emoji_id"] = EMOJI_IDS[icon]
        text = _strip_emoji(text)
    return InlineKeyboardButton(text=text, callback_data=data, **extra)


def ikb(rows):
    """rows: [[(matn, data[, style[, icon]]), ...], ...]"""
    return InlineKeyboardMarkup(inline_keyboard=[[ibtn(*b) for b in row] for row in rows])


def audience_kb(prefix="aud"):
    return ikb([[(CATALOG["s"]["title"], f"{prefix}:s", "primary", "student")],
                [(CATALOG["t"]["title"], f"{prefix}:t", "success", "teacher")]])


SVC_ICON = {"taqdimot": "image", "dars": "image", "mustaqil": "edit", "kurs": "channel",
            "portfolio": "star", "oum": "bot", "tadbir": "fire"}


def services_kb(aud):
    rows = []
    for key, s in CATALOG[aud]["services"].items():
        price = min(p[1] for p in s["packages"].values()) if "packages" in s else s["price"]
        rows.append([(f"{s['name']} — {money(price)}dan" if "packages" in s else f"{s['name']} — {money(price)}",
                      f"svc:{aud}:{key}", None, SVC_ICON.get(key))])
    rows.append([("⬅️ Orqaga", "back:aud", "danger", "cancel")])
    return ikb(rows)


def packages_kb(aud, svc):
    pk = CATALOG[aud]["services"][svc]["packages"]
    styles = {"start": None, "pro": "primary", "premium": "success"}
    icons = {"start": "star", "pro": "fire", "premium": "heart"}
    rows = [[(f"{v[0]} — {money(v[1])}", f"pkg:{aud}:{svc}:{k}", styles.get(k), icons.get(k))] for k, v in pk.items()]
    rows.append([("🎨 Namunalarni ko'rish", "samples", None, "samples")])
    rows.append([("⬅️ Orqaga", f"aud:{aud}", "danger")])
    return ikb(rows)


SKIP_KB = ikb([[("⏭ O'tkazib yuborish", "skip", "primary")]])
DEADLINE_KB = ikb([[(DEADLINES["normal"], "dl:normal", "primary", "orders")], [(DEADLINES["urgent"], "dl:urgent", "danger", "fire")]])
CONFIRM_KB = ikb([[("✅ Tasdiqlash", "confirm", "success", "ok")],
                  [("✏️ Qaytadan", "restart", "primary", "edit"), ("❌ Bekor qilish", "cancel", "danger", "cancel")]])


def admin_kb(oid, status):
    if status == "paid":
        return ikb([[("✅ To'lov tasdiqlandi", f"adm:ok:{oid}", "success", "ok"), ("❌ Rad etish", f"adm:no:{oid}", "danger", "cancel")]])
    if status == "work":
        return ikb([[("📤 Tayyor ishni yuborish", f"adm:send:{oid}", "primary")]])
    return None


# ------------------------------------------------------------------ holatlar
class Order(StatesGroup):
    topic = State()
    details = State()
    files = State()
    deadline = State()
    confirm = State()
    cheque = State()


class AdminSend(StatesGroup):
    file = State()


router = Router()


def is_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


async def notify_admins(bot: Bot, text: str, kb=None, photo=None, document=None):
    for aid in ADMIN_IDS:
        try:
            if photo:
                await bot.send_photo(aid, photo, caption=text, reply_markup=kb)
            elif document:
                await bot.send_document(aid, document, caption=text, reply_markup=kb)
            else:
                await bot.send_message(aid, text, reply_markup=kb)
        except Exception as e:  # admin botni bloklagan bo'lishi mumkin
            logging.warning("Adminga yuborilmadi %s: %s", aid, e)


# ------------------------------------------------------------------ asosiy menyu
@router.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    text = (f"Assalomu alaykum, <b>{html.escape(m.from_user.first_name)}</b>! {pe('hi', '👋')}\n\n"
            f"{pe('star', '✨')} <b>{BOT_NAME}</b> — taqdimot, portfolio, mustaqil ish va kurs ishlarini "
            "chiroyli dizaynda, o'z vaqtida tayyorlab beradi.\n\n"
            f"{pe('student', '🎓')} Talabalar uchun — <b>40 000 so'mdan</b>\n"
            f"{pe('teacher', '👩‍🏫')} Ustozlar uchun — <b>60 000 so'mdan</b>\n\n"
            + (f"{pe('app', '📱')} <b>«✨ Mini ilova»</b> tugmasini bosib, hammasini chiroyli ko'rinishda ko'ring!\n\n" if WEBAPP_URL else "")
            + f"Quyidagi menyudan tanlang {pe('down', '👇')}")
    banner = ASSETS / "banner.png"
    if banner.exists():
        await m.answer_photo(FSInputFile(banner), caption=text, reply_markup=MAIN_KB)
    else:
        await m.answer(text, reply_markup=MAIN_KB)


@router.message(F.text.in_({"🛒 Buyurtma berish", "Buyurtma berish"}))
@router.message(Command("order"))
async def order_start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Kim uchun buyurtma? 👇", reply_markup=audience_kb())


@router.message(F.text.in_({"💰 Narxlar", "Narxlar"}))
async def prices(m: Message):
    imgs = [ASSETS / "prices_students.png", ASSETS / "prices_teachers.png"]
    if all(p.exists() for p in imgs):
        await m.answer_media_group([InputMediaPhoto(media=FSInputFile(p)) for p in imgs])
    else:
        await m.answer(prices_text())
    await m.answer(f"⚡ Shoshilinch buyurtma: <b>+{int(URGENT_EXTRA*100)}%</b>\n🔁 Tuzatishlar bepul\n\n"
                   "Buyurtma berish uchun tugmani bosing 👇", reply_markup=ikb([[("🛒 Buyurtma berish", "go_order", "success", "order")]]))


def prices_text() -> str:
    parts = []
    for aud in CATALOG.values():
        lines = [f"<b>{aud['title']}</b>"]
        for s in aud["services"].values():
            if "packages" in s:
                lines.append(f"• {s['name']}:")
                for name, price, desc in s["packages"].values():
                    lines.append(f"    ◦ {name} — <b>{money(price)}</b>\n       <i>{desc}</i>")
            else:
                lines.append(f"• {s['name']} — <b>{money(s['price'])}</b>dan\n    <i>{s['desc']}</i>")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


@router.callback_query(F.data == "go_order")
async def go_order(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer("Kim uchun buyurtma? 👇", reply_markup=audience_kb())
    await c.answer()


@router.message(F.text.in_({"🎨 Namunalar", "Namunalar"}))
async def samples_msg(m: Message):
    await send_samples(m)


@router.callback_query(F.data == "samples")
async def samples_cb(c: CallbackQuery):
    await c.answer()
    await send_samples(c.message)


def sample_files():
    # namunalar: "1_..pptx", "2_..pptx", "4_..mp4" kabi raqam bilan boshlanadigan fayllar
    return sorted(p for p in SAMPLES.glob("[0-9]_*") if p.is_file())


async def send_samples(m: Message):
    files = sample_files()
    if not files:
        await m.answer("Namunalar tez orada qo'shiladi 🙂")
        return
    await m.answer("Mana ishlarimdan namunalar 👇\n<i>Animatsiyalar kompyuterdagi PowerPoint'da to'liq ko'rinadi.</i>")
    for p in files:
        try:
            if p.suffix.lower() == ".mp4":
                await m.answer_video(FSInputFile(p))
            else:
                await m.answer_document(FSInputFile(p))
        except Exception as e:
            logging.warning("Namuna yuborilmadi %s: %s", p, e)


@router.message(F.text.in_({"📦 Buyurtmalarim", "Buyurtmalarim"}))
async def my_orders(m: Message):
    rows = user_orders(m.from_user.id)
    if not rows:
        await m.answer("Sizda hali buyurtma yo'q. «🛒 Buyurtma berish» tugmasini bosing.")
        return
    await m.answer("\n\n".join(order_text(o) for o in rows))


@router.message(F.text.in_({"📞 Aloqa", "Aloqa"}))
async def contact(m: Message):
    await m.answer(f"Savollar bo'lsa yozing: {CONTACT}")


# ------------------------------------------------------------------ buyurtma oqimi
@router.callback_query(F.data == "back:aud")
async def back_aud(c: CallbackQuery):
    await c.message.edit_text("Kim uchun buyurtma? 👇", reply_markup=audience_kb())
    await c.answer()


@router.callback_query(F.data.startswith("aud:"))
async def choose_aud(c: CallbackQuery, state: FSMContext):
    aud = c.data.split(":")[1]
    await state.update_data(aud=aud)
    await c.message.edit_text(f"<b>{CATALOG[aud]['title']}</b>\nXizmatni tanlang 👇", reply_markup=services_kb(aud))
    await c.answer()


@router.callback_query(F.data.startswith("svc:"))
async def choose_svc(c: CallbackQuery, state: FSMContext):
    _, aud, svc = c.data.split(":")
    s = CATALOG[aud]["services"][svc]
    await state.update_data(aud=aud, svc=svc, pkg="")
    if "packages" in s:
        txt = [f"<b>{s['name']}</b> — paketni tanlang:\n"]
        for name, price, desc in s["packages"].values():
            txt.append(f"• <b>{name}</b> — {money(price)}\n  <i>{desc}</i>")
        await c.message.edit_text("\n".join(txt), reply_markup=packages_kb(aud, svc))
    else:
        await state.update_data(base_price=s["price"])
        await ask_topic(c.message, state, f"<b>{s['name']}</b> — {money(s['price'])}dan\n<i>{s['desc']}</i>")
    await c.answer()


@router.callback_query(F.data.startswith("pkg:"))
async def choose_pkg(c: CallbackQuery, state: FSMContext):
    _, aud, svc, pkg = c.data.split(":")
    name, price, desc = CATALOG[aud]["services"][svc]["packages"][pkg]
    await state.update_data(aud=aud, svc=svc, pkg=pkg, base_price=price)
    await ask_topic(c.message, state, f"Tanlandi: <b>{name}</b> — {money(price)}\n<i>{desc}</i>")
    await c.answer()


async def ask_topic(m: Message, state: FSMContext, header: str):
    await state.set_state(Order.topic)
    await m.answer(f"{header}\n\n📝 <b>Mavzuni yozing</b> (masalan: «Sun'iy intellekt ta'limda»):")


@router.message(Order.topic, F.text)
async def got_topic(m: Message, state: FSMContext):
    if len(m.text) > 300:
        await m.answer("Mavzu juda uzun, qisqaroq yozing (300 belgigacha).")
        return
    await state.update_data(topic=m.text.strip())
    await state.set_state(Order.details)
    await m.answer("ℹ️ <b>Qo'shimcha talablar?</b>\nMasalan: fan nomi, o'qituvchi, slayd soni, ism-familiya, rang…\n"
                   "Bo'lmasa — o'tkazib yuboring.", reply_markup=SKIP_KB)


@router.message(Order.details, F.text)
async def got_details(m: Message, state: FSMContext):
    await state.update_data(details=m.text.strip()[:1000])
    await ask_files(m, state)


@router.callback_query(Order.details, F.data == "skip")
async def skip_details(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await ask_files(c.message, state)


async def ask_files(m: Message, state: FSMContext):
    await state.set_state(Order.files)
    await state.update_data(files=[])
    await m.answer("📎 <b>Fayl yoki rasm bormi?</b> (namuna, topshiriq sharti, rasmlar)\n"
                   "Yuboring, tugatgach «✅ Tayyor» tugmasini bosing. Bo'lmasa — o'tkazib yuboring.",
                   reply_markup=ikb([[("✅ Tayyor / O'tkazish", "files_done", "success")]]))


@router.message(Order.files, F.document | F.photo)
async def got_file(m: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get("files", [])
    if len(files) >= 10:
        await m.answer("Ko'pi bilan 10 ta fayl. «✅ Tayyor» ni bosing.")
        return
    if m.document:
        files.append({"type": "doc", "id": m.document.file_id})
    else:
        files.append({"type": "photo", "id": m.photo[-1].file_id})
    await state.update_data(files=files)
    await m.answer(f"Qabul qilindi ({len(files)} ta). Yana yuboring yoki «✅ Tayyor» ni bosing.",
                   reply_markup=ikb([[("✅ Tayyor", "files_done", "success")]]))


@router.callback_query(Order.files, F.data == "files_done")
async def files_done(c: CallbackQuery, state: FSMContext):
    await c.answer()
    data = await state.get_data()
    if data.get("deadline"):  # Mini ilovadan kelgan — muddat tanlangan
        await show_confirm(c.message, state)
        return
    await state.set_state(Order.deadline)
    await c.message.answer("⏱ <b>Muddatni tanlang:</b>", reply_markup=DEADLINE_KB)


@router.callback_query(Order.deadline, F.data.startswith("dl:"))
async def got_deadline(c: CallbackQuery, state: FSMContext):
    await state.update_data(deadline=c.data.split(":")[1])
    await show_confirm(c.message, state)
    await c.answer()


async def show_confirm(m: Message, state: FSMContext):
    data = await state.get_data()
    dl = data["deadline"]
    price = int(data["base_price"] * (1 + URGENT_EXTRA)) if dl == "urgent" else data["base_price"]
    price = round(price / 1000) * 1000
    await state.update_data(price=price)
    await state.set_state(Order.confirm)
    s = CATALOG[data["aud"]]["services"][data["svc"]]
    label = s["name"] + (f" — {s['packages'][data['pkg']][0]}" if data.get("pkg") else "")
    txt = (f"{pe('check', '📋')} <b>Buyurtmangizni tekshiring:</b>\n\n"
           f"📦 {label}\n📝 Mavzu: {html.escape(data['topic'])}\n"
           + (f"ℹ️ Qo'shimcha: {html.escape(data['details'])}\n" if data.get("details") else "")
           + f"📎 Fayllar: {len(data.get('files', []))} ta\n"
           f"⏱ Muddat: {DEADLINES[dl]}\n\n{pe('money', '💰')} Jami: <b>{money(price)}</b>")
    await m.answer(txt, reply_markup=CONFIRM_KB)


# ------------------------------------------------------------------ Mini ilova
@router.message(F.web_app_data)
async def webapp_data(m: Message, state: FSMContext):
    try:
        d = json.loads(m.web_app_data.data)
    except (json.JSONDecodeError, TypeError):
        await m.answer("Ma'lumot o'qilmadi, qaytadan urinib ko'ring.")
        return
    if d.get("cmd") == "samples":
        await send_samples(m)
        return
    if d.get("cmd") != "order":
        return
    aud, svc, pkg = d.get("aud"), d.get("svc"), d.get("pkg") or ""
    s = CATALOG.get(aud, {}).get("services", {}).get(svc)
    if not s or ("packages" in s and pkg not in s["packages"]):
        await m.answer("Xizmat yoki paket topilmadi. Qaytadan tanlang.")
        return
    topic = str(d.get("topic", "")).strip()[:300]
    if len(topic) < 2:
        await m.answer("Mavzu yozilmagan.")
        return
    base = s["packages"][pkg][1] if "packages" in s else s["price"]
    await state.clear()
    await state.update_data(aud=aud, svc=svc, pkg=pkg if "packages" in s else "", base_price=base, topic=topic,
                            details=str(d.get("details", "")).strip()[:1000],
                            deadline="urgent" if d.get("deadline") == "urgent" else "normal")
    await m.answer(f"{pe('app', '✨')} Mini ilovadan buyurtma qabul qilindi!", reply_markup=MAIN_KB)
    await ask_files(m, state)


@router.callback_query(F.data == "restart")
async def restart(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer("Qaytadan boshlaymiz. Kim uchun buyurtma? 👇", reply_markup=audience_kb())
    await c.answer()


@router.callback_query(F.data == "cancel")
async def cancel(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer("Buyurtma bekor qilindi.", reply_markup=MAIN_KB)
    await c.answer()


@router.callback_query(Order.confirm, F.data == "confirm")
async def confirm(c: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    oid = create_order(data, c.from_user)
    await state.set_state(Order.cheque)
    await state.update_data(order_id=oid)
    await c.message.answer(
        f"✅ <b>Buyurtma #{oid} qabul qilindi!</b>\n\n"
        f"💳 To'lov uchun karta:\n<code>{CARD_NUMBER}</code>\n👤 {CARD_OWNER}\n\n"
        f"💰 Summa: <b>{money(data['price'])}</b>\n\n"
        "To'lovdan so'ng <b>chek rasmini (skrinshot)</b> shu yerga yuboring 📸",
        reply_markup=MAIN_KB)
    o = get_order(oid)
    await notify_admins(bot, "🆕 Yangi buyurtma (to'lov kutilmoqda)\n\n" + order_text(o, True))
    for f in data.get("files", []):
        for aid in ADMIN_IDS:
            try:
                if f["type"] == "photo":
                    await bot.send_photo(aid, f["id"], caption=f"#{oid} fayli")
                else:
                    await bot.send_document(aid, f["id"], caption=f"#{oid} fayli")
            except Exception as e:
                logging.warning("Fayl yuborilmadi: %s", e)
    await c.answer()


@router.message(Order.cheque, F.photo | F.document)
async def got_cheque(m: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    oid = data["order_id"]
    set_status(oid, "paid")
    await state.clear()
    await m.answer("🧾 Chek qabul qilindi! Tekshirib, tez orada ishni boshlaymiz. "
                   "Holatini «📦 Buyurtmalarim» bo'limida ko'rasiz.", reply_markup=MAIN_KB)
    o = get_order(oid)
    text = "🧾 Chek keldi!\n\n" + order_text(o, True)
    if m.photo:
        await notify_admins(bot, text, admin_kb(oid, "paid"), photo=m.photo[-1].file_id)
    else:
        await notify_admins(bot, text, admin_kb(oid, "paid"), document=m.document.file_id)


@router.message(Order.cheque)
async def cheque_wrong(m: Message):
    await m.answer("Iltimos, to'lov <b>chekining rasmini</b> yuboring 📸")


# ------------------------------------------------------------------ admin
@router.callback_query(F.data.startswith("adm:"))
async def admin_action(c: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(c.from_user.id):
        await c.answer("Ruxsat yo'q", show_alert=True)
        return
    _, act, oid = c.data.split(":")
    oid = int(oid)
    o = get_order(oid)
    if not o:
        await c.answer("Buyurtma topilmadi", show_alert=True)
        return
    if act == "ok":
        set_status(oid, "work")
        await bot.send_message(o["user_id"], f"✅ To'lov tasdiqlandi! Buyurtma #{oid} tayyorlanmoqda 🛠")
        await c.message.answer(f"#{oid} — ishga olindi. Tayyor bo'lgach tugmani bosing:", reply_markup=admin_kb(oid, "work"))
    elif act == "no":
        set_status(oid, "rejected")
        await bot.send_message(o["user_id"], f"❌ Buyurtma #{oid} bo'yicha to'lov tasdiqlanmadi.\n"
                                             f"Savol bo'lsa: {CONTACT}")
        await c.message.answer(f"#{oid} — rad etildi.")
    elif act == "send":
        await state.set_state(AdminSend.file)
        await state.update_data(send_oid=oid)
        await c.message.answer(f"#{oid} uchun tayyor faylni yuboring (bir nechta bo'lishi mumkin). "
                               "Tugatgach /done yozing.")
    await c.answer()


@router.message(AdminSend.file, Command("done"))
async def admin_done(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data())["send_oid"]
    set_status(oid, "done")
    await state.clear()
    o = get_order(oid)
    await bot.send_message(o["user_id"], f"🎉 Buyurtma #{oid} tayyor! Rahmat 🙏\n"
                                         f"Tuzatish kerak bo'lsa yozing: {CONTACT}")
    await m.answer(f"#{oid} — topshirildi ✅")


@router.message(AdminSend.file, F.document | F.photo | F.video)
async def admin_file(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data())["send_oid"]
    o = get_order(oid)
    cap = f"📦 Buyurtma #{oid}"
    if m.document:
        await bot.send_document(o["user_id"], m.document.file_id, caption=cap)
    elif m.video:
        await bot.send_video(o["user_id"], m.video.file_id, caption=cap)
    else:
        await bot.send_photo(o["user_id"], m.photo[-1].file_id, caption=cap)
    await m.answer("Yuborildi. Yana fayl bo'lsa yuboring yoki /done.")


@router.message(Command("orders"))
async def admin_orders(m: Message):
    if not is_admin(m.from_user.id):
        return
    rows = last_orders()
    if not rows:
        await m.answer("Buyurtmalar yo'q.")
        return
    for o in rows:
        await m.answer(order_text(o, True), reply_markup=admin_kb(o["id"], o["status"]))


@router.message(Command("emoji"))
async def emoji_help(m: Message):
    if is_admin(m.from_user.id):
        await m.answer("Premium emoji ID olish: menga premium emojili xabar yuboring — ID'larini qaytaraman.")


@router.message(lambda m: bool(m.entities) and any(e.type == "custom_emoji" for e in m.entities))
async def emoji_ids(m: Message, state: FSMContext):
    if not is_admin(m.from_user.id) or await state.get_state() is not None:
        return
    ids = [e.custom_emoji_id for e in m.entities if e.type == "custom_emoji"]
    await m.answer("Emoji ID'lari:\n" + "\n".join(f"<code>{i}</code>" for i in ids))


@router.message(Command("privacy"))
async def privacy_cmd(m: Message):
    url = f"{WEBAPP_URL}/privacy" if WEBAPP_URL else None
    await m.answer(f"🔒 Maxfiylik siyosati: {url}" if url else f"🔒 Maxfiylik siyosati bo'yicha savollar: {CONTACT}")


@router.message(Command("myid"))
async def myid(m: Message):
    await m.answer(f"Sizning ID: <code>{m.from_user.id}</code>")


@router.message(F.text)
async def fallback(m: Message, state: FSMContext):
    if await state.get_state() is None:
        await m.answer("Menyudan tanlang 👇", reply_markup=MAIN_KB)


# ------------------------------------------------------------------ ishga tushirish
# ------------------------------------------------------------------ veb-server (Mini ilova)
def catalog_json():
    return {"urgent": URGENT_EXTRA,
            **{a: {"title": v["title"], "services": v["services"]} for a, v in CATALOG.items()}}


def make_web_app():
    app = web.Application()

    async def index(_):
        return web.FileResponse(WEBAPP_DIR / "index.html")

    async def catalog(_):
        return web.json_response(catalog_json())

    async def health(_):
        return web.Response(text="ok")

    app.router.add_get("/", index)
    async def privacy(_):
        return web.FileResponse(WEBAPP_DIR / "privacy.html")

    app.router.add_get("/privacy", privacy)
    app.router.add_get("/api/catalog", catalog)
    app.router.add_get("/health", health)
    allowed = {p.name: p for p in sample_files()}

    async def sample(request):
        p = allowed.get(request.match_info["name"])
        if not p:
            raise web.HTTPNotFound()
        return web.FileResponse(p)

    app.router.add_get("/samples/{name}", sample)
    return app


async def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN o'rnatilmagan")
    init_db()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    runner = web.AppRunner(make_web_app())
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    logging.info("Mini ilova serveri %s portda ishga tushdi", PORT)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
