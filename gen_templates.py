"""Yangi slayd shablonlari uchun fon rasmlari: bg_t{n}.jpg (muqova), bg_c{n}.jpg (ichki slayd), bg_a4{n}.jpg (hujjat muqovasi).

Ishga tushirish:  python gen_templates.py 13 14 ...   (raqamsiz — barcha yangi shablonlar)
Start 13–22 (toza, yorug'), Professional 33–42 (neon), Premium 53–62 (lyuks).
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

BASE = Path(__file__).resolve().parent


def hx(c, a=255):
    c = c.lstrip("#")
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), a)


def mix(c1, c2, t):
    a, b = hx(c1), hx(c2)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


class Canvas:
    def __init__(self, W, H, bg):
        self.W, self.H = W, H
        self.base = Image.new("RGBA", (W, H), hx(bg))
        self.u = min(W, H) / 900          # masshtab birligi

    def layer(self):
        return Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))

    def put(self, lay, blur=0, alpha=1.0):
        if blur:
            lay = lay.filter(ImageFilter.GaussianBlur(blur * self.u))
        if alpha < 1:
            a = lay.getchannel("A").point(lambda v: int(v * alpha))
            lay.putalpha(a)
        self.base = Image.alpha_composite(self.base, lay)

    def glow(self, draw_fn, blur=18, alpha=1.0, sharp=True):
        """Neon: xira nur + o'tkir chiziq."""
        lay = self.layer(); draw_fn(ImageDraw.Draw(lay)); self.put(lay, blur, alpha)
        if sharp:
            lay = self.layer(); draw_fn(ImageDraw.Draw(lay)); self.put(lay, 0, alpha)

    def vgrad(self, top, bottom, alpha=255):
        lay = self.layer(); d = ImageDraw.Draw(lay)
        for y in range(self.H):
            c = mix(top, bottom, y / self.H)
            d.line([(0, y), (self.W, y)], fill=c[:3] + (alpha,))
        self.put(lay)

    def radial(self, cx, cy, r, color, alpha=160):
        lay = self.layer(); d = ImageDraw.Draw(lay)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hx(color, alpha))
        self.put(lay, blur=r / self.u * .55)

    def stars(self, n, color="#FFFFFF", maxr=2.2, seed=1, alpha=200):
        rnd = random.Random(seed); lay = self.layer(); d = ImageDraw.Draw(lay)
        for _ in range(n):
            x, y, r = rnd.random() * self.W, rnd.random() * self.H, rnd.random() * maxr * self.u + .4
            d.ellipse([x - r, y - r, x + r, y + r], fill=hx(color, int(alpha * (.35 + rnd.random() * .65))))
        self.put(lay)

    def frame(self, color, inset=26, width=2, alpha=150, corners=False):
        u = self.u; i = inset * u
        self.glow(lambda d: d.rounded_rectangle([i, i, self.W - i, self.H - i], radius=14 * u, outline=hx(color, alpha), width=max(1, int(width * u))),
                  blur=6, alpha=.9)
        if corners:
            L = 46 * u
            for (x, y, sx, sy) in ((i, i, 1, 1), (self.W - i, i, -1, 1), (i, self.H - i, 1, -1), (self.W - i, self.H - i, -1, -1)):
                self.glow(lambda d, x=x, y=y, sx=sx, sy=sy: (d.line([(x + sx * 10 * u, y + sy * 10 * u), (x + sx * L, y + sy * 10 * u)], fill=hx(color), width=int(3 * u)),
                                                             d.line([(x + sx * 10 * u, y + sy * 10 * u), (x + sx * 10 * u, y + sy * L)], fill=hx(color), width=int(3 * u))), blur=5)

    def out(self):
        return self.base.convert("RGB")


