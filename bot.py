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
import io
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
                           InlineKeyboardMarkup, InputMediaDocument, InputMediaPhoto, KeyboardButton, LinkPreviewOptions, BufferedInputFile,
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
TURTLE_ADDON = int(os.getenv("TURTLE_ADDON", "50000"))  # talabalar uchun 🐢 qo'shimcha narxi
GROUP_RULES = [(5, 20), (3, 15)]   # guruh: 5+ ish −20%, 3+ ish −15%
GROUP_BONUS = int(os.getenv("GROUP_BONUS", "5000"))   # 5+ ishli guruhni yig'ganga bonus
LOYALTY_LEVELS = [(10, 10), (5, 5)]  # 10+ buyurtma −10% (Oltin), 5+ −5% (Kumush); har 5-buyurtma −50%
REMIND_PAY_HOURS = 3                 # to'lanmagan buyurtma haqida mijozga eslatma
TZ_OFFSET = 5                        # Toshkent vaqti (UTC+5)
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
    # animatsion bayroqlar va kitob (Birzumda Yukla bilan bir xil)
    "flag_uz": "5222404546575219535", "flag_ru": "5449408995691341691", "flag_en": "5224518800061245598",
    "book": "5226512880362332956",
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

from texts import (BRIEF_REQUIRED, BRIEF_REQ_TX, FX, TPL, TPL_TX, tpl_label, SAMPLE_PKG, SAMPLE_TX, BRIEF_GROUPS, BRIEF_LABEL, BRIEF_LABEL_TR, BRIEF_Q, BRIEF_TX, SVC_GROUP,  # noqa: E402
                   BTN, CAT_TR, CHANNEL_LINE, COMMANDS, CURRENCY, DESCRIPTION, SHORT_DESC, DEFAULT_LANG, FROM, LANGS, NEGOTIABLE, TURTLE_ADDON_TX, TX,  # noqa: E402
                   DEADLINES as DL_TR, STATUS as ST_TR)
import autogen as AG  # noqa: E402

# Matnlardagi {e[kalit]} uchun premium emoji (ID bo'lmasa oddiy emoji)
E_FALLBACK = {"hi": "👋", "star": "✨", "bot": "🤖", "student": "🎓", "teacher": "👩‍🏫", "edit": "✍️",
              "heart": "🎁", "ok": "✅", "image": "🎨", "fire": "⚡", "orders": "📋", "contact": "💜",
              "down": "👇", "money": "💰", "check": "📋", "globe": "🌐", "app": "✨", "channel": "📢", "samples": "🎨",
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
                "start": ("Start", 20000, "10–12 slayd, zamonaviy dizayn, 3 soat"),
                "pro": ("Professional", 30000, "15–20 slayd, animatsiya, diagrammalar, 6 soat"),
                "premium": ("Premium", 40000, "20–25 slayd, Morph, neon dizayn, nutq matni, 12 soat"),
            }},
            "mustaqil": {"name": "Mustaqil ish", "price": 25000, "desc": "Word formatda, chiroyli muqova bilan"},
            "kurs": {"name": "Kurs ishi", "price": 30000, "desc": "Reja, boblar, xulosa, adabiyotlar ro'yxati"},
            "maqola": {"name": "Maqola / tezis", "price": 25000, "desc": "Ilmiy maqola yoki konferensiya tezisi"},
            "amaliy": {"name": "Amaliy / laboratoriya ishi", "price": 20000, "desc": "Topshiriq sharti asosida, hisobot bilan"},
            "referat": {"name": "Referat", "price": 20000, "desc": "Reja, matn, adabiyotlar, chiroyli muqova"},
            "portfolio": {"name": "Portfolio", "price": 25000, "desc": "Talaba portfoliosi va rezyume"},
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
            "portfolio": {"name": "Portfolio taqdimoti (rasmlar bilan)", "packages": {
                "start": ("Start", 200000, "15–20 slayd, rasmlar, yutuqlar, sertifikatlar"),
                "pro": ("Professional", 250000, "20–25 slayd, animatsiya, fotokollajlar, 🐢 Toshbaqa o'qituvchi"),
                "premium": ("Premium", 300000, "25–30 slayd, Morph, video va musiqa, nutq matni, 🐢 Toshbaqa o'qituvchi")}},
            "oum": {"name": "O'quv-uslubiy majmua", "price": 40000, "desc": "Ma'ruza, amaliy mashg'ulot, testlar"},
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
        con.execute("""CREATE TABLE IF NOT EXISTS subs(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, plan TEXT, starts TEXT, ends TEXT,
            quota INTEGER, used INTEGER DEFAULT 0, order_id INTEGER, created_at TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS reviews(
            order_id INTEGER PRIMARY KEY, user_id INTEGER, stars INTEGER, text TEXT DEFAULT '',
            consent INTEGER DEFAULT 0, published INTEGER DEFAULT 0, created_at TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS shop(
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, price INTEGER, file_id TEXT, file_type TEXT,
            preview_id TEXT, sold INTEGER DEFAULT 0, active INTEGER DEFAULT 1, created_at TEXT)""")
        # eski bazaga yangi ustunlar (bir marta qo'shiladi)
        for table, col, decl in [
            ("users", "referred_by", "INTEGER"), ("users", "bonus", "INTEGER DEFAULT 0"),
            ("users", "ref_rewarded", "INTEGER DEFAULT 0"), ("users", "welcome_used", "INTEGER DEFAULT 0"), ("users", "lang", "TEXT"),
            ("orders", "full_price", "INTEGER DEFAULT 0"), ("orders", "discount", "INTEGER DEFAULT 0"),
            ("orders", "promo", "TEXT DEFAULT ''"), ("orders", "bonus_used", "INTEGER DEFAULT 0"),
            ("orders", "welcome", "INTEGER DEFAULT 0"), ("orders", "brief", "TEXT DEFAULT '[]'"), ("orders", "turtle", "INTEGER DEFAULT 0"),
            ("orders", "qty", "INTEGER DEFAULT 1"), ("orders", "paid_at", "TEXT"), ("orders", "remind_pay", "INTEGER DEFAULT 0"),
            ("orders", "remind_adm", "INTEGER DEFAULT 0"), ("orders", "shop_id", "INTEGER"),
            ("orders", "ai_cost", "REAL DEFAULT 0"), ("orders", "auto", "TEXT DEFAULT ''"),
            ("users", "ad_seen", "INTEGER DEFAULT 0")]:
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
               topic, details, deadline, files, status, created_at, full_price, discount, promo, bonus_used, welcome, brief,
               turtle, qty, shop_id) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (user.id, user.username or "", user.full_name, data.get("phone", ""), data["aud"], data["svc"],
             data.get("pkg", ""), data["price"], data["topic"], data.get("details", ""), data["deadline"],
             json.dumps(data.get("files", [])), "new", datetime.now().strftime("%Y-%m-%d %H:%M"),
             data.get("full_price", data["price"]), data.get("discount", 0), data.get("promo", ""),
             data.get("bonus_used", 0), data.get("welcome", 0), json.dumps(data.get("brief", []), ensure_ascii=False),
             turtle_kind(data.get("aud"), data.get("svc"), data.get("pkg"), data.get("turtle")) or "",
             data.get("qty", 1), data.get("shop_id")))
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


def fx(lang: str, key: str, **kw):
    v = FX[key].get(lang) or FX[key]["uz"]
    return v.format(e=E, **kw) if isinstance(v, str) else v


def group_pct(qty: int) -> int:
    for need, pct in GROUP_RULES:
        if qty >= need:
            return pct
    return 0


def paid_count(uid: int) -> int:
    """To'langan (ishga olingan yoki topshirilgan) buyurtmalar soni — do'kondan tashqari."""
    with db() as con:
        return con.execute("SELECT COUNT(*) FROM orders WHERE user_id=? AND status IN ('work','done') "
                           "AND service!='shop'", (uid,)).fetchone()[0]


def loyalty_level(n: int) -> int:
    return 2 if n >= 10 else 1 if n >= 5 else 0


def loyalty_pct(uid: int) -> int:
    n = paid_count(uid)
    if (n + 1) % 5 == 0:  # har 5-buyurtma
        return 50
    for need, pct in LOYALTY_LEVELS:
        if n >= need:
            return pct
    return 0


