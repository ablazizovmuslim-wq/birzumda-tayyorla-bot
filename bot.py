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
from urllib.parse import quote
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, InputMediaPhoto, KeyboardButton, LinkPreviewOptions,
                           Message, ReplyKeyboardMarkup, WebAppInfo)

# ------------------------------------------------------------------ sozlamalar
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_ID", "0").replace(" ", "").split(",") if x}
CARD_NUMBER = os.getenv("CARD_NUMBER", "0000 0000 0000 0000")
CARD_OWNER = os.getenv("CARD_OWNER", "Ism Familiya")
CONTACT = os.getenv("CONTACT", "@Abdulazizov_prince")
CHANNEL = os.getenv("CHANNEL", "@Birzumda_Tayyorla").strip()
OTHER_BOTS = os.getenv("OTHER_BOTS", "@Birzumda_Yukla_bot")  # boshqa Birzumda botlari  # bot kanali: @username yoki https://t.me/... havola
DB_PATH = os.getenv("DB_PATH", "orders.db")
BASE = Path(__file__).parent
SAMPLES = BASE
ASSETS = BASE
BOT_NAME = os.getenv("BOT_NAME", "Birzumda Taqdimot")
URGENT_EXTRA = 0.5  # shoshilinch: +50%
# --- referal / bonus / aksiya
BOT_USERNAME = os.getenv("BOT_USERNAME", "Birzumda_Tayyorla_bot")
REF_BONUS = int(os.getenv("REF_BONUS", "5000"))       # taklif qilganga: do'sti birinchi to'lovni qilganda
REF_WELCOME = int(os.getenv("REF_WELCOME", "5000"))   # taklif qilinganga: birinchi buyurtmaga chegirma
BONUS_MAX_PCT = int(os.getenv("BONUS_MAX_PCT", "30"))  # bonus bilan buyurtmaning ko'pi bilan 30% to'lanadi
MAX_DISCOUNT_PCT = 50                                   # barcha chegirmalar jami ko'pi bilan 50%
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

from texts import (BTN, CAT_TR, CHANNEL_LINE, COMMANDS, CURRENCY, DESCRIPTION, SHORT_DESC, DEFAULT_LANG, FROM, LANGS, NEGOTIABLE, TURTLE_LONG, TX,  # noqa: E402
                   DEADLINES as DL_TR, STATUS as ST_TR)

# Matnlardagi {e[kalit]} uchun premium emoji (ID bo'lmasa oddiy emoji)
E_FALLBACK = {"hi": "👋", "star": "✨", "bot": "🤖", "student": "🎓", "teacher": "👩‍🏫", "edit": "✍️",
              "heart": "🎁", "ok": "✅", "image": "🎨", "fire": "⚡", "orders": "📋", "contact": "💜",
              "down": "👇", "money": "💰", "check": "📋", "globe": "🌐", "app": "✨", "channel": "📢",
              "n1": "1️⃣", "n2": "2️⃣", "n3": "3️⃣", "n4": "4️⃣"}
E = {k: pe(k, v) for k, v in E_FALLBACK.items()}


def tr(lang: str, key: str, **kw) -> str:
    t = TX[key].get(lang) or TX[key][DEFAULT_LANG]
    return t.format(e=E, **kw)


def b(lang: str, key: str, **kw) -> str:
    t = BTN[key].get(lang) or BTN[key][DEFAULT_LANG]
    return t.format(**kw) if kw else t

# ------------------------------------------------------------------ narxlar
# packages: (nomi, narx, tavsif)
CATALOG = {
    "s": {
        "title": "🎓 Talabalar uchun",
        "services": {
            "taqdimot": {"name": "Slayd (taqdimot)", "packages": {
                "start": ("Start", 25000, "10–12 slayd, zamonaviy dizayn, 1 kun"),
                "pro": ("Professional", 35000, "15–20 slayd, animatsiya, diagrammalar, 🐢 Toshbaqa o'qituvchi, 1–2 kun"),
                "premium": ("Premium", 50000, "20–25 slayd, Morph, neon dizayn, 🐢 Toshbaqa o'qituvchi, nutq matni, 2–3 kun"),
            }},
            "mustaqil": {"name": "Mustaqil ish", "price": 35000, "desc": "Word formatda, chiroyli muqova bilan"},
            "kurs": {"name": "Kurs ishi", "price": 50000, "desc": "Reja, boblar, xulosa, adabiyotlar ro'yxati"},
            "maqola": {"name": "Maqola / tezis", "price": 40000, "desc": "Ilmiy maqola yoki konferensiya tezisi"},
            "amaliy": {"name": "Amaliy / laboratoriya ishi", "price": 20000, "desc": "Topshiriq sharti asosida, hisobot bilan"},
            "referat": {"name": "Referat", "price": 20000, "desc": "Reja, matn, adabiyotlar, chiroyli muqova"},
            "portfolio": {"name": "Portfolio", "price": 30000, "desc": "Talaba portfoliosi va rezyume"},
            "boshqa": {"name": "Boshqa — o'zingiz yozing", "price": None, "desc": "Ro'yxatda yo'q ishni yozing, narxni kelishamiz"},
        },
    },
    "t": {
        "title": "👩‍🏫 Ustozlar uchun",
        "services": {
            "dars": {"name": "Taqdimot (slayd)", "packages": {
                "start": ("Start", 50000, "12–15 slayd, ochiq dars uchun"),
                "pro": ("Professional", 80000, "15–20 slayd, animatsiya, diagrammalar, 🐢 Toshbaqa o'qituvchi"),
                "premium": ("Premium", 120000, "20–25 slayd, Morph, 🐢 Toshbaqa o'qituvchi, nutq matni, video"),
            }},
            "portfolio": {"name": "Portfolio", "price": 90000, "desc": "Attestatsiya va «Eng yaxshi tyutor» tanlovi"},
            "oum": {"name": "O'quv-uslubiy majmua", "price": 200000, "desc": "Ma'ruza, amaliy mashg'ulot, testlar"},
            "ishlanma": {"name": "Dars ishlanmasi", "price": 45000, "desc": "Ochiq dars yoki kundalik dars rejasi"},
            "maqola": {"name": "Ilmiy maqola / tezis", "price": 90000, "desc": "Jurnal yoki konferensiya uchun"},
            "test": {"name": "Test va topshiriqlar", "price": 40000, "desc": "Fan bo'yicha test, savollar, keyslar"},
            "tadbir": {"name": "Tadbir taqdimoti", "price": 60000, "desc": "Konferensiya, tadbir, hisobot"},
            "boshqa": {"name": "Boshqa — o'zingiz yozing", "price": None, "desc": "Kerakli ishni yozing, narxni kelishamiz"},
        },
    },
}

DEADLINES = {"normal": "Oddiy muddat", "urgent": f"⚡ Shoshilinch (+{int(URGENT_EXTRA * 100)}%)"}


def dl_name(key: str, lang: str = "uz") -> str:
    return DL_TR[key][lang].format(pct=int(URGENT_EXTRA * 100)) if key in DL_TR else key

STATUS = {
    "quote": "💬 Narx kelishilmoqda",
    "new": "🕐 To'lov kutilmoqda",
    "paid": "🧾 Chek tekshirilmoqda",
    "work": "🛠 Tayyorlanmoqda",
    "done": "✅ Topshirildi",
    "rejected": "❌ Rad etildi",
}


def som(n, lang: str = "uz") -> str:
    """Bonus va chegirmalar uchun: 0 bo'lsa ham «0 so'm»."""
    return f"{n or 0:,}".replace(",", " ") + " " + CURRENCY.get(lang, "so'm")


def money(n, lang: str = "uz") -> str:
    if not n:
        return NEGOTIABLE.get(lang, "kelishiladi")
    return som(n, lang)


def price_from(n, lang: str = "uz") -> str:
    return FROM[lang].format(p=money(n, lang)) if n else money(n, lang)