# ======================================================================== START (yorug', toza)
def m_waves(c, th, soft):            # Okean shabadasi
    W, H, u = c.W, c.H, c.u
    for k, (col, a) in enumerate([(th["a2"], 70), (th["a1"], 55), (th["a2"], 110)]):
        lay = c.layer(); d = ImageDraw.Draw(lay)
        base = H * (.74 + k * .07)
        pts = [(x, base + math.sin(x / W * 6.28 * 1.3 + k * 1.7) * 26 * u + math.sin(x / W * 15 + k) * 9 * u) for x in range(0, W + 8, 8)]
        d.polygon(pts + [(W, H), (0, H)], fill=hx(col, a))
        c.put(lay, blur=1)
    c.radial(W * .88, H * .14, 150 * u, th["a2"], 60)


def m_origami(c, th, soft):          # Qog'oz origami
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(3)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for i in range(9):
        x0, y0 = W - (i % 3) * 120 * u, (i // 3) * 120 * u
        tri = [(x0, y0), (x0 - 120 * u, y0), (x0, y0 + 120 * u)] if (i % 2) else [(x0 - 120 * u, y0), (x0 - 120 * u, y0 + 120 * u), (x0, y0 + 120 * u)]
        d.polygon(tri, fill=hx(th["a2"] if i % 3 == 0 else th["a1"], 55 + rnd.randint(0, 70)))
    for i in range(5):
        x0, y0 = i * 100 * u, H - 100 * u * (1 + i % 2)
        d.polygon([(x0, H), (x0 + 100 * u, H), (x0 + 50 * u, y0)], fill=hx(th["a1"], 45 + i * 12))
    c.put(lay)
    lay = c.layer(); ImageDraw.Draw(lay).rectangle([0, 0, 10 * u, H], fill=hx(th["a2"], 220)); c.put(lay)


def m_flowers(c, th, soft):          # Gul bog'i
    W, H, u = c.W, c.H, c.u
    def flower(cx, cy, r, col, a):
        lay = c.layer(); d = ImageDraw.Draw(lay)
        for k in range(6):
            ang = k * math.pi / 3
            px, py = cx + math.cos(ang) * r * .6, cy + math.sin(ang) * r * .6
            d.ellipse([px - r * .5, py - r * .5, px + r * .5, py + r * .5], fill=hx(col, a))
        d.ellipse([cx - r * .25, cy - r * .25, cx + r * .25, cy + r * .25], fill=hx(th["a1"], min(255, a + 60)))
        c.put(lay, blur=1.5)
    for (fx, fy, fr, col, a) in [(.93, .12, 120, th["a2"], 90), (.82, .02, 70, th["a1"], 60), (1.0, .32, 80, th["a2"], 70),
                                  (.04, .95, 110, th["a2"], 80), (.15, 1.02, 70, th["a1"], 55)]:
        flower(W * fx, H * fy, fr * u, col, a)
    c.stars(40, th["a2"], 3, seed=5, alpha=120)


def m_nordic(c, th, soft):           # Shimoliy minimal
    W, H, u = c.W, c.H, c.u
    lay = c.layer(); d = ImageDraw.Draw(lay)
    step = int(60 * u)
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=hx(th["a2"], 40), width=1)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=hx(th["a2"], 40), width=1)
    d.rectangle([W - 300 * u, 0, W, H], fill=hx(th["a2"], 60)); d.rectangle([W - 300 * u, 0, W - 292 * u, H], fill=hx(th["a1"], 200))
    d.ellipse([W - 230 * u, H * .62, W - 70 * u, H * .62 + 160 * u], outline=hx(th["a1"], 160), width=int(3 * u))
    d.line([(60 * u, H - 60 * u), (380 * u, H - 60 * u)], fill=hx(th["a1"], 200), width=int(4 * u))
    c.put(lay)


def m_arches(c, th, soft):           # Terrakota arklar
    W, H, u = c.W, c.H, c.u
    for k, (col, a) in enumerate([(th["a2"], 70), (th["a1"], 80), ("#E9C9A8", 160)]):
        lay = c.layer(); d = ImageDraw.Draw(lay)
        r = (240 - k * 60) * u; cx = W - 210 * u
        d.rounded_rectangle([cx - r, H - 2.2 * r - 40 * u * k, cx + r, H + r], radius=int(r), fill=hx(col, a))
        c.put(lay)
    c.radial(W * .12, H * .1, 140 * u, th["a2"], 50)