def calc_price(uid: int, price: int, promo_pct: int = 0, use_bonus: bool = False, qty: int = 1) -> dict:
    """Chegirmalar: guruh → sodiqlik → do'st → promokod → bonus. Jami ko'pi bilan MAX_DISCOUNT_PCT%."""
    total = price * max(1, qty)
    res = {"full_price": total, "unit": price, "qty": qty, "group_off": 0, "grp_pct": 0, "loyalty_off": 0, "loy_pct": 0,
           "welcome": 0, "promo_off": 0, "bonus_used": 0, "discount": 0, "price": total}
    if not price:
        return res
    cap = total * MAX_DISCOUNT_PCT // 100
    used = 0
    res["grp_pct"] = group_pct(qty)
    res["group_off"] = min(total * res["grp_pct"] // 100, cap - used); used += res["group_off"]
    res["loy_pct"] = loyalty_pct(uid)
    res["loyalty_off"] = min(total * res["loy_pct"] // 100, cap - used); used += res["loyalty_off"]
    if welcome_available(uid):
        res["welcome"] = min(REF_WELCOME, cap - used); used += res["welcome"]
    if promo_pct:
        res["promo_off"] = min(total * promo_pct // 100, cap - used); used += res["promo_off"]
    if use_bonus:
        res["bonus_used"] = max(0, min(bonus_balance(uid), total * BONUS_MAX_PCT // 100, cap - used)); used += res["bonus_used"]
    res["discount"] = used
    res["price"] = total - used
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
    if o["service"] == "shop":
        return f"Do'kon: {o['topic']}"
    if o["service"] == "sub":
        return f"💎 {SUB_TX['name'][lang].get(o['package'], o['package'])}"
    label = svc_tr(o["audience"], o["service"], lang)[0]
    if (o["qty"] if "qty" in o.keys() else 1) > 1:
        label = f"👥 {o['qty']} × " + label
    if o["package"]:
        label += f" — {pkg_tr(o['audience'], o['service'], o['package'], lang)[0]}"
    return label


def order_text(o, for_admin=False, lang: str = "uz") -> str:
    if for_admin:
        lang = "uz"
    tk = o["turtle"] if "turtle" in o.keys() else ""
    t = (f"<b>{tr(lang, 'f_order')} #{o['id']}</b>\n"
         f"📦 {service_label(o, lang)}\n"
         + (ttr(lang, "line_in" if tk == "in" else "line_add", sum=money(TURTLE_ADDON, lang)) + "\n" if tk else "")
         + f"{tr(lang, 'f_topic')}: {html.escape(o['topic'])}\n")
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
    # Mini ilova — buyurtma shu yerdan; Mini ilova bo'lmasa — oddiy «Buyurtma berish» tugmasi
    if WEBAPP_URL:
        rows = [[kbtn(b(lang, "app"), "success", "app", web_app=WebAppInfo(url=f"{WEBAPP_URL}/?lang={lang}"))]]
    else:
        rows = [[kbtn(b(lang, "order"), "success", "order")]]
    rows += [
        [kbtn(b(lang, "prices"), "primary", "prices"), kbtn(b(lang, "samples"), "primary", "samples")],
        [kbtn(b(lang, "sub"), "success", "fire"), kbtn(b(lang, "bonus"), "danger", "heart")],
        [kbtn(b(lang, "shop"), "primary", "fire")],
        [kbtn(b(lang, "info"), "primary", "book"), kbtn(b(lang, "channel"), "success", "channel")],
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
    rows = [[(f"{pkg_tr(aud, svc, k, lang)[0]} — {money(v[1], lang)}" + (" · 🐢" if turtle_kind(aud, svc, k) else ""),
              f"pkg:{aud}:{svc}:{k}", styles.get(k), icons.get(k))] for k, v in pk.items()]
    rows.append([(b(lang, "see_samples"), "samples", None, "samples")])
    rows.append([(b(lang, "back"), f"aud:{aud}", "danger")])
    return ikb(rows)


TURTLE_PKGS = {"pro", "premium"}  # 🐢 ustozlar uchun Professional va Premium'ga kiradi


def turtle_kind(aud, svc, pkg, chosen=False):
    """'in' — paketga kiradi (ustozlar Pro/Premium), 'add' — talaba qo'shimcha tanlagan, None — yo'q."""
    if aud == "t" and svc in ("dars", "portfolio") and pkg in TURTLE_PKGS:
        return "in"
    if aud == "s" and svc == "taqdimot" and chosen:
        return "add"
    return None


def turtle_available(aud, svc) -> bool:
    """Talaba slaydiga 🐢 qo'shimcha sifatida qo'shish mumkinmi."""
    return aud == "s" and svc == "taqdimot"


def ttr(lang, key, **kw):
    return (TURTLE_ADDON_TX[key].get(lang) or TURTLE_ADDON_TX[key]["uz"]).format(**kw)


def skip_kb(lang):
    return ikb([[(b(lang, "skip"), "skip", "primary")]])


def deadline_kb(lang):
    return ikb([[(dl_name("normal", lang), "dl:normal", "primary", "orders")],
                [(dl_name("urgent", lang), "dl:urgent", "danger", "fire")]])


def confirm_kb(has_price: bool, promo: str, balance: int, use_bonus: bool, lang: str = DEFAULT_LANG,
               turtle: str | None = None, qty: int = 1):
    rows = [[(b(lang, "confirm"), "confirm", "success", "ok")]]
    if has_price:
        rows.append([(b(lang, "group") if qty <= 1 else b(lang, "group_off"), "grp:start" if qty <= 1 else "grp:off",
                      "primary" if qty <= 1 else None, "student")])
    if turtle is not None:  # None — mumkin emas; "" — tanlanmagan; "on" — tanlangan
        rows.append([(ttr(lang, "btn_off") if turtle else ttr(lang, "btn_add", sum=money(TURTLE_ADDON, lang)),
                      "turtle:toggle", None if turtle else "danger")])
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
        return ikb([[("📤 Tayyor ishni yuborish", f"adm:send:{oid}", "primary")],
                    [("👀 Namuna yuborish", f"adm:prev:{oid}", None)]])
    if status == "new":
        return ikb([[("👀 Namuna yuborish (to'lovdan oldin)", f"adm:prev:{oid}", None)]])
    return None


# ------------------------------------------------------------------ holatlar
class Order(StatesGroup):
    topic = State()
    details = State()
    files = State()
    deadline = State()
    confirm = State()
    promo = State()
    group = State()
    gtopics = State()
    cheque = State()


class Brief(StatesGroup):
    q = State()


class FixReq(StatesGroup):
    text = State()


class Support(StatesGroup):
    text = State()


class Review(StatesGroup):
    text = State()


class AdminSend(StatesGroup):
    preview = State()
    post = State()
    post_confirm = State()
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
    with db() as con:
        r = con.execute("SELECT ad_seen FROM users WHERE user_id=?", (user.id,)).fetchone()
    if not r or not r["ad_seen"]:
        await send_ad(m)
        with db() as con:
            con.execute("UPDATE users SET ad_seen=1 WHERE user_id=?", (user.id,))
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
    await m.answer(tr(lang, "prices_footer", pct=int(URGENT_EXTRA * 100), turtle=money(TURTLE_ADDON, lang)),
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


# ------------------------------------------------------------------ namunalar karuseli
SAMPLE_NAMES = {1: "Start", 2: "Professional", 3: "Premium"}
SAMPLE_PKG_KEY = {1: "start", 2: "pro", 3: "premium"}
SAMPLE_STYLE = {1: None, 2: "primary", 3: "danger"}
PHOTO_CACHE: dict[str, str] = {}  # rasm yo'li -> Telegram file_id (qayta yuklamaslik uchun)


def sample_count(k: int) -> int:
    return len(list(SAMPLES.glob(f"sx{k}-*.jpg")))


def sample_pptx(k: int):
    found = sorted(SAMPLES.glob(f"{k}_*.pptx"))
    return found[0] if found else None


def stx(lang, key, **kw):
    return (SAMPLE_TX[key].get(lang) or SAMPLE_TX[key]["uz"]).format(e=E, **kw)


def sample_caption(k: int, i: int, lang: str) -> str:
    pk = SAMPLE_PKG_KEY[k]
    s_price = CATALOG["s"]["services"]["taqdimot"]["packages"][pk][1]
    t_price = CATALOG["t"]["services"]["dars"]["packages"][pk][1]
    turtle = stx(lang, "turtle_in" if pk in TURTLE_PKGS else "turtle_add", sum=money(TURTLE_ADDON, lang))
    return (f"{stx(lang, 'title', pkg=SAMPLE_NAMES[k])}\n<i>{SAMPLE_PKG[k][lang]}</i>\n\n"
            f"{stx(lang, 'prices', s=money(s_price, lang), t=money(t_price, lang))}\n{turtle}\n\n"
            f"<i>{stx(lang, 'slide', i=i, n=sample_count(k))}</i>")


def sample_kb(k: int, i: int, lang: str):
    n = sample_count(k)
    rows = [[("◀️", f"smp:{k}:{(i - 2) % n + 1}", "primary"), (f"{i} / {n}", "smp:noop", None),
             ("▶️", f"smp:{k}:{i % n + 1}", "primary")],
            [(("✅ " if j == k else "") + SAMPLE_NAMES[j], f"smp:{j}:1", "success" if j == k else SAMPLE_STYLE[j])
             for j in SAMPLE_NAMES]]
    if sample_pptx(k):
        rows.append([(stx(lang, "download"), f"smp:dl:{k}", None, "down")])
    rows.append([(ttx(lang, "btn"), "tpl:gallery", "primary", "image")])
    rows.append([(b(lang, "order"), "go_order", "success", "order")])
    return ikb(rows)


def sample_photo(k: int, i: int):
    path = str(SAMPLES / f"sx{k}-{i}.jpg")
    return PHOTO_CACHE.get(path) or FSInputFile(path), path


def remember_photo(path: str, msg):
    if isinstance(msg, Message) and msg.photo:
        PHOTO_CACHE[path] = msg.photo[-1].file_id


async def send_samples(m: Message, lang: str = DEFAULT_LANG):
    if not sample_count(1):  # karusel rasmlari yo'q — eski usul: fayllarni yuborish
        files = [f for f in sample_files() if f.suffix.lower() == ".pptx"]
        if not files:
            await m.answer(tr(lang, "samples_soon"))
            return
        await m.answer(tr(lang, "samples_intro"))
        for f in files:
            await m.answer_document(FSInputFile(f))
        return
    media, path = sample_photo(1, 1)
    msg = await m.answer_photo(media, caption=sample_caption(1, 1, lang), reply_markup=sample_kb(1, 1, lang))
    remember_photo(path, msg)


@router.callback_query(F.data.startswith("smp:"))
async def sample_nav(c: CallbackQuery, bot: Bot):
    lang = L(c.from_user.id)
    parts = c.data.split(":")
    if parts[1] == "noop":
        await c.answer()
        return
    if parts[1] == "dl":
        k = int(parts[2])
        f = sample_pptx(k)
        await c.answer("📥")
        if f:
            await c.message.answer_document(FSInputFile(f), caption=stx(lang, "pptx_cap", pkg=SAMPLE_NAMES[k]))
        return
    k, i = int(parts[1]), int(parts[2])
    if k not in SAMPLE_NAMES or not 1 <= i <= sample_count(k):
        await c.answer()
        return
    await c.answer()
    media, path = sample_photo(k, i)
    try:
        msg = await c.message.edit_media(InputMediaPhoto(media=media, caption=sample_caption(k, i, lang)),
                                         reply_markup=sample_kb(k, i, lang))
        remember_photo(path, msg)
    except Exception as e:  # xabar juda eski yoki o'zgarmagan bo'lsa
        logging.info("Namuna tahrirlanmadi: %s", e)


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
    await start_brief(m, state, lang)


@router.message(Order.details, F.text)
async def got_details(m: Message, state: FSMContext):
    await state.update_data(details=m.text.strip()[:1000])
    await ask_files(m, state, L(m.from_user.id))


@router.callback_query(Order.details, F.data == "skip")
async def skip_details(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await ask_files(c.message, state, L(c.from_user.id))


# ------------------------------------------------------------------ batafsil so'rovnoma
def btr(lang: str, key: str, **kw) -> str:
    return (BRIEF_TX[key].get(lang) or BRIEF_TX[key]["uz"]).format(e=E, **kw)


def brief_label(key: str, lang: str = "uz") -> str:
    return BRIEF_LABEL_TR.get(lang, {}).get(key) or BRIEF_LABEL[key]


def brief_kb(lang: str, key: str):
    opts = BRIEF_Q[key].get("opts", {}).get(lang, [])
    btns = [(o, f"bq:o:{i}", "primary") for i, o in enumerate(opts)]
    rows = [btns[i:i + 2] for i in range(0, len(btns), 2)]
    last = [(btr(lang, "finish"), "bq:done", "success")]
    if key not in BRIEF_REQUIRED:
        last.insert(0, (btr(lang, "skip"), "bq:skip", None))
    rows.append(last)
    return ikb(rows)


async def start_brief(m: Message, state: FSMContext, lang: str):
    data = await state.get_data()
    qs = list(BRIEF_GROUPS[SVC_GROUP.get(data.get("svc"), "other")])
    if data.get("details") and "extra" in qs:  # Mini ilovada qo'shimcha yozilgan
        qs.remove("extra")
    preset = data.get("preset_brief", [])  # Mini ilovada tanlangan shablon
    qs = [q for q in qs if q not in {k for k, _ in preset}]
    await state.update_data(bq=qs, bi=0, brief=list(preset), preset_brief=[])
    await state.set_state(Brief.q)
    await m.answer(btr(lang, "intro"))
    await ask_brief(m, state, lang)


async def ask_brief(m: Message, state: FSMContext, lang: str):
    data = await state.get_data()
    qs, i = data["bq"], data["bi"]
    if i >= len(qs):
        await m.answer(btr(lang, "done"))
        await ask_files(m, state, lang)
        return
    q = BRIEF_Q[qs[i]]
    if qs[i] in ("style", "cover"):
        await send_tpl_album(m, "s" if qs[i] == "style" else "c", lang, "album_" + qs[i])
    await m.answer(f"<i>{btr(lang, 'step', i=i + 1, n=len(qs))}</i>\n{q.get(lang) or q['uz']}",
                   reply_markup=brief_kb(lang, qs[i]))


async def brief_next(m: Message, state: FSMContext, lang: str, answer: str | None, finish: bool = False):
    data = await state.get_data()
    qs, i, brief = data["bq"], data["bi"], data.get("brief", [])
    if i < len(qs) and answer:
        brief.append([qs[i], answer.strip()])
    await state.update_data(brief=brief, bi=len(qs) if finish else i + 1)
    await ask_brief(m, state, lang)


MENU_TEXTS = set().union(*(btn_texts(k) for k in ("app", "order", "prices", "samples", "bonus", "orders",
                                                    "contact", "lang", "info", "channel", "shop", "sub")))


@router.message(Brief.q, F.text, ~F.text.startswith("/"), ~F.text.in_(MENU_TEXTS))
async def brief_text_answer(m: Message, state: FSMContext):
    lang = L(m.from_user.id)
    if len(m.text) > 500:
        await m.answer(btr(lang, "too_long"))
        return
    await brief_next(m, state, lang, m.text)


@router.callback_query(Brief.q, F.data.startswith("bq:"))
async def brief_button(c: CallbackQuery, state: FSMContext):
    lang = L(c.from_user.id)
    await c.answer()
    parts = c.data.split(":")
    data = await state.get_data()
    qs, i = data["bq"], data["bi"]
    if parts[1] == "o" and i < len(qs):
        opts = BRIEF_Q[qs[i]].get("opts", {}).get(lang, [])
        idx = int(parts[2])
        await brief_next(c.message, state, lang, opts[idx] if idx < len(opts) else None)
    elif parts[1] == "skip":
        if i < len(qs) and qs[i] in BRIEF_REQUIRED:
            await c.message.answer(BRIEF_REQ_TX.get(lang) or BRIEF_REQ_TX["uz"])
            return
        await brief_next(c.message, state, lang, None)
    else:  # done — qolgan majburiy savollar baribir so'raladi
        rest = [k for k in qs[i:] if k in BRIEF_REQUIRED]
        if rest:
            await state.update_data(bq=qs[:i] + rest, bi=i)
            if qs[i] not in BRIEF_REQUIRED:
                await ask_brief(c.message, state, lang)
            else:
                await c.message.answer(BRIEF_REQ_TX.get(lang) or BRIEF_REQ_TX["uz"])
            return
        await brief_next(c.message, state, lang, None, finish=True)


def brief_lines(brief, lang: str) -> list:
    return [f"• {brief_label(k, lang)}: {html.escape(v[:150])}" for k, v in brief]


def tz_text(o) -> str:
    """Admin uchun texnik topshiriq — oddiy matn, nusxa olib yuborish uchun."""
    try:
        brief = json.loads(o["brief"] or "[]")
    except (TypeError, json.JSONDecodeError):
        brief = []
    flist = json.loads(o["files"] or "[]")
    files = len(flist)
    ph, dc = file_counts(flist)
    notes = [f"  {i}) {f['cap']}" for i, f in enumerate(flist, 1) if f.get("cap")]
    tk = o["turtle"] if "turtle" in o.keys() else ""
    lines = [f"Buyurtma #{o['id']}: {service_label(o)}" + (f" — {o['qty']} ta ish" if o["qty"] and o["qty"] > 1 else ""),
             f"Kim uchun: {'Talabalar' if o['audience'] == 's' else 'Ustozlar'}",
             f"Mavzu: {o['topic']}"]
    if o["details"]:
        lines.append(f"Qo'shimcha: {o['details']}")
    lines += [f"{brief_label(k)}: {v}" for k, v in brief]
    if tk:
        lines.append("🐢 Toshbaqa o'qituvchi: HA" + (" (paketga kiradi)" if tk == "in" else f" (+{money(TURTLE_ADDON)})"))
    lines += [f"Muddat turi: {DEADLINES.get(o['deadline'], o['deadline'])}",
              f"Mijoz tili: {LANGS.get(L(o['user_id']), '')}",
              f"Mijoz rasmlari/fayllari: {files} ta" + (f" (rasm: {ph}, hujjat: {dc}) — yuqorida yuborildi" if files else "")]
    if notes:
        lines += ["Rasmlarga izohlar:"] + notes
    return "\n".join(lines)


async def send_tz(bot: Bot, o):
    await notify_admins(bot, f"📋 <b>TEXNIK TOPSHIRIQ #{o['id']}</b> — bosib nusxa oling:\n"
                             f"<pre>{html.escape(tz_text(o))[:3800]}</pre>")


@router.message(Command("tz"))
async def tz_cmd(m: Message, command: CommandObject, bot: Bot):
    if not is_admin(m.from_user.id):
        return
    arg = (command.args or "").strip().lstrip("#")
    o = get_order(int(arg)) if arg.isdigit() else None
    if not o:
        await m.answer("Ishlatish: <code>/tz 12</code> — buyurtma raqami")
        return
    await m.answer(f"📋 <b>TEXNIK TOPSHIRIQ #{o['id']}</b>\n<pre>{html.escape(tz_text(o))[:3800]}</pre>")


def ttx(lang: str, key: str) -> str:
    return TPL_TX[key].get(lang) or TPL_TX[key]["uz"]


async def send_tpl_album(m: Message, kind: str, lang: str, title_key: str):
    """8 ta shablon rasmini albom qilib yuboradi (file_id keshlanadi)."""
    paths = [str(SAMPLES / f"tpl_{kind}{n}.jpg") for n in TPL]
    if not all(os.path.exists(x) for x in paths):
        return
    media = [InputMediaPhoto(media=PHOTO_CACHE.get(x) or FSInputFile(x),
                             caption=ttx(lang, title_key) if i == 0 else None) for i, x in enumerate(paths)]
    try:
        msgs = await m.answer_media_group(media)
        for x, mm in zip(paths, msgs):
            remember_photo(x, mm)
    except Exception as e:
        logging.warning("Shablon albomi yuborilmadi: %s", e)


@router.message(Command("shablon", "templates"))
async def templates_cmd(m: Message):
    lang = L(m.from_user.id)
    await m.answer(ttx(lang, "gallery"))
    await send_tpl_album(m, "s", lang, "album_style")
    await send_tpl_album(m, "c", lang, "album_cover")


@router.callback_query(F.data == "tpl:gallery")
async def templates_cb(c: CallbackQuery):
    await c.answer()
    lang = L(c.from_user.id)
    await send_tpl_album(c.message, "s", lang, "album_style")
    await send_tpl_album(c.message, "c", lang, "album_cover")


async def ask_files(m: Message, state: FSMContext, lang: str = DEFAULT_LANG):
    await state.set_state(Order.files)
    await state.update_data(files=[])
    await m.answer(tr(lang, "files_ask", mx=MAX_FILES), reply_markup=ikb([[(b(lang, "files_done"), "files_done", "success")]]))


CHECK_TX = {"uz": "🔎 <b>Tekshirib oling:</b> mavzu, ism-familiya, raqamlar va rasmlar to'g'rimi? Xato bo'lsa — «Orqaga» bosib tuzating. "
                  "Hammasi to'g'ri bo'lsa — tasdiqlang ✅",
            "ru": "🔎 <b>Проверьте:</b> тема, ФИО, цифры и фото верны? Если есть ошибка — нажмите «Назад» и исправьте. Всё верно — подтвердите ✅",
            "en": "🔎 <b>Please check:</b> topic, name, numbers and photos — all correct? If not, tap «Back» and fix it. All good — confirm ✅"}

QWARN_TX = {"uz": "⚠️ <b>Rasm sifati past</b> — slaydda xira chiqishi mumkin. Aslini <b>📎 → Fayl</b> qilib qayta yuboring:",
            "ru": "⚠️ <b>Низкое качество фото</b> — на слайде может быть размыто. Отправьте оригинал через <b>📎 → Файл</b>:",
            "en": "⚠️ <b>Low photo quality</b> — it may look blurry on a slide. Re-send the original via <b>📎 → File</b>:"}


def photo_warning(m: Message) -> str:
    """Telegram siqgan rasm o'lchamiga qarab ogohlantirish (fayl qilib yuborilsa — sifat to'liq)."""
    if m.photo:
        p = m.photo[-1]
        side = max(p.width, p.height)
        if side < 700:
            return f"juda kichik ({p.width}×{p.height})"
        if min(p.width, p.height) < 420:
            return "juda tor/kichik"
        if p.file_size and p.file_size < 45_000 and side < 1100:
            return "sifati past (siqilgan)"
    elif m.document and (m.document.mime_type or "").startswith("image/"):
        if m.document.file_size and m.document.file_size < 40_000:
            return "fayl juda kichik — xira bo'lishi mumkin"
    return ""


MAX_FILES = 30
_FILE_LOCKS: dict = {}
_ALBUM_ACK: set = set()


def file_counts(files) -> tuple:
    ph = sum(1 for f in files if f["type"] == "photo" or f.get("img"))
    return ph, len(files) - ph


@router.message(Order.files, F.document | F.photo | F.video)
async def got_file(m: Message, state: FSMContext):
    """Mijoz rasmlarini yuboradi: bittadan yoki galereyadan albom qilib (bir nechta birdan)."""
    lang = L(m.from_user.id)
    lock = _FILE_LOCKS.setdefault(m.from_user.id, asyncio.Lock())
    async with lock:  # albomdagi rasmlar bir vaqtda keladi — yo'qolmasligi uchun navbat bilan
        data = await state.get_data()
        files = data.get("files", [])
        if len(files) >= MAX_FILES:
            if (m.media_group_id or m.message_id) not in _ALBUM_ACK:
                _ALBUM_ACK.add(m.media_group_id or m.message_id)
                await m.answer(tr(lang, "files_max", n=MAX_FILES),
                               reply_markup=ikb([[(b(lang, "ready"), "files_done", "success")]]))
            return
        cap = (m.caption or "").strip()[:200]
        warn = photo_warning(m)
        if warn:
            ws = data.get("qwarn", [])
            ws.append(f"{len(files) + 1}-rasm: {warn}")
            await state.update_data(qwarn=ws)
        if m.photo:
            f = {"type": "photo", "id": m.photo[-1].file_id}
        elif m.video:
            f = {"type": "video", "id": m.video.file_id}
        else:
            mime = m.document.mime_type or ""
            f = {"type": "doc", "id": m.document.file_id, "name": (m.document.file_name or "")[:60]}
            if mime.startswith("image/"):
                f["img"] = 1
        if cap:
            f["cap"] = cap
        f["mid"] = m.message_id
        files.append(f)
        files.sort(key=lambda x: x.get("mid", 0))  # albom tartibi saqlansin
        await state.update_data(files=files)
    if m.media_group_id:  # albom: bitta javob, hammasi kelgach
        if m.media_group_id in _ALBUM_ACK:
            return
        _ALBUM_ACK.add(m.media_group_id)
        await asyncio.sleep(1.5)
        _ALBUM_ACK.discard(m.media_group_id)
        files = (await state.get_data()).get("files", [])
    ph, dc = file_counts(files)
    ws = (await state.get_data()).get("qwarn", [])
    extra = ""
    if ws:
        await state.update_data(qwarn=[])
        extra = "\n\n" + (QWARN_TX.get(lang) or QWARN_TX["uz"]) + "\n• " + "\n• ".join(ws[:10])
    await m.answer(tr(lang, "files_got", n=len(files), ph=ph, dc=dc, mx=MAX_FILES) + extra,
                   reply_markup=ikb([[(b(lang, "ready"), "files_done", "success")]]))


@router.message(Order.files, F.text, ~F.text.startswith("/"), ~F.text.in_(MENU_TEXTS))
async def files_note(m: Message, state: FSMContext):
    """Rasmlar bosqichida matn yozsa — oxirgi rasmga izoh sifatida saqlaymiz."""
    lang = L(m.from_user.id)
    data = await state.get_data()
    files = data.get("files", [])
    if not files:
        await m.answer(tr(lang, "files_first"), reply_markup=ikb([[(b(lang, "files_done"), "files_done", "success")]]))
        return
    files[-1]["cap"] = ((files[-1].get("cap", "") + " " + m.text.strip()).strip())[:300]
    await state.update_data(files=files)
    await m.answer(tr(lang, "files_note_ok", n=len(files)), reply_markup=ikb([[(b(lang, "ready"), "files_done", "success")]]))


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
    tk = turtle_kind(data["aud"], data["svc"], data.get("pkg"), data.get("turtle"))
    if price and tk == "add":
        price += TURTLE_ADDON  # 🐢 talaba tanlagan qo'shimcha
    uid = data.get("uid") or m.chat.id
    lang = L(uid)
    promo = data.get("promo", "")
    p = get_promo(promo) if promo else None
    if promo and not p:  # muddati tugagan bo'lsa
        promo = ""
    qty = data.get("qty", 1) if price else 1
    calc = calc_price(uid, price, p["percent"] if p else 0, data.get("use_bonus", False), qty)
    sub = active_sub(uid) if price and qty == 1 else None
    sub_line, sub_use = "", False
    if sub:
        if sub_covers(data["aud"], data["svc"], tk, data.get("pkg") or ""):
            sub_use = True
            calc.update(price=0, discount=calc["full_price"], bonus_used=0, welcome=0, promo_off=0)
            sub_line = SUB_TX["covered"][lang].format(left=sub["quota"] - sub["used"] - 1)
        else:
            off = round(calc["price"] * SUB_DISC / 100 / 1000) * 1000
            calc["price"] -= off
            calc["discount"] += off
            sub_line = SUB_TX["disc"][lang].format(pct=SUB_DISC, sum=money(off, lang))
    await state.update_data(price=calc["price"], full_price=calc["full_price"], discount=calc["discount"],
                            bonus_used=calc["bonus_used"], welcome=calc["welcome"], promo=promo, sub_use=sub_use)
    await state.set_state(Order.confirm)
    label = svc_tr(data["aud"], data["svc"], lang)[0]
    if data.get("pkg"):
        label += f" — {pkg_tr(data['aud'], data['svc'], data['pkg'], lang)[0]}"
    if tk == "in":
        label += f"\n{ttr(lang, 'line_in')}"
    elif tk == "add":
        label += f"\n{ttr(lang, 'line_add', sum=money(TURTLE_ADDON, lang))}"
    lines = []
    if qty > 1:
        lines.append(fx(lang, "grp_line", n=qty, unit=money(calc["unit"], lang)))
    if calc["discount"]:
        lines.append(f"{tr(lang, 'f_price')}: <s>{money(calc['full_price'], lang)}</s>")
        if calc["group_off"]:
            lines.append(f"{fx(lang, 'grp_off', pct=calc['grp_pct'])}: −{money(calc['group_off'], lang)}")
        if calc["loyalty_off"]:
            lines.append(f"{fx(lang, 'loy_off', pct=calc['loy_pct'])}: −{money(calc['loyalty_off'], lang)}")
        if calc["welcome"]:
            lines.append(f"{tr(lang, 'f_welcome')}: −{money(calc['welcome'], lang)}")
        if calc["promo_off"]:
            lines.append(f"{tr(lang, 'f_promo')} {promo} ({p['percent']}%): −{money(calc['promo_off'], lang)}")
        if calc["bonus_used"]:
            lines.append(f"{tr(lang, 'f_bonus')}: −{money(calc['bonus_used'], lang)}")
    if sub_line:
        lines.append(sub_line)
    price_block = (("\n".join(lines) + "\n" if lines else "")
                   + f"{E['money']} {tr(lang, 'f_total')}: <b>{money(calc['price'], lang)}</b>")
    txt = (f"{tr(lang, 'confirm_title')}\n\n"
           f"📦 {label}\n{tr(lang, 'f_topic')}: {html.escape(data['topic'])}\n"
           + (f"{tr(lang, 'f_details')}: {html.escape(data['details'])}\n" if data.get("details") else "")
           + (btr(lang, "summary") + "\n" + "\n".join(brief_lines(data["brief"], lang)) + "\n" if data.get("brief") else "")
           + (f"📝 {html.escape(data['group_topics'][:300])}\n" if qty > 1 and data.get("group_topics") else "")
           + f"{tr(lang, 'f_files', n=len(data.get('files', [])))}\n"
           f"{tr(lang, 'f_deadline')}: {dl_name(dl, lang)}\n\n{price_block}")
    txt += "\n\n" + (CHECK_TX.get(lang) or CHECK_TX["uz"])
    can_turtle = bool(price) and turtle_available(data["aud"], data["svc"])
    if not price:
        txt += "\n" + tr(lang, "admin_price")
    elif can_turtle and tk != "add":
        txt += "\n\n" + ttr(lang, "hint", sum=money(TURTLE_ADDON, lang))
    await m.answer(txt, reply_markup=confirm_kb(bool(price), promo, bonus_balance(uid), data.get("use_bonus", False),
                                                lang, ("on" if tk == "add" else "") if can_turtle else None, qty))


@router.callback_query(Order.confirm, F.data == "turtle:toggle")
async def turtle_toggle(c: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(turtle=not data.get("turtle", False))
    await c.answer("🐢")
    await show_confirm(c.message, state)


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
                            details=str(d.get("details", "")).strip()[:1000], uid=uid, turtle=bool(d.get("turtle")),
                            deadline="urgent" if d.get("deadline") == "urgent" else "normal")
    await m.answer(tr(lang, "wa_ok"), reply_markup=MAIN_KBS[lang])
    try:
        tpl = int(d.get("tpl") or 0)
    except (TypeError, ValueError):
        tpl = 0
    if tpl in TPL:
        key = "cover" if d.get("tpl_kind") == "c" else "style"
        await state.update_data(preset_brief=[[key, tpl_label(tpl, lang)]])
    code = str(d.get("promo", "")).strip().upper()[:32]
    if code:
        if get_promo(code):
            await state.update_data(promo=code)
            await m.answer(tr(lang, "wa_promo_ok", code=html.escape(code)))
        else:
            await m.answer(tr(lang, "wa_promo_bad", code=html.escape(code)))
    await start_brief(m, state, lang)


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
    if data.get("sub_use") and not quote:
        sub = active_sub(c.from_user.id)
        if not sub:
            await c.answer(SUB_TX["gone"][lang], show_alert=True)
            await show_confirm(c.message, state)
            return
        oid = create_order(dict(data, price=0, bonus_used=0, welcome=0, promo=""), c.from_user)
        with db() as con:
            con.execute("UPDATE subs SET used=used+1 WHERE id=?", (sub["id"],))
            con.execute("UPDATE orders SET status='paid', details=details || ? WHERE id=?", (f" [💎 obuna #{sub['id']}]", oid))
        await state.clear()
        await c.message.answer(SUB_TX["used_ok"][lang].format(left=sub["quota"] - sub["used"] - 1), reply_markup=MAIN_KBS[lang])
        o = get_order(oid)
        await notify_admins(bot, f"💎 <b>Obuna bilan buyurtma</b> (to'lovsiz)\n🌐 {LANGS[lang]}\n\n" + order_text(o, True))
        await send_order_files(bot, oid, data.get("files", []))
        await send_tz(bot, o)
        await approve_order(bot, oid, None, f"💎 #{oid} — obuna hisobidan (qoldi {sub['quota'] - sub['used'] - 1} ta).")
        await c.answer()
        return
    if quote:
        data.update(price=0, full_price=0, discount=0, bonus_used=0, welcome=0, promo="")
    # bonusni yechib olamiz (balans o'zgargan bo'lsa — bonussiz)
    if data.get("bonus_used") and not take_bonus(c.from_user.id, data["bonus_used"]):
        data["price"] += data["bonus_used"]
        data["discount"] -= data["bonus_used"]
        data["bonus_used"] = 0
    if data.get("qty", 1) > 1 and data.get("group_topics"):
        data["brief"] = list(data.get("brief", [])) + [["group", data["group_topics"]]]
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
    await send_order_files(bot, oid, data.get("files", []))
    await send_tz(bot, o)
    await c.answer()


async def send_order_files(bot: Bot, oid: int, files: list):
    """Mijoz rasmlari/fayllarini adminlarga albom qilib (10 tadan) yuboradi, izohlari bilan."""
    if not files:
        return
    n = len(files)
    def cap(i, f):
        c = f"#{oid} · {i}/{n}"
        return c + (f"\n💬 {f['cap']}" if f.get("cap") else "")
    photos = [(i, f) for i, f in enumerate(files, 1) if f["type"] in ("photo", "video")]
    docs = [(i, f) for i, f in enumerate(files, 1) if f["type"] == "doc"]
    for aid in ADMIN_IDS:
        for group, kind in ((photos, "p"), (docs, "d")):
            for k in range(0, len(group), 10):
                chunk = group[k:k + 10]
                try:
                    if len(chunk) == 1:
                        i, f = chunk[0]
                        if f["type"] == "photo":
                            await bot.send_photo(aid, f["id"], caption=cap(i, f))
                        elif f["type"] == "video":
                            await bot.send_video(aid, f["id"], caption=cap(i, f))
                        else:
                            await bot.send_document(aid, f["id"], caption=cap(i, f))
                    elif kind == "p":
                        from aiogram.types import InputMediaVideo
                        await bot.send_media_group(aid, [
                            (InputMediaPhoto if f["type"] == "photo" else InputMediaVideo)(media=f["id"], caption=cap(i, f))
                            for i, f in chunk])
                    else:
                        await bot.send_media_group(aid, [InputMediaDocument(media=f["id"], caption=cap(i, f)) for i, f in chunk])
                except Exception as e:
                    logging.warning("Fayllar yuborilmadi #%s: %s", oid, e)


def payment_text(oid: int, price: int, lang: str = DEFAULT_LANG) -> str:
    return tr(lang, "payment", oid=oid, card=CARD_NUMBER, owner=CARD_OWNER, sum=money(price, lang))


async def accept_cheque(m: Message, bot: Bot, oid: int):
    set_status(oid, "paid")
    await m.answer(tr(L(m.from_user.id), "cheque_ok"), reply_markup=mkb(m.from_user.id))
    o = get_order(oid)
    text = "🧾 Chek keldi!\n\n" + order_text(o, True)
    smart = (auto_ready(o) or (o["service"] == "sub" and AG.enabled())) and get_setting("auto_cheque", "on") == "on"
    if smart:
        text += "\n\n🤖 <b>Chek avtomatik tekshirilmoqda…</b> To'g'ri bo'lsa, ish o'zi boshlanadi — sizga xabar keladi."
    elif auto_ready(o):
        text += "\n\n🤖 <b>Tasdiqlasangiz — ish avtomatik tayyorlanib, mijozga darhol yuboriladi.</b>"
    if m.photo:
        await notify_admins(bot, text, admin_kb(oid, "paid"), photo=m.photo[-1].file_id)
    else:
        await notify_admins(bot, text, admin_kb(oid, "paid"), document=m.document.file_id)
    if smart:
        if m.photo:
            fid, uid, mime = m.photo[-1].file_id, m.photo[-1].file_unique_id, "image/jpeg"
        else:
            fid, uid, mime = m.document.file_id, m.document.file_unique_id, m.document.mime_type or ""
        if mime.startswith("image/") or mime == "application/pdf":
            asyncio.create_task(check_cheque(bot, oid, fid, uid, mime))


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
             pct=BONUS_MAX_PCT, channel=channel_name(), contact=CONTACT, yukla=OTHER_BOTS,
             turtle=money(TURTLE_ADDON, lang))
    rows = [[(CX["faq_btn"][lang], "help:faq", "primary"), (CX["sup_btn"][lang], "help:sup", "success")]]
    url = channel_url()
    kb = ikb(rows)
    if url:
        kb.inline_keyboard.append(channel_kb(lang).inline_keyboard[0])
    await m.answer(txt, reply_markup=kb, link_preview_options=LinkPreviewOptions(is_disabled=True))


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
    n = paid_count(uid)
    left = 4 - (n % 5)
    loy = fx(lang, "loy_menu", lvl=fx(lang, "lvl")[loyalty_level(n)], n=n,
             next=fx(lang, "loy_now") if left == 0 else fx(lang, "loy_next", k=left)) + "<i>" + fx(lang, "loy_rules") + "</i>"
    txt = txt + "\n\n" + loy
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


# ------------------------------------------------------------------ 👥 guruh buyurtmasi
def group_kb(lang: str):
    return ikb([[("2", "grp:n:2", None), ("3", "grp:n:3", "primary"), ("5", "grp:n:5", "success"), ("10", "grp:n:10", "success")],
                [(fx(lang, "grp_other"), "grp:other", None)],
                [(b(lang, "back"), "grp:back", "danger", "cancel")]])


@router.callback_query(Order.confirm, F.data == "grp:start")
async def group_start(c: CallbackQuery, state: FSMContext):
    lang = L(c.from_user.id)
    (n2, p2), (n1, p1) = GROUP_RULES[0], GROUP_RULES[1]
    await state.set_state(Order.group)
    await c.message.answer(fx(lang, "grp_ask", n1=n1, p1=p1, n2=n2, p2=p2), reply_markup=group_kb(lang))
    await c.answer()


@router.callback_query(StateFilter(Order.group, Order.gtopics, Order.confirm), F.data.in_({"grp:back", "grp:off", "grp:skip"}))
async def group_back(c: CallbackQuery, state: FSMContext):
    if c.data == "grp:off":
        await state.update_data(qty=1, group_topics="")
    await c.answer()
    await show_confirm(c.message, state)


@router.callback_query(Order.group, F.data == "grp:other")
async def group_other(c: CallbackQuery):
    await c.message.answer(fx(L(c.from_user.id), "grp_custom"))
    await c.answer()


async def group_set(m: Message, state: FSMContext, qty: int, lang: str):
    await state.update_data(qty=qty)
    await state.set_state(Order.gtopics)
    await m.answer(fx(lang, "grp_topics"), reply_markup=ikb([[(b(lang, "skip"), "grp:skip", "primary")]]))


@router.callback_query(Order.group, F.data.startswith("grp:n:"))
async def group_pick(c: CallbackQuery, state: FSMContext):
    await c.answer()
    await group_set(c.message, state, int(c.data.split(":")[2]), L(c.from_user.id))


@router.message(Order.group, F.text, ~F.text.startswith("/"))
async def group_custom(m: Message, state: FSMContext):
    lang = L(m.from_user.id)
    n = "".join(ch for ch in m.text if ch.isdigit())
    if not n or not 2 <= int(n) <= 50:
        await m.answer(fx(lang, "grp_custom"))
        return
    await group_set(m, state, int(n), lang)


@router.message(Order.gtopics, F.text, ~F.text.startswith("/"))
async def group_topics(m: Message, state: FSMContext):
    await state.update_data(group_topics=m.text.strip()[:1500])
    await show_confirm(m, state)


# ------------------------------------------------------------------ ⭐ baho va sharhlar
def stars_kb(oid: int):
    return ikb([[(f"{n}⭐", f"rv:s:{oid}:{n}", "success" if n >= 4 else None) for n in range(1, 6)]])


async def ask_review(bot: Bot, o):
    try:
        await bot.send_message(o["user_id"], fx(L(o["user_id"]), "rv_ask", oid=o["id"]), reply_markup=stars_kb(o["id"]))
    except Exception as e:
        logging.info("Baho so'ralmadi: %s", e)


def get_review(oid: int):
    with db() as con:
        return con.execute("SELECT * FROM reviews WHERE order_id=?", (oid,)).fetchone()


@router.callback_query(F.data.startswith("rv:s:"))
async def review_stars(c: CallbackQuery, state: FSMContext):
    _, _, oid, n = c.data.split(":")
    oid, n = int(oid), int(n)
    o = get_order(oid)
    lang = L(c.from_user.id)
    if not o or o["user_id"] != c.from_user.id or not 1 <= n <= 5:
        await c.answer()
        return
    with db() as con:
        con.execute("INSERT INTO reviews(order_id, user_id, stars, created_at) VALUES(?,?,?,?) "
                    "ON CONFLICT(order_id) DO UPDATE SET stars=excluded.stars",
                    (oid, c.from_user.id, n, datetime.now().strftime("%Y-%m-%d %H:%M")))
    await c.answer("⭐" * n)
    try:
        await c.message.edit_text(fx(lang, "rv_ask", oid=oid) + "\n\n" + "⭐" * n)
    except Exception:
        pass
    await state.set_state(Review.text)
    await state.update_data(rv_oid=oid)
    await c.message.answer(fx(lang, "rv_comment"), reply_markup=ikb([[(b(lang, "skip"), f"rv:skip:{oid}", "primary")]]))


@router.message(Review.text, F.text, ~F.text.startswith("/"))
async def review_text(m: Message, state: FSMContext):
    lang = L(m.from_user.id)
    oid = (await state.get_data()).get("rv_oid")
    await state.clear()
    with db() as con:
        con.execute("UPDATE reviews SET text=? WHERE order_id=?", (m.text.strip()[:700], oid))
    rv = get_review(oid)
    if rv and rv["stars"] >= 4:
        await m.answer(fx(lang, "rv_consent"), reply_markup=ikb([[(fx(lang, "rv_yes"), f"rv:c:{oid}:1", "success"),
                                                                 (fx(lang, "rv_no"), f"rv:c:{oid}:0", None)]]))
    else:
        await review_finish(m, m.bot, oid, lang)


@router.callback_query(F.data.startswith("rv:skip:"))
async def review_skip(c: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await c.answer()
    await review_finish(c.message, bot, int(c.data.split(":")[2]), L(c.from_user.id))


@router.callback_query(F.data.startswith("rv:c:"))
async def review_consent(c: CallbackQuery, bot: Bot):
    _, _, oid, yes = c.data.split(":")
    with db() as con:
        con.execute("UPDATE reviews SET consent=? WHERE order_id=? AND user_id=?", (int(yes), int(oid), c.from_user.id))
    await c.answer()
    await review_finish(c.message, bot, int(oid), L(c.from_user.id))


async def review_finish(m: Message, bot: Bot, oid: int, lang: str):
    rv, o = get_review(oid), get_order(oid)
    if not rv or not o:
        return
    await m.answer(fx(lang, "rv_thanks") if rv["stars"] >= 4 else fx(lang, "rv_low"))
    who = f"@{o['username']}" if o["username"] else html.escape(o["full_name"] or "")
    head = ("⭐" * rv["stars"]) + f" — #{oid} {service_label(o)}\n👤 {who}"
    body = f"\n\n«{html.escape(rv['text'])}»" if rv["text"] else ""
    if rv["stars"] <= 3:
        head = "⚠️ <b>Past baho!</b> Mijoz bilan bog'laning.\n" + head
    kb = None
    if rv["stars"] >= 4 and rv["text"] and rv["consent"] and channel_url():
        kb = ikb([[("📢 Kanalga joylash", f"adm:rvpub:{oid}", "success")]])
    elif rv["stars"] >= 4 and rv["text"] and not rv["consent"]:
        body += "\n<i>(mijoz kanalga joylashga rozi emas)</i>"
    await notify_admins(bot, head + body, kb)


def channel_chat() -> str:
    url = channel_url()
    return "@" + url.rstrip("/").split("/")[-1] if url else ""


def order_button(lang: str = "uz"):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=fx(lang, "post_btn"), url=f"https://t.me/{BOT_USERNAME}?start=kanal", style="success")]])


async def publish_review(c: CallbackQuery, bot: Bot, oid: int):
    rv, o = get_review(oid), get_order(oid)
    if not rv or not rv["consent"] or not rv["text"]:
        await c.message.answer("Bu sharhni joylab bo'lmaydi (rozilik yoki matn yo'q).")
        return
    if rv["published"]:
        await c.message.answer("Bu sharh allaqachon kanalda.")
        return
    name = (o["full_name"] or "").split()[0] if o["full_name"] else "Mijoz"
    text = (f"{'⭐' * rv['stars']}\n\n«{html.escape(rv['text'])}»\n\n— <b>{html.escape(name)}</b>, "
            f"{html.escape(service_label(o).replace("Do'kon: ", ''))}\n\n💜 Birzumda Tayyorla")
    try:
        await bot.send_message(channel_chat(), text, reply_markup=order_button())
    except Exception as e:
        await c.message.answer(f"❌ Kanalga yuborilmadi: {html.escape(str(e))[:200]}\n"
                               "Botni kanalga <b>admin</b> qilib qo'shing (xabar yuborish huquqi bilan).")
        return
    with db() as con:
        con.execute("UPDATE reviews SET published=1 WHERE order_id=?", (oid,))
    await c.message.answer("✅ Sharh kanalga joylandi!")


@router.message(Command("reviews", "sharhlar"))
async def reviews_cmd(m: Message):
    if not is_admin(m.from_user.id):
        return
    with db() as con:
        rows = con.execute("SELECT * FROM reviews ORDER BY created_at DESC LIMIT 10").fetchall()
        avg = con.execute("SELECT AVG(stars), COUNT(*) FROM reviews").fetchone()
    if not rows:
        await m.answer("Hali sharhlar yo'q.")
        return
    lines = [f"{'⭐' * r['stars']} #{r['order_id']}" + (f" — {html.escape(r['text'][:80])}" if r["text"] else "")
             + (" 📢" if r["published"] else "") for r in rows]
    await m.answer(f"⭐ <b>Sharhlar</b> · o'rtacha {avg[0]:.1f} ({avg[1]} ta)\n\n" + "\n".join(lines))


# ------------------------------------------------------------------ 📦 tayyor ishlar do'koni
def shop_items(active_only=True):
    with db() as con:
        q = "SELECT * FROM shop" + (" WHERE active=1" if active_only else "") + " ORDER BY id DESC LIMIT 40"
        return con.execute(q).fetchall()


def shop_item(sid: int):
    with db() as con:
        return con.execute("SELECT * FROM shop WHERE id=?", (sid,)).fetchone()


def shop_list_kb(lang: str):
    rows = [[(f"{it['title'][:40]} — {money(it['price'], lang)}", f"shop:i:{it['id']}", "primary")] for it in shop_items()]
    return ikb(rows) if rows else None


@router.message(F.text.in_(btn_texts("shop")))
@router.message(Command("tayyor", "shop"))
async def shop_menu(m: Message):
    lang = L(m.from_user.id)
    if m.text and m.text.startswith("/shop") and is_admin(m.from_user.id):
        await shop_admin_list(m)
        return
    kb = shop_list_kb(lang)
    await m.answer(fx(lang, "shop_title") if kb else fx(lang, "shop_empty"), reply_markup=kb)


@router.callback_query(F.data.startswith("shop:"))
async def shop_cb(c: CallbackQuery, state: FSMContext, bot: Bot):
    lang = L(c.from_user.id)
    _, act, *rest = c.data.split(":")
    await c.answer()
    if act == "list":
        kb = shop_list_kb(lang)
        await c.message.answer(fx(lang, "shop_title") if kb else fx(lang, "shop_empty"), reply_markup=kb)
        return
    it = shop_item(int(rest[0]))
    if not it or not it["active"]:
        await c.message.answer(fx(lang, "shop_empty"))
        return
    if act == "i":
        rows = [[(fx(lang, "shop_buy"), f"shop:b:{it['id']}", "success", "money")]]
        if it["preview_id"]:
            rows.append([(fx(lang, "shop_prev"), f"shop:p:{it['id']}", "primary")])
        rows.append([(fx(lang, "shop_back"), "shop:list", None)])
        await c.message.answer(fx(lang, "shop_item", title=html.escape(it["title"]), price=money(it["price"], lang)),
                               reply_markup=ikb(rows))
    elif act == "p" and it["preview_id"]:
        img = await watermark(bot, it["preview_id"])
        await c.message.answer_photo(BufferedInputFile(img, "namuna.jpg"),
                                     reply_markup=ikb([[(fx(lang, "shop_buy"), f"shop:b:{it['id']}", "success", "money")]]))
    elif act == "b":
        data = {"aud": "s", "svc": "shop", "pkg": "", "price": it["price"], "full_price": it["price"], "topic": it["title"],
                "deadline": "normal", "files": [], "brief": [], "shop_id": it["id"]}
        oid = create_order(data, c.from_user)
        await state.clear()
        await state.set_state(Order.cheque)
        await state.update_data(order_id=oid)
        await c.message.answer(payment_text(oid, it["price"], lang), reply_markup=mkb(c.from_user.id))
        await notify_admins(bot, f"🛒 <b>Do'kon</b>: #{oid} «{html.escape(it['title'])}» — {money(it['price'])}\n"
                                 f"👤 {html.escape(c.from_user.full_name)} · to'lov kutilmoqda")


async def deliver_shop(bot: Bot, o):
    it = shop_item(o["shop_id"]) if o["shop_id"] else None
    lang = L(o["user_id"])
    set_status(o["id"], "done")
    if not it:
        await notify_admins(bot, f"⚠️ #{o['id']} do'kon mahsuloti topilmadi — faylni qo'lda yuboring.")
        return
    await bot.send_message(o["user_id"], fx(lang, "shop_paid"))
    if it["file_type"] == "photo":
        await bot.send_photo(o["user_id"], it["file_id"], caption=tr(lang, "file_cap", oid=o["id"]))
    else:
        await bot.send_document(o["user_id"], it["file_id"], caption=tr(lang, "file_cap", oid=o["id"]))
    with db() as con:
        con.execute("UPDATE shop SET sold=sold+1 WHERE id=?", (it["id"],))
    await ask_review(bot, o)


@router.message(F.document | F.photo, F.caption.regexp(r"^/(sell|preview)\b"))
async def shop_admin_upload(m: Message):
    if not is_admin(m.from_user.id):
        return
    parts = m.caption.split(maxsplit=2)
    if parts[0] == "/preview":
        if len(parts) < 2 or not parts[1].isdigit() or not m.photo or not shop_item(int(parts[1])):
            await m.answer("Namuna qo'shish: rasm yuboring, izohiga <code>/preview ID</code> yozing.")
            return
        with db() as con:
            con.execute("UPDATE shop SET preview_id=? WHERE id=?", (m.photo[-1].file_id, int(parts[1])))
        await m.answer(f"✅ #{parts[1]} uchun namuna rasmi saqlandi (mijozga «NAMUNA» belgisi bilan ko'rinadi).")
        return
    if len(parts) < 3 or not parts[1].isdigit():
        await m.answer("Tayyor ish qo'shish: faylni yuboring, izohiga yozing:\n<code>/sell 15000 Sun'iy intellekt — slayd, 12 slayd</code>")
        return
    fid, ftype = (m.document.file_id, "doc") if m.document else (m.photo[-1].file_id, "photo")
    with db() as con:
        cur = con.execute("INSERT INTO shop(title, price, file_id, file_type, created_at) VALUES(?,?,?,?,?)",
                          (parts[2][:120], int(parts[1]), fid, ftype, datetime.now().strftime("%Y-%m-%d %H:%M")))
    await m.answer(f"✅ Do'konga qo'shildi: #{cur.lastrowid} «{html.escape(parts[2][:120])}» — {money(int(parts[1]))}\n"
                   f"Namuna rasmi: rasm yuborib, izohiga <code>/preview {cur.lastrowid}</code> yozing.\nRo'yxat: /dokon")


async def shop_admin_list(m: Message):
    rows = shop_items(active_only=False)
    if not rows:
        await m.answer("Do'kon bo'sh. Qo'shish: fayl + izoh <code>/sell 15000 Nomi</code>")
        return
    lines = [f"{'🟢' if r['active'] else '⚪️'} #{r['id']} {html.escape(r['title'][:50])} — {money(r['price'])} · "
             f"sotildi {r['sold']}" + (" · 👀" if r["preview_id"] else "") for r in rows]
    await m.answer("📦 <b>Do'kon</b>\n\n" + "\n".join(lines) + "\n\nO'chirish: <code>/delshop ID</code>")


@router.message(Command("dokon"))
async def dokon_cmd(m: Message):
    if is_admin(m.from_user.id):
        await shop_admin_list(m)


@router.message(Command("ochir", "delorder"))
async def ochir_cmd(m: Message, command: CommandObject):
    """Admin: /ochir 1 2 — sinov buyurtmalarini butunlay o'chirish (tasdiq bilan)."""
    if not is_admin(m.from_user.id):
        return
    ids = sorted({int(x) for x in (command.args or "").replace(",", " ").replace("#", " ").split() if x.isdigit()})
    rows = [get_order(i) for i in ids]
    rows = [o for o in rows if o]
    if not rows:
        await m.answer("Ishlatish: <code>/ochir 1 2</code> — buyurtma raqamlari")
        return
    lines = "\n".join(f"#{o['id']} · {html.escape(service_label(o))} · {html.escape((o['topic'] or '')[:40])} · "
                      f"{STATUS.get(o['status'], o['status'])}" for o in rows)
    key = "-".join(str(o["id"]) for o in rows)
    await m.answer(f"🗑 Shu buyurtmalar <b>butunlay o'chiriladi</b> (statistika va daromaddan ham):\n\n{lines}\n\nTasdiqlaysizmi?",
                   reply_markup=ikb([[("🗑 Ha, o'chirish", f"del:{key}", "danger"), ("Bekor", "del:no", None)]]))


@router.callback_query(F.data.startswith("del:"))
async def ochir_cb(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer("Ruxsat yo'q", show_alert=True)
        return
    arg = c.data.split(":", 1)[1]
    if arg == "no":
        await c.answer("Bekor qilindi")
        await c.message.edit_reply_markup(reply_markup=None)
        return
    ids = [int(x) for x in arg.split("-") if x.isdigit()]
    with db() as con:
        for i in ids:
            con.execute("DELETE FROM orders WHERE id=?", (i,))
            con.execute("DELETE FROM reviews WHERE order_id=?", (i,))
            con.execute("DELETE FROM settings WHERE key=?", (f"ai_file_{i}",))
    await c.answer("O'chirildi")
    await c.message.edit_text("✅ O'chirildi: " + ", ".join(f"#{i}" for i in ids))


@router.message(Command("delshop"))
async def delshop_cmd(m: Message, command: CommandObject):
    if not is_admin(m.from_user.id):
        return
    arg = (command.args or "").strip().lstrip("#")
    with db() as con:
        cur = con.execute("UPDATE shop SET active=0 WHERE id=?", (int(arg),)) if arg.isdigit() else None
    await m.answer(f"⚪️ #{arg} o'chirildi." if cur and cur.rowcount else "Ishlatish: <code>/delshop 3</code>")


# ------------------------------------------------------------------ 👀 to'lovdan oldin namuna (suv belgisi bilan)
async def watermark(bot: Bot, file_id: str) -> bytes:
    from io import BytesIO
    from PIL import Image, ImageDraw, ImageFont
    buf = BytesIO()
    await bot.download(file_id, destination=buf)
    img = Image.open(BytesIO(buf.getvalue())).convert("RGB")
    w, h = img.size
    layer = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    size = max(18, w // 22)
    try:
        font = ImageFont.load_default(size=size)
    except TypeError:
        font = ImageFont.load_default()
    text = "BIRZUMDA  -  NAMUNA     "
    tw = d.textlength(text, font=font)
    for y in range(0, h * 2, size * 4):
        x = -((y // (size * 4)) % 2) * tw / 2
        while x < w * 2:
            d.text((x, y), text, font=font, fill=(255, 255, 255, 85))
            x += tw
    layer = layer.rotate(28, resample=Image.BICUBIC).crop((w // 2, h // 2, w // 2 + w, h // 2 + h))
    out = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    res = BytesIO()
    out.save(res, "JPEG", quality=85)
    return res.getvalue()


@router.message(AdminSend.preview, F.photo)
async def preview_photo(m: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    o = get_order(data["prev_oid"])
    lang = L(o["user_id"])
    img = await watermark(bot, m.photo[-1].file_id)
    cap = fx(lang, "prev_msg", oid=o["id"]) if not data.get("prev_n") else None
    await bot.send_photo(o["user_id"], BufferedInputFile(img, "namuna.jpg"), caption=cap)
    await state.update_data(prev_n=data.get("prev_n", 0) + 1)
    await m.answer("Yuborildi (suv belgisi bilan). Yana rasm yoki /done.")


@router.message(AdminSend.preview, Command("done"))
async def preview_done(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data())["prev_oid"]
    await state.clear()
    o = get_order(oid)
    lang = L(o["user_id"])
    if o["status"] == "new":
        await bot.send_message(o["user_id"], fx(lang, "prev_ok") + "\n\n" + payment_text(oid, o["price"], lang))
    await m.answer(f"#{oid} — namuna mijozga yuborildi ✅")


@router.message(AdminSend.preview, ~F.text.startswith("/"))
async def preview_wrong(m: Message):
    await m.answer("Rasm (skrinshot) yuboring yoki /done.")


# ------------------------------------------------------------------ 📊 daromad
def parse_dt(s: str):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return None


@router.message(Command("daromad", "income"))
async def daromad_cmd(m: Message):
    if not is_admin(m.from_user.id):
        return
    from datetime import timedelta
    now = datetime.now()
    with db() as con:
        rows = con.execute("SELECT * FROM orders WHERE status IN ('work','done')").fetchall()
    per = {"today": [0, 0], "week": [0, 0], "month": [0, 0], "all": [0, 0]}
    top: dict[str, list] = {}
    for o in rows:
        d = parse_dt(o["paid_at"] or o["created_at"]) or now
        local_today = (now + timedelta(hours=TZ_OFFSET)).date()
        age = now - d
        keys = ["all"] + (["month"] if age.days < 30 else []) + (["week"] if age.days < 7 else []) + \
               (["today"] if (d + timedelta(hours=TZ_OFFSET)).date() == local_today else [])
        for k in keys:
            per[k][0] += o["price"] or 0
            per[k][1] += 1
        name = ("📦 Do'kon" if o["service"] == "shop" else "💎 Obuna" if o["service"] == "sub"
                else svc_tr(o["audience"], o["service"], "uz")[0])
        top.setdefault(name, [0, 0])
        top[name][0] += o["price"] or 0
        top[name][1] += 1
    best = sorted(top.items(), key=lambda kv: -kv[1][0])[:6]
    lines = "\n".join(f"{i + 1}. {html.escape(n)} — <b>{money(v[0])}</b> ({v[1]} ta)" for i, (n, v) in enumerate(best))
    await m.answer("📊 <b>Daromad</b>\n\n"
                   f"Bugun: <b>{som(per['today'][0])}</b> ({per['today'][1]} ta)\n"
                   f"7 kun: <b>{som(per['week'][0])}</b> ({per['week'][1]} ta)\n"
                   f"30 kun: <b>{som(per['month'][0])}</b> ({per['month'][1]} ta)\n"
                   f"Jami: <b>{som(per['all'][0])}</b> ({per['all'][1]} ta)\n\n"
                   f"🏆 <b>Eng ko'p daromad:</b>\n{lines or '—'}")


# ------------------------------------------------------------------ 🤖 avtomatik bajarish
AUTO_LOW_USD = 1.0


def auto_on() -> bool:
    return AG.enabled() and get_setting("auto_mode", "on") == "on"


def auto_ready(o) -> bool:
    return auto_on() and AG.kind_for(o) is not None and o["service"] != "shop"


def api_balance():
    try:
        top = float(get_setting("api_topup", "0") or 0)
    except ValueError:
        top = 0.0
    with db() as con:
        spent = con.execute("SELECT COALESCE(SUM(ai_cost),0) FROM orders").fetchone()[0] or 0.0
    return top, spent, (top - spent if top else None)


async def check_low_balance(bot: Bot):
    top, spent, left = api_balance()
    if left is None:
        return
    if left < AUTO_LOW_USD and get_setting("api_low_warned") != "1":
        set_setting("api_low_warned", "1")
        await notify_admins(bot, f"⚠️ <b>API balansi tugayapti</b>: taxminan <b>${max(left, 0):.2f}</b> qoldi "
                                 f"(to'ldirilgan ${top:.2f}, sarflangan ${spent:.2f}).\n"
                                 "platform.claude.com → Billing da to'ldiring, keyin yozing: <code>/avto +5</code>")


async def run_auto(bot: Bot, oid: int, to_client: bool = True):
    o = get_order(oid)
    if not o:
        return
    ul = L(o["user_id"])
    acc = AG.cost_tracker()
    with db() as con:
        con.execute("UPDATE orders SET auto='run' WHERE id=?", (oid,))
    try:
        name, data, report = await asyncio.wait_for(
            AG.generate(bot, o, svc_tr(o["audience"], o["service"], "uz")[0], ul), timeout=900)
        file = BufferedInputFile(data, filename=name)
        cost = acc[0]
        with db() as con:
            con.execute("UPDATE orders SET auto='ok', ai_cost=COALESCE(ai_cost,0)+? WHERE id=?", (cost, oid))
        kb = ikb([[("🔁 Qayta yaratish", f"adm:regen:{oid}", None)]] +
                 ([] if to_client else [[("📤 Mijozga yuborish", f"adm:pushai:{oid}", "success")]]))
        cap = (f"🤖 #{oid} — {'mijozga yuborildi ✅' if to_client else 'yangi variant (mijoz hali ko‘rmadi)'}\n"
               f"{html.escape(service_label(o))} · {report}\n💵 ${cost:.2f}")
        sent_fid = None
        for aid in ADMIN_IDS:
            try:
                msg = await bot.send_document(aid, file, caption=cap, reply_markup=kb)
                if msg and msg.document:
                    sent_fid = sent_fid or msg.document.file_id
                    file = msg.document.file_id  # keyingi yuborishlar uchun qayta yuklamaymiz
            except Exception as e:
                logging.warning("Admin nusxasi yuborilmadi: %s", e)
        if sent_fid:
            set_setting(f"ai_file_{oid}", sent_fid)
        if to_client:
            await bot.send_document(o["user_id"], file, caption=tr(ul, "file_cap", oid=oid))
            set_status(oid, "done")
            await bot.send_message(o["user_id"], tr(ul, "done", oid=oid, contact=CONTACT), reply_markup=fix_kb(oid, ul))
            await ask_review(bot, get_order(oid))
    except Exception as e:
        cost = acc[0]
        with db() as con:
            con.execute("UPDATE orders SET auto='fail', ai_cost=COALESCE(ai_cost,0)+? WHERE id=?", (cost, oid))
        logging.warning("Avto #%s xato: %s", oid, e)
        msg = str(e)[:300]
        if to_client:
            due = due_time(get_order(oid))
            try:
                await bot.send_message(o["user_id"], fx(ul, "auto_manual", oid=oid, due=fmt_local(due) if due else "—"))
            except Exception:
                pass
        head = "💳 <b>API balansi tugagan!</b>" if msg.startswith("BALANS") else "⚠️ <b>Avtomatik bajarilmadi</b>"
        await notify_admins(bot, f"{head} — #{oid}\n<code>{html.escape(msg)}</code>\n\n"
                                 + (f"Mijozga muddat yozildi. Qo'lda bajaring: /yubor_{oid}" if to_client else ""),
                            admin_kb(oid, "work") if to_client else None)
    await check_low_balance(bot)


async def approve_order(bot: Bot, oid: int, reply_to: Message | None = None, auto_note: str = ""):
    """To'lovni tasdiqlash: admin tugmasi yoki avtomatik chek tekshiruvi."""
    o = get_order(oid)
    with db() as con:
        con.execute("UPDATE orders SET paid_at=? WHERE id=?", (datetime.now().strftime("%Y-%m-%d %H:%M"), oid))
    ul = L(o["user_id"])
    await reward_referrer(bot, o["user_id"])

    async def tell(text, kb=None):
        if reply_to is not None:
            await reply_to.answer(text, reply_markup=kb)
        else:
            await notify_admins(bot, text, kb)

    if o["service"] == "shop":  # tayyor ish — faylni darhol yuboramiz
        await deliver_shop(bot, o)
        await tell(f"#{oid} — do'kon fayli mijozga avtomatik yuborildi ✅")
        return
    if o["service"] == "sub":
        s = activate_sub(o)
        set_status(oid, "done")
        await bot.send_message(o["user_id"], SUB_TX["active"][ul].format(
            plan=SUB_TX["name"][ul][o["package"]], till=fmt_local(datetime.strptime(s["ends"], "%Y-%m-%d %H:%M")), n=s["quota"]),
            reply_markup=MAIN_KBS[ul])
        await tell((auto_note + "\n" if auto_note else "") + f"💎 #{oid} — obuna faollashtirildi: {o['package']}, {s['quota']} ta ish.")
        return
    set_status(oid, "work")
    o = get_order(oid)
    due = due_time(o)
    if auto_ready(o):
        await bot.send_message(o["user_id"], fx(ul, "auto_wait", oid=oid))
        await tell((auto_note or f"#{oid} — ✅ tasdiqlandi.") + "\n🤖 Ish avtomatik tayyorlanmoqda (1–5 daqiqa), tayyor bo'lgach "
                   "mijozga yuboriladi va sizga nusxasi keladi.",
                   ikb([[("🚩 Soxta chek", f"adm:fake:{oid}", "danger")]]) if auto_note else None)
        asyncio.create_task(run_auto(bot, oid))
        return
    await bot.send_message(o["user_id"], tr(ul, "paid_ok", oid=oid, due=fmt_local(due) if due else "—"))
    if (o["qty"] or 1) >= 5 and GROUP_BONUS:
        add_bonus(o["user_id"], GROUP_BONUS)
        await bot.send_message(o["user_id"], fx(ul, "grp_bonus", sum=money(GROUP_BONUS, ul)))
    await tell(f"#{oid} — ishga olindi ✅ Mijozga muddat yozildi: <b>{fmt_local(due) if due else '—'}</b>\n\n"
               f"Tayyor bo'lgach: tugmani bosing yoki /yubor_{oid} → faylni tashlang → /done", admin_kb(oid, "work"))


def _digits(s) -> str:
    return "".join(ch for ch in str(s or "") if ch.isdigit())


async def check_cheque(bot: Bot, oid: int, file_id: str, unique_id: str, mime: str):
    """🧾 Chekni Claude bilan o'qib tekshiradi: summa, karta, sana, takror chek. Hammasi mos — avtomatik tasdiq."""
    from datetime import timedelta
    acc = AG.cost_tracker()
    reasons, info = [], {}
    try:
        if get_setting(f"cheque_{unique_id}"):
            reasons.append("bu chek avval boshqa buyurtmada ishlatilgan")
        buf = io.BytesIO()
        await bot.download(file_id, destination=buf)
        info = await asyncio.wait_for(AG.read_cheque(buf.getvalue(), mime if mime == "application/pdf" else "image/jpeg"), timeout=90)
        o = get_order(oid)
        need = int(o["price"] or 0)
        amount = int(_digits(info.get("amount")) or 0)
        last4 = _digits(info.get("recipient_card_last4"))[-4:]
        mine = _digits(CARD_NUMBER)[-4:]
        if not info.get("is_receipt"):
            reasons.append("rasm to'lov chekiga o'xshamaydi")
        if info.get("success") is False:
            reasons.append("chekda to'lov muvaffaqiyatli emas")
        if info.get("edited_signs"):
            reasons.append("tahrirlangan belgilar bor")
        if not need or amount < need - 500:
            reasons.append(f"summa mos emas ({money(amount) if amount else 'o‘qilmadi'} / kerak {money(need)})")
        if not last4 or last4 != mine:
            reasons.append(f"qabul qiluvchi karta mos emas (*{last4 or '?'} / sizniki *{mine})")
        dt = None
        try:
            dt = datetime.strptime(str(info.get("datetime"))[:16], "%Y-%m-%d %H:%M") - timedelta(hours=TZ_OFFSET)
        except (TypeError, ValueError):
            pass
        if not dt:
            reasons.append("chekda sana o'qilmadi")
        elif not (datetime.now() - timedelta(hours=36) <= dt <= datetime.now() + timedelta(minutes=30)):
            reasons.append("chek sanasi eski yoki noto'g'ri")
    except Exception as e:
        reasons.append(f"chek o'qilmadi ({str(e)[:120]})")
    with db() as con:
        con.execute("UPDATE orders SET ai_cost=COALESCE(ai_cost,0)+? WHERE id=?", (acc[0], oid))
    o = get_order(oid)
    if not o or o["status"] != "paid":  # admin allaqachon qaror qilgan
        return
    if reasons:
        await notify_admins(bot, f"🧾 #{oid} — <b>chek avtomatik tasdiqlanmadi</b>:\n• " + "\n• ".join(html.escape(r) for r in reasons)
                            + "\n\nKartangizni tekshirib, o'zingiz qaror qiling:", admin_kb(oid, "paid"))
        return
    set_setting(f"cheque_{unique_id}", str(oid))
    note = (f"✅ #{oid} — <b>chek avtomatik tasdiqlandi</b>: {money(int(_digits(info.get('amount'))))} → karta "
            f"*{_digits(CARD_NUMBER)[-4:]}, {html.escape(str(info.get('datetime')))}.\nVaqtingiz bo'lganda kartangizga tushganini tekshirib qo'ying.")
    await approve_order(bot, oid, None, note)


@router.message(Command("avto", "auto"))
async def avto_cmd(m: Message, command: CommandObject, bot: Bot):
    if not is_admin(m.from_user.id):
        return
    arg = (command.args or "").strip().lower().replace(",", ".")
    if arg in ("on", "yoq", "yoqish"):
        set_setting("auto_mode", "on")
    elif arg in ("off", "o'chir", "ochir"):
        set_setting("auto_mode", "off")
    elif arg in ("chek on", "chek off"):
        set_setting("auto_cheque", arg.split()[1])
    elif arg.startswith("+"):
        try:
            add = float(arg[1:].replace("$", ""))
            top = float(get_setting("api_topup", "0") or 0)
            set_setting("api_topup", f"{top + add:.2f}")
            set_setting("api_low_warned", None)
        except ValueError:
            await m.answer("Masalan: <code>/avto +5</code>")
            return
    elif arg.startswith("balans"):
        try:
            left = float(arg.split()[1].replace("$", ""))
            _, spent, _ = api_balance()
            set_setting("api_topup", f"{spent + left:.2f}")
            set_setting("api_low_warned", None)
        except (IndexError, ValueError):
            await m.answer("Masalan: <code>/avto balans 4.30</code> — platform.claude.com dagi qoldiq")
            return
    top, spent, left = api_balance()
    month = datetime.now().strftime("%Y-%m")
    with db() as con:
        r = con.execute("SELECT COUNT(*), COALESCE(SUM(ai_cost),0) FROM orders WHERE auto='ok' AND substr(paid_at,1,7)=?",
                        (month,)).fetchone()
        fails = con.execute("SELECT COUNT(*) FROM orders WHERE auto='fail' AND substr(paid_at,1,7)=?", (month,)).fetchone()[0]
    state = ("🟢 YOQILGAN" if auto_on() else "🔴 O'CHIRILGAN" if AG.enabled() else "⚪ API kalit yo'q (Railway → Variables → ANTHROPIC_API_KEY)")
    avg = (r[1] / r[0]) if r[0] else 0
    await m.answer(
        f"🤖 <b>Avtomatik bajarish</b>: {state}\n\n"
        f"Bu oy: <b>{r[0]}</b> ta ish avtomatik, {fails} ta qo'lda qoldi\n"
        f"Bu oy sarf: <b>${r[1]:.2f}</b>" + (f" (o'rtacha ${avg:.2f} / ish)" if r[0] else "") + "\n"
        + (f"API balansi: taxminan <b>${max(left, 0):.2f}</b> qoldi (to'ldirilgan ${top:.2f})\n" if left is not None
           else "API balansi: kiritilmagan — <code>/avto +5</code> deb yozing\n")
        + "\n<b>Avtomatik:</b> slayd (talaba), mustaqil ish, kurs ishi, referat, maqola, amaliy ish; ustozlar: taqdimot (Start), "
          "tadbir, maqola, test, dars ishlanmasi.\n<b>Qo'lda:</b> portfolio, O'UM, Boshqa, toshbaqa o'qituvchi, guruh buyurtmalari.\n\n"
          "<code>/avto off</code> — o'chirish · <code>/avto on</code> — yoqish\n"
          f"🧾 Chekni avtomatik tekshirish: <b>{'yoqilgan' if get_setting('auto_cheque', 'on') == 'on' else 'o‘chirilgan'}</b> — "
          "<code>/avto chek off</code> / <code>/avto chek on</code>\n"
          "<code>/avto +5</code> — $5 to'ldirdim · <code>/avto balans 4.30</code> — aniq qoldiq")


# ------------------------------------------------------------------ 💎 obuna
SUB_PLANS = {"day": (20000, 1, 3), "week": (50000, 7, 10), "month": (100000, 30, 25), "year": (300000, 365, 150)}
SUB_DISC = 30  # obunachilarga qolgan (qo'lda) ishlarga chegirma, %
SUB_TX = {
    "name": {"uz": {"day": "Kunlik obuna", "week": "Haftalik obuna", "month": "Oylik obuna", "year": "Yillik obuna"},
             "ru": {"day": "Подписка на день", "week": "Подписка на неделю", "month": "Подписка на месяц", "year": "Подписка на год"},
             "en": {"day": "Daily plan", "week": "Weekly plan", "month": "Monthly plan", "year": "Yearly plan"}},
    "menu": {"uz": "💎 <b>Obuna — ko'p ish, kam pul</b>\n\nObuna davomida <b>avtomatik ishlar</b> (slayd Start/Pro, mustaqil ish, referat, kurs ishi, maqola, test, dars ishlanmasi) <b>to'lovsiz</b> — bir necha daqiqada tayyor.\nPremium, portfolio, O'UM va boshqa ishlarga — <b>−{pct}%</b>.\n\n{plans}\n\n{status}",
             "ru": "💎 <b>Подписка — больше работ, меньше денег</b>\n\nВо время подписки <b>автоматические работы</b> (слайды Start/Pro, самостоятельная, реферат, курсовая, статья, тест, разработка урока) — <b>без оплаты</b>, готово за минуты.\nНа Premium, портфолио, УМК и др. — <b>−{pct}%</b>.\n\n{plans}\n\n{status}",
             "en": "💎 <b>Subscription — more work, less money</b>\n\nWhile subscribed, <b>automatic works</b> (Start/Pro slides, papers, essays, term papers, articles, tests, lesson plans) are <b>free</b> — ready in minutes.\nPremium, portfolio and other works — <b>−{pct}%</b>.\n\n{plans}\n\n{status}"},
    "plan": {"uz": "• <b>{name}</b> — {price} · {n} ta ish", "ru": "• <b>{name}</b> — {price} · {n} работ", "en": "• <b>{name}</b> — {price} · {n} works"},
    "none": {"uz": "Hozir obunangiz yo'q 👇 Tarifni tanlang:", "ru": "Сейчас подписки нет 👇 Выберите тариф:", "en": "No active plan 👇 Pick one:"},
    "have": {"uz": "✅ <b>Faol obuna:</b> {plan}\n⏰ {till} gacha · qoldi <b>{left}</b> ta ish", "ru": "✅ <b>Активна:</b> {plan}\n⏰ до {till} · осталось <b>{left}</b> работ",
             "en": "✅ <b>Active:</b> {plan}\n⏰ until {till} · <b>{left}</b> works left"},
    "covered": {"uz": "💎 Obuna hisobidan: <b>0 so'm</b> (keyin qoladi: {left} ta)", "ru": "💎 По подписке: <b>0 сум</b> (останется: {left})",
                "en": "💎 Covered by plan: <b>0</b> ({left} left after)"},
    "disc": {"uz": "💎 Obunachi chegirmasi {pct}%: −{sum}", "ru": "💎 Скидка подписчика {pct}%: −{sum}", "en": "💎 Subscriber discount {pct}%: −{sum}"},
    "used_ok": {"uz": "💎 Obuna hisobidan qabul qilindi! Ish hozir tayyorlanmoqda ⚡ (qoldi: {left} ta)", "ru": "💎 Принято по подписке! Работа уже готовится ⚡ (осталось: {left})",
                "en": "💎 Accepted on your plan! Your work is being prepared ⚡ ({left} left)"},
    "gone": {"uz": "Obuna tugagan yoki limit tugadi", "ru": "Подписка закончилась или лимит исчерпан", "en": "Plan expired or limit reached"},
    "active": {"uz": "🎉 <b>{plan} faollashtirildi!</b>\n⏰ {till} gacha · {n} ta ish.\nEndi buyurtma berganda avtomatik ishlar to'lovsiz bo'ladi 💎",
               "ru": "🎉 <b>{plan} активирована!</b>\n⏰ до {till} · {n} работ.\nТеперь автоматические работы — без оплаты 💎",
               "en": "🎉 <b>{plan} activated!</b>\n⏰ until {till} · {n} works.\nAutomatic works are now free for you 💎"},
}


def active_sub(uid: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with db() as con:
        return con.execute("SELECT * FROM subs WHERE user_id=? AND ends>? AND used<quota ORDER BY ends DESC LIMIT 1",
                           (uid, now)).fetchone()


def sub_covers(aud: str, svc: str, tk, pkg: str = "") -> bool:
    """Obuna faqat avtomatik ishlarni qoplaydi; Premium va toshbaqa — chegirma bilan."""
    return svc in AG.AUTO_SERVICES.get(aud, {}) and not tk and pkg != "premium"


def activate_sub(o):
    from datetime import timedelta
    price, days, quota = SUB_PLANS[o["package"]]
    now = datetime.now()
    with db() as con:
        cur = con.execute("SELECT * FROM subs WHERE user_id=? AND ends>? ORDER BY ends DESC LIMIT 1", (o["user_id"], now.strftime("%Y-%m-%d %H:%M"))).fetchone()
        start = datetime.strptime(cur["ends"], "%Y-%m-%d %H:%M") if cur else now  # uzaytirish — oxiriga qo'shiladi
        ends = (start + timedelta(days=days)).strftime("%Y-%m-%d %H:%M")
        con.execute("INSERT INTO subs(user_id, plan, starts, ends, quota, used, order_id, created_at) VALUES(?,?,?,?,?,0,?,?)",
                    (o["user_id"], o["package"], start.strftime("%Y-%m-%d %H:%M"), ends, quota, o["id"], now.strftime("%Y-%m-%d %H:%M")))
        return con.execute("SELECT * FROM subs WHERE order_id=?", (o["id"],)).fetchone()


def sub_menu_text(uid: int, lang: str) -> str:
    plans = "\n".join(SUB_TX["plan"][lang].format(name=SUB_TX["name"][lang][k], price=money(p, lang), n=q) for k, (p, d, q) in SUB_PLANS.items())
    s = active_sub(uid)
    status = (SUB_TX["have"][lang].format(plan=SUB_TX["name"][lang][s["plan"]], till=fmt_local(datetime.strptime(s["ends"], "%Y-%m-%d %H:%M")),
                                         left=s["quota"] - s["used"]) if s else SUB_TX["none"][lang])
    return SUB_TX["menu"][lang].format(pct=SUB_DISC, plans=plans, status=status)


def sub_kb(lang: str):
    btns = [(f"{SUB_TX['name'][lang][k]} · {money(p, lang)}", f"sub:{k}", "success" if k == "month" else "primary")
            for k, (p, d, q) in SUB_PLANS.items()]
    return ikb([btns[:2], btns[2:]])


@router.message(F.text.in_(btn_texts("sub")))
@router.message(Command("obuna", "sub", "podpiska"))
async def sub_menu(m: Message):
    lang = L(m.from_user.id)
    await m.answer(sub_menu_text(m.from_user.id, lang), reply_markup=sub_kb(lang))


@router.callback_query(F.data.startswith("sub:"))
async def sub_buy(c: CallbackQuery, state: FSMContext, bot: Bot):
    plan = c.data.split(":")[1]
    if plan not in SUB_PLANS:
        await c.answer()
        return
    lang = L(c.from_user.id)
    price = SUB_PLANS[plan][0]
    data = {"aud": "s", "svc": "sub", "pkg": plan, "price": price, "full_price": price, "topic": SUB_TX["name"]["uz"][plan],
            "deadline": "normal"}
    oid = create_order(data, c.from_user)
    await state.set_state(Order.cheque)
    await state.update_data(order_id=oid)
    await c.answer()
    await c.message.answer(payment_text(oid, price, lang), reply_markup=MAIN_KBS[lang])
    await notify_admins(bot, f"💎 Yangi obuna so'rovi #{oid}: {SUB_TX['name']['uz'][plan]} — {money(price)}\n"
                             f"👤 {html.escape(c.from_user.full_name)} (<code>{c.from_user.id}</code>) — chek kutilmoqda")


@router.message(Command("obunalar"))
async def subs_admin(m: Message):
    if not is_admin(m.from_user.id):
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with db() as con:
        rows = con.execute("SELECT s.*, u.full_name FROM subs s LEFT JOIN users u ON u.user_id=s.user_id WHERE s.ends>? ORDER BY s.ends",
                           (now,)).fetchall()
    if not rows:
        await m.answer("Faol obuna yo'q.")
        return
    lines = [f"• {html.escape(r['full_name'] or str(r['user_id']))} — {r['plan']}, {r['used']}/{r['quota']}, "
             f"{fmt_local(datetime.strptime(r['ends'], '%Y-%m-%d %H:%M'))} gacha" for r in rows]
    await m.answer("💎 <b>Faol obunalar</b>\n\n" + "\n".join(lines))


# ------------------------------------------------------------------ 🎬 reklama, ✏️ tuzatish, 💬 yordam, ❓ FAQ
CX = {
    "fix_btn": {"uz": "✏️ Tuzatish so'rash", "ru": "✏️ Попросить правки", "en": "✏️ Request changes"},
    "fix_ask": {"uz": "✏️ Buyurtma #{oid}: <b>nimani o'zgartirish kerak?</b>\nAniq yozing (masalan: «3-slayddagi rasmni almashtiring, 5-slaydga raqam qo'shing»). Rasm/fayl ham yuborsangiz bo'ladi. Tuzatish <b>bepul</b> 🔁",
                "ru": "✏️ Заказ #{oid}: <b>что нужно изменить?</b>\nНапишите конкретно (например: «замените фото на 3-м слайде»). Можно приложить фото/файл. Правки <b>бесплатно</b> 🔁",
                "en": "✏️ Order #{oid}: <b>what should we change?</b>\nBe specific (e.g. «replace the photo on slide 3»). You can attach a photo/file. Revisions are <b>free</b> 🔁"},
    "fix_ok": {"uz": "✅ Qabul qilindi! Tuzatilgan variant shu chatga keladi.", "ru": "✅ Принято! Исправленный вариант придёт в этот чат.",
               "en": "✅ Got it! The revised version will arrive in this chat."},
    "faq_btn": {"uz": "❓ Savol-javob", "ru": "❓ Вопросы", "en": "❓ FAQ"},
    "sup_btn": {"uz": "💬 Adminga yozish", "ru": "💬 Написать админу", "en": "💬 Message admin"},
    "sup_ask": {"uz": "💬 Savolingizni yozing (rasm ham bo'ladi) — admin shu yerda javob beradi.",
                "ru": "💬 Напишите вопрос (можно с фото) — админ ответит здесь.", "en": "💬 Type your question (photos OK) — the admin will reply here."},
    "sup_ok": {"uz": "✅ Yuborildi! Javob shu chatga keladi.", "ru": "✅ Отправлено! Ответ придёт сюда.", "en": "✅ Sent! The reply will come here."},
    "sup_reply": {"uz": "💬 <b>Admin javobi:</b>\n", "ru": "💬 <b>Ответ админа:</b>\n", "en": "💬 <b>Admin reply:</b>\n"},
    "faq": {"uz": "❓ <b>Ko'p beriladigan savollar</b>\n\n<b>Qanday to'layman?</b> — Buyurtma oxirida karta raqami chiqadi. O'tkazib, chek rasmini yuborasiz.\n\n"
                  "<b>Qancha vaqtda tayyor?</b> — Ko'p ishlar to'lovdan keyin bir necha daqiqada avtomatik keladi. Murakkab ishlar — paketga qarab 3–12 soat.\n\n"
                  "<b>Tuzatish bepulmi?</b> — Ha. Ish kelgach «✏️ Tuzatish so'rash» ni bosing.\n\n"
                  "<b>Rasmlarimni qo'shasizmi?</b> — Ha. Buyurtmada galereyadan yuboring; sifat yo'qolmasin desangiz 📎 Fayl qilib.\n\n"
                  "<b>Qaysi formatda beriladi?</b> — Slayd: PPTX (xohlasangiz PDF), yozma ishlar: Word (DOCX).\n\n"
                  "<b>Lotin yoki kirill?</b> — Qaysi birini tanlasangiz, o'shanda.",
            "ru": "❓ <b>Частые вопросы</b>\n\n<b>Как оплатить?</b> — В конце заказа появится номер карты. Переведите и отправьте фото чека.\n\n"
                  "<b>Когда будет готово?</b> — Большинство работ приходит автоматически через несколько минут после оплаты. Сложные — 3–12 часов по пакету.\n\n"
                  "<b>Правки бесплатно?</b> — Да. После получения нажмите «✏️ Попросить правки».\n\n"
                  "<b>Добавите мои фото?</b> — Да. Отправьте их при заказе; для лучшего качества — через 📎 Файл.\n\n"
                  "<b>Формат?</b> — Слайды: PPTX (по желанию PDF), письменные работы: Word (DOCX).",
            "en": "❓ <b>FAQ</b>\n\n<b>How do I pay?</b> — The card number appears at the end of the order. Transfer and send the receipt photo.\n\n"
                  "<b>How fast?</b> — Most work arrives automatically minutes after payment. Complex work: 3–12 hours by package.\n\n"
                  "<b>Are revisions free?</b> — Yes. Tap «✏️ Request changes» after delivery.\n\n"
                  "<b>Will you add my photos?</b> — Yes. Send them when ordering; for best quality use 📎 File.\n\n"
                  "<b>Format?</b> — Slides: PPTX (PDF on request), papers: Word (DOCX)."},
}


def fix_kb(oid: int, lang: str):
    return ikb([[(CX["fix_btn"][lang], f"fix:{oid}", "primary")]])


@router.callback_query(F.data.startswith("fix:"))
async def fix_start(c: CallbackQuery, state: FSMContext):
    oid = int(c.data.split(":")[1])
    o = get_order(oid)
    if not o or o["user_id"] != c.from_user.id:
        await c.answer()
        return
    await c.answer()
    await state.set_state(FixReq.text)
    await state.update_data(fix_oid=oid)
    await c.message.answer(CX["fix_ask"][L(c.from_user.id)].format(oid=oid))


@router.message(FixReq.text, ~F.text.startswith("/") | ~F.text)
async def fix_got(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data()).get("fix_oid")
    await state.clear()
    o = get_order(oid)
    lang = L(m.from_user.id)
    with db() as con:
        con.execute("UPDATE orders SET status='work' WHERE id=?", (oid,))
    for aid in ADMIN_IDS:
        try:
            await bot.send_message(aid, f"✏️ <b>Tuzatish so'raldi</b> — #{oid} {html.escape(service_label(o))}\n"
                                        f"👤 {html.escape(m.from_user.full_name)} (<code>{m.from_user.id}</code>)\n\n"
                                        f"Tuzatilgan faylni yuborish: /yubor_{oid}")
            await bot.copy_message(aid, m.chat.id, m.message_id)
        except Exception as e:
            logging.warning("Tuzatish so'rovi yuborilmadi: %s", e)
    await m.answer(CX["fix_ok"][lang], reply_markup=mkb(m.from_user.id))


@router.callback_query(F.data.startswith("help:"))
async def help_cb(c: CallbackQuery, state: FSMContext):
    lang = L(c.from_user.id)
    await c.answer()
    if c.data == "help:faq":
        await c.message.answer(CX["faq"][lang])
    else:
        await state.set_state(Support.text)
        await c.message.answer(CX["sup_ask"][lang])


@router.message(Command("faq", "savol"))
async def faq_cmd(m: Message):
    await m.answer(CX["faq"][L(m.from_user.id)])


@router.message(Command("yordam", "support"))
async def support_cmd(m: Message, state: FSMContext):
    await state.set_state(Support.text)
    await m.answer(CX["sup_ask"][L(m.from_user.id)])


@router.message(Support.text)
async def support_got(m: Message, state: FSMContext, bot: Bot):
    await state.clear()
    for aid in ADMIN_IDS:
        try:
            await bot.send_message(aid, f"💬 <b>Mijozdan savol</b> — {html.escape(m.from_user.full_name)} (<code>{m.from_user.id}</code>)\n"
                                        f"Javob: <code>/javob {m.from_user.id} matn</code>")
            await bot.copy_message(aid, m.chat.id, m.message_id)
        except Exception as e:
            logging.warning("Savol yuborilmadi: %s", e)
    await m.answer(CX["sup_ok"][L(m.from_user.id)], reply_markup=mkb(m.from_user.id))


@router.message(Command("javob"))
async def javob_cmd(m: Message, command: CommandObject, bot: Bot):
    if not is_admin(m.from_user.id):
        return
    parts = (command.args or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[0].isdigit():
        await m.answer("Ishlatish: <code>/javob 123456789 matn</code>")
        return
    uid = int(parts[0])
    try:
        await bot.send_message(uid, CX["sup_reply"][L(uid)] + html.escape(parts[1]))
        await m.answer("✅ Javob yuborildi")
    except Exception as e:
        await m.answer(f"❌ Yuborilmadi: {html.escape(str(e))[:200]}")


# --- 🎬 reklama video (/start da birinchi marta)
AD_FILE = BASE / "reklama.mp4"


async def send_ad(m: Message):
    fid = get_setting("ad_file_id")
    try:
        if fid:
            await m.answer_video(fid)
        elif AD_FILE.exists():
            msg = await m.answer_video(FSInputFile(AD_FILE), width=1080, height=1350, supports_streaming=True)
            if msg and msg.video:
                set_setting("ad_file_id", msg.video.file_id)
    except Exception as e:
        logging.warning("Reklama yuborilmadi: %s", e)


@router.message(F.video, F.caption.regexp(r"^/reklama\b"))
async def set_ad(m: Message):
    if not is_admin(m.from_user.id):
        return
    set_setting("ad_file_id", m.video.file_id)
    with db() as con:
        con.execute("UPDATE users SET ad_seen=0")
    await m.answer("✅ Reklama video yangilandi. Endi /start bosgan har bir foydalanuvchi uni bir marta ko'radi.")


@router.message(Command("reklama"))
async def show_ad_cmd(m: Message):
    await send_ad(m)


# ------------------------------------------------------------------ ⏰ eslatmalar (muddat va to'lov)
PKG_HOURS = {"start": 3, "pro": 6, "premium": 12}  # to'lovdan keyin, soatda
URGENT_HOURS = 2
OTHER_HOURS = 6                                       # paketsiz xizmatlar (mustaqil ish, referat…)
WORK_FROM, WORK_TO = 10, 22                           # tunda tushsa — ertalab 10:00 ga


def due_time(o):
    """Tayyor bo'lish muddati (UTC). Tunga (22:00–10:00, Toshkent) tushsa — ertalab 10:00."""
    from datetime import timedelta
    start = parse_dt(o["paid_at"] or o["created_at"])
    if not start:
        return None
    hours = URGENT_HOURS if o["deadline"] == "urgent" else PKG_HOURS.get(o["package"] or "", OTHER_HOURS)
    local = start + timedelta(hours=TZ_OFFSET + hours)
    if local.hour >= WORK_TO:
        local = (local + timedelta(days=1)).replace(hour=WORK_FROM, minute=0)
    elif local.hour < WORK_FROM:
        local = local.replace(hour=WORK_FROM, minute=0)
    return local - timedelta(hours=TZ_OFFSET)


def fmt_local(d) -> str:
    from datetime import timedelta
    return (d + timedelta(hours=TZ_OFFSET)).strftime("%d.%m %H:%M")


async def check_reminders(bot: Bot):
    from datetime import timedelta
    now = datetime.now()
    with db() as con:
        unpaid = con.execute("SELECT * FROM orders WHERE status='new' AND remind_pay=0").fetchall()
        working = con.execute("SELECT * FROM orders WHERE status='work' AND remind_adm<2").fetchall()
    for o in unpaid:
        created = parse_dt(o["created_at"])
        if created and now - created >= timedelta(hours=REMIND_PAY_HOURS):
            with db() as con:
                con.execute("UPDATE orders SET remind_pay=1 WHERE id=?", (o["id"],))
            try:
                await bot.send_message(o["user_id"], fx(L(o["user_id"]), "pay_remind", oid=o["id"]))
            except Exception as e:
                logging.info("To'lov eslatmasi yuborilmadi: %s", e)
    for o in working:
        due = due_time(o)
        if not due:
            continue
        level = 2 if now >= due else 1 if now >= due - timedelta(hours=1) else 0
        if level > o["remind_adm"]:
            with db() as con:
                con.execute("UPDATE orders SET remind_adm=? WHERE id=?", (level, o["id"]))
            head = "🔴 <b>Muddat o'tdi!</b>" if level == 2 else "⏰ <b>Muddat yaqin</b> — 1 soatdan kam qoldi"
            await notify_admins(bot, f"{head} — #{o['id']} {html.escape(service_label(o))}\n"
                                     f"📝 {html.escape(o['topic'][:80])}\n🕐 Muddat: {fmt_local(due)}\n📤 Yuborish: /yubor_{o['id']}",
                                admin_kb(o["id"], "work"))


async def reminders_loop(bot: Bot):
    await asyncio.sleep(20)
    while True:
        try:
            await check_reminders(bot)
        except Exception as e:
            logging.warning("Eslatmalar xatosi: %s", e)
        await asyncio.sleep(300)  # har 5 daqiqada


@router.message(Command("muddat", "deadlines"))
async def muddat_cmd(m: Message):
    if not is_admin(m.from_user.id):
        return
    with db() as con:
        rows = con.execute("SELECT * FROM orders WHERE status='work'").fetchall()
    items = sorted(((due_time(o), o) for o in rows if due_time(o)), key=lambda x: x[0])
    if not items:
        await m.answer("Hozir ishda buyurtma yo'q ✅")
        return
    now = datetime.now()
    lines = [f"{'🔴' if d <= now else '🟡' if (d - now).total_seconds() < 3600 else '🟢'} #{o['id']} "
             f"{html.escape(service_label(o))} — <b>{fmt_local(d)}</b>  /yubor_{o['id']}" for d, o in items]
    await m.answer("⏰ <b>Ishdagi buyurtmalar muddati</b>\n\n" + "\n".join(lines))


# ------------------------------------------------------------------ 📢 kanalga post
@router.message(Command("post"))
async def post_start(m: Message, state: FSMContext):
    if not is_admin(m.from_user.id):
        return
    if not channel_chat():
        await m.answer("Kanal sozlanmagan (CHANNEL).")
        return
    await state.set_state(AdminSend.post)
    await m.answer(f"📢 {channel_chat()} kanaliga post: matn, rasm yoki video yuboring.\n"
                   "Postga «✨ Buyurtma berish» tugmasi avtomatik qo'shiladi. Bekor qilish: /cancel")


@router.message(AdminSend.post, ~F.text.startswith("/"))
async def post_preview(m: Message, state: FSMContext, bot: Bot):
    await state.update_data(post_chat=m.chat.id, post_msg=m.message_id)
    await state.set_state(AdminSend.post_confirm)
    await bot.copy_message(m.chat.id, m.chat.id, m.message_id, reply_markup=order_button())
    await m.answer("👆 Kanalda shunday ko'rinadi. Yuboraymi?",
                   reply_markup=ikb([[("📢 Kanalga yuborish", "post:go", "success"), ("❌ Bekor", "post:no", "danger")]]))


@router.callback_query(AdminSend.post_confirm, F.data.startswith("post:"))
async def post_go(c: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    await c.answer()
    if c.data == "post:no":
        await c.message.answer("Bekor qilindi.")
        return
    try:
        await bot.copy_message(channel_chat(), data["post_chat"], data["post_msg"], reply_markup=order_button())
        await c.message.answer(f"✅ Post {channel_chat()} kanaliga joylandi!")
    except Exception as e:
        await c.message.answer(f"❌ Yuborilmadi: {html.escape(str(e))[:200]}\n"
                               "Botni kanalga <b>admin</b> qilib qo'shing (xabar yuborish huquqi bilan).")


# ------------------------------------------------------------------ admin yordam
@router.message(Command("admin"))
async def admin_help(m: Message):
    if not is_admin(m.from_user.id):
        return
    await m.answer(
        "🛠 <b>Admin buyruqlari</b>\n\n"
        "📊 /daromad — daromad · /stats — statistika · /orders — oxirgi buyurtmalar\n"
        "⏰ /muddat — ishdagi buyurtmalar muddati\n"
        "📤 /yubor 12 — tayyor ishni mijozga yuborish\n"
        "🤖 /avto — avtomatik bajarish, API balansi\n"
        "🗑 /ochir 1 2 — sinov buyurtmalarini o'chirish\n"
        "🎬 Video + izoh /reklama — /start reklamasini almashtirish\n"
        "💬 /javob ID matn — mijoz savoliga javob\n"
        "💎 /obunalar — faol obunalar\n"
        "📋 <code>/tz 12</code> — texnik topshiriq\n"
        "⭐ /reviews — sharhlar\n"
        "📦 /dokon — tayyor ishlar · fayl + <code>/sell 15000 Nomi</code> · rasm + <code>/preview ID</code> · "
        "<code>/delshop ID</code>\n"
        "🎟 <code>/promo KOD FOIZ [SONI]</code> · /promos · <code>/delpromo KOD</code>\n"
        "🔥 <code>/aksiya matn</code> · 🎁 <code>/addbonus ID SUMMA</code>\n"
        "📢 /post — kanalga post · /broadcast — hammaga xabar\n"
        "👀 Buyurtmadagi «Namuna yuborish» — to'lovdan oldin suv belgili rasmlar")


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
        await approve_order(bot, oid, c.message)
    elif act == "fake":
        set_status(oid, "rejected")
        try:
            await bot.send_message(o["user_id"], tr(L(o["user_id"]), "rejected", oid=oid, contact=CONTACT))
        except Exception:
            pass
        await c.message.answer(f"🚩 #{oid} — soxta chek deb belgilandi, mijozga xabar yuborildi.")
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
    elif act == "prev":
        await state.set_state(AdminSend.preview)
        await state.update_data(prev_oid=oid, prev_n=0)
        await c.message.answer(f"#{oid} uchun 2–3 ta slayd rasmini (skrinshot) yuboring — bot ularga «NAMUNA» suv belgisini "
                               "qo'yib mijozga yuboradi. Tugatgach /done yozing.")
    elif act == "rvpub":
        await publish_review(c, bot, oid)
    elif act == "regen":
        await c.message.answer(f"🔁 #{oid} qayta yaratilmoqda… Tayyor bo'lgach avval sizga keladi (mijozga emas).")
        asyncio.create_task(run_auto(bot, oid, to_client=False))
    elif act == "pushai":
        fid = get_setting(f"ai_file_{oid}")
        if not fid:
            await c.answer("Fayl topilmadi", show_alert=True)
            return
        ul = L(o["user_id"])
        await bot.send_document(o["user_id"], fid, caption=tr(ul, "file_cap", oid=oid) + " (yangilangan)")
        await c.message.answer(f"#{oid} — yangi variant mijozga yuborildi ✅")
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


async def start_send(m: Message, state: FSMContext, arg: str):
    """Admin: tayyor ishni yuborish rejimi (tugmani qidirmasdan)."""
    o = get_order(int(arg)) if arg.isdigit() else None
    if not o:
        with db() as con:
            rows = con.execute("SELECT id, topic FROM orders WHERE status='work' ORDER BY id").fetchall()
        lst = "\n".join(f"/yubor_{r['id']} — {html.escape((r['topic'] or '')[:40])}" for r in rows) or "Ishdagi buyurtma yo'q ✅"
        await m.answer("Qaysi buyurtma? Masalan: <code>/yubor 12</code>\n\n<b>Ishdagilar:</b>\n" + lst)
        return
    if o["status"] in ("new", "quote"):
        await m.answer(f"#{o['id']} hali to'lanmagan ({STATUS.get(o['status'], o['status'])}). Avval to'lovni tasdiqlang.")
        return
    await state.set_state(AdminSend.file)
    await state.update_data(send_oid=o["id"])
    await m.answer(f"📤 #{o['id']} — <b>{html.escape(service_label(o))}</b>\n📝 {html.escape(o['topic'][:80])}\n\n"
                   "Tayyor fayl(lar)ni shu yerga tashlang (PPTX, DOCX, PDF…), keyin /done yozing.")


@router.message(Command("yubor", "send"))
async def yubor_cmd(m: Message, command: CommandObject, state: FSMContext):
    if is_admin(m.from_user.id):
        await start_send(m, state, (command.args or "").strip().lstrip("#"))


@router.message(F.text.regexp(r"^/yubor_\d+"))
async def yubor_link(m: Message, state: FSMContext):
    if is_admin(m.from_user.id):
        await start_send(m, state, m.text.split("_", 1)[1].split("@")[0].strip())


@router.message(AdminSend.file, Command("done"))
async def admin_done(m: Message, state: FSMContext, bot: Bot):
    oid = (await state.get_data())["send_oid"]
    set_status(oid, "done")
    await state.clear()
    o = get_order(oid)
    await bot.send_message(o["user_id"], tr(L(o["user_id"]), "done", oid=oid, contact=CONTACT), reply_markup=fix_kb(oid, L(o["user_id"])))
    await ask_review(bot, o)
    await m.answer(f"#{oid} — topshirildi ✅ Mijozdan baho so'raldi.")


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
    return {"urgent": URGENT_EXTRA, "turtle": TURTLE_ADDON,
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


class RetryMiddleware:
    """Telegram'ga ulanish uzilsa (Connection reset), so'rovni 3 martagacha qayta yuboradi."""

    async def __call__(self, make_request, bot, method):
        from aiogram.exceptions import TelegramNetworkError
        for attempt in range(3):
            try:
                return await make_request(bot, method)
            except TelegramNetworkError as e:
                if attempt == 2:
                    raise
                logging.warning("Tarmoq xatosi, qayta urinish %s: %s", attempt + 1, e)
                await asyncio.sleep(1 + attempt * 2)


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
    bot.session.middleware(RetryMiddleware())
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
    asyncio.create_task(reminders_loop(bot))
    global BOT_USERNAME
    try:
        BOT_USERNAME = (await bot.get_me()).username or BOT_USERNAME
    except Exception as e:
        logging.warning("get_me: %s", e)
    runner = web.AppRunner(make_web_app())
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    logging.info("Mini ilova serveri %s portda ishga tushdi", PORT)
    await bot.delete_webhook(drop_pending_updates=False)  # qayta ishga tushganda xabarlar yo'qolmasin
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