# ------------------------------------------------------------------ katalog tarjimasi
def aud_title(aud: str, lang: str) -> str:
    return CAT_TR.get(lang, {}).get(aud, {}).get("title") or CATALOG[aud]["title"]


def svc_tr(aud: str, key: str, lang: str):
    """(nomi, tavsifi) foydalanuvchi tilida."""
    base = CATALOG[aud]["services"][key]
    t = CAT_TR.get(lang, {}).get(aud, {}).get("services", {}).get(key, {})
    return t.get("name", base["name"]), t.get("desc", base.get("desc", ""))


def pkg_tr(aud: str, svc: str, pkg: str, lang: str):
    """(paket nomi, tavsifi) foydalanuvchi tilida."""
    base = CATALOG[aud]["services"][svc]["packages"][pkg]
    t = CAT_TR.get(lang, {}).get(aud, {}).get("services", {}).get(svc, {}).get("packages", {}).get(pkg)
    return (t[0], t[1]) if t else (base[0], base[2])


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
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT,
            joined_at TEXT, last_seen TEXT, blocked INTEGER DEFAULT 0)""")
        con.execute("""CREATE TABLE IF NOT EXISTS promos(
            code TEXT PRIMARY KEY, percent INTEGER, uses_left INTEGER, used INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1, created_at TEXT)""")
        con.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)")
        # eski bazaga yangi ustunlar (bir marta qo'shiladi)
        for table, col, decl in [
            ("users", "referred_by", "INTEGER"), ("users", "bonus", "INTEGER DEFAULT 0"),
            ("users", "ref_rewarded", "INTEGER DEFAULT 0"), ("users", "welcome_used", "INTEGER DEFAULT 0"), ("users", "lang", "TEXT"),
            ("orders", "full_price", "INTEGER DEFAULT 0"), ("orders", "discount", "INTEGER DEFAULT 0"),
            ("orders", "promo", "TEXT DEFAULT ''"), ("orders", "bonus_used", "INTEGER DEFAULT 0"),
            ("orders", "welcome", "INTEGER DEFAULT 0")]:
            cols = {r["name"] for r in con.execute(f"PRAGMA table_info({table})")}
            if col not in cols:
                con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")


def touch_user(user):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with db() as con:
        con.execute("""INSERT INTO users(user_id, username, full_name, joined_at, last_seen, blocked)
                       VALUES(?,?,?,?,?,0)
                       ON CONFLICT(user_id) DO UPDATE SET username=excluded.username,
                       full_name=excluded.full_name, last_seen=excluded.last_seen, blocked=0""",
                    (user.id, user.username or "", user.full_name, now, now))


LANG_CACHE: dict[int, str] = {}


def get_lang(uid: int):
    """Tanlangan til yoki None (hali tanlamagan)."""
    if uid in LANG_CACHE:
        return LANG_CACHE[uid]
    with db() as con:
        r = con.execute("SELECT lang FROM users WHERE user_id=?", (uid,)).fetchone()
    lang = r["lang"] if r and r["lang"] in LANGS else None
    if lang:
        LANG_CACHE[uid] = lang
    return lang


def L(uid: int) -> str:
    return get_lang(uid) or DEFAULT_LANG


def set_lang(uid: int, lang: str):
    with db() as con:
        con.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, uid))
    LANG_CACHE[uid] = lang


def all_user_ids():
    with db() as con:
        return [r["user_id"] for r in con.execute("SELECT user_id FROM users WHERE blocked=0")]


def mark_blocked(uid: int):
    with db() as con:
        con.execute("UPDATE users SET blocked=1 WHERE user_id=?", (uid,))


def user_stats():
    with db() as con:
        total = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        blocked = con.execute("SELECT COUNT(*) FROM users WHERE blocked=1").fetchone()[0]
        today = con.execute("SELECT COUNT(*) FROM users WHERE joined_at LIKE ?",
                            (datetime.now().strftime("%Y-%m-%d") + "%",)).fetchone()[0]
        orders = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        done = con.execute("SELECT COUNT(*) FROM orders WHERE status='done'").fetchone()[0]
    return total, blocked, today, orders, done


def create_order(data: dict, user) -> int:
    with db() as con:
        cur = con.execute(
            """INSERT INTO orders(user_id, username, full_name, phone, audience, service, package, price,
               topic, details, deadline, files, status, created_at, full_price, discount, promo, bonus_used, welcome)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (user.id, user.username or "", user.full_name, data.get("phone", ""), data["aud"], data["svc"],
             data.get("pkg", ""), data["price"], data["topic"], data.get("details", ""), data["deadline"],
             json.dumps(data.get("files", [])), "new", datetime.now().strftime("%Y-%m-%d %H:%M"),
             data.get("full_price", data["price"]), data.get("discount", 0), data.get("promo", ""),
             data.get("bonus_used", 0), data.get("welcome", 0)))
        return cur.lastrowid


# ------------------------------------------------------------------ referal, bonus, promokod
def get_user(uid: int):
    with db() as con:
        return con.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()


def order_count(uid: int) -> int:
    with db() as con:
        return con.execute("SELECT COUNT(*) FROM orders WHERE user_id=? AND status!='rejected'",
                           (uid,)).fetchone()[0]


def set_referrer(uid: int, ref: int) -> bool:
    """Do'st havolasi orqali kelganini yozadi. Faqat yangi (buyurtmasiz) foydalanuvchi uchun."""
    if uid == ref or not get_user(ref) or order_count(uid):
        return False
    with db() as con:
        cur = con.execute("UPDATE users SET referred_by=? WHERE user_id=? AND referred_by IS NULL", (ref, uid))
        return cur.rowcount > 0


def ref_stats(uid: int):
    with db() as con:
        invited = con.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (uid,)).fetchone()[0]
        paid = con.execute("SELECT COUNT(*) FROM users WHERE referred_by=? AND ref_rewarded=1", (uid,)).fetchone()[0]
    return invited, paid


def bonus_balance(uid: int) -> int:
    u = get_user(uid)
    return (u["bonus"] or 0) if u else 0


def add_bonus(uid: int, amount: int):
    with db() as con:
        con.execute("UPDATE users SET bonus=MAX(0, COALESCE(bonus,0)+?) WHERE user_id=?", (amount, uid))


def take_bonus(uid: int, amount: int) -> bool:
    with db() as con:
        cur = con.execute("UPDATE users SET bonus=bonus-? WHERE user_id=? AND bonus>=?", (amount, uid, amount))
        return cur.rowcount > 0


def welcome_available(uid: int) -> bool:
    u = get_user(uid)
    return bool(u and u["referred_by"] and not u["welcome_used"] and not order_count(uid))


def get_promo(code: str):
    with db() as con:
        return con.execute("SELECT * FROM promos WHERE code=? AND active=1 AND (uses_left IS NULL OR uses_left>0)",
                           (code.upper(),)).fetchone()


def use_promo(code: str, delta: int = 1):
    with db() as con:
        con.execute("UPDATE promos SET used=used+?, uses_left=CASE WHEN uses_left IS NULL THEN NULL "
                    "ELSE uses_left-? END WHERE code=?", (delta, delta, code))


def get_setting(key: str, default: str = "") -> str:
    with db() as con:
        r = con.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return r["value"] if r else default