def m_leaves(c, th, soft):           # Zaytun barglari
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(8)
    for (sx, sy, ang0) in [(W * .98, H * .02, 2.3), (W * .02, H * .98, -.9)]:
        lay = c.layer(); d = ImageDraw.Draw(lay)
        for i in range(9):
            t = i / 8
            ang = ang0 + (rnd.random() - .5) * .9
            px, py = sx + math.cos(ang0) * t * 360 * u, sy + math.sin(ang0) * t * 360 * u
            L = (90 - i * 6) * u
            for side in (-1, 1):
                a = ang0 + side * 1.0
                ex, ey = px + math.cos(a) * L, py + math.sin(a) * L
                mx, my = (px + ex) / 2, (py + ey) / 2
                nx, ny = -(ey - py) * .25, (ex - px) * .25
                d.polygon([(px, py), (mx + nx, my + ny), (ex, ey), (mx - nx, my - ny)], fill=hx(th["a1"] if i % 2 else th["a2"], 90 + rnd.randint(0, 50)))
        d.line([(sx, sy), (sx + math.cos(ang0) * 360 * u, sy + math.sin(ang0) * 360 * u)], fill=hx(th["a1"], 150), width=int(3 * u))
        c.put(lay, blur=.6)


def m_notebook(c, th, soft):         # Daftar
    W, H, u = c.W, c.H, c.u
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for y in range(int(110 * u), H, int(38 * u)):
        d.line([(0, y), (W, y)], fill=hx(th["a1"], 34), width=max(1, int(1.4 * u)))
    d.line([(96 * u, 0), (96 * u, H)], fill=hx(th["a2"], 120), width=int(2 * u))
    for y in (H * .2, H * .5, H * .8):
        d.ellipse([28 * u, y - 13 * u, 54 * u, y + 13 * u], fill=hx("#E5E7EB", 255), outline=hx("#CBD5E1"), width=int(2 * u))
    c.put(lay)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([W - 190 * u, -20 * u, W - 120 * u, 150 * u], radius=int(8 * u), fill=hx(th["a2"], 160))
    c.put(lay)


def m_dawn(c, th, soft):             # Tong gradient
    W, H, u = c.W, c.H, c.u
    c.radial(W * .85, H * .2, 330 * u, th["a2"], 90)
    c.radial(W * .1, H * .95, 360 * u, th["a1"], 60)
    c.radial(W * .55, H * 1.05, 260 * u, "#F9A8D4", 60)


def m_bauhaus(c, th, soft):          # Bauhaus
    W, H, u = c.W, c.H, c.u
    lay = c.layer(); d = ImageDraw.Draw(lay)
    d.ellipse([W - 330 * u, -110 * u, W - 30 * u, 190 * u], fill=hx(th["a2"], 215))
    d.rectangle([W - 150 * u, H - 260 * u, W, H], fill=hx(th["a1"], 215))
    d.polygon([(W - 380 * u, H), (W - 150 * u, H), (W - 265 * u, H - 200 * u)], fill=hx("#F2B705", 230))
    d.rectangle([0, H - 14 * u, W * .45, H], fill=hx(th["a1"], 230))
    d.ellipse([-60 * u, -60 * u, 90 * u, 90 * u], outline=hx(th["a1"], 220), width=int(10 * u))
    c.put(lay)


def m_latte(c, th, soft):            # Kofe latte
    W, H, u = c.W, c.H, c.u
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for (cx, cy, r) in [(W * .92, H * .15, 120), (W * .86, H * .24, 80), (W * .06, H * .9, 140)]:
        R = r * u
        for k in range(3):
            d.ellipse([cx - R + k * 4 * u, cy - R, cx + R + k * 4 * u, cy + R], outline=hx(th["a2"], 70 - k * 18), width=int((8 - k * 2) * u))
    c.put(lay, blur=1.2)
    c.radial(W * .5, H * 1.1, 400 * u, th["a2"], 40)


