"""🤖 Avtomatik bajarish: to'lov tasdiqlangach ishni Claude API orqali yozib, PPTX/DOCX qilib yig'adi.

Kerak: ANTHROPIC_API_KEY (Railway Variables). Model: AUTO_MODEL (standart claude-sonnet-5-5).
"""
import asyncio
import base64
import contextvars
import io
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path

import aiohttp
from PIL import Image

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

from docx import Document as DocxDocument
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn as dqn
from docx.shared import Cm, Pt as DPt, RGBColor as DRGB

BASE = Path(__file__).resolve().parent
API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = os.getenv("AUTO_MODEL", "claude-sonnet-5-5")
API_URL = "https://api.anthropic.com/v1/messages"
# $ / 1M token (Claude Sonnet 5.5). Boshqa model qo'yilsa — AUTO_PRICE_IN / AUTO_PRICE_OUT
PRICE_IN = float(os.getenv("AUTO_PRICE_IN", "2"))
PRICE_OUT = float(os.getenv("AUTO_PRICE_OUT", "10"))
_COST = contextvars.ContextVar("auto_cost", default=None)


def cost_tracker() -> list:
    """Shu vazifa ichidagi barcha so'rovlar narxini yig'adi: [dollar]."""
    acc = [0.0]
    _COST.set(acc)
    return acc

# Avtomatik qilinadigan xizmatlar (qolganlari — qo'lda)
AUTO_SERVICES = {
    "s": {"taqdimot": "slides", "mustaqil": "paper", "kurs": "paper", "maqola": "article", "amaliy": "paper", "referat": "paper"},
    "t": {"dars": "slides", "tadbir": "slides", "maqola": "article", "test": "test", "ishlanma": "lesson"},
}

# n: name, bg, a1, a2, text, muted, card, card_alpha, border, light, title_font
THEMES = {
    1: ("Binafsha Neon", "07050D", "C9A6FF", "FF5FC8", "F4EEFF", "B9AECB", "1C142C", 72, "B48CFF", False, "Arial"),
    2: ("Ko'k Kosmos", "030914", "5CC8FF", "00F0FF", "EAF6FF", "9FB6CF", "0A1830", 72, "5CC8FF", False, "Arial"),
    3: ("Yashil Zumrad", "03100B", "4BF0A0", "C8FF6B", "EAFFF3", "9CC9B2", "082218", 72, "4BF0A0", False, "Arial"),
    4: ("Oq Premium", "F7F5FC", "7B2CBF", "FF4FD8", "16121F", "6B6478", "FFFFFF", 80, "7B2CBF", True, "Arial"),
    5: ("Qizil Olov", "0D0505", "FF6A3D", "FFC24B", "FFF1EC", "D7AFA6", "280E0C", 72, "FF6A3D", False, "Arial"),
    6: ("Oltin Lyuks", "0A0907", "F5D27A", "C99A2E", "F7EEDB", "C9BB9C", "1E1A12", 75, "F5D27A", False, "Georgia"),
    7: ("Pastel Orzu", "FFF4FA", "FF6FB5", "6C8CFF", "2F2448", "7A6E93", "FFFFFF", 66, "FF6FB5", True, "Arial"),
    8: ("Aurora Gradient", "0A0618", "FF8AD8", "7FE3FF", "FFFFFF", "D5CCEA", "FFFFFF", 12, "FFFFFF", False, "Arial"),
}
DEFAULT_THEME = 1

LANG_NAMES = {"uz": "o'zbek (lotin yozuvida)", "ru": "rus", "en": "ingliz"}
WORDS_PER_PAGE = 260  # Times New Roman 14, 1.5 interval


class AutoError(Exception):
    pass


def enabled() -> bool:
    return bool(API_KEY)


def kind_for(o) -> str | None:
    if (o["turtle"] if "turtle" in o.keys() else ""):
        return None  # toshbaqa o'qituvchi — qo'lda
    if (o["qty"] or 1) > 1:
        return None  # guruh buyurtmasi — qo'lda
    return AUTO_SERVICES.get(o["audience"], {}).get(o["service"])


# ------------------------------------------------------------------ Claude API
async def claude(system: str, content, max_tokens: int = 8000, retries: int = 2) -> str:
    if not API_KEY:
        raise AutoError("ANTHROPIC_API_KEY yo'q")
    body = {"model": MODEL, "max_tokens": max_tokens, "system": system,
            "messages": [{"role": "user", "content": content}]}
    headers = {"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    last = None
    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=420)) as s:
                async with s.post(API_URL, json=body, headers=headers) as r:
                    data = await r.json(content_type=None)
                    if r.status == 200:
                        u = data.get("usage") or {}
                        acc = _COST.get()
                        if acc is not None:
                            tin = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
                            acc[0] += tin * PRICE_IN / 1e6 + u.get("output_tokens", 0) * PRICE_OUT / 1e6
                        return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
                    err = (data.get("error") or {}).get("message", str(data))[:300]
                    last = AutoError(f"API {r.status}: {err}")
                    if r.status in (400, 401, 403, 404):  # qayta urinishdan foyda yo'q (balans, kalit, model)
                        if "credit" in err.lower() or "balance" in err.lower():
                            raise AutoError("BALANS: API balansi tugagan — platform.claude.com da to'ldiring")
                        raise last
        except AutoError:
            raise
        except Exception as e:  # tarmoq
            last = AutoError(f"Tarmoq: {e}")
        await asyncio.sleep(4 * (attempt + 1))
    raise last


def parse_json(txt: str):
    t = txt.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    a, b = t.find("{"), t.rfind("}")
    if a < 0 or b < 0:
        raise AutoError("Javobda JSON yo'q")
    try:
        return json.loads(t[a:b + 1])
    except json.JSONDecodeError as e:
        raise AutoError(f"JSON xato: {e}")


# ------------------------------------------------------------------ buyurtma ma'lumotlari
def brief_dict(o) -> dict:
    try:
        return {k: v for k, v in json.loads(o["brief"] or "[]")}
    except Exception:
        return {}


def work_lang(o, client_lang: str) -> str:
    w = (brief_dict(o).get("wlang") or "").lower()
    if any(x in w for x in ("rus", "рус", "russian")):
        return "ru"
    if any(x in w for x in ("ingl", "англ", "english")):
        return "en"
    if any(x in w for x in ("o'zb", "узб", "uzbek")):
        return "uz"
    return client_lang if client_lang in LANG_NAMES else "uz"