def set_setting(key: str, value: str | None):
    with db() as con:
        if value is None:
            con.execute("DELETE FROM settings WHERE key=?", (key,))
        else:
            con.execute("INSERT INTO settings(key, value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, value))


def ref_link(uid: int) -> str:
    return f"https://t.me/{BOT_USERNAME}?start=ref_{uid}"


def calc_price(uid: int, price: int, promo_pct: int = 0, use_bonus: bool = False) -> dict:
    """Chegirmalarni hisoblaydi: do'st chegirmasi → promokod → bonus. Jami ko'pi bilan MAX_DISCOUNT_PCT%."""
    res = {"full_price": price, "welcome": 0, "promo_off": 0, "bonus_used": 0, "discount": 0, "price": price}
    if not price:
        return res
    cap = price * MAX_DISCOUNT_PCT // 100
    if welcome_available(uid):
        res["welcome"] = min(REF_WELCOME, cap)
    if promo_pct:
        res["promo_off"] = min(price * promo_pct // 100, cap - res["welcome"])
    if use_bonus:
        left = cap - res["welcome"] - res["promo_off"]
        res["bonus_used"] = max(0, min(bonus_balance(uid), price * BONUS_MAX_PCT // 100, left))
    res["discount"] = res["welcome"] + res["promo_off"] + res["bonus_used"]
    res["price"] = price - res["discount"]
    return res


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


def service_label(o, lang: str = "uz") -> str:
    label = svc_tr(o["audience"], o["service"], lang)[0]
    if o["package"]:
        label += f" — {pkg_tr(o['audience'], o['service'], o['package'], lang)[0]}"
    return label


def order_text(o, for_admin=False, lang: str = "uz") -> str:
    if for_admin:
        lang = "uz"
    t = (f"<b>{tr(lang, 'f_order')} #{o['id']}</b>\n"
         f"📦 {service_label(o, lang)}\n"
         f"{tr(lang, 'f_topic')}: {html.escape(o['topic'])}\n")
    if o["details"]:
        t += f"{tr(lang, 'f_details')}: {html.escape(o['details'])}\n"
    t += (f"{tr(lang, 'f_deadline')}: {dl_name(o['deadline'], lang)}\n"
          + (f"{tr(lang, 'f_discount')}: −{money(o['discount'], lang)}"
             + (f" ({o['promo']})" if o["promo"] else "") + "\n" if o["discount"] else "")
          + f"💰 {tr(lang, 'f_price')}: <b>{money(o['price'], lang)}</b>\n"
          f"{tr(lang, 'f_status')}: {ST_TR.get(o['status'], {}).get(lang, o['status'])}")
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


def main_kb(lang: str = DEFAULT_LANG):
    rows = []
    if WEBAPP_URL:
        rows.append([kbtn(b(lang, "app"), "primary", "app", web_app=WebAppInfo(url=f"{WEBAPP_URL}/?lang={lang}"))])
    rows += [
        [kbtn(b(lang, "order"), "success", "order")],
        [kbtn(b(lang, "prices"), "primary", "prices"), kbtn(b(lang, "samples"), "primary", "samples")],
        [kbtn(b(lang, "bonus"), "danger", "heart")],
        [kbtn(b(lang, "info"), "primary", "bot"), kbtn(b(lang, "channel"), "success", "channel")],
        [kbtn(b(lang, "orders"), None, "orders"), kbtn(b(lang, "contact"), None, "contact"),
         kbtn(b(lang, "lang"), None, "globe")],
    ]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=rows)


MAIN_KBS = {lang: main_kb(lang) for lang in LANGS}
MAIN_KB = MAIN_KBS[DEFAULT_LANG]


def mkb(uid: int):
    return MAIN_KBS[L(uid)]


def btn_texts(key: str) -> set:
    """Pastki tugma matni barcha tillarda (premium ikonka bo'lsa emojisiz ham)."""
    out = set()
    for lang in LANGS:
        t = BTN[key][lang]
        out |= {t, _strip_emoji(t)}
    return out


# til tanlash: animatsion bayroqlar — EMOJI_IDS ga flag_uz / flag_ru / flag_en premium ID qo'shilsa ishlaydi
LANG_STYLE = {"uz": "success", "ru": "primary", "en": "danger"}


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


def lang_kb():
    return ikb([[(name, f"lang:{code}", LANG_STYLE[code], f"flag_{code}")] for code, name in LANGS.items()])


def audience_kb(lang: str = DEFAULT_LANG, prefix="aud"):
    return ikb([[(aud_title("s", lang), f"{prefix}:s", "primary", "student")],
                [(aud_title("t", lang), f"{prefix}:t", "success", "teacher")]])


SVC_ICON = {"taqdimot": "image", "dars": "image", "mustaqil": "edit", "kurs": "channel",
            "portfolio": "star", "oum": "bot", "tadbir": "fire", "maqola": "globe", "amaliy": "orders",
            "referat": "music", "ishlanma": "check", "test": "ok", "boshqa": "heart"}


def services_kb(aud, lang: str = DEFAULT_LANG):
    rows = []
    for key, s in CATALOG[aud]["services"].items():
        price = min(p[1] for p in s["packages"].values()) if "packages" in s else s["price"]
        name = svc_tr(aud, key, lang)[0]
        label = f"{name} — {price_from(price, lang)}" if price else name
        rows.append([(label,
                      f"svc:{aud}:{key}", "success" if key == "boshqa" else "primary", SVC_ICON.get(key))])
    rows.append([(b(lang, "back"), "back:aud", "danger", "cancel")])
    return ikb(rows)


def packages_kb(aud, svc, lang: str = DEFAULT_LANG):
    pk = CATALOG[aud]["services"][svc]["packages"]
    styles = {"start": None, "pro": "primary", "premium": "success"}
    icons = {"start": "star", "pro": "fire", "premium": "heart"}
    rows = [[(f"{pkg_tr(aud, svc, k, lang)[0]} — {money(v[1], lang)}" + (" · 🐢" if k in TURTLE_PKGS else ""),
              f"pkg:{aud}:{svc}:{k}", styles.get(k), icons.get(k))] for k, v in pk.items()]
    rows.append([(b(lang, "see_samples"), "samples", None, "samples")])
    rows.append([(b(lang, "back"), f"aud:{aud}", "danger")])
    return ikb(rows)


TURTLE_PKGS = {"pro", "premium"}  # 🐢 Toshbaqa o'qituvchi — faqat Professional va Premium


def skip_kb(lang):
    return ikb([[(b(lang, "skip"), "skip", "primary")]])


def deadline_kb(lang):
    return ikb([[(dl_name("normal", lang), "dl:normal", "primary", "orders")],
                [(dl_name("urgent", lang), "dl:urgent", "danger", "fire")]])


def confirm_kb(has_price: bool, promo: str, balance: int, use_bonus: bool, lang: str = DEFAULT_LANG):
    rows = [[(b(lang, "confirm"), "confirm", "success", "ok")]]
    if has_price:
        extra = [(b(lang, "promo") if not promo else b(lang, "promo_off"), "promo" if not promo else "promo:off",
                  "primary", "star")]
        if balance:
            extra.append((b(lang, "bonus_off") if use_bonus else b(lang, "bonus_use", sum=money(balance, lang)),
                          "bonus:toggle", "primary", "money"))
        rows.append(extra)
    rows.append([(b(lang, "restart"), "restart", "primary", "edit"), (b(lang, "cancel"), "cancel", "danger", "cancel")])
    return ikb(rows)


def admin_kb(oid, status):
    if status == "quote":
        return ikb([[("💰 Narx belgilash", f"adm:price:{oid}", "success", "money")],
                    [("❌ Rad etish", f"adm:no:{oid}", "danger", "cancel")]])
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
    promo = State()
    cheque = State()


class AdminSend(StatesGroup):
    file = State()
    price = State()
    broadcast = State()
    broadcast_confirm = State()


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
async def send_welcome(m: Message, user, lang: str):
    text = tr(lang, "welcome", name=html.escape(user.first_name), bot=BOT_NAME, contact=CONTACT)
    banner = ASSETS / "banner.png"
    if banner.exists():
        await m.answer_photo(FSInputFile(banner), caption=text, reply_markup=MAIN_KBS[lang])
    else:
        await m.answer(text, reply_markup=MAIN_KBS[lang])


@router.message(CommandStart())
async def start(m: Message, state: FSMContext, bot: Bot, command: CommandObject):
    await state.clear()
    uid = m.from_user.id
    arg = (command.args or "").strip()
    referred = False
    if arg.startswith("ref_") and arg[4:].isdigit() and set_referrer(uid, int(arg[4:])):
        ref = int(arg[4:])
        referred = True
        try:
            await bot.send_message(ref, tr(L(ref), "ref_joined", name=html.escape(m.from_user.first_name),
                                           sum=money(REF_BONUS, L(ref))))
        except Exception as e:
            logging.info("Referal xabari yuborilmadi: %s", e)
    if not get_lang(uid):  # birinchi marta — avval til tanlanadi
        await state.update_data(ref_new=referred)
        await m.answer(tr(DEFAULT_LANG, "pick_lang"), reply_markup=lang_kb())
        return
    lang = L(uid)
    if referred:
        await m.answer(tr(lang, "ref_welcome", sum=money(REF_WELCOME, lang)))
    await send_welcome(m, m.from_user, lang)


@router.message(F.text.in_(btn_texts("lang")))
@router.message(Command("lang", "language", "til", "yazyk"))
async def lang_cmd(m: Message):
    await m.answer(tr(L(m.from_user.id), "pick_lang"), reply_markup=lang_kb())


@router.callback_query(F.data.startswith("lang:"))
async def lang_set(c: CallbackQuery, state: FSMContext):
    lang = c.data.split(":")[1]
    if lang not in LANGS:
        await c.answer()
        return
    first = get_lang(c.from_user.id) is None
    set_lang(c.from_user.id, lang)
    await c.answer(LANGS[lang])
    try:
        await c.message.delete()
    except Exception:
        pass
    if first:
        data = await state.get_data()
        await state.clear()
        if data.get("ref_new"):
            await c.message.answer(tr(lang, "ref_welcome", sum=money(REF_WELCOME, lang)))
        await send_welcome(c.message, c.from_user, lang)
    else:
        await c.message.answer(tr(lang, "lang_set"), reply_markup=MAIN_KBS[lang])


@router.message(F.text.in_(btn_texts("order")))
@router.message(Command("order"))
async def order_start(m: Message, state: FSMContext):
    await state.clear()
    lang = L(m.from_user.id)
    await m.answer(tr(lang, "who_for"), reply_markup=audience_kb(lang))


@router.message(F.text.in_(btn_texts("prices")))
async def prices(m: Message):
    lang = L(m.from_user.id)
    imgs = [ASSETS / "prices_students.png", ASSETS / "prices_teachers.png"]
    if lang == "uz" and all(p.exists() for p in imgs):  # rasmlar o'zbekcha
        await m.answer_media_group([InputMediaPhoto(media=FSInputFile(p)) for p in imgs])
    else:
        await m.answer(prices_text(lang))
    await m.answer(tr(lang, "prices_footer", pct=int(URGENT_EXTRA * 100)),
                   reply_markup=ikb([[(b(lang, "order"), "go_order", "success", "order")]]))


def prices_text(lang: str = "uz") -> str:
    parts = []
    for aud_key, aud in CATALOG.items():
        lines = [f"<b>{aud_title(aud_key, lang)}</b>"]
        for key, s in aud["services"].items():
            name, desc = svc_tr(aud_key, key, lang)
            if "packages" in s:
                lines.append(f"• {name}:")
                for pk, (_, price, _) in s["packages"].items():
                    pname, pdesc = pkg_tr(aud_key, key, pk, lang)
                    lines.append(f"    ◦ {pname} — <b>{money(price, lang)}</b>\n       <i>{pdesc}</i>")
            else:
                pr = f"<b>{price_from(s['price'], lang)}</b>" if s["price"] else f"<b>{money(None, lang)}</b>"
                lines.append(f"• {name} — {pr}\n    <i>{desc}</i>")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


@router.callback_query(F.data == "go_order")
async def go_order(c: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = L(c.from_user.id)
    await c.message.answer(tr(lang, "who_for"), reply_markup=audience_kb(lang))
    await c.answer()


@router.message(F.text.in_(btn_texts("samples")))
async def samples_msg(m: Message):
    await send_samples(m, L(m.from_user.id))


@router.callback_query(F.data == "samples")
async def samples_cb(c: CallbackQuery):
    await c.answer()
    await send_samples(c.message, L(c.from_user.id))


def sample_files():
    # namunalar: "1_..pptx", "2_..pptx", "4_..mp4" kabi raqam bilan boshlanadigan fayllar
    return sorted(p for p in SAMPLES.glob("[0-9]_*") if p.is_file())


async def send_samples(m: Message, lang: str = DEFAULT_LANG):
    files = sample_files()
    if not files:
        await m.answer(tr(lang, "samples_soon"))
        return
    await m.answer(tr(lang, "samples_intro"))
    for p in files:
        try:
            if p.suffix.lower() == ".mp4":
                await m.answer_video(FSInputFile(p))
            else:
                await m.answer_document(FSInputFile(p))
        except Exception as e:
            logging.warning("Namuna yuborilmadi %s: %s", p, e)


@router.message(F.text.in_(btn_texts("orders")))
async def my_orders(m: Message):
    lang = L(m.from_user.id)
    rows = user_orders(m.from_user.id)
    if not rows:
        await m.answer(tr(lang, "no_orders"))
        return
    await m.answer("\n\n".join(order_text(o, lang=lang) for o in rows))


@router.message(F.text.in_(btn_texts("contact")))
async def contact(m: Message):
    await m.answer(tr(L(m.from_user.id), "contact", contact=CONTACT))


# ------------------------------------------------------------------ buyurtma oqimi
@router.callback_query(F.data == "back:aud")
async def back_aud(c: CallbackQuery):
    lang = L(c.from_user.id)
    await c.message.edit_text(tr(lang, "who_for"), reply_markup=audience_kb(lang))
    await c.answer()


@router.callback_query(F.data.startswith("aud:"))
async def choose_aud(c: CallbackQuery, state: FSMContext):
    aud = c.data.split(":")[1]
    lang = L(c.from_user.id)
    await state.update_data(aud=aud, uid=c.from_user.id)
    await c.message.edit_text(tr(lang, "choose_service", title=aud_title(aud, lang)), reply_markup=services_kb(aud, lang))
    await c.answer()


@router.callback_query(F.data.startswith("svc:"))
async def choose_svc(c: CallbackQuery, state: FSMContext):
    _, aud, svc = c.data.split(":")
    lang = L(c.from_user.id)
    s = CATALOG[aud]["services"][svc]
    name, desc = svc_tr(aud, svc, lang)
    await state.update_data(aud=aud, svc=svc, pkg="", uid=c.from_user.id)
    if "packages" in s:
        txt = [tr(lang, "choose_pkg", name=name)]
        for pk, (_, price, _) in s["packages"].items():
            pname, pdesc = pkg_tr(aud, svc, pk, lang)
            txt.append(f"• <b>{pname}</b> — {money(price, lang)}\n  <i>{pdesc}</i>")
        await c.message.edit_text("\n".join(txt), reply_markup=packages_kb(aud, svc, lang))
    else:
        await state.update_data(base_price=s["price"])
        if s["price"] is None:
            await state.set_state(Order.topic)
            await c.message.answer(tr(lang, "other_ask"))
        else:
            await ask_topic(c.message, state, f"<b>{name}</b> — {price_from(s['price'], lang)}\n<i>{desc}</i>", lang)
    await c.answer()


@router.callback_query(F.data.startswith("pkg:"))
async def choose_pkg(c: CallbackQuery, state: FSMContext):
    _, aud, svc, pkg = c.data.split(":")
    lang = L(c.from_user.id)
    price = CATALOG[aud]["services"][svc]["packages"][pkg][1]
    name, desc = pkg_tr(aud, svc, pkg, lang)
    await state.update_data(aud=aud, svc=svc, pkg=pkg, base_price=price, uid=c.from_user.id)
    await ask_topic(c.message, state, tr(lang, "picked", name=name, price=money(price, lang), desc=desc), lang)
    await c.answer()


async def ask_topic(m: Message, state: FSMContext, header: str, lang: str = DEFAULT_LANG):
    await state.set_state(Order.topic)
    await m.answer(tr(lang, "topic_ask", header=header))


@router.message(Order.topic, F.text)
async def got_topic(m: Message, state: FSMContext):
    lang = L(m.from_user.id)
    if len(m.text) > 300:
        await m.answer(tr(lang, "topic_long"))
        return
    await state.update_data(topic=m.text.strip())
    await state.set_state(Order.details)
    await m.answer(tr(lang, "details_ask"), reply_markup=skip_kb(lang))


@router.message(Order.details, F.text)
async def got_details(m: Message, state: FSMContext):
    await state.update_data(details=m.text.strip()[:1000])
    await ask_files(m, state, L(m.from_user.id))


@router.callback_query(Order.details, F.data == "skip")
async def skip_details(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await ask_files(c.message, state, L(c.from_user.id))


async def ask_files(m: Message, state: FSMContext, lang: str = DEFAULT_LANG):
    await state.set_state(Order.files)
    await state.update_data(files=[])
    await m.answer(tr(lang, "files_ask"), reply_markup=ikb([[(b(lang, "files_done"), "files_done", "success")]]))


@router.message(Order.files, F.document | F.photo)
async def got_file(m: Message, state: FSMContext):
    lang = L(m.from_user.id)
    data = await state.get_data()
    files = data.get("files", [])
    if len(files) >= 10:
        await m.answer(tr(lang, "files_max"))
        return
    if m.document:
        files.append({"type": "doc", "id": m.document.file_id})
    else:
        files.append({"type": "photo", "id": m.photo[-1].file_id})
    await state.update_data(files=files)
    await m.answer(tr(lang, "files_got", n=len(files)), reply_markup=ikb([[(b(lang, "ready"), "files_done", "success")]]))


@router.callback_query(Order.files, F.data == "files_done")
async def files_done(c: CallbackQuery, state: FSMContext):
    await c.answer()
    data = await state.get_data()
    if data.get("deadline"):  # Mini ilovadan kelgan — muddat tanlangan
        await show_confirm(c.message, state)
        return
    await state.set_state(Order.deadline)
    await c.message.answer(tr(L(c.from_user.id), "deadline_ask"), reply_markup=deadline_kb(L(c.from_user.id)))


@router.callback_query(Order.deadline, F.data.startswith("dl:"))
async def got_deadline(c: CallbackQuery, state: FSMContext):
    await state.update_data(deadline=c.data.split(":")[1])
    await show_confirm(c.message, state)
    await c.answer()


async def show_confirm(m: Message, state: FSMContext):
    data = await state.get_data()
    dl = data["deadline"]
    base = data.get("base_price")
    if base:
        price = int(base * (1 + URGENT_EXTRA)) if dl == "urgent" else base
        price = round(price / 1000) * 1000
    else:
        price = 0
    uid = data.get("uid") or m.chat.id
    lang = L(uid)
    promo = data.get("promo", "")
    p = get_promo(promo) if promo else None
    if promo and not p:  # muddati tugagan bo'lsa
        promo = ""
    calc = calc_price(uid, price, p["percent"] if p else 0, data.get("use_bonus", False))
    await state.update_data(price=calc["price"], full_price=calc["full_price"], discount=calc["discount"],
                            bonus_used=calc["bonus_used"], welcome=calc["welcome"], promo=promo)
    await state.set_state(Order.confirm)
    label = svc_tr(data["aud"], data["svc"], lang)[0]
    if data.get("pkg"):
        label += f" — {pkg_tr(data['aud'], data['svc'], data['pkg'], lang)[0]}"
        if data["pkg"] in TURTLE_PKGS and data["svc"] in ("taqdimot", "dars"):
            label += f"\n{TURTLE_LONG[lang]}"
    lines = []
    if calc["discount"]:
        lines.append(f"{tr(lang, 'f_price')}: <s>{money(calc['full_price'], lang)}</s>")
        if calc["welcome"]:
            lines.append(f"{tr(lang, 'f_welcome')}: −{money(calc['welcome'], lang)}")
        if calc["promo_off"]:
            lines.append(f"{tr(lang, 'f_promo')} {promo} ({p['percent']}%): −{money(calc['promo_off'], lang)}")
        if calc["bonus_used"]:
            lines.append(f"{tr(lang, 'f_bonus')}: −{money(calc['bonus_used'], lang)}")
    price_block = (("\n".join(lines) + "\n" if lines else "")
                   + f"{E['money']} {tr(lang, 'f_total')}: <b>{money(calc['price'], lang)}</b>")
    txt = (f"{tr(lang, 'confirm_title')}\n\n"
           f"📦 {label}\n{tr(lang, 'f_topic')}: {html.escape(data['topic'])}\n"
           + (f"{tr(lang, 'f_details')}: {html.escape(data['details'])}\n" if data.get("details") else "")
           + f"{tr(lang, 'f_files', n=len(data.get('files', [])))}\n"
           f"{tr(lang, 'f_deadline')}: {dl_name(dl, lang)}\n\n{price_block}")
    if not price:
        txt += "\n" + tr(lang, "admin_price")
    await m.answer(txt, reply_markup=confirm_kb(bool(price), promo, bonus_balance(uid),
                                                data.get("use_bonus", False), lang))


@router.callback_query(Order.confirm, F.data == "promo")
async def promo_ask(c: CallbackQuery, state: FSMContext):
    lang = L(c.from_user.id)
    await state.set_state(Order.promo)
    await c.message.answer(tr(lang, "promo_ask"), reply_markup=ikb([[(b(lang, "back"), "promo:back", "danger", "cancel")]]))
    await c.answer()


@router.callback_query(StateFilter(Order.confirm, Order.promo), F.data.in_({"promo:off", "promo:back"}))
async def promo_off(c: CallbackQuery, state: FSMContext):
    if c.data == "promo:off":
        await state.update_data(promo="")
    await c.answer()
    await show_confirm(c.message, state)


@router.message(Order.promo, F.text, ~F.text.startswith("/"))
async def promo_got(m: Message, state: FSMContext):
    lang = L(m.from_user.id)
    code = m.text.strip().upper()[:32]
    p = get_promo(code)
    if not p:
        await m.answer(tr(lang, "promo_bad"), reply_markup=ikb([[(b(lang, "back"), "promo:back", "danger", "cancel")]]))
        return
    await state.update_data(promo=code)
    await m.answer(tr(lang, "promo_ok", code=html.escape(code), pct=p["percent"]))
    await show_confirm(m, state)


@router.callback_query(Order.confirm, F.data == "bonus:toggle")
async def bonus_toggle(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(use_bonus=not data.get("use_bonus", False))
    await c.answer()
    await show_confirm(c.message, state)


# ------------------------------------------------------------------ Mini ilova
@router.message(F.web_app_data)
async def webapp_data(m: Message, state: FSMContext):
    uid = m.from_user.id
    try:
        d = json.loads(m.web_app_data.data)
    except (json.JSONDecodeError, TypeError):
        await m.answer(tr(L(uid), "wa_bad"))
        return
    if d.get("lang") in LANGS and d["lang"] != get_lang(uid):  # Mini ilovada til almashtirilgan
        set_lang(uid, d["lang"])
    lang = L(uid)
    if d.get("cmd") == "samples":
        await send_samples(m, lang)
        return
    if d.get("cmd") != "order":
        return
    aud, svc, pkg = d.get("aud"), d.get("svc"), d.get("pkg") or ""
    s = CATALOG.get(aud, {}).get("services", {}).get(svc)
    if not s or ("packages" in s and pkg not in s["packages"]):
        await m.answer(tr(lang, "wa_notfound"))
        return
    topic = str(d.get("topic", "")).strip()[:300]
    if len(topic) < 2:
        await m.answer(tr(lang, "wa_notopic"))
        return
    base = s["packages"][pkg][1] if "packages" in s else s["price"]
    await state.clear()
    await state.update_data(aud=aud, svc=svc, pkg=pkg if "packages" in s else "", base_price=base, topic=topic,
                            details=str(d.get("details", "")).strip()[:1000], uid=uid,
                            deadline="urgent" if d.get("deadline") == "urgent" else "normal")
    await m.answer(tr(lang, "wa_ok"), reply_markup=MAIN_KBS[lang])
    code = str(d.get("promo", "")).strip().upper()[:32]
    if code:
        if get_promo(code):
            await state.update_data(promo=code)
            await m.answer(tr(lang, "wa_promo_ok", code=html.escape(code)))
        else:
            await m.answer(tr(lang, "wa_promo_bad", code=html.escape(code)))
    await ask_files(m, state, lang)


@router.callback_query(F.data == "restart")
async def restart(c: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = L(c.from_user.id)
    await c.message.answer(tr(lang, "restart"), reply_markup=audience_kb(lang))
    await c.answer()


@router.callback_query(F.data == "cancel")
async def cancel(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.answer(tr(L(c.from_user.id), "cancelled"), reply_markup=mkb(c.from_user.id))
    await c.answer()


@router.callback_query(Order.confirm, F.data == "confirm")
async def confirm(c: CallbackQuery, state: FSMContext, bot: Bot):
    lang = L(c.from_user.id)
    data = await state.get_data()
    quote = not data.get("full_price", data.get("price"))
    if quote:
        data.update(price=0, full_price=0, discount=0, bonus_used=0, welcome=0, promo="")
    # bonusni yechib olamiz (balans o'zgargan bo'lsa — bonussiz)
    if data.get("bonus_used") and not take_bonus(c.from_user.id, data["bonus_used"]):
        data["price"] += data["bonus_used"]
        data["discount"] -= data["bonus_used"]
        data["bonus_used"] = 0
    oid = create_order(data, c.from_user)
    if data.get("promo"):
        use_promo(data["promo"])
    if data.get("welcome"):
        with db() as con:
            con.execute("UPDATE users SET welcome_used=1 WHERE user_id=?", (c.from_user.id,))
    if quote:
        set_status(oid, "quote")
        await state.clear()
        await c.message.answer(tr(lang, "quote_ok", oid=oid), reply_markup=MAIN_KBS[lang])
    else:
        await state.set_state(Order.cheque)
        await state.update_data(order_id=oid)
        await c.message.answer(payment_text(oid, data["price"], lang), reply_markup=MAIN_KBS[lang])
    o = get_order(oid)
    head = "🆕 Yangi so'rov — NARX BELGILANG" if quote else "🆕 Yangi buyurtma (to'lov kutilmoqda)"
    head += f"\n🌐 Mijoz tili: {LANGS[lang]}"
    await notify_admins(bot, head + "\n\n" + order_text(o, True), admin_kb(oid, o["status"]))
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


def payment_text(oid: int, price: int, lang: str = DEFAULT_LANG) -> str:
    return tr(lang, "payment", oid=oid, card=CARD_NUMBER, owner=CARD_OWNER, sum=money(price, lang))


async def accept_cheque(m: Message, bot: Bot, oid: int):
    set_status(oid, "paid")
    await m.answer(tr(L(m.from_user.id), "cheque_ok"), reply_markup=mkb(m.from_user.id))
    o = get_order(oid)
    text = "🧾 Chek keldi!\n\n" + order_text(o, True)
    if m.photo:
        await notify_admins(bot, text, admin_kb(oid, "paid"), photo=m.photo[-1].file_id)
    else:
        await notify_admins(bot, text, admin_kb(oid, "paid"), document=m.document.file_id)


def awaiting_payment(uid: int):
    with db() as con:
        return con.execute("SELECT id FROM orders WHERE user_id=? AND status='new' ORDER BY id DESC LIMIT 1",
                           (uid,)).fetchone()


@router.message(Order.cheque, F.photo | F.document)
async def got_cheque(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data())["order_id"]
    await state.clear()
    await accept_cheque(m, bot, oid)


@router.message(Order.cheque)
async def cheque_wrong(m: Message):
    await m.answer(tr(L(m.from_user.id), "cheque_wrong"))


async def reward_referrer(bot: Bot, uid: int):
    """Do'st birinchi marta to'lov qilganda taklif qilganga bonus beradi (bir marta)."""
    u = get_user(uid)
    if not u or not u["referred_by"] or u["ref_rewarded"]:
        return
    with db() as con:
        cur = con.execute("UPDATE users SET ref_rewarded=1 WHERE user_id=? AND ref_rewarded=0", (uid,))
        if not cur.rowcount:
            return
    ref = u["referred_by"]
    add_bonus(ref, REF_BONUS)
    lang = L(ref)
    try:
        await bot.send_message(ref, tr(lang, "ref_reward", sum=money(REF_BONUS, lang),
                                       name=html.escape(u["full_name"] or ""), bal=som(bonus_balance(ref), lang)))
    except Exception as e:
        logging.info("Bonus xabari yuborilmadi: %s", e)


def refund_discounts(o):
    """Rad etilgan buyurtmada bonus, do'st chegirmasi va promokod qaytariladi."""
    if o["bonus_used"]:
        add_bonus(o["user_id"], o["bonus_used"])
    if o["welcome"]:
        with db() as con:
            con.execute("UPDATE users SET welcome_used=0 WHERE user_id=?", (o["user_id"],))
    if o["promo"]:
        use_promo(o["promo"], -1)


# ------------------------------------------------------------------ ma'lumot va kanal
def channel_url() -> str:
    if not CHANNEL:
        return ""
    if CHANNEL.startswith("http"):
        return CHANNEL
    return "https://t.me/" + CHANNEL.lstrip("@")


def channel_name() -> str:
    url = channel_url()
    return "@" + url.rstrip("/").split("/")[-1] if url else "—"


def channel_kb(lang: str):
    url = channel_url()
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=b(lang, "subscribe"), url=url, style="success",
        **({"icon_custom_emoji_id": EMOJI_IDS["channel"]} if EMOJI_IDS.get("channel") else {}))]]) if url else None


def min_price(aud: str) -> int:
    prices = []
    for s in CATALOG[aud]["services"].values():
        if "packages" in s:
            prices += [p[1] for p in s["packages"].values()]
        elif s["price"]:
            prices.append(s["price"])
    return min(prices)


@router.message(F.text.in_(btn_texts("info")))
@router.message(Command("info", "help"))
async def info_cmd(m: Message):
    lang = L(m.from_user.id)
    txt = tr(lang, "info", bot=BOT_NAME, min_s=price_from(min_price("s"), lang), min_t=price_from(min_price("t"), lang),
             urgent=int(URGENT_EXTRA * 100), welcome=money(REF_WELCOME, lang), bonus=money(REF_BONUS, lang),
             pct=BONUS_MAX_PCT, channel=channel_name(), contact=CONTACT, yukla=OTHER_BOTS)
    await m.answer(txt, reply_markup=channel_kb(lang), link_preview_options=LinkPreviewOptions(is_disabled=True))


@router.message(F.text.in_(btn_texts("channel")))
@router.message(Command("channel", "kanal"))
async def channel_cmd(m: Message):
    lang = L(m.from_user.id)
    kb = channel_kb(lang)
    await m.answer(tr(lang, "channel_msg") if kb else tr(lang, "channel_soon"), reply_markup=kb)


# ------------------------------------------------------------------ bonus va aksiyalar
@router.message(F.text.in_(btn_texts("bonus")))
@router.message(Command("bonus"))
async def bonus_menu(m: Message):
    uid = m.from_user.id
    lang = L(uid)
    invited, paid = ref_stats(uid)
    link = ref_link(uid)
    ak = get_setting(f"aksiya_{lang}") or get_setting("aksiya")
    txt = tr(lang, "bonus_menu", aksiya=tr(lang, "aksiya_line", text=ak) if ak else "",
             bal=som(bonus_balance(uid), lang), inv=invited, paid=paid, welcome=money(REF_WELCOME, lang),
             bonus=money(REF_BONUS, lang), pct=BONUS_MAX_PCT, link=link)
    share = (f"https://t.me/share/url?url={quote(link)}&text="
             + quote(tr(lang, "share_text", sum=money(REF_WELCOME, lang))))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=b(lang, "share"), url=share, style="success")],
        [ibtn(b(lang, "order"), "go_order", "primary", "order")]])
    await m.answer(txt, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))