# ======================================================================== PRO (neon, qorong'i)
def m_city(c, th, soft):             # Neon shahar
    W, H, u = c.W, c.H, c.u
    c.vgrad(th["bg"], "{:02X}{:02X}{:02X}".format(*mix(th["bg"], th["a2"], .25)[:3]))
    rnd = random.Random(4); x = 0; pts = [(0, H)]
    while x < W:
        bw, bh = rnd.uniform(40, 110) * u, rnd.uniform(.07, .24) * H
        pts += [(x, H - bh), (x + bw, H - bh)]; x += bw
    pts += [(W, H)]
    c.glow(lambda d: d.line(pts, fill=hx(th["a1"]), width=int(3 * u)), blur=10)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for i in range(1, len(pts) - 2, 2):
        (x1, y1), (x2, _) = pts[i], pts[i + 1]
        for yy in range(int(y1 + 16 * u), H - int(10 * u), int(22 * u)):
            for xx in range(int(x1 + 10 * u), int(x2 - 10 * u), int(18 * u)):
                if rnd.random() < .35:
                    d.rectangle([xx, yy, xx + 7 * u, yy + 9 * u], fill=hx(th["a2"], 150))
    c.put(lay)
    c.stars(120, "#FFFFFF", 1.6, seed=2, alpha=160)


def m_lasers(c, th, soft):           # Lazer nurlar
    W, H, u = c.W, c.H, c.u
    for k in range(7):
        col = th["a1"] if k % 2 else th["a2"]
        x0 = W * (.35 + k * .12)
        c.glow(lambda d, x0=x0, col=col: d.line([(x0, -20), (x0 - W * .55, H + 20)], fill=hx(col, 210), width=int(3 * u)), blur=14, alpha=.85)
    c.radial(W * .9, H * .05, 220 * u, th["a2"], 90)
    c.frame(th["a1"], alpha=90)


def m_prism(c, th, soft):            # Kristall prizma (low-poly)
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(11)
    cols, rows = 9, 6
    pts = [[(i / cols * W + (rnd.random() - .5) * W / cols * .7 * (0 < i < cols), j / rows * H + (rnd.random() - .5) * H / rows * .7 * (0 < j < rows))
            for i in range(cols + 1)] for j in range(rows + 1)]
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for j in range(rows):
        for i in range(cols):
            a, b, cc, dd = pts[j][i], pts[j][i + 1], pts[j + 1][i], pts[j + 1][i + 1]
            for tri in ((a, b, dd), (a, dd, cc)):
                t = (sum(p[0] for p in tri) / 3) / W
                col = mix(th["a1"], th["a2"], t)
                alpha = int(30 + rnd.random() * 110 * (t ** 1.2))
                d.polygon(tri, fill=col[:3] + (alpha,), outline=col[:3] + (70,))
    c.put(lay)


def m_dotwave(c, th, soft):          # Raqamli to'lqin
    W, H, u = c.W, c.H, c.u
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for j in range(18):
        for i in range(70):
            x = i / 69 * W
            y = H * .62 + j * 14 * u + math.sin(i * .17 + j * .35) * 50 * u * (1 - j / 22)
            r = (1 + 2.2 * (1 - j / 18)) * u
            col = mix(th["a1"], th["a2"], i / 69)
            d.ellipse([x - r, y - r, x + r, y + r], fill=col[:3] + (int(230 * (1 - j / 20)),))
    c.put(lay, blur=.4)
    c.put(lay.filter(ImageFilter.GaussianBlur(6 * u)), alpha=.8)


def m_orbit(c, th, soft):            # Kosmik orbita
    W, H, u = c.W, c.H, c.u
    c.stars(200, "#FFFFFF", 1.8, seed=9)
    cx, cy, r = W * .8, H * .55, 150 * u
    c.radial(cx, cy, r * 1.6, th["a2"], 70)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for k in range(int(r)):
        t = k / r
        col = mix(th["a2"], th["bg"], t * .8)
        d.ellipse([cx - r + k * .4, cy - r + k * .4, cx + r - k * 1.2, cy + r - k * 1.2], fill=col)
    c.put(lay)
    c.glow(lambda d: d.ellipse([cx - r * 2.1, cy - r * .42, cx + r * 2.1, cy + r * .42], outline=hx(th["a1"], 230), width=int(4 * u)), blur=10)


