"""
mybirzumda.uz sayti uchun API (Birzumda Tayyorla bazasidan o'qiydi).

Bot ichidagi web-serverga ulanadi: bot.py → make_web_app() → site_api.register(app, ...)

Muhit o'zgaruvchilari (ixtiyoriy):
  SITE_ORIGINS — saytga ruxsat berilgan manzillar, vergul bilan
                 (standart: https://mybirzumda.uz,https://www.mybirzumda.uz)

Yo'llar:
  GET  /api/site/stats            — foydalanuvchilar, bajarilgan buyurtmalar, bot holati
  GET  /api/site/reviews          — tasdiqlangan sharhlar
  GET  /api/site/catalog          — xizmatlar, paketlar, narxlar va obuna tariflari
  POST /api/site/auth             — Telegram Login Widget ma'lumotini tekshiradi → token
  POST /api/site/login/start      — tezkor kirish: bot uchun bir martalik havola (t.me/...?start=login_X)
  GET  /api/site/login/check      — sayt shu yerni so'raydi; botda tasdiqlangach → token
  GET  /api/site/me               — shaxsiy kabinet (token kerak)
  POST /api/site/reviews          — sharh qoldirish (token + bajarilgan buyurtma kerak)
  GET  /api/site/admin            — admin panel ma'lumotlari (faqat ADMIN_ID)
  POST /api/site/admin/review/ID  — sharhni tasdiqlash (faqat ADMIN_ID)
"""
import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime

from aiohttp import web

TOKEN_DAYS = 30
LOGIN_MAX_AGE = 24 * 3600  # Telegram login ma'lumoti 24 soatdan eski bo'lmasin

# ---------------------------------------------------------------- tezkor kirish (raqamsiz)
# Sayt «Kirish»ni bosadi → bot ochiladi (/start login_TOKEN) → «✅ Ha, kiraman» → sayt tokenni oladi.
# poll_key faqat saytning o'zida turadi: havolani ko'rgan boshqa odam sessiyani ololmaydi.
QUICK_TTL = 300
QUICK_MAX = 20000
PENDING: dict[str, dict] = {}


def _quick_clean():
    now = time.time()
    for k in [k for k, v in PENDING.items() if v["exp"] < now]:
        PENDING.pop(k, None)


def quick_pending(token: str):
    """Bot uchun: token haqiqiymi (muddati o'tmaganmi). Saytdagi tilni qaytaradi."""
    v = PENDING.get(token)
    if not v or v["exp"] < time.time() or v.get("uid"):
        return None
    return v


def quick_confirm(token: str, user) -> bool:
    """Bot uchun: foydalanuvchi «Ha, kiraman»ni bosdi."""
    v = quick_pending(token)
    if not v:
        return False
    v["uid"] = user.id
    v["user"] = {"id": user.id, "first_name": user.first_name or "", "username": user.username or "",
                 "photo_url": ""}
    v["exp"] = time.time() + 120   # sayt 2 daqiqa ichida olib ketsin
    return True


def quick_cancel(token: str):
    PENDING.pop(token, None)


_DB = {"db": None}


def quick_revoke(uid: int):
    """«Bu men emasman»: shu foydalanuvchining saytdagi barcha sessiyalarini bekor qiladi."""
    if _DB["db"] is None:
        return
    with _DB["db"]() as con:
        con.execute("CREATE TABLE IF NOT EXISTS site_revoke(uid INTEGER PRIMARY KEY, ts INTEGER)")
        con.execute("INSERT OR REPLACE INTO site_revoke(uid, ts) VALUES(?, ?)", (uid, int(time.time()) + 1))