# ------------------------------------------------------------------ admin: promokod, aksiya, bonus
@router.message(Command("promo"))
async def promo_create(m: Message, command: CommandObject):
    if not is_admin(m.from_user.id):
        return
    parts = (command.args or "").split()
    if len(parts) < 2 or not parts[1].isdigit() or not 1 <= int(parts[1]) <= 90 \
            or (len(parts) > 2 and not parts[2].isdigit()):
        await m.answer("Promokod yaratish:\n<code>/promo KOD FOIZ [SONI]</code>\n\n"
                       "Masalan:\n<code>/promo YANGI20 20 50</code> — 20% chegirma, 50 marta\n"
                       "<code>/promo TALABA10 10</code> — 10%, cheksiz\n\n"
                       "Ro'yxat: /promos · O'chirish: <code>/delpromo KOD</code>")
        return
    code, pct = parts[0].upper()[:32], int(parts[1])
    limit = int(parts[2]) if len(parts) > 2 else None
    with db() as con:
        con.execute("""INSERT INTO promos(code, percent, uses_left, used, active, created_at) VALUES(?,?,?,0,1,?)
                       ON CONFLICT(code) DO UPDATE SET percent=excluded.percent, uses_left=excluded.uses_left,
                       active=1""", (code, pct, limit, datetime.now().strftime("%Y-%m-%d %H:%M")))
    await m.answer(f"✅ Promokod <code>{html.escape(code)}</code> — {pct}% "
                   f"({f'{limit} marta' if limit else 'cheksiz'}) tayyor.\n"
                   f"Hammaga e'lon qilish: /broadcast · Bonus bo'limida ko'rsatish: <code>/aksiya matn</code>")