def m_mountains(c, th, soft):        # Neon tog'lar
    W, H, u = c.W, c.H, c.u
    c.radial(W * .5, H * .62, 260 * u, th["a1"], 90)
    for k, (col, base, amp) in enumerate([(th["a2"], .55, .22), (th["a1"], .68, .18)]):
        rnd = random.Random(20 + k); pts = []; x = 0
        while x <= W:
            pts.append((x, H * base + (rnd.random() - .5) * H * amp)); x += rnd.uniform(60, 160) * u
        pts.append((W, H * base))
        lay = c.layer(); ImageDraw.Draw(lay).polygon(pts + [(W, H), (0, H)], fill=hx(th["bg"], 255)); c.put(lay)
        c.glow(lambda d, pts=pts, col=col: d.line(pts, fill=hx(col), width=int(3 * u)), blur=10)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for i in range(14):
        y = H * .8 + (i ** 1.6) * 3 * u
        d.line([(0, y), (W, y)], fill=hx(th["a1"], 70), width=1)
    c.put(lay)


def m_glitch(c, th, soft):           # Glitch
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(7)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for _ in range(26):
        y, hh, x = rnd.random() * H, rnd.uniform(2, 16) * u, rnd.random() * W
        w = rnd.uniform(.1, .45) * W
        d.rectangle([x, y, x + w, y + hh], fill=hx(th["a1"] if rnd.random() < .5 else th["a2"], rnd.randint(50, 160)))
    c.put(lay)
    for dx, col in ((-6, th["a1"]), (6, th["a2"])):
        c.glow(lambda d, dx=dx, col=col: d.rectangle([W * .62 + dx * u, H * .18, W * .94 + dx * u, H * .82], outline=hx(col, 200), width=int(3 * u)), blur=8, alpha=.8)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for y in range(0, H, int(4 * u) or 1):
        d.line([(0, y), (W, y)], fill=(0, 0, 0, 40))
    c.put(lay)


def m_bokeh(c, th, soft):            # Bokeh tun
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(13)
    for blur in (14, 5):
        lay = c.layer(); d = ImageDraw.Draw(lay)
        for _ in range(22):
            x, y, r = rnd.random() * W, rnd.random() * H, rnd.uniform(18, 70) * u
            col = th["a1"] if rnd.random() < .55 else th["a2"]
            d.ellipse([x - r, y - r, x + r, y + r], fill=hx(col, rnd.randint(40, 110)), outline=hx(col, 160), width=int(2 * u))
        c.put(lay, blur=blur)


def m_code(c, th, soft):             # Matritsa kod
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(15)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    cw = 22 * u
    for i in range(int(W / cw)):
        if rnd.random() < .45:
            continue
        L = rnd.randint(6, 22); y0 = rnd.random() * H
        for k in range(L):
            a = int(220 * (1 - k / L))
            y = y0 - k * cw
            d.rectangle([i * cw + 4 * u, y, i * cw + 4 * u + cw * .5, y + cw * .7], fill=hx(th["a1"] if k else th["a2"], a))
    c.put(lay)
    c.put(lay.filter(ImageFilter.GaussianBlur(5 * u)), alpha=.7)


def m_plasma(c, th, soft):           # Elektr ko'k
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(21)
    c.radial(W * .82, H * .5, 230 * u, th["a1"], 110)
    for k in range(5):
        pts = [(W * .82, H * .5)]
        ang = rnd.uniform(0, 6.28); x, y = pts[0]
        for _ in range(12):
            ang += rnd.uniform(-.8, .8); x += math.cos(ang) * 45 * u; y += math.sin(ang) * 45 * u; pts.append((x, y))
        c.glow(lambda d, pts=pts: d.line(pts, fill=hx(th["a2"], 230), width=int(2.5 * u)), blur=9)
    c.glow(lambda d: d.ellipse([W * .82 - 40 * u, H * .5 - 40 * u, W * .82 + 40 * u, H * .5 + 40 * u], fill=hx(th["a2"])), blur=20)
    c.frame(th["a1"], alpha=80)