def register(app: web.Application, *, db, bot_token: str, admin_ids, ref_link, ref_stats,
             bonus_balance, service_label, status_tr, get_setting,
             catalog_json=None, sub_plans=None, sub_names=None, sub_disc=0, login_tokens=()):
    origins = {o.strip().rstrip("/") for o in os.getenv(
        "SITE_ORIGINS", "https://mybirzumda.uz,https://www.mybirzumda.uz").split(",") if o.strip()}
    # Telegram Login tekshiruvi: asosiy bot va sayt uchun alohida kirish boti (SITE_LOGIN_BOT_TOKEN)
    login_secrets = [hashlib.sha256(t.encode()).digest() for t in (bot_token, *login_tokens) if t]
    token_secret = hashlib.sha256(b"site-session:" + bot_token.encode()).digest()  # o'z tokenlarimiz uchun

    # ---------------------------------------------------------------- CORS
    @web.middleware
    async def cors(request, handler):
        if not request.path.startswith("/api/site/"):
            return await handler(request)
        if request.method == "OPTIONS":
            resp = web.Response(status=204)
        else:
            try:
                resp = await handler(request)
            except web.HTTPException as e:
                resp = e
        origin = request.headers.get("Origin", "").rstrip("/")
        if origin in origins:
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
            resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return resp

    app.middlewares.append(cors)
    _DB["db"] = db
    with db() as con:
        con.execute("CREATE TABLE IF NOT EXISTS site_revoke(uid INTEGER PRIMARY KEY, ts INTEGER)")

    # ---------------------------------------------------------------- token
    def make_token(uid: int) -> str:
        payload = f"{uid}.{int(time.time()) + TOKEN_DAYS * 86400}"
        sig = hmac.new(token_secret, payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{sig}"

    def read_token(request):
        auth = request.headers.get("Authorization", "")
        tok = auth[7:] if auth.startswith("Bearer ") else ""
        try:
            uid, exp, sig = tok.split(".")
            good = hmac.new(token_secret, f"{uid}.{exp}".encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(sig, good) and int(exp) > time.time():
                with db() as con:
                    row = con.execute("SELECT ts FROM site_revoke WHERE uid=?", (int(uid),)).fetchone()
                issued = int(exp) - TOKEN_DAYS * 86400
                if not row or issued >= row[0]:
                    return int(uid)
        except ValueError:
            pass
        raise web.HTTPUnauthorized(text='{"error":"auth"}', content_type="application/json")

    def lang_of(request):
        lang = request.query.get("lang", "uz")
        return lang if lang in ("uz", "ru", "en") else "uz"

    # ---------------------------------------------------------------- ochiq yo'llar
    async def stats(_):
        with db() as con:
            users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            done = con.execute("SELECT COUNT(*) FROM orders WHERE status='done'").fetchone()[0]
        # bu javob kelgan bo'lsa — Tayyorla boti ishlayapti (server bot bilan bitta jarayonda)
        return web.json_response({"users": users, "orders": done, "downloads": None,
                                  "status": {"tayyorla": True, "yukla": None}})

    async def reviews(_):
        with db() as con:
            rows = con.execute("""SELECT r.stars, r.text, r.created_at, o.full_name FROM reviews r
                                  LEFT JOIN orders o ON o.id = r.order_id
                                  WHERE r.consent=1 AND r.published=1 AND r.text<>''
                                  ORDER BY r.created_at DESC LIMIT 12""").fetchall()
        return web.json_response([{"name": ((r["full_name"] or "Mijoz").split() or ["Mijoz"])[0],
                                   "stars": r["stars"], "text": r["text"]} for r in rows])

    async def auth(request):
        data = await request.json()
        data = {k: str(v) for k, v in data.items() if v is not None}
        got_hash = data.pop("hash", "")
        check = "\n".join(f"{k}={data[k]}" for k in sorted(data))
        if not any(hmac.compare_digest(got_hash, hmac.new(sec, check.encode(), hashlib.sha256).hexdigest())
                   for sec in login_secrets):
            return web.json_response({"error": "bad_hash"}, status=403)
        if time.time() - int(data.get("auth_date", 0)) > LOGIN_MAX_AGE:
            return web.json_response({"error": "expired"}, status=403)
        uid = int(data["id"])
        return web.json_response({"token": make_token(uid), "admin": uid in admin_ids,
                                  "user": {"id": uid, "first_name": data.get("first_name", ""),
                                           "username": data.get("username", ""),
                                           "photo_url": data.get("photo_url", "")}})

    async def quick_start(request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        _quick_clean()
        if len(PENDING) >= QUICK_MAX:
            return web.json_response({"error": "busy"}, status=503)
        lang = body.get("lang") if body.get("lang") in ("uz", "ru", "en") else "uz"
        token, key = secrets.token_urlsafe(16), secrets.token_urlsafe(24)
        PENDING[token] = {"key": key, "exp": time.time() + QUICK_TTL, "lang": lang, "uid": None}
        return web.json_response({"token": token, "key": key, "ttl": QUICK_TTL,
                                  "start": f"login_{token}"})

    async def quick_check(request):
        token, key = request.query.get("t", ""), request.query.get("k", "")
        v = PENDING.get(token)
        if not v or v["exp"] < time.time() or not hmac.compare_digest(key, v["key"]):
            return web.json_response({"error": "expired"}, status=410)
        if not v.get("uid"):
            return web.json_response({"wait": True})
        PENDING.pop(token, None)   # bir martalik
        uid = v["uid"]
        return web.json_response({"token": make_token(uid), "admin": uid in admin_ids, "user": v["user"]})

    async def catalog(_):
        subs = [{"id": k, "price": v[0], "days": v[1], "works": v[2],
                 "name": {lang: (sub_names or {}).get(lang, {}).get(k, k) for lang in ("uz", "ru", "en")}}
                for k, v in (sub_plans or {}).items()]
        return web.json_response({"catalog": catalog_json() if catalog_json else {},
                                  "subs": subs, "sub_disc": sub_disc})

    # ---------------------------------------------------------------- kabinet
    async def me(request):
        uid = read_token(request)
        lang = lang_of(request)
        with db() as con:
            orders = con.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 20", (uid,)).fetchall()
            credits = con.execute("SELECT tier, left FROM credits WHERE user_id=? AND left>0", (uid,)).fetchall()
            known = con.execute("SELECT 1 FROM users WHERE user_id=?", (uid,)).fetchone() is not None
            weekly = None
            code = get_setting("weekly_code", "")
            if code:
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                p = con.execute("""SELECT code, percent, expires_at FROM promos WHERE code=? AND active=1
                                   AND (uses_left IS NULL OR uses_left>0) AND expires_at>?""", (code, now)).fetchone()
                if p:
                    weekly = {"code": p["code"], "percent": p["percent"], "until": p["expires_at"]}
        invited, paid = ref_stats(uid)

        def label(o):
            try:
                return service_label(o, lang)
            except Exception:
                return str(o["service"])

        return web.json_response({
            "known": known,                     # botdan foydalanganmi
            "admin": uid in admin_ids,
            "bonus": bonus_balance(uid),
            "ref": {"link": ref_link(uid), "invited": invited, "paid": paid},
            "credits": [{"tier": c["tier"], "left": c["left"]} for c in credits],
            "weekly_promo": weekly,
            "orders": [{"id": o["id"], "title": label(o), "price": o["price"], "created_at": o["created_at"],
                        "status": o["status"],
                        "status_text": status_tr.get(o["status"], {}).get(lang, o["status"])} for o in orders],
        })

    async def add_review(request):
        uid = read_token(request)
        body = await request.json()
        stars = int(body.get("stars", 0))
        text = str(body.get("text", "")).strip()[:400]
        if not 1 <= stars <= 5:
            return web.json_response({"error": "stars"}, status=400)
        with db() as con:
            o = con.execute("""SELECT o.id FROM orders o LEFT JOIN reviews r ON r.order_id = o.id
                               WHERE o.user_id=? AND o.status='done' AND r.order_id IS NULL
                               ORDER BY o.id DESC LIMIT 1""", (uid,)).fetchone()
            if not o:
                return web.json_response({"error": "no_order"}, status=403)
            con.execute("""INSERT INTO reviews(order_id, user_id, stars, text, consent, published, created_at)
                           VALUES(?,?,?,?,1,0,?)""", (o["id"], uid, stars, text, datetime.now().strftime("%Y-%m-%d %H:%M")))
        return web.json_response({"ok": True})

    # ---------------------------------------------------------------- admin
    def need_admin(request):
        uid = read_token(request)
        if uid not in admin_ids:
            raise web.HTTPForbidden(text='{"error":"admin"}', content_type="application/json")
        return uid

    async def admin(request):
        need_admin(request)
        today = datetime.now().strftime("%Y-%m-%d") + "%"
        with db() as con:
            q = lambda sql, *a: con.execute(sql, a).fetchone()[0]
            data = {
                "users": q("SELECT COUNT(*) FROM users"),
                "users_today": q("SELECT COUNT(*) FROM users WHERE joined_at LIKE ?", today),
                "orders_by_status": {r["status"]: r["n"] for r in con.execute(
                    "SELECT status, COUNT(*) n FROM orders GROUP BY status")},
                "revenue": q("SELECT COALESCE(SUM(price),0) FROM orders WHERE status IN ('work','done')"),
                "revenue_today": q("SELECT COALESCE(SUM(price),0) FROM orders WHERE status IN ('work','done') "
                                   "AND COALESCE(paid_at, created_at) LIKE ?", today),
                "last_orders": [{"id": o["id"], "name": o["full_name"], "username": o["username"],
                                 "title": service_label(o, "ru") if o["service"] else "",
                                 "price": o["price"], "status": o["status"], "created_at": o["created_at"]}
                                for o in con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20")],
                "pending_reviews": [{"order_id": r["order_id"], "stars": r["stars"], "text": r["text"],
                                     "name": r["full_name"]} for r in con.execute(
                    """SELECT r.*, o.full_name FROM reviews r LEFT JOIN orders o ON o.id=r.order_id
                       WHERE r.consent=1 AND r.published=0 AND r.text<>'' ORDER BY r.created_at DESC LIMIT 20""")],
                "promos": [{"code": p["code"], "percent": p["percent"], "used": p["used"],
                            "uses_left": p["uses_left"], "expires_at": p["expires_at"]} for p in con.execute(
                    "SELECT * FROM promos WHERE active=1 ORDER BY created_at DESC LIMIT 15")],
            }
        return web.json_response(data)

    async def approve_review(request):
        need_admin(request)
        oid = int(request.match_info["oid"])
        with db() as con:
            con.execute("UPDATE reviews SET published=1 WHERE order_id=? AND consent=1", (oid,))
        return web.json_response({"ok": True})

    # ---------------------------------------------------------------- yo'llar
    r = app.router
    r.add_get("/api/site/stats", stats)
    r.add_get("/api/site/reviews", reviews)
    r.add_get("/api/site/catalog", catalog)
    r.add_post("/api/site/reviews", add_review)
    r.add_post("/api/site/auth", auth)
    r.add_post("/api/site/login/start", quick_start)
    r.add_get("/api/site/login/check", quick_check)
    r.add_get("/api/site/me", me)
    r.add_get("/api/site/admin", admin)
    r.add_post("/api/site/admin/review/{oid:\\d+}", approve_review)
    return {"read_token": read_token, "lang_of": lang_of}