@router.message(Command("promos"))
async def promo_list(m: Message):
    if not is_admin(m.from_user.id):
        return
    with db() as con:
        rows = con.execute("SELECT * FROM promos ORDER BY active DESC, created_at DESC LIMIT 30").fetchall()
    if not rows:
        await m.answer("Promokodlar yo'q. Yaratish: <code>/promo KOD FOIZ [SONI]</code>")
        return
    lines = [f"{'🟢' if r['active'] and (r['uses_left'] is None or r['uses_left'] > 0) else '⚪️'} "
             f"<code>{html.escape(r['code'])}</code> — {r['percent']}% · ishlatildi {r['used']}"
             + (f" · qoldi {r['uses_left']}" if r["uses_left"] is not None else " · cheksiz") for r in rows]
    await m.answer("🎟 <b>Promokodlar</b>\n\n" + "\n".join(lines))


@router.message(Command("delpromo"))
async def promo_delete(m: Message, command: CommandObject):
    if not is_admin(m.from_user.id):
        return
    code = (command.args or "").strip().upper()
    with db() as con:
        cur = con.execute("UPDATE promos SET active=0 WHERE code=?", (code,))
    await m.answer(f"⚪️ {html.escape(code)} o'chirildi." if cur.rowcount else "Bunday promokod yo'q.")