# ======================================================================== PREMIUM (lyuks)
def m_deco(c, th, soft):             # Oltin art deko
    W, H, u = c.W, c.H, c.u
    for (cx, cy, sgn) in ((W, 0, 1), (0, H, -1)):
        lay = c.layer(); d = ImageDraw.Draw(lay)
        for k in range(1, 9):
            r = k * 46 * u
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=hx(th["a1"], 245 - k * 14), width=int(2.4 * u))
        for k in range(12):
            a = math.pi / 2 * (1 + sgn) / 2 + k / 11 * math.pi / 2 * (-1 if sgn > 0 else 1) + (math.pi / 2 if sgn > 0 else 0)
            d.line([(cx, cy), (cx + math.cos(a) * 370 * u * -sgn, cy + math.sin(a) * 370 * u * sgn)], fill=hx(th["a2"], 150), width=max(1, int(1.4 * u)))
        c.put(lay)
    c.radial(W, 0, 300 * u, th["a1"], 70); c.radial(0, H, 300 * u, th["a1"], 70)
    c.frame(th["a1"], inset=22, alpha=230, corners=True)


def m_silk(c, th, soft):             # Ipak to'lqin
    W, H, u = c.W, c.H, c.u
    c.radial(W * .6, H * .62, 380 * u, th["a2"], 70)
    for k in range(24):
        t = k / 23
        col = mix(th["a1"], th["a2"], t)
        pts = [(x, H * (.45 + t * .3) + math.sin(x / W * 4.2 + t * 2.4) * 90 * u + math.sin(x / W * 9 - t) * 18 * u) for x in range(0, W + 10, 10)]
        c.glow(lambda d, pts=pts, col=col, t=t: d.line(pts, fill=col[:3] + (int(170 + 85 * (1 - abs(t - .5) * 2)),), width=int(2.6 * u)), blur=7, alpha=.95)
    c.radial(W * .2, H * .2, 200 * u, th["a2"], 40)


def m_marble(c, th, soft):           # Qora marmar
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(31)
    for k in range(7):
        x, y = W * (.5 + rnd.random() * .5), -20
        pts = [(x, y)]
        while y < H + 20:
            x += rnd.uniform(-38, 38) * u; y += rnd.uniform(25, 55) * u; pts.append((x, y))
        w = rnd.choice([1, 1, 2, 3])
        col = th["a1"] if k % 3 == 0 else "#9CA3AF"
        c.glow(lambda d, pts=pts, col=col, w=w: d.line(pts, fill=hx(col, 235 if col == th["a1"] else 110), width=int((w + 1) * u)), blur=5, alpha=1)
    c.frame(th["a1"], inset=30, width=1.5, alpha=170)


def m_velvet(c, th, soft):           # Shoh baxmal
    W, H, u = c.W, c.H, c.u
    c.radial(W * .5, H * .45, 440 * u, th["a2"], 150); c.radial(W * .5, H * .1, 200 * u, th["a1"], 50)
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for k in range(0, W, int(26 * u)):
        d.line([(k, 0), (k + 60 * u, H)], fill=(255, 255, 255, 6), width=int(10 * u))
    c.put(lay, blur=4)
    c.frame(th["a1"], inset=22, width=2.5, alpha=220, corners=True)
    c.frame(th["a1"], inset=34, width=1, alpha=120)


def m_diamond(c, th, soft):          # Kristal olmos
    W, H, u = c.W, c.H, c.u
    cx, cy, R = W * .8, H * .48, 230 * u
    top = [(cx + math.cos(a) * R, cy - R * .35 + math.sin(a) * R * .25) for a in [i * math.pi / 4 for i in range(8)]]
    lay = c.layer(); d = ImageDraw.Draw(lay)
    tip = (cx, cy + R * 1.1)
    for i in range(8):
        p1, p2 = top[i], top[(i + 1) % 8]
        shade = 40 + (i * 23) % 120
        d.polygon([p1, p2, tip], fill=hx(th["a2"] if i % 2 else th["a1"], shade), outline=hx("#FFFFFF", 120))
        d.polygon([p1, p2, (cx, cy - R * .35)], fill=hx(th["a1"], 30 + i * 8), outline=hx("#FFFFFF", 90))
    c.put(lay)
    c.glow(lambda d: d.polygon(top, outline=hx("#FFFFFF", 200)), blur=8)
    c.stars(60, "#FFFFFF", 2.6, seed=17, alpha=220)