def theme_no(o, key: str) -> int:
    m = re.search(r"№\s*(\d)", brief_dict(o).get(key, ""))
    return int(m.group(1)) if m and int(m.group(1)) in THEMES else 0


def order_context(o, svc_name: str, files_note: str) -> str:
    b = brief_dict(o)
    lines = [f"Ish turi: {svc_name}", f"Paket: {o['package'] or '-'}", f"Mavzu: {o['topic']}"]
    if o["details"]:
        lines.append(f"Mijoz qo'shimcha yozgan: {o['details']}")
    labels = {"subject": "Fan", "slides": "Slaydlar soni", "pages": "Hajmi (bet)", "wlang": "Ish tili", "title": "Titul ma'lumotlari",
              "plan": "Reja", "format": "Rasmiylashtirish", "grade": "Kurs/sinf", "count": "Hajm", "extra": "Qo'shimcha istaklar",
              "who": "Kim uchun", "sections": "Bo'limlar", "free": "Batafsil"}
    for k, v in b.items():
        if k in labels:
            lines.append(f"{labels[k]}: {v}")
    if files_note:
        lines.append(files_note)
    return "\n".join(lines)


async def collect_files(bot, o, max_images: int = 8):
    """Mijoz fayllari: rasmlar (baytlar), PDF (base64), DOCX matni."""
    try:
        files = json.loads(o["files"] or "[]")
    except Exception:
        files = []
    images, blocks, texts = [], [], []
    for f in files:
        try:
            if f["type"] == "video":
                continue
            buf = io.BytesIO()
            await bot.download(f["id"], destination=buf)
            data = buf.getvalue()
            name = (f.get("name") or "").lower()
            if f["type"] == "photo" or f.get("img"):
                im = Image.open(io.BytesIO(data)).convert("RGB")
                im.thumbnail((1600, 1600))
                out = io.BytesIO(); im.save(out, "JPEG", quality=88)
                images.append({"bytes": out.getvalue(), "cap": f.get("cap", ""), "w": im.width, "h": im.height})
            elif name.endswith(".pdf") and len(data) < 8_000_000:
                blocks.append({"type": "document", "source": {"type": "base64", "media_type": "application/pdf",
                                                              "data": base64.b64encode(data).decode()}})
            elif name.endswith(".docx"):
                d = DocxDocument(io.BytesIO(data))
                texts.append("\n".join(p.text for p in d.paragraphs if p.text.strip())[:12000])
        except Exception as e:
            logging.warning("Mijoz fayli o'qilmadi: %s", e)
    return images, blocks, texts


def content_blocks(prompt: str, images, blocks, texts, max_images=8):
    c = []
    for i, im in enumerate(images[:max_images], 1):
        c.append({"type": "text", "text": f"Mijoz rasmi #{i}" + (f" — izohi: {im['cap']}" if im["cap"] else "")})
        c.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                              "data": base64.b64encode(im["bytes"]).decode()}})
    c += blocks
    for t in texts:
        c.append({"type": "text", "text": "Mijoz yuborgan Word fayl matni:\n" + t})
    c.append({"type": "text", "text": prompt})
    return c


# ------------------------------------------------------------------ SLAYDLAR
SLIDES_SYSTEM = """Sen O'zbekistondagi talaba va o'qituvchilar uchun professional taqdimot yozuvchisisan.
Faqat bitta JSON obyekt qaytar, boshqa hech narsa yozma. Matnlar qisqa, aniq, ilmiy-ommabop bo'lsin.
Faktlar to'g'ri bo'lsin; ishonching komil bo'lmagan aniq raqam, sana yoki iqtibos o'ylab topma."""


def slides_prompt(ctx: str, lang: str, n_slides: int, n_images: int, notes: bool) -> str:
    img = (f"Mijoz {n_images} ta rasm yubordi (yuqorida, raqamlangan). Ularni mazmuniga mos slaydlarga joylashtir: "
           f"slaydda \"image\": rasm raqami (1..{n_images}). Har rasmni ko'pi bilan bir marta ishlat. "
           "Agar rasm topshiriq sharti/namuna bo'lsa (slaydga qo'yish uchun emas) — uni ishlatma, faqat mazmunini hisobga ol.\n"
           if n_images else "")
    return f"""BUYURTMA:
{ctx}

Til: {LANG_NAMES[lang]}. Jami {n_slides} ta slayd (titul va yakuniy slayd shu songa kiradi).
{img}
JSON tuzilishi:
{{
 "cover": {{"university": "OTM nomi yoki bo'sh", "author": "F.I.Sh yoki bo'sh", "group": "guruh/lavozim yoki bo'sh", "teacher": "ilmiy rahbar yoki bo'sh", "city": "shahar yoki bo'sh"}},
 "kicker": "TAQDIMOT yoki shunga o'xshash 1-2 so'z (ish tilida)",
 "title": "sarlavha (≤ 60 belgi)",
 "subtitle": "bir jumlali tavsif (≤ 110 belgi)",
 "plan": ["reja bandlari, 3–5 ta, har biri ≤ 45 belgi"],
 "slides": [
   {{"layout": "cards|bullets|stat|timeline|quote|compare",
     "title": "≤ 55 belgi",
     "points": [{{"h": "≤ 32 belgi sarlavha", "t": "≤ 120 belgi izoh"}}],
     "stat": {{"value": "raqam/foiz (≤ 8 belgi)", "label": "≤ 40 belgi", "text": "≤ 160 belgi"}},
     "quote": {{"text": "≤ 170 belgi", "author": "≤ 40 belgi"}},
     "image": 0,
     "notes": "{'nutq matni — 60–110 so‘z, slaydni gapirib berish uchun' if notes else 'bo‘sh'}"}}
 ],
 "conclusion": ["xulosa, 3–4 ta qisqa band, har biri ≤ 110 belgi"],
 "thanks": "E'tiboringiz uchun rahmat! (ish tilida)"
}}
Qoidalar: "slides" massivida titul, reja va yakuniy slayd YO'Q — ularni men qo'shaman, shuning uchun "slides" uzunligi {max(n_slides - 4, 2)} ta bo'lsin.
Layoutlarni almashtirib ishlat (ketma-ket bir xil bo'lmasin). cards: 3 ta point; bullets: 3–4 point; timeline: 3–5 point (bosqichlar);
compare: aniq 2 point (taqqoslash); stat: stat to'ldiriladi + 2 point; quote: faqat haqiqiy, mashhur iqtibos bo'lsa.
"image" faqat bullets yoki stat layoutda bo'lishi mumkin; rasm bo'lmasa 0. Titul ma'lumotlarini mijoz yozganidan ol, yo'q bo'lsa bo'sh qoldir."""