@router.message(Command("aksiya"))
async def aksiya_cmd(m: Message, command: CommandObject):
    if not is_admin(m.from_user.id):
        return
    arg = (command.args or "").strip()
    key = "aksiya"
    first, _, rest = arg.partition(" ")
    if first.lower() in LANGS:  # /aksiya ru Текст — faqat shu til uchun
        key, arg = f"aksiya_{first.lower()}", rest.strip()
    if not arg:
        cur = get_setting(key)
        await m.answer("Joriy aksiya matni («🎁 Bonus va aksiyalar» bo'limida chiqadi):\n\n"
                       + (cur or "<i>yo'q</i>") + "\n\nO'rnatish: <code>/aksiya matn</code> (hamma tilga)\n"
                       "Til bo'yicha: <code>/aksiya ru Текст</code> · <code>/aksiya en Text</code>\n"
                       "O'chirish: <code>/aksiya off</code> yoki <code>/aksiya ru off</code>")
        return
    if arg.lower() == "off":
        set_setting(key, None)
        await m.answer("Aksiya o'chirildi.")
        return
    set_setting(key, html.escape(arg[:600]))
    await m.answer("✅ Aksiya saqlandi. Mijozlar «🎁 Bonus va aksiyalar» bo'limida ko'radi.")


@router.message(Command("addbonus"))
async def addbonus_cmd(m: Message, command: CommandObject, bot: Bot):
    if not is_admin(m.from_user.id):
        return
    parts = (command.args or "").split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].lstrip("-").isdigit() or not get_user(int(parts[0])):
        await m.answer("Bonus qo'shish/ayirish: <code>/addbonus USER_ID SUMMA</code>\n"
                       "Masalan: <code>/addbonus 123456789 10000</code> yoki <code>-5000</code>")
        return
    uid, amount = int(parts[0]), int(parts[1])
    add_bonus(uid, amount)
    await m.answer(f"✅ {uid}: balans {som(bonus_balance(uid))}")
    if amount > 0:
        try:
            await bot.send_message(uid, tr(L(uid), "bonus_gift", sum=money(amount, L(uid))))
        except Exception:
            pass


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
        if o["status"] != "paid":
            await c.answer(f"Holat: {STATUS.get(o['status'], o['status'])}", show_alert=True)
            return
        set_status(oid, "work")
        await bot.send_message(o["user_id"], tr(L(o["user_id"]), "paid_ok", oid=oid))
        await reward_referrer(bot, o["user_id"])
        await c.message.answer(f"#{oid} — ishga olindi. Tayyor bo'lgach tugmani bosing:", reply_markup=admin_kb(oid, "work"))
    elif act == "no":
        if o["status"] in ("rejected", "done"):
            await c.answer("Bu buyurtma allaqachon yopilgan", show_alert=True)
            return
        set_status(oid, "rejected")
        refund_discounts(o)
        await bot.send_message(o["user_id"], tr(L(o["user_id"]), "rejected", oid=oid, contact=CONTACT))
        await c.message.answer(f"#{oid} — rad etildi.")
    elif act == "price":
        await state.set_state(AdminSend.price)
        await state.update_data(price_oid=oid)
        await c.message.answer(f"#{oid} uchun narxni yozing (faqat raqam, masalan 150000):")
    elif act == "send":
        await state.set_state(AdminSend.file)
        await state.update_data(send_oid=oid)
        await c.message.answer(f"#{oid} uchun tayyor faylni yuboring (bir nechta bo'lishi mumkin). "
                               "Tugatgach /done yozing.")
    await c.answer()