def m_naqsh(c, th, soft):            # Sharqona naqsh (8 qirrali yulduz)
    W, H, u = c.W, c.H, c.u
    s = 120 * u
    lay = c.layer(); d = ImageDraw.Draw(lay)
    for j in range(-1, int(H / s) + 2):
        for i in range(-1, int(W / s) + 2):
            cx, cy = i * s + (s / 2 if j % 2 else 0), j * s
            star = []
            for k in range(16):
                a = k * math.pi / 8; r = s * (.42 if k % 2 == 0 else .25)
                star.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            d.polygon(star, outline=hx(th["a1"], 150), width=max(1, int(1.8 * u)))
            d.ellipse([cx - 5 * u, cy - 5 * u, cx + 5 * u, cy + 5 * u], fill=hx(th["a2"], 220))
    c.put(lay)
    # o'rtada o'qish uchun yumshoq dog'
    c.radial(W * .36, H * .5, 330 * u, th["bg"], 200)
    c.frame(th["a1"], inset=22, width=2.5, alpha=220, corners=True)


def m_goldust(c, th, soft):          # Oltin changlar
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(41)
    for blur, n, rr in ((10, 40, 26), (3, 120, 8), (0, 260, 2.4)):
        lay = c.layer(); d = ImageDraw.Draw(lay)
        for _ in range(n):
            x = W * (.45 + rnd.random() ** .7 * .55); y = rnd.random() * H
            r = rnd.uniform(.3, 1) * rr * u
            d.ellipse([x - r, y - r, x + r, y + r], fill=hx(th["a1"] if rnd.random() < .7 else th["a2"], rnd.randint(70, 220)))
        c.put(lay, blur=blur)
    c.frame(th["a1"], inset=26, width=1.5, alpha=150)


def m_nebula(c, th, soft):           # Galaktika lyuks
    W, H, u = c.W, c.H, c.u
    rnd = random.Random(51)
    for _ in range(14):
        c.radial(W * (.5 + rnd.random() * .5), H * rnd.random(), rnd.uniform(90, 230) * u, th["a1"] if rnd.random() < .5 else th["a2"], rnd.randint(60, 120))
    c.stars(260, "#FFFFFF", 1.8, seed=52)
    c.stars(14, "#FFFFFF", 4, seed=53, alpha=255)
    c.frame(th["a1"], inset=24, width=1.5, alpha=140, corners=True)


def m_rosegold(c, th, soft):         # Atirgul oltin (yorug' premium)
    W, H, u = c.W, c.H, c.u
    c.radial(W * .88, H * .12, 320 * u, th["a2"], 190)
    c.radial(W * .05, H * .95, 260 * u, th["a1"], 60)
    for k in range(6):
        pts = [(x, H * (.78 + k * .035) + math.sin(x / W * 5 + k * .7) * 30 * u) for x in range(0, W + 10, 10)]
        c.glow(lambda d, pts=pts, k=k: d.line(pts, fill=hx(th["a1"], 230 - k * 22), width=int(2.4 * u)), blur=3, alpha=1)
    c.frame(th["a1"], inset=24, width=1.6, alpha=170, corners=True)


def m_palace(c, th, soft):           # Zumrad saroy (ark)
    W, H, u = c.W, c.H, c.u
    i = 40 * u
    def arch(d, pad, col, a, w):
        x0, x1, top = i + pad, W - i - pad, i + pad + 140 * u
        d.line([(x0, H - i - pad), (x0, top)], fill=hx(col, a), width=w)
        d.line([(x1, H - i - pad), (x1, top)], fill=hx(col, a), width=w)
        d.arc([x0, i + pad, x1, top + (top - i - pad)], 180, 360, fill=hx(col, a), width=w)
        d.line([(x0, H - i - pad), (x1, H - i - pad)], fill=hx(col, a), width=w)
    c.glow(lambda d: arch(d, 0, th["a1"], 230, int(3 * u)), blur=8)
    c.glow(lambda d: arch(d, 14 * u, th["a1"], 110, int(1.4 * u)), blur=0, sharp=False)
    c.radial(W * .5, 60 * u, 340 * u, th["a2"], 130)
    c.stars(90, th["a1"], 2.8, seed=61, alpha=230)