def _rgb(h):
    return RGBColor.from_string(h)


def _on(color_hex: str) -> str:
    """Rang ustidagi matn uchun: och fonda — to'q, to'q fonda — oq."""
    r, g, b = (int(color_hex[i:i + 2], 16) for i in (0, 2, 4))
    return "1A1325" if (0.299 * r + 0.587 * g + 0.114 * b) > 170 else "FFFFFF"


def _alpha(shape_fill_el, val):
    """srgbClr ga shaffoflik (0-100 %) qo'shish."""
    for clr in shape_fill_el.iter(qn("a:srgbClr")):
        for a in clr.findall(qn("a:alpha")):
            clr.remove(a)
        el = clr.makeelement(qn("a:alpha"), {"val": str(int(val * 1000))})
        clr.append(el)


class Deck:
    W, H = Inches(13.333), Inches(7.5)

    def __init__(self, theme: int, lang: str):
        self.th = THEMES.get(theme or DEFAULT_THEME)
        self.tn = theme or DEFAULT_THEME
        (self.name, self.bg, self.a1, self.a2, self.tx, self.mu, self.card, self.card_a, self.border,
         self.light, self.font) = self.th
        self.lang = lang
        self.p = Presentation()
        self.p.slide_width, self.p.slide_height = self.W, self.H
        self.blank = self.p.slide_layouts[6]
        self.n = 0

    # --- primitivlar
    def slide(self, kind="c"):
        s = self.p.slides.add_slide(self.blank)
        bgp = BASE / f"bg_{kind}{self.tn}.jpg"
        if bgp.exists():
            s.shapes.add_picture(str(bgp), 0, 0, self.W, self.H)
        else:
            r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, self.W, self.H)
            r.fill.solid(); r.fill.fore_color.rgb = _rgb(self.bg); r.line.fill.background()
        self.n += 1
        return s

    def text(self, s, x, y, w, h, txt, size=18, color=None, bold=False, align=PP_ALIGN.LEFT, font=None,
             anchor=MSO_ANCHOR.TOP, spacing=1.1, italic=False):
        tb = s.shapes.add_textbox(x, y, w, h)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = anchor
        lines = txt if isinstance(txt, list) else [txt]
        for i, line in enumerate(lines):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = align
            para.line_spacing = spacing
            r = para.add_run()
            r.text = line
            f = r.font
            f.size = Pt(size); f.bold = bold; f.italic = italic
            f.color.rgb = _rgb(color or self.tx)
            f.name = font or ("Georgia" if self.font == "Georgia" and size >= 26 else "Arial")
        return tb

    def box(self, s, x, y, w, h, fill=None, alpha=None, line=None, line_alpha=60, radius=0.12, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
        r = s.shapes.add_shape(shape, x, y, w, h)
        if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            r.adjustments[0] = radius
        r.fill.solid(); r.fill.fore_color.rgb = _rgb(fill or self.card)
        _alpha(r.fill._xPr, alpha if alpha is not None else self.card_a)
        if line:
            r.line.color.rgb = _rgb(line); r.line.width = Pt(1.25)
            _alpha(r.line._get_or_add_ln(), line_alpha)
        else:
            r.line.fill.background()
        r.shadow.inherit = False
        return r

    def glass(self, s, x, y, w, h, radius=0.1):
        return self.box(s, x, y, w, h, line=self.border, line_alpha=45, radius=radius)

    def badge(self, s, x, y, d, label, color=None):
        c = self.box(s, x, y, d, d, fill=color or self.a1, alpha=100, radius=0.3)
        tf = c.text_frame; tf.margin_left = tf.margin_right = 0
        para = tf.paragraphs[0]; para.alignment = PP_ALIGN.CENTER
        r = para.add_run(); r.text = label
        r.font.size = Pt(int(d / 12700 * 0.42)); r.font.bold = True; r.font.name = "Arial"
        r.font.color.rgb = _rgb(_on(color or self.a1))
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        return c

    def neon(self, s, x, y, w, h=Inches(0.05)):
        r = self.box(s, x, y, w, h, fill=self.a1, alpha=100, radius=0.5)
        return r

    def chip(self, s, x, y, label):
        w = Inches(0.45 + 0.13 * len(label))
        self.box(s, x, y, w, Inches(0.42), fill=self.a1, alpha=14, line=self.a1, line_alpha=55, radius=0.5)
        dot = self.box(s, x + Inches(0.18), y + Inches(0.165), Inches(0.09), Inches(0.09), fill=self.a2, alpha=100,
                       shape=MSO_SHAPE.OVAL)
        self.text(s, x + Inches(0.36), y + Inches(0.085), w, Inches(0.3), label.upper(), 11, self.a1, True)

    def footer(self, s):
        self.text(s, Inches(0.7), Inches(6.95), Inches(0.6), Inches(0.3), f"{self.n:02d}", 11, self.mu, True)
        self.neon(s, Inches(1.25), Inches(7.06), Inches(0.9), Inches(0.035))

    def title(self, s, txt, y=Inches(0.55)):
        size = 34 if len(txt) <= 38 else 28 if len(txt) <= 52 else 24
        self.text(s, Inches(0.75), y, Inches(11.8), Inches(0.9), txt, size, self.tx, True)
        self.neon(s, Inches(0.78), y + Inches(0.95 if size >= 30 else 0.85), Inches(0.7))

    def picture(self, s, img, x, y, w, h):
        """Rasmni ramkaga sig'diradi (kesib), neon chegarali."""
        im = Image.open(io.BytesIO(img["bytes"]))
        tw, th = w / h, im.width / im.height
        if th > tw:  # keng — yon tomonlarini kesamiz
            nw = int(im.height * tw); left = (im.width - nw) // 2
            im = im.crop((left, 0, left + nw, im.height))
        else:
            nh = int(im.width / tw); top = (im.height - nh) // 2
            im = im.crop((0, top, im.width, top + nh))
        out = io.BytesIO(); im.save(out, "JPEG", quality=88); out.seek(0)
        frame = self.box(s, x - Inches(0.06), y - Inches(0.06), w + Inches(0.12), h + Inches(0.12),
                         fill=self.a1, alpha=30, line=self.a1, line_alpha=80, radius=0.06)
        pic = s.shapes.add_picture(out, x, y, w, h)
        return pic

    # --- slayd turlari
    def cover_slide(self, d, plan):
        s = self.slide("t")
        self.chip(s, Inches(0.8), Inches(1.35), d.get("kicker") or "TAQDIMOT")
        t = d.get("title", "")
        size = 50 if len(t) <= 26 else 42 if len(t) <= 40 else 34
        self.text(s, Inches(0.8), Inches(2.0), Inches(7.0), Inches(2.4), t, size, self.a1 if not self.light else self.tx, True,
                  anchor=MSO_ANCHOR.TOP, spacing=1.0)
        self.text(s, Inches(0.8), Inches(4.35), Inches(6.6), Inches(0.9), d.get("subtitle", ""), 17, self.mu)
        c = d.get("cover") or {}
        who = c.get("author") or ""
        sub = " · ".join(x for x in (c.get("group"), c.get("university")) if x)
        if who or sub:
            self.box(s, Inches(0.8), Inches(5.45), Inches(0.62), Inches(0.62), fill=self.a1, alpha=100, shape=MSO_SHAPE.OVAL)
            self.text(s, Inches(1.6), Inches(5.43), Inches(5.8), Inches(0.4), who or sub, 16, self.tx, True)
            if who and sub:
                self.text(s, Inches(1.6), Inches(5.8), Inches(5.8), Inches(0.35), sub, 12, self.mu)
        # o'ng tomonda reja kartasi
        if plan:
            x, y, w = Inches(8.35), Inches(1.25), Inches(4.2)
            h = Inches(0.95 + 0.72 * len(plan[:5]))
            self.glass(s, x, y, w, h)
            self.text(s, x + Inches(0.35), y + Inches(0.3), w, Inches(0.3), "REJA" if self.lang == "uz" else "ПЛАН" if self.lang == "ru" else "OUTLINE", 12, self.a1, True)
            for i, item in enumerate(plan[:5]):
                yy = y + Inches(0.8 + 0.72 * i)
                self.badge(s, x + Inches(0.35), yy, Inches(0.46), str(i + 1))
                self.text(s, x + Inches(1.0), yy + Inches(0.02), w - Inches(1.25), Inches(0.5), item, 13, self.tx, anchor=MSO_ANCHOR.MIDDLE)
        year = str(datetime.now().year)
        city = (c.get("city") or "").upper()
        self.text(s, Inches(0.8), Inches(6.85), Inches(4), Inches(0.3), "01", 11, self.mu, True)
        self.neon(s, Inches(1.35), Inches(6.97), Inches(9.9), Inches(0.04))
        self.text(s, Inches(11.35), Inches(6.85), Inches(1.4), Inches(0.3), (city + " " if city else "") + year, 11, self.mu, True,
                  align=PP_ALIGN.RIGHT)

    def plan_slide(self, plan):
        s = self.slide("c")
        self.title(s, {"uz": "Reja", "ru": "План", "en": "Outline"}[self.lang])
        n = len(plan)
        cols = 1 if n <= 3 else 2
        rows = (n + cols - 1) // cols
        cw = Inches(11.85 / cols - (0.2 if cols > 1 else 0))
        rh = min(Inches(1.5), int(Inches(4.6) / rows) - Inches(0.25))
        y0 = Inches(1.95) + (Inches(4.6) - rows * (rh + Inches(0.25))) // 2
        for i, item in enumerate(plan):
            row, col = divmod(i, cols)
            x = Inches(0.75) + col * (cw + Inches(0.4))
            y = y0 + row * (rh + Inches(0.25))
            self.glass(s, x, y, cw, rh)
            self.badge(s, x + Inches(0.3), y + (rh - Inches(0.75)) / 2, Inches(0.75), f"{i + 1:02d}")
            self.text(s, x + Inches(1.35), y, cw - Inches(1.6), rh, item, 21, self.tx, True, anchor=MSO_ANCHOR.MIDDLE)
        self.footer(s)

    def content_slide(self, d, images):
        lay = d.get("layout", "bullets")
        pts = [p for p in d.get("points", []) if isinstance(p, dict)][:5]
        img = None
        try:
            k = int(d.get("image") or 0)
            if 1 <= k <= len(images) and not images[k - 1].get("used"):
                img = images[k - 1]; img["used"] = True
        except (TypeError, ValueError):
            pass
        s = self.slide("c")
        self.title(s, d.get("title", ""))
        top = Inches(1.95)
        if lay == "cards" and len(pts) >= 2 and not img:
            n = min(len(pts), 4)
            gap = Inches(0.3); cw = int((Inches(11.85) - gap * (n - 1)) / n)
            for i, p in enumerate(pts[:n]):
                x = Inches(0.75) + i * (cw + gap)
                self.glass(s, x, top, cw, Inches(4.55))
                self.badge(s, x + Inches(0.35), top + Inches(0.4), Inches(0.75), f"{i + 1:02d}")
                self.text(s, x + Inches(0.35), top + Inches(1.45), cw - Inches(0.7), Inches(0.9), p.get("h", ""), 22 if n < 4 else 19, self.tx, True)
                self.text(s, x + Inches(0.35), top + Inches(2.35), cw - Inches(0.7), Inches(2.1), p.get("t", ""), 17 if n < 4 else 15, self.mu, spacing=1.2)
        elif lay == "timeline" and len(pts) >= 2:
            n = min(len(pts), 5)
            y = Inches(3.35)
            self.neon(s, Inches(0.9), y, Inches(11.5), Inches(0.05))
            step = Inches(11.5) / n
            for i, p in enumerate(pts[:n]):
                cx = Inches(0.9) + int(step * i + step / 2)
                self.box(s, cx - Inches(0.3), y - Inches(0.28), Inches(0.6), Inches(0.6), fill=self.a1, alpha=100, shape=MSO_SHAPE.OVAL)
                self.text(s, cx - Inches(0.3), y - Inches(0.22), Inches(0.6), Inches(0.5), str(i + 1), 16, _on(self.a1), True, align=PP_ALIGN.CENTER)
                w = int(step - Inches(0.25))
                self.glass(s, cx - w // 2, Inches(4.05), w, Inches(2.55))
                self.text(s, cx - w // 2 + Inches(0.22), Inches(4.25), w - Inches(0.44), Inches(0.75), p.get("h", ""), 18 if n <= 4 else 16, self.tx, True)
                self.text(s, cx - w // 2 + Inches(0.22), Inches(4.95), w - Inches(0.44), Inches(1.6), p.get("t", ""), 15 if n <= 4 else 13, self.mu, spacing=1.15)
        elif lay == "compare" and len(pts) >= 2:
            cw = Inches(5.75)
            for i, p in enumerate(pts[:2]):
                x = Inches(0.75) + i * (cw + Inches(0.35))
                self.glass(s, x, top, cw, Inches(4.55))
                self.box(s, x, top, cw, Inches(0.12), fill=self.a1 if i == 0 else self.a2, alpha=100, radius=0.5)
                self.text(s, x + Inches(0.45), top + Inches(0.5), cw - Inches(0.9), Inches(0.8), p.get("h", ""), 26, self.a1 if i == 0 else self.a2, True)
                self.text(s, x + Inches(0.45), top + Inches(1.4), cw - Inches(0.9), Inches(2.9), p.get("t", ""), 20, self.tx, spacing=1.3)
            self.box(s, Inches(6.33), Inches(3.7), Inches(0.66), Inches(0.66), fill=self.a2, alpha=100, shape=MSO_SHAPE.OVAL)
            self.text(s, Inches(6.33), Inches(3.82), Inches(0.66), Inches(0.4), "VS", 13, _on(self.a2), True, align=PP_ALIGN.CENTER)
        elif lay == "quote" and d.get("quote", {}).get("text"):
            q = d["quote"]
            self.glass(s, Inches(1.4), top + Inches(0.15), Inches(10.5), Inches(4.2))
            self.text(s, Inches(1.85), top + Inches(0.1), Inches(1.5), Inches(1.5), "“", 110, self.a1, True, font="Georgia")
            self.text(s, Inches(2.0), top + Inches(1.2), Inches(9.3), Inches(2.2), q["text"], 24, self.tx, False, italic=True, spacing=1.2)
            self.neon(s, Inches(2.0), top + Inches(3.55), Inches(0.6))
            self.text(s, Inches(2.8), top + Inches(3.4), Inches(8), Inches(0.4), q.get("author", ""), 15, self.mu, True)
        else:  # bullets / stat (+ ixtiyoriy rasm)
            st = d.get("stat") or {}
            text_w = Inches(6.6) if img or (lay == "stat" and st.get("value")) else Inches(11.85)
            items = pts[:4]
            ih = Inches(4.55) / max(len(items), 1)
            for i, p in enumerate(items):
                y = top + i * ih
                self.glass(s, Inches(0.75), y, text_w, ih - Inches(0.18))
                self.badge(s, Inches(1.0), y + (ih - Inches(0.18)) / 2 - Inches(0.27), Inches(0.54), str(i + 1))
                big = len(items) <= 3
                self.text(s, Inches(1.75), y + Inches(0.18 if big else 0.12), text_w - Inches(1.2), Inches(0.45), p.get("h", ""), 20 if big else 17, self.tx, True)
                self.text(s, Inches(1.75), y + Inches(0.65 if big else 0.52), text_w - Inches(1.2), ih - Inches(0.8), p.get("t", ""), 16 if big else 14, self.mu, spacing=1.15)
            rx = Inches(0.75) + text_w + Inches(0.4)
            rw = Inches(12.6) - rx
            if img:
                self.picture(s, img, rx + Inches(0.06), top + Inches(0.06), rw - Inches(0.12), Inches(4.43))
            elif lay == "stat" and st.get("value"):
                self.glass(s, rx, top, rw, Inches(4.55))
                self.text(s, rx + Inches(0.4), top + Inches(0.35), rw - Inches(0.8), Inches(1.6), st["value"], 80, self.a1, True)
                self.text(s, rx + Inches(0.4), top + Inches(2.05), rw - Inches(0.8), Inches(0.6), st.get("label", ""), 22, self.tx, True)
                self.text(s, rx + Inches(0.4), top + Inches(2.75), rw - Inches(0.8), Inches(1.7), st.get("text", ""), 16, self.mu, spacing=1.2)
        if d.get("notes"):
            s.notes_slide.notes_text_frame.text = d["notes"]
        self.footer(s)

    def conclusion_slide(self, points):
        s = self.slide("c")
        self.title(s, {"uz": "Xulosa", "ru": "Заключение", "en": "Conclusion"}[self.lang])
        ih = Inches(4.55) / max(len(points[:4]), 1)
        for i, p in enumerate(points[:4]):
            y = Inches(1.95) + i * ih
            self.glass(s, Inches(0.75), y, Inches(11.85), ih - Inches(0.2))
            self.badge(s, Inches(1.05), y + (ih - Inches(0.2)) / 2 - Inches(0.27), Inches(0.54), "✓", self.a2)
            self.text(s, Inches(1.9), y, Inches(10.4), ih - Inches(0.2), p, 20, self.tx, anchor=MSO_ANCHOR.MIDDLE, spacing=1.15)
        self.footer(s)

    def thanks_slide(self, d):
        s = self.slide("t")
        self.text(s, Inches(1), Inches(2.55), Inches(11.33), Inches(1.4), d.get("thanks") or "E'tiboringiz uchun rahmat!",
                  44, self.a1 if not self.light else self.tx, True, align=PP_ALIGN.CENTER)
        self.neon(s, Inches(5.97), Inches(4.05), Inches(1.4))
        c = d.get("cover") or {}
        who = " · ".join(x for x in (c.get("author"), c.get("group")) if x)
        if who:
            self.text(s, Inches(1), Inches(4.35), Inches(11.33), Inches(0.5), who, 16, self.mu, align=PP_ALIGN.CENTER)

    def build(self, d, images) -> bytes:
        plan = [str(x) for x in d.get("plan", [])][:6]
        self.cover_slide(d, plan[:5])
        if plan:
            self.plan_slide(plan)
        for sl in d.get("slides", []):
            if isinstance(sl, dict):
                self.content_slide(sl, images)
        if d.get("conclusion"):
            self.conclusion_slide([str(x) for x in d["conclusion"]])
        self.thanks_slide(d)
        out = io.BytesIO(); self.p.save(out)
        return out.getvalue()


def slide_count(o) -> int:
    v = brief_dict(o).get("slides", "")
    m = re.search(r"\d+", v)
    if m:
        return max(6, min(int(m.group()), 30))
    return {"start": 11, "pro": 16, "premium": 22}.get(o["package"] or "", 12)


# ------------------------------------------------------------------ YOZMA ISHLAR (DOCX)
PAPER_SYSTEM = """Sen O'zbekiston OTMlari uchun ilmiy-uslubiy yozma ishlar (mustaqil ish, referat, kurs ishi, maqola, dars ishlanmasi, testlar) yozuvchisisan.
Uslub: ilmiy, ravon, takrorlarsiz, plagiatsiz — o'z so'zlaring bilan. Faqat so'ralgan JSON ni qaytar.
Faktlarga e'tibor ber: aniq bo'lmagan statistika, sana yoki iqtibos o'ylab topma. Adabiyotlar ro'yxatida faqat haqiqatda mavjud,
taniqli darsliklar, qonunlar va rasmiy hujjatlarni keltir; URL o'ylab topma."""


def paper_outline_prompt(ctx, lang, pages, kind):
    extra = {"paper": "2–3 bob, har bobda 2–3 paragraf (1.1, 1.2 …).",
             "article": "Maqola tuzilishi: Annotatsiya, Kalit so'zlar, Kirish, Asosiy qism (2–3 bo'lim), Xulosa. Bob raqamlarisiz.",
             "lesson": "Dars ishlanmasi: Dars maqsadi (ta'limiy, tarbiyaviy, rivojlantiruvchi), Dars jihozlari, Dars turi va metodi, Dars borishi (bosqichlar vaqti bilan), Uyga vazifa, Baholash.",
             "test": "Testlar: mavzu bo'yicha test savollari to'plami."}[kind]
    return f"""BUYURTMA:
{ctx}

Til: {LANG_NAMES[lang]}. Hajm: taxminan {pages} bet (Times New Roman 14, 1.5 interval).
Avval ishning rejasini tuz. {extra}
JSON:
{{
 "cover": {{"ministry": "vazirlik nomi (ish tilida, OTM uchun: O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi; maktab bo'lsa Maktabgacha va maktab ta'limi vazirligi)",
            "university": "OTM/maktab nomi yoki bo'sh", "faculty": "fakultet/kafedra yoki bo'sh", "author": "bajardi F.I.Sh yoki bo'sh",
            "group": "guruh yoki bo'sh", "teacher": "tekshirdi / ilmiy rahbar yoki bo'sh", "subject": "fan nomi yoki bo'sh", "city": "shahar yoki bo'sh"}},
 "work_type": "MUSTAQIL ISH / REFERAT / KURS ISHI / MAQOLA / DARS ISHLANMASI / TEST (ish tilida, katta harflarda)",
 "title": "mavzu (to'g'rilangan, chiroyli)",
 "sections": [{{"heading": "KIRISH", "subs": [], "share": 0.1}}, {{"heading": "I BOB. …", "subs": ["1.1. …", "1.2. …"], "share": 0.35}}, …, {{"heading": "XULOSA", "subs": [], "share": 0.08}}],
 "references": ["8–12 ta adabiyot (haqiqiy)"]
}}
"share" — bo'limning umumiy hajmdagi ulushi (yig'indisi ≈ 1). Titul ma'lumotlarini faqat mijoz yozganidan ol, bo'lmasa bo'sh qoldir.
{"Test uchun sections: bitta bo'lim 'TEST SAVOLLARI', share 1, references bo'sh bo'lishi mumkin." if kind == "test" else ""}"""


def section_prompt(ctx, lang, outline, sec, words, kind):
    other = "; ".join(s["heading"] for s in outline["sections"])
    if kind == "test":
        m = re.search(r"Hajm: [^\n]*?(\d+)", ctx)
        n = max(10, min(int(m.group(1)), 60)) if m else 25
        return f"""BUYURTMA:\n{ctx}\n\nTil: {LANG_NAMES[lang]}. Mavzu bo'yicha {n} ta test savoli tuz (har birida 4 variant: A, B, C, D, bittasi to'g'ri).
JSON: {{"blocks": [{{"q": "savol", "a": ["A variant", "B", "C", "D"], "c": "A"}}]}}"""
    return f"""BUYURTMA:\n{ctx}\n\nIsh: "{outline.get('title')}". Ishning barcha bo'limlari: {other}.
Hozir faqat shu bo'limni yoz: "{sec['heading']}"{(' — paragraflari: ' + '; '.join(sec['subs'])) if sec.get('subs') else ''}.
Til: {LANG_NAMES[lang]}. Hajm: taxminan {words} so'z (shundan kam bo'lmasin).
JSON: {{"blocks": [{{"h": "paragraf sarlavhasi (faqat subs bo'lsa, aynan shu nom bilan)"}}, {{"p": "abzats matni (80–160 so'z)"}}, …]}}
Bo'lim sarlavhasini o'zini yozma (men qo'shaman). Abzatslar mantiqan bog'langan, misollar bilan bo'lsin."""


def _set_cell_shading(par, color):
    pPr = par._p.get_or_add_pPr()
    shd = OxmlElement("w:shd"); shd.set(dqn("w:val"), "clear"); shd.set(dqn("w:color"), "auto"); shd.set(dqn("w:fill"), color)
    pPr.append(shd)


def _page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    for tag, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar"); el.set(dqn("w:fldCharType"), tag); run._r.append(el)
        else:
            it = OxmlElement("w:instrText"); it.set(dqn("xml:space"), "preserve"); it.text = txt; run._r.append(it)
    run.font.size = DPt(12); run.font.name = "Times New Roman"


def _behind_image(paragraph, path, width_emu, height_emu):
    """Rasmni sahifa ortiga (matn orqasiga) to'liq A4 qilib joylash."""
    run = paragraph.add_run()
    run.add_picture(str(path), width=width_emu, height=height_emu)
    inline = run._r.find(".//" + dqn("wp:inline"))
    if inline is None:
        return
    graphic = inline.find(dqn("a:graphic"))
    docpr = inline.find(dqn("wp:docPr"))
    anchor = OxmlElement("wp:anchor")
    for k, v in {"distT": "0", "distB": "0", "distL": "0", "distR": "0", "simplePos": "0", "relativeHeight": "0",
                 "behindDoc": "1", "locked": "1", "layoutInCell": "1", "allowOverlap": "1"}.items():
        anchor.set(k, v)
    sp = OxmlElement("wp:simplePos"); sp.set("x", "0"); sp.set("y", "0"); anchor.append(sp)
    for axis, rel in (("wp:positionH", "page"), ("wp:positionV", "page")):
        el = OxmlElement(axis); el.set("relativeFrom", rel)
        off = OxmlElement("wp:posOffset"); off.text = "0"; el.append(off); anchor.append(el)
    ext = OxmlElement("wp:extent"); ext.set("cx", str(width_emu)); ext.set("cy", str(height_emu)); anchor.append(ext)
    ee = OxmlElement("wp:effectExtent")
    for k in ("l", "t", "r", "b"):
        ee.set(k, "0")
    anchor.append(ee)
    anchor.append(OxmlElement("wp:wrapNone"))
    anchor.append(docpr)
    anchor.append(OxmlElement("wp:cNvGraphicFramePr"))
    anchor.append(graphic)
    inline.getparent().replace(inline, anchor)


class Paper:
    def __init__(self, lang, cover_theme: int):
        self.lang = lang
        self.th = THEMES.get(cover_theme) if cover_theme else None
        self.tn = cover_theme
        self.d = DocxDocument()
        sec = self.d.sections[0]
        sec.page_width, sec.page_height = Cm(21), Cm(29.7)
        sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(3), Cm(1.5), Cm(2), Cm(2)
        st = self.d.styles["Normal"]
        st.font.name = "Times New Roman"; st.font.size = DPt(14)
        st.element.rPr.rFonts.set(dqn("w:eastAsia"), "Times New Roman")
        pf = st.paragraph_format
        pf.line_spacing = 1.5; pf.space_after = DPt(0); pf.space_before = DPt(0)

    def para(self, text="", bold=False, size=14, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, color=None, italic=False,
             before=0, after=0, upper=False, spacing=None):
        p = self.d.add_paragraph()
        p.alignment = align
        pf = p.paragraph_format
        pf.first_line_indent = Cm(1.25) if indent else Cm(0)
        pf.space_before, pf.space_after = DPt(before), DPt(after)
        if spacing:
            pf.line_spacing = spacing
        if text:
            r = p.add_run(text.upper() if upper else text)
            r.bold = bold; r.italic = italic; r.font.size = DPt(size)
            if color:
                r.font.color.rgb = DRGB.from_string(color)
        return p

    def page_break(self):
        self.d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def cover(self, o_cover, work_type, title):
        c = o_cover or {}
        C = WD_ALIGN_PARAGRAPH.CENTER
        dark = self.th and not self.th[9]
        tx = self.th[4] if self.th else None
        acc = self.th[2] if self.th else None
        mu = self.th[5] if self.th else None
        first = self.para("", align=C, indent=False)
        if self.th:
            bg = BASE / f"bg_a4{self.tn}.jpg"
            if bg.exists():
                _behind_image(first, bg, Cm(21), Cm(29.7))
        self.para(c.get("ministry") or "", True, 13, C, False, tx, upper=True, spacing=1.15)
        if c.get("university"):
            self.para(c["university"], True, 14, C, False, tx, upper=True, before=6, spacing=1.15)
        if c.get("faculty"):
            self.para(c["faculty"], False, 13, C, False, mu or tx, before=4, spacing=1.15)
        for _ in range(5):
            self.para("", indent=False)
        if c.get("subject"):
            self.para({"uz": "Fan", "ru": "Дисциплина", "en": "Subject"}[self.lang] + f": {c['subject']}", False, 14, C, False, mu or tx)
        self.para(work_type, True, 26 if self.th else 22, C, False, acc, before=8, after=6, spacing=1.1)
        self.para({"uz": "Mavzu", "ru": "Тема", "en": "Topic"}[self.lang] + ":", False, 14, C, False, mu or tx)
        self.para(f"«{title}»", True, 20 if self.th else 18, C, False, tx, spacing=1.15)
        for _ in range(6):
            self.para("", indent=False)
        lab = {"uz": ("Bajardi", "Guruh", "Tekshirdi"), "ru": ("Выполнил(а)", "Группа", "Проверил(а)"),
               "en": ("Prepared by", "Group", "Checked by")}[self.lang]
        R = WD_ALIGN_PARAGRAPH.RIGHT
        for label, key in zip(lab, ("author", "group", "teacher")):
            if c.get(key):
                p = self.para("", align=R, indent=False, spacing=1.3)
                r1 = p.add_run(f"{label}: "); r1.font.size = DPt(14)
                if mu: r1.font.color.rgb = DRGB.from_string(mu)
                r2 = p.add_run(c[key]); r2.bold = True; r2.font.size = DPt(14)
                if tx: r2.font.color.rgb = DRGB.from_string(tx)
        for _ in range(5):
            self.para("", indent=False)
        city = (c.get("city") or "").strip()
        self.para((city + " — " if city else "") + str(datetime.now().year), True, 14, C, False, mu or tx)
        # muqovadan keyin yangi bo'lim — sahifa raqami 2 dan
        new = self.d.add_section(WD_SECTION.NEW_PAGE)
        new.footer.is_linked_to_previous = False
        _page_number(new)
        self.d.sections[0].footer.is_linked_to_previous = False

    def contents(self, sections):
        C = WD_ALIGN_PARAGRAPH.CENTER
        self.para({"uz": "REJA", "ru": "СОДЕРЖАНИЕ", "en": "CONTENTS"}[self.lang], True, 14, C, False, after=10)
        for s in sections:
            self.para(s["heading"], True, 14, WD_ALIGN_PARAGRAPH.LEFT, False)
            for sub in s.get("subs", []):
                p = self.para(sub, False, 14, WD_ALIGN_PARAGRAPH.LEFT, False)
                p.paragraph_format.left_indent = Cm(1)
        self.page_break()

    def section(self, heading, blocks, first=False):
        if not first:
            self.page_break()
        self.para(heading, True, 14, WD_ALIGN_PARAGRAPH.CENTER, False, after=8)
        for b in blocks:
            if not isinstance(b, dict):
                continue
            if b.get("h"):
                self.para(b["h"], True, 14, WD_ALIGN_PARAGRAPH.CENTER, False, before=6, after=6)
            elif b.get("p"):
                self.para(b["p"].strip())

    def tests(self, blocks):
        self.para({"uz": "TEST SAVOLLARI", "ru": "ТЕСТОВЫЕ ВОПРОСЫ", "en": "TEST QUESTIONS"}[self.lang], True, 14,
                  WD_ALIGN_PARAGRAPH.CENTER, False, after=8)
        keys = []
        for i, b in enumerate([b for b in blocks if isinstance(b, dict) and b.get("q")], 1):
            self.para(f"{i}. {b['q']}", True, 14, WD_ALIGN_PARAGRAPH.LEFT, False, before=6)
            for letter, ans in zip("ABCD", b.get("a", [])):
                clean = re.sub(r"^[A-D][).]\s*", "", str(ans))
                p = self.para(f"{letter}) {clean}", False, 14, WD_ALIGN_PARAGRAPH.LEFT, False)
                p.paragraph_format.left_indent = Cm(1)
            keys.append(f"{i}-{b.get('c', '?')}")
        self.page_break()
        self.para({"uz": "TO'G'RI JAVOBLAR KALITI", "ru": "КЛЮЧ ОТВЕТОВ", "en": "ANSWER KEY"}[self.lang], True, 14,
                  WD_ALIGN_PARAGRAPH.CENTER, False, after=8)
        self.para(",  ".join(keys), False, 14, WD_ALIGN_PARAGRAPH.LEFT, False)

    def references(self, refs):
        self.page_break()
        self.para({"uz": "FOYDALANILGAN ADABIYOTLAR", "ru": "СПИСОК ЛИТЕРАТУРЫ", "en": "REFERENCES"}[self.lang], True, 14,
                  WD_ALIGN_PARAGRAPH.CENTER, False, after=8)
        for i, r in enumerate(refs, 1):
            self.para(f"{i}. {r}", False, 14, WD_ALIGN_PARAGRAPH.JUSTIFY, False)

    def bytes(self) -> bytes:
        out = io.BytesIO(); self.d.save(out)
        return out.getvalue()


def page_count(o, kind) -> int:
    b = brief_dict(o)
    m = re.search(r"\d+", b.get("pages", "") or b.get("count", ""))
    if m and kind != "test":
        return max(5, min(int(m.group()), 45))
    return {"article": 6, "lesson": 6, "test": 6}.get(kind, 30 if o["service"] == "kurs" else 15)


# ------------------------------------------------------------------ asosiy kirish nuqtasi
def safe_name(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U).strip()
    return (re.sub(r"\s+", "_", s)[:50] or "ish")


async def generate(bot, o, svc_name: str, client_lang: str):
    """→ (fayl_nomi, baytlar, qisqa_hisobot)"""
    kind = kind_for(o)
    if not kind:
        raise AutoError("Bu xizmat avtomatik qilinmaydi")
    lang = work_lang(o, client_lang)
    images, blocks, texts = await collect_files(bot, o)
    note = (f"Mijoz {len(images)} ta rasm" + (f", {len(blocks)} ta PDF" if blocks else "") +
            (f", {len(texts)} ta Word fayl" if texts else "") + " yubordi (yuqorida).") if (images or blocks or texts) else ""
    ctx = order_context(o, svc_name, note)

    if kind == "slides":
        n = slide_count(o)
        notes = (o["package"] or "") in ("pro", "premium")
        raw = await claude(SLIDES_SYSTEM, content_blocks(slides_prompt(ctx, lang, n, len(images), notes), images, blocks, texts),
                           max_tokens=12000)
        d = parse_json(raw)
        deck = Deck(theme_no(o, "style"), lang)
        data = deck.build(d, images)
        return f"{safe_name(d.get('title') or o['topic'])}.pptx", data, f"{deck.n} ta slayd, shablon №{deck.tn}"

    pages = page_count(o, kind)
    outline = parse_json(await claude(PAPER_SYSTEM, content_blocks(paper_outline_prompt(ctx, lang, pages, kind), images, blocks, texts),
                                      max_tokens=4000))
    secs = [s for s in outline.get("sections", []) if isinstance(s, dict) and s.get("heading")]
    if not secs:
        raise AutoError("Reja tuzilmadi")
    total_words = pages * WORDS_PER_PAGE - 350  # titul + reja + adabiyotlar
    tot_share = sum(float(s.get("share") or 0) for s in secs) or 1

    async def one(sec):
        words = max(180, int(total_words * float(sec.get("share") or 1 / len(secs)) / tot_share))
        mt = min(16000, int(words * 3.2) + 1500)
        raw = await claude(PAPER_SYSTEM, content_blocks(section_prompt(ctx, lang, outline, sec, words, kind), images[:3], [], texts[:1]),
                           max_tokens=mt)
        return parse_json(raw).get("blocks", [])

    sem = asyncio.Semaphore(4)

    async def guarded(sec):
        async with sem:
            return await one(sec)

    bodies = await asyncio.gather(*(guarded(s) for s in secs))
    paper = Paper(lang, theme_no(o, "cover"))
    paper.cover(outline.get("cover"), outline.get("work_type") or svc_name.upper(), outline.get("title") or o["topic"])
    if kind == "test":
        paper.tests([b for body in bodies for b in body])
    else:
        paper.contents(secs)
        for i, (sec, body) in enumerate(zip(secs, bodies)):
            paper.section(sec["heading"], body, first=(i == 0))
        if outline.get("references"):
            paper.references([str(r) for r in outline["references"]])
    words = sum(len(str(b.get("p", ""))) // 7 for body in bodies for b in body if isinstance(b, dict))
    return (f"{safe_name(outline.get('title') or o['topic'])}.docx", paper.bytes(),
            f"{len(secs)} bo'lim, ~{max(words // WORDS_PER_PAGE, 1) + 3} bet" + (f", muqova №{paper.tn}" if paper.tn else ""))


# ------------------------------------------------------------------ 🧾 chek o'qish
CHEQUE_SYSTEM = """Sen to'lov cheklarini (Click, Payme, Uzum, Paynet, bank ilovalari skrinshotlari) o'qiydigan yordamchisan.
Faqat JSON qaytar. Ko'rmagan narsangni o'ylab topma — bilmasang null yoz."""

CHEQUE_PROMPT = """Bu rasm to'lov chekimi? Undan ma'lumotlarni ol.
JSON:
{"is_receipt": true/false,
 "success": true/false/null,            // to'lov muvaffaqiyatli o'tganmi (Успешно, Muvaffaqiyatli, Выполнено, ✓)
 "amount": 25000,                        // o'tkazilgan summa so'mda, butun son (komissiyasiz asosiy summa); bo'lmasa null
 "recipient_card_last4": "9012",         // QABUL QILUVCHI karta raqamining oxirgi 4 raqami; bo'lmasa null
 "recipient_name": "…",                  // qabul qiluvchi ismi (bo'lsa)
 "datetime": "2026-11-14 15:30",         // chekdagi sana va vaqt (YYYY-MM-DD HH:MM); bo'lmasa null
 "edited_signs": false}                  // tahrirlangan/soxta belgilar ko'rinsa true (shriftlar mos emas, raqamlar ustidan yozilgan)"""


async def read_cheque(data: bytes, mime: str = "image/jpeg") -> dict:
    if mime == "application/pdf":
        block = {"type": "document", "source": {"type": "base64", "media_type": mime, "data": base64.b64encode(data).decode()}}
    else:
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((1600, 1600))
        out = io.BytesIO(); im.save(out, "JPEG", quality=90)
        block = {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(out.getvalue()).decode()}}
    raw = await claude(CHEQUE_SYSTEM, [block, {"type": "text", "text": CHEQUE_PROMPT}], max_tokens=600, retries=1)
    return parse_json(raw)