@router.message(AdminSend.price, F.text)
async def admin_price(m: Message, state: FSMContext, bot: Bot):
    digits = "".join(ch for ch in m.text if ch.isdigit())
    if not digits:
        await m.answer("Faqat raqam yozing, masalan 150000")
        return
    price = int(digits)
    oid = (await state.get_data())["price_oid"]
    await state.clear()
    with db() as con:
        con.execute("UPDATE orders SET price=?, full_price=?, status='new' WHERE id=?", (price, price, oid))
    o = get_order(oid)
    ul = L(o["user_id"])
    await bot.send_message(o["user_id"], tr(ul, "price_set", oid=oid) + payment_text(oid, price, ul))
    await m.answer(f"#{oid} — narx {money(price)} mijozga yuborildi ✅")


@router.message(AdminSend.file, Command("done"))
async def admin_done(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data())["send_oid"]
    set_status(oid, "done")
    await state.clear()
    o = get_order(oid)
    await bot.send_message(o["user_id"], tr(L(o["user_id"]), "done", oid=oid, contact=CONTACT))
    await m.answer(f"#{oid} — topshirildi ✅")


@router.message(AdminSend.file, F.document | F.photo | F.video)
async def admin_file(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data())["send_oid"]
    o = get_order(oid)
    cap = tr(L(o["user_id"]), "file_cap", oid=oid)
    if m.document:
        await bot.send_document(o["user_id"], m.document.file_id, caption=cap)
    elif m.video:
        await bot.send_video(o["user_id"], m.video.file_id, caption=cap)
    else:
        await bot.send_photo(o["user_id"], m.photo[-1].file_id, caption=cap)
    await m.answer("Yuborildi. Yana fayl bo'lsa yuboring yoki /done.")


