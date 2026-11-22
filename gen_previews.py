"""Shablon prevyulari: tpl_s{n}.jpg (slayd muqovasi), tpl_c{n}.jpg (hujjat muqovasi) va varaqlar.

Kerak: LibreOffice (soffice) va pdftoppm.  Ishga tushirish:  python gen_previews.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import autogen
from autogen import THEMES, TIER, Deck, Paper

BASE = Path(__file__).resolve().parent
SAMPLE = {"kicker": "TAQDIMOT", "title": "Sun'iy intellekt ta'limda",
          "subtitle": "Zamonaviy texnologiyalar o'quv jarayonini qanday o'zgartirmoqda",
          "cover": {"author": "Aliyev Ali", "group": "101-guruh", "university": "Andijon davlat pedagogika instituti",
                    "teacher": "Karimova N.", "city": "Andijon"}}
PLAN = ["Tushuncha va tarix", "Ta'limdagi imkoniyatlar", "Xavf va cheklovlar", "Kelajak istiqbollari"]
COVER = {"ministry": "O'zbekiston Respublikasi Oliy ta'lim, fan va innovatsiyalar vazirligi",
         "university": "Andijon davlat pedagogika instituti", "faculty": "Fizika-matematika fakulteti",
         "subject": "Informatika", "author": "Aliyev Ali", "group": "101-guruh", "teacher": "Karimova N.", "city": "Andijon"}
TIER_LABEL = {"start": ("START", "#22C55E", "#062B14"), "pro": ("PROFESSIONAL", "#A78BFA", "#1A0B33"),
              "premium": ("PREMIUM", "#F2C14E", "#2A1D04")}
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(sz):
    try:
        return ImageFont.truetype(FONT, sz)
    except OSError:
        return ImageFont.load_default()


def badge(img, n):
    d = ImageDraw.Draw(img)
    lab, bg, fg = TIER_LABEL[TIER[n]]
    f1, f2 = font(15), font(12)
    t1 = f"№{n} · {THEMES[n][0]}"
    w1 = d.textlength(t1, font=f1); w2 = d.textlength(lab, font=f2) + 18
    W = int(w1 + w2 + 34); x0 = img.width - W - 10
    d.rounded_rectangle([x0, 6, img.width - 10, 34], radius=14, fill=(11, 8, 18))
    d.text((x0 + 12, 11), t1, font=f1, fill="white")
    bx = x0 + 12 + w1 + 10
    d.rounded_rectangle([bx, 11, bx + w2, 29], radius=9, fill=bg)
    d.text((bx + 9, 13), lab, font=f2, fill=fg)
    return img


def soffice(files, out):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(out)] + [str(f) for f in files],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=900)


def first_page(pdf, width):
    stem = pdf.with_suffix("")
    subprocess.run(["pdftoppm", "-png", "-f", "1", "-l", "1", "-scale-to-x", str(width), "-scale-to-y", "-1",
                    str(pdf), str(stem)], check=True)
    pngs = sorted(pdf.parent.glob(stem.name + "*.png"))
    return Image.open(pngs[0]).convert("RGB")


def main(nums):
    tmp = Path(tempfile.mkdtemp())
    decks, docs = [], []
    for n in nums:
        dk = Deck(n, "uz"); dk.cover_slide(SAMPLE, PLAN)
        f = tmp / f"s{n}.pptx"; dk.p.save(f); decks.append(f)
        pp = Paper("uz", n); pp.cover(COVER, "MUSTAQIL ISH", "Sun'iy intellekt ta'limda")
        f = tmp / f"c{n}.docx"; pp.d.save(f); docs.append(f)
    soffice(decks + docs, tmp)
    for n in nums:
        badge(first_page(tmp / f"s{n}.pdf", 1280), n).save(BASE / f"tpl_s{n}.jpg", quality=88)
        im = first_page(tmp / f"c{n}.pdf", 640).resize((640, 904))
        im.save(BASE / f"tpl_c{n}.jpg", quality=86)
        print("ok", n)


def sheet(nums, title, out, kind="s", cols=4):
    tw, th_ = (440, 248) if kind == "s" else (300, 424)
    pad, top = 14, 52
    rows = (len(nums) + cols - 1) // cols
    W, H = cols * (tw + pad) + pad, top + rows * (th_ + pad + (0 if kind == "s" else 24)) + pad
    img = Image.new("RGB", (W, H), (14, 11, 22)); d = ImageDraw.Draw(img)
    d.text((pad + 4, 14), title, font=font(24), fill=(196, 181, 253))
    for i, n in enumerate(nums):
        x = pad + (i % cols) * (tw + pad); y = top + (i // cols) * (th_ + pad + (0 if kind == "s" else 24))
        im = Image.open(BASE / f"tpl_{kind}{n}.jpg").resize((tw, th_)); img.paste(im, (x, y))
        if kind == "c":
            lab, bg, fg = TIER_LABEL[TIER[n]]
            d.text((x + 2, y + th_ + 4), f"№{n} {THEMES[n][0]}", font=font(15), fill="white")
    img.save(BASE / out, quality=86)


def sheets():
    for tier, (a, b), name in (("start", (1, 22), "START"), ("pro", (23, 42), "PROFESSIONAL"), ("premium", (43, 62), "PREMIUM")):
        nums = list(range(a, b + 1)); half = (len(nums) + 1) // 2
        sheet(nums[:half], f"{name} shablonlari ({nums[0]}–{nums[half - 1]})", f"tpl_sheet_{tier}1.jpg", cols=4)
        sheet(nums[half:], f"{name} shablonlari ({nums[half]}–{nums[-1]})", f"tpl_sheet_{tier}2.jpg", cols=4)
    for k in range(4):
        nums = list(range(1 + k * 16, min(62, 16 + k * 16) + 1))
        sheet(nums, f"Muqova shablonlari ({nums[0]}–{nums[-1]})", f"tpl_csheet{k + 1}.jpg", kind="c", cols=8)


if __name__ == "__main__":
    args = sys.argv[1:]
    if args != ["sheets"]:
        main([int(x) for x in args] or list(range(1, 63)))
    sheets()