# ======================================================================== ro'yxat
# n: (motif, palitra) — palitra autogen.THEMES bilan bir xil
NEW = {
    13: (m_waves, "F2FAFC", "0E7490", "22D3EE"), 14: (m_origami, "FBFAF6", "334155", "F59E0B"),
    15: (m_flowers, "FFF8F6", "BE185D", "FDA4AF"), 16: (m_nordic, "F7F9FB", "1E3A5F", "94A3B8"),
    17: (m_arches, "FBF5EF", "9A3412", "F97316"), 18: (m_leaves, "F7F8F1", "4D7C0F", "A3B18A"),
    19: (m_notebook, "FFFEF9", "1D4ED8", "EF4444"), 20: (m_dawn, "FFF7F3", "7C3AED", "FB923C"),
    21: (m_bauhaus, "FAF7F0", "1E40AF", "DC2626"), 22: (m_latte, "FAF6F1", "6F4E37", "C8A27A"),
    33: (m_city, "070818", "22D3EE", "F472B6"), 34: (m_lasers, "08040F", "F43F5E", "A855F7"),
    35: (m_prism, "050A14", "60A5FA", "C084FC"), 36: (m_dotwave, "02100E", "2DD4BF", "A3E635"),
    37: (m_orbit, "04030D", "FBBF24", "818CF8"), 38: (m_mountains, "0A0414", "E879F9", "38BDF8"),
    39: (m_glitch, "060608", "FF3D7F", "00E5FF"), 40: (m_bokeh, "0B0712", "FB923C", "FDE047"),
    41: (m_code, "010A04", "22C55E", "86EFAC"), 42: (m_plasma, "020617", "3B82F6", "E0F2FE"),
    53: (m_deco, "0B0A08", "E8C468", "B08D3C"), 54: (m_silk, "120E14", "F3D9B1", "C084FC"),
    55: (m_marble, "0A0A0C", "D4AF37", "E5E7EB"), 56: (m_velvet, "14051F", "F5C542", "A855F7"),
    57: (m_diamond, "06080F", "E2E8F0", "7DD3FC"), 58: (m_naqsh, "04131A", "E9C46A", "2A9D8F"),
    59: (m_goldust, "050B1A", "F6D365", "FDA085"), 60: (m_nebula, "07030F", "F0ABFC", "93C5FD"),
    61: (m_rosegold, "FBF3F1", "B76E79", "E8C4A0"), 62: (m_palace, "021A14", "E9C46A", "34D399"),
}


def render(n, W, H, soft):
    fn, bg, a1, a2 = NEW[n]
    th = {"bg": bg, "a1": a1, "a2": a2}
    c = Canvas(W, H, bg)
    fn(c, th, soft)
    img = c.out()
    if soft:   # ichki slayd: naqsh yumshoqroq, matn o'qilsin
        plain = Image.new("RGB", (W, H), hx(bg)[:3])
        img = Image.blend(plain, img, .62)
    return img


def make(n):
    render(n, 1600, 900, False).save(BASE / f"bg_t{n}.jpg", quality=90)
    render(n, 1600, 900, True).save(BASE / f"bg_c{n}.jpg", quality=90)
    a4 = render(n, 1240, 1754, False)
    plain = Image.new("RGB", a4.size, hx(NEW[n][1])[:3])
    Image.blend(plain, a4, .8).save(BASE / f"bg_a4{n}.jpg", quality=88)


if __name__ == "__main__":
    nums = [int(x) for x in sys.argv[1:]] or sorted(NEW)
    for n in nums:
        make(n)
        print("ok", n)