@router.message(Command("stats"))
async def stats_cmd(m: Message):
    if not is_admin(m.from_user.id):
        return
    total, blocked, today, orders, done = user_stats()
    with db() as con:
        refs = con.execute("SELECT COUNT(*) FROM users WHERE referred_by IS NOT NULL").fetchone()[0]
        bonus_sum = con.execute("SELECT COALESCE(SUM(bonus),0) FROM users").fetchone()[0]
    await m.answer(f"📊 <b>Statistika</b>\n\n👥 Foydalanuvchilar: <b>{total}</b>\n🆕 Bugun: <b>{today}</b>\n"
                   f"🚫 Botni bloklagan: <b>{blocked}</b>\n🤝 Referal orqali kelgan: <b>{refs}</b>\n"
                   f"💰 Mijozlardagi bonuslar: <b>{bonus_sum:,}</b> so'm\n\n"
                   f"📦 Buyurtmalar: <b>{orders}</b>\n✅ Topshirilgan: <b>{done}</b>".replace(",", " "))


@router.message(Command("broadcast"))
async def broadcast_start(m: Message, state: FSMContext):
    if not is_admin(m.from_user.id):
        return
    await state.set_state(AdminSend.broadcast)
    await m.answer(f"📢 <b>Hammaga xabar</b>\n\nYubormoqchi bo'lgan xabarni yuboring: matn, rasm, video, "
                   f"fayl yoki ovozli xabar — xuddi shu ko'rinishda hamma {len(all_user_ids())} ta foydalanuvchiga boradi.\n\n"
                   "Bekor qilish: /cancel")


@router.message(Command("cancel"))
async def cancel_cmd(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(tr(L(m.from_user.id), "cancel_cmd"), reply_markup=mkb(m.from_user.id))


@router.message(AdminSend.broadcast)
async def broadcast_preview(m: Message, state: FSMContext):
    await state.update_data(bc_chat=m.chat.id, bc_msg=m.message_id)
    await state.set_state(AdminSend.broadcast_confirm)
    await m.answer(f"Yuqoridagi xabar <b>{len(all_user_ids())}</b> ta foydalanuvchiga yuborilsinmi?",
                   reply_markup=ikb([[("✅ Yuborish", "bc:go", "success", "ok"), ("❌ Bekor", "bc:no", "danger", "cancel")]]))


@router.callback_query(AdminSend.broadcast_confirm, F.data.startswith("bc:"))
async def broadcast_go(c: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    await c.answer()
    if c.data == "bc:no":
        await c.message.answer("Bekor qilindi.")
        return
    ids = all_user_ids()
    status = await c.message.answer(f"📤 Yuborilmoqda... 0 / {len(ids)}")
    asyncio.create_task(run_broadcast(bot, ids, data["bc_chat"], data["bc_msg"], status))


async def run_broadcast(bot: Bot, ids, from_chat, msg_id, status_msg):
    from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter, TelegramBadRequest
    ok = fail = 0
    for n, uid in enumerate(ids, 1):
        try:
            await bot.copy_message(uid, from_chat, msg_id)
            ok += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
            try:
                await bot.copy_message(uid, from_chat, msg_id)
                ok += 1
            except Exception:
                fail += 1
        except (TelegramForbiddenError, TelegramBadRequest):
            mark_blocked(uid)
            fail += 1
        except Exception as e:
            logging.warning("Broadcast %s: %s", uid, e)
            fail += 1
        await asyncio.sleep(0.05)  # ~20 ta xabar/soniya — Telegram limitidan past
        if n % 50 == 0:
            try:
                await status_msg.edit_text(f"📤 Yuborilmoqda... {n} / {len(ids)}")
            except Exception:
                pass
    await status_msg.edit_text(f"✅ <b>Tayyor!</b>\n\n📨 Yetkazildi: <b>{ok}</b>\n🚫 Yetkazilmadi (bloklagan): <b>{fail}</b>")


@router.message(StateFilter(None), F.photo | F.document)
async def loose_cheque(m: Message, bot: Bot):
    row = awaiting_payment(m.from_user.id)
    if row:
        await accept_cheque(m, bot, row["id"])
    else:
        await m.answer(tr(L(m.from_user.id), "loose_file"), reply_markup=mkb(m.from_user.id))


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
    url = f"{WEBAPP_URL}/privacy.html" if WEBAPP_URL else None
    await m.answer(tr(L(m.from_user.id), "privacy", url=url or CONTACT))


@router.message(Command("myid"))
async def myid(m: Message):
    await m.answer(tr(L(m.from_user.id), "myid", id=m.from_user.id))


@router.message(F.text)
async def fallback(m: Message, state: FSMContext):
    if await state.get_state() is None:
        await m.answer(tr(L(m.from_user.id), "menu"), reply_markup=mkb(m.from_user.id))


# ------------------------------------------------------------------ ishga tushirish
# ------------------------------------------------------------------ veb-server (Mini ilova)
def catalog_json():
    """Mini ilova uchun: s/t — o'zbekcha (eski versiya bilan mos), i18n — ru/en tarjimalar."""
    return {"urgent": URGENT_EXTRA,
            **{a: {"title": v["title"], "services": v["services"]} for a, v in CATALOG.items()},
            "i18n": CAT_TR}


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

    async def catalog_file(_):
        return web.json_response(catalog_json())

    async def video(_):
        return web.FileResponse(SAMPLES / "4_Reklama.mp4")

    app.router.add_get("/catalog.json", catalog_file)
    if (SAMPLES / "4_Reklama.mp4").exists():
        app.router.add_get("/4_Reklama.mp4", video)
    app.router.add_get("/privacy.html", privacy)
    return app


async def set_commands(bot: Bot):
    """Chap pastdagi «Menu» ro'yxati — har bir til uchun alohida."""
    from aiogram.types import BotCommand
    try:
        for lang, cmds in COMMANDS.items():
            items = [BotCommand(command=c, description=d) for c, d in cmds]
            await bot.set_my_commands(items, language_code=lang)
            if lang == DEFAULT_LANG:
                await bot.set_my_commands(items)  # boshqa tildagi foydalanuvchilar uchun
    except Exception as e:
        logging.warning("set_my_commands: %s", e)
    # bot profilidagi tavsif — hamma ko'radi («Bu bot nima qila oladi?» va bio)
    for lang in DESCRIPTION:
        ch = CHANNEL_LINE[lang].format(ch=channel_name()) if channel_url() else ""
        desc = DESCRIPTION[lang].format(channel_line=ch, contact=CONTACT, yukla=OTHER_BOTS)[:512]
        short = SHORT_DESC[lang].format(contact=CONTACT)[:120]
        try:
            for code in ([lang, None] if lang == DEFAULT_LANG else [lang]):
                await bot.set_my_description(description=desc, language_code=code)
                await bot.set_my_short_description(short_description=short, language_code=code)
        except Exception as e:
            logging.warning("set_my_description %s: %s", lang, e)


async def main():
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN o'rnatilmagan")
    init_db()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    @dp.update.outer_middleware()
    async def remember_user(handler, event, data):
        user = data.get("event_from_user")
        if user and not user.is_bot:
            try:
                touch_user(user)
            except Exception as e:
                logging.warning("touch_user: %s", e)
        return await handler(event, data)

    dp.include_router(router)
    await set_commands(bot)
    global BOT_USERNAME
    try:
        BOT_USERNAME = (await bot.get_me()).username or BOT_USERNAME
    except Exception as e:
        logging.warning("get_me: %s", e)
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
