#!/usr/bin/env python3
"""THE WORLD TODAY — Monday 23 November 2026. Front-page dense news image.
Draws entry.png (1024x1024) with PIL. All 31 stories dated 23 Nov 2026.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1024, 1024
M = 24  # margin
BG = (250, 248, 242)
NAVY = (13, 27, 46)
NAVY2 = (24, 48, 80)
GOLD = (198, 154, 52)
GOLD_L = (232, 196, 110)
INK = (18, 18, 18)
GREY = (90, 90, 90)
RED = (178, 34, 34)
RED_BG = (252, 235, 235)
LINE = (200, 192, 178)
CHIP_BG = (13, 27, 46)
CLAIM_BG = (178, 34, 34)
WHITE = (255, 255, 255)

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def tw(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def fit_font(draw, text, path, size, max_w, min_size=8):
    """Largest font size <= size whose width fits max_w."""
    s = size
    while s > min_size and tw(draw, text, font(path, s)) > max_w:
        s -= 1
    return font(path, s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(draw, t, fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, text, fnt, x, y, max_w, fill, lh=None, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    if lh is None:
        lh = fnt.size + 3
    for i, ln in enumerate(lines):
        draw.text((x, y + i * lh), ln, font=fnt, fill=fill)
    return y + len(lines) * lh


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# ---------------------------------------------------------------- masthead
d.rectangle([0, 0, W, 58], fill=NAVY)
d.rectangle([0, 58, W, 61], fill=GOLD)
f_mast = font(SERIF_B, 40)
d.text((M, 8), "THE WORLD TODAY", font=f_mast, fill=WHITE)
f_date = font(SANS_B, 15)
date_txt = "MONDAY 23 NOVEMBER 2026"
d.text((W - M - tw(d, date_txt, f_date), 22), date_txt, font=f_date, fill=GOLD_L)

# kicker
f_kick = font(SANS_B, 12)
kick = "AI ROUT SHAKES ASIA  ·  GUTERRES: REGULATE AI NOW  ·  US LEAD OVER CHINA AT RECORD LOW"
d.text(((W - tw(d, kick, f_kick)) / 2, 68), kick, font=f_kick, fill=NAVY)

# ---------------------------------------------------------------- number strip
STRIP = [
    ("-3.3%", "KOSPI FALLS"),
    ("5.3", "US-CHINA GAP"),
    ("11,762", "EBOLA CASES, DRC"),
    ("10T WON", "SEOUL RESCUE FUND"),
    ("2%", "BILLIONAIRE TAX"),
    ("$450M", "SKUBAL METS DEAL"),
    ("165", "MISSILES / WEEK"),
    ("12,000", "CLEARED, MANCHESTER"),
    ("264 KG", "EXPLOSIVES, LEBANON"),
    ("$107.3B", "ANTHROPIC IPO"),
]
sy, sh = 88, 62
d.rectangle([M, sy, W - M, sy + sh], outline=NAVY, width=2)
cw = (W - 2 * M) / 5
for row in range(2):
    for col in range(5):
        i = row * 5 + col
        val, lab = STRIP[i]
        x0 = M + col * cw
        y0 = sy + row * 31
        fv = fit_font(d, val, SANS_B, 19, cw - 10, 12)
        d.text((x0 + (cw - tw(d, val, fv)) / 2, y0 + 1), val, font=fv, fill=NAVY)
        fl = fit_font(d, lab, SANS, 9, cw - 8, 7)
        d.text((x0 + (cw - tw(d, lab, fl)) / 2, y0 + 20), lab, font=fl, fill=GREY)
        if col:
            d.line([x0, y0 + 4, x0, y0 + 27], fill=LINE, width=1)

# ---------------------------------------------------------------- region bar
ry = 158
f_reg = font(SANS_B, 11)
regions = [("ASIA-PACIFIC", 7), ("AMERICAS", 8), ("MIDDLE EAST", 6),
           ("EUROPE", 5), ("AFRICA", 3), ("WORLD", 2)]
parts = []
for name, n in regions:
    parts.append((name, n))
total_w = 0
segs = []
for name, n in parts:
    t = "%s %d" % (name, n)
    segs.append((t, tw(d, t, f_reg)))
    total_w += tw(d, t, f_reg)
gap = 26
total_w += gap * (len(segs) - 1)
x = (W - total_w) / 2
d.rectangle([M, ry, W - M, ry + 20], fill=NAVY2)
for t, wdt in segs:
    d.text((x, ry + 4), t, font=f_reg, fill=WHITE)
    x += wdt + gap

# ---------------------------------------------------------------- hero scenes
HEROES = [
    ("AI ROUT HITS ASIA",
     "Kospi -3.3% to 4,708.54, sheds 161 pts; intraday -5.8%. "
     "Samsung -3.1%, SK Hynix -2.5%.", "REUTERS", "kospi"),
    ("GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
     "150 delegates back a risk framework at the Bridgetown summit "
     "- a blueprint, not a treaty.", "AP", "guterres"),
    ("US LEAD OVER CHINA AT RECORD LOW",
     "Asia Power Index 2026: US 78.9, China 73.6 - gap 5.3, "
     "narrowest since 2018. India 3rd at 40.5.", "LOWY INSTITUTE", "power"),
]
hy = 186
hcol_w = (W - 2 * M - 16) / 3
scene_h = 118


def draw_scene(x0, y0, w, h, kind):
    x0, y0, w, h = int(x0), int(y0), int(w), int(h)
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY)
    if kind == "kospi":
        # skyline with lit windows + falling orange chart line
        import random
        rnd = random.Random(7)
        bx = x0 + 6
        while bx < x0 + w - 26:
            bw = rnd.randint(18, 30)
            bh = rnd.randint(34, 72)
            d.rectangle([bx, y0 + h - bh, bx + bw, y0 + h], fill=(38, 66, 104))
            for wy in range(y0 + h - bh + 5, y0 + h - 4, 9):
                for wx in range(bx + 4, bx + bw - 3, 8):
                    if rnd.random() < 0.55:
                        d.rectangle([wx, wy, wx + 3, wy + 4], fill=GOLD_L)
            bx += bw + 4
        pts = [(x0 + 8, y0 + 58), (x0 + w * 0.3, y0 + 66),
               (x0 + w * 0.55, y0 + 60), (x0 + w * 0.8, y0 + 82),
               (x0 + w - 8, y0 + 94)]
        d.line(pts, fill=(255, 122, 26), width=3)
        fbig = font(SANS_B, 26)
        d.text((x0 + 10, y0 + 8), "-3.3%", font=fbig, fill=(255, 122, 26))
        fcap = font(SANS, 10)
        d.rectangle([x0, y0 + h - 18, x0 + w, y0 + h], fill=(8, 18, 34))
        d.text((x0 + 8, y0 + h - 16),
               "KOSPI 4,708.54  -161 PTS", font=fcap, fill=WHITE)
    elif kind == "guterres":
        # globe + gold text
        cx, cy, r = x0 + w - 58, y0 + 52, 40
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 110, 168),
                  outline=GOLD, width=2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(120, 180, 220))
        d.arc([cx - r + 12, cy - r, cx + r - 12, cy + r], 250, 110,
              fill=(120, 180, 220), width=2)
        d.line([cx - r, cy, cx + r, cy], fill=(120, 180, 220), width=1)
        d.line([cx, cy - r, cx, cy + r], fill=(120, 180, 220), width=1)
        fg1 = font(SANS_B, 17)
        d.text((x0 + 10, y0 + 10), "150 DELEGATES", font=fg1, fill=GOLD_L)
        fg2 = font(SANS_B, 13)
        d.text((x0 + 10, y0 + 34), "BACK A RISK", font=fg2, fill=GOLD_L)
        d.text((x0 + 10, y0 + 52), "FRAMEWORK", font=fg2, fill=GOLD_L)
        fcap = font(SANS, 10)
        d.rectangle([x0, y0 + h - 18, x0 + w, y0 + h], fill=(8, 18, 34))
        d.text((x0 + 8, y0 + h - 16), "BRIDGETOWN SUMMIT",
               font=fcap, fill=WHITE)
    else:
        # power-index bars
        bars = [("US", 78.9, GOLD), ("CHINA", 73.6, (180, 60, 60)),
                ("INDIA", 40.5, (90, 140, 200))]
        by = y0 + 12
        for name, val, col in bars:
            d.text((x0 + 10, by), name, font=font(SANS_B, 12), fill=WHITE)
            bw = (w - 110) * val / 100.0
            d.rectangle([x0 + 76, by + 2, x0 + 76 + bw, by + 14], fill=col)
            d.text((x0 + 80 + bw, by), "%.1f" % val,
                   font=font(SANS_B, 12), fill=WHITE)
            by += 26
        fcap = font(SANS, 10)
        d.rectangle([x0, y0 + h - 18, x0 + w, y0 + h], fill=(8, 18, 34))
        d.text((x0 + 8, y0 + h - 16), "GAP 5.3 - NARROWEST SINCE 2018",
               font=fcap, fill=WHITE)


for ci, (head, body, src, kind) in enumerate(HEROES):
    x0 = M + ci * (hcol_w + 8)
    draw_scene(x0, hy, hcol_w, scene_h, kind)
    ty = hy + scene_h + 6
    fh = fit_font(d, head, SANS_B, 15, hcol_w, 11)
    # headline up to 2 lines
    hl = wrap(d, head, fh, hcol_w)
    for li, ln in enumerate(hl[:2]):
        d.text((x0, ty + li * 18), ln, font=fh, fill=NAVY)
    ty += len(hl[:2]) * 18 + 2
    fb = font(SANS, 11)
    ty = draw_wrapped(d, body, fb, x0, ty, hcol_w, INK, lh=14, max_lines=3)
    # source + chip row
    fsrc = font(SANS_B, 9)
    chip_txt = "REPORTED"
    cwdt = tw(d, chip_txt, fsrc) + 10
    d.rectangle([x0 + hcol_w - cwdt, ty + 2, x0 + hcol_w, ty + 15],
                fill=CHIP_BG)
    d.text((x0 + hcol_w - cwdt + 5, ty + 4), chip_txt, font=fsrc, fill=WHITE)
    d.text((x0, ty + 4), src, font=fsrc, fill=GREY)

# ---------------------------------------------------------------- more-of-day bar
by = 430
d.rectangle([M, by, W - M, by + 22], fill=NAVY)
d.text((M + 8, by + 5), "MORE OF THE DAY", font=font(SANS_B, 12), fill=GOLD_L)

# ---------------------------------------------------------------- cards (10)
CARDS = [
    ("BESSENT DEMANDS NVIDIA ANSWERS",
     "Treasury chief presses chipmaker over China sales.", "REUTERS", False),
    ("FBI PROBES NCIC POLICE-DATABASE HACK",
     "Agents investigate breach of law-enforcement system.", "AP", False),
    ("TRUMP: IRAN STRIKES MAY RESUME",
     "President says strikes may resume in the New Year.", "REUTERS", False),
    ("NASDAQ FUTURES JUMP 3%",
     "Holiday-week rally lifts US futures.", "BLOOMBERG", False),
    ("SKUBAL SIGNS $450M METS DEAL",
     "Two-time Cy Young winner, nine years - largest ever for a pitcher.",
     "ESPN", False),
    ("TOM JACKSON DIES AT 75",
     "NFL star turned broadcaster passes away.", "AP", False),
    ("STATES SUE SPACEX OVER AI SAFETY",
     "Attorneys general challenge AI safety claims.", "REUTERS", False),
    ("ANTHROPIC IPO AT $107.3B",
     "Raised at $83 a share; debut close $97.17.", "BLOOMBERG", False),
    ("POLAND: 3 RUSSIAN MISSILES CROSSED AIRSPACE",
     "Warsaw says Kh-101s entered its skies.", "AP", True),
    ("INTEL WARNS OF RUSSIAN NUCLEAR SATELLITE",
     "US intelligence flags orbital weapon risk.", "REUTERS", True),
]
cy = by + 30
ccol_w = (W - 2 * M - 4 * 8) / 5
crow_h = 66
for row in range(2):
    for col in range(5):
        i = row * 5 + col
        head, body, src, claim = CARDS[i]
        x0 = M + col * (ccol_w + 8)
        y0 = cy + row * (crow_h + 8)
        d.rectangle([x0, y0, x0 + ccol_w, y0 + crow_h], outline=LINE, width=1)
        fh = fit_font(d, head, SANS_B, 11, ccol_w - 10, 8)
        hl = wrap(d, head, fh, ccol_w - 10)
        ty = y0 + 4
        for li, ln in enumerate(hl[:2]):
            d.text((x0 + 5, ty + li * 13), ln, font=fh, fill=NAVY)
        ty += len(hl[:2]) * 13 + 1
        fb = font(SANS, 10)
        # body: at most 2 lines, must end above the source row
        bl = wrap(d, body, fb, ccol_w - 10)
        src_y = y0 + crow_h - 15
        avail = src_y - ty - 1
        max_bl = max(1, avail // 12)
        for li, ln in enumerate(bl[:max_bl]):
            d.text((x0 + 5, ty + li * 12), ln, font=fb, fill=INK)
        fsrc = font(SANS_B, 8)
        chip_txt = "CLAIM" if claim else "REPORTED"
        chip_fill = CLAIM_BG if claim else CHIP_BG
        cwdt = tw(d, chip_txt, fsrc) + 8
        d.rectangle([x0 + ccol_w - cwdt - 4, src_y, x0 + ccol_w - 4,
                     src_y + 11], fill=chip_fill)
        d.text((x0 + ccol_w - cwdt, src_y + 1), chip_txt, font=fsrc, fill=WHITE)
        d.text((x0 + 5, src_y + 1), src, font=fsrc, fill=GREY)

# ---------------------------------------------------------------- map + ALSO
my = cy + 2 * crow_h + 8 + 6
map_w = 500
also_x = M + map_w + 12
also_w = W - M - also_x
d.rectangle([M, my, M + map_w, my + 168], outline=NAVY, width=2)
d.text((M + 8, my + 5), "THE WORLD IN ONE DAY", font=font(SANS_B, 11),
       fill=NAVY)
# stylised continents (two blobs)
d.rounded_rectangle([M + 14, my + 30, M + 150, my + 120], radius=18,
                    fill=(214, 226, 238))
d.rounded_rectangle([M + 170, my + 26, M + 486, my + 96], radius=18,
                    fill=(214, 226, 238))
d.rounded_rectangle([M + 210, my + 96, M + 330, my + 150], radius=16,
                    fill=(214, 226, 238))
# pins: (x, y, label) inside map box
PINS = [
    (430, 66, "1"), (120, 100, "2"), (84, 62, "3"), (98, 74, "4"),
    (238, 58, "5"), (226, 48, "6"), (212, 40, "7"), (300, 56, "8"),
    (330, 74, "9"), (322, 88, "10"), (288, 116, "11"), (262, 128, "12"),
    (248, 142, "13"),
]
fpin = font(SANS_B, 9)
for px, py, lab in PINS:
    ax, ay = M + px, my + py
    d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], fill=RED, outline=WHITE,
              width=1)
    d.text((ax - tw(d, lab, fpin) / 2, ay - 5), lab, font=fpin, fill=WHITE)
fleg = font(SANS, 9)
leg = ["1 Seoul  2 Bridgetown  3 Washington  4 New York  5 Paris",
       "6 London  7 Manchester  8 Kyiv  9 Beirut  10 Gaza",
       "11 Benghazi  12 Khartoum  13 Kinshasa"]
for li, ln in enumerate(leg):
    d.text((M + 10, my + 152 + li * 0), ln, font=fleg, fill=GREY) \
        if False else None
# legend below map box instead (keeps pins clean)
leg_y = my + 172
for li, ln in enumerate(leg):
    d.text((M + 4, leg_y + li * 11), ln, font=fleg, fill=GREY)

# ALSO list (18 items, 2 columns x 9)
ALSO = [
    "Paris: 100+ back 2% billionaire tax",
    "Manchester: 12,000 cleared",
    "Zelenskyy: 165 Russian missiles in a week",
    "COP31: the day after Antalya pact rejected",
    "Israel unity talks resume",
    "Gaza: two killed in Israeli strike",
    "West Bank settler attacks",
    "Iran war: no deal in sight",
    "Lebanon seizes 264 kg explosives",
    "Bahrain: Iranian strike hits plant, 2 hurt",
    "Benghazi: UN demands port probe [CLAIM]",
    "Sudan: drones downed in Khartoum [CLAIM]",
    "DRC: fighting traps Ebola teams",
    "Bangladesh: Hasina jailed if she returns",
    "Seoul minister quits over AI exam chaos",
    "SK Telecom -7.3%",
    "China eases margin rules to 80%",
    "Seoul readies 10T-won stabilisation fund",
]
d.text((also_x, my + 5), "ALSO ON MONDAY", font=font(SANS_B, 11), fill=NAVY)
fa = font(SANS, 10)
col_w = also_w / 2
for idx, item in enumerate(ALSO):
    col = idx // 9
    row = idx % 9
    x0 = also_x + col * col_w
    y0 = my + 24 + row * 17
    t = fit_font(d, item, SANS, 10, col_w - 12, 8)
    d.text((x0, y0), "\u2022 " + item, font=t, fill=INK)

# ---------------------------------------------------------------- DATE CHECK
dy = my + 172 + 3 * 11 + 8
d.rectangle([M, dy, W - M, dy + 78], fill=RED_BG, outline=RED, width=2)
d.text((M + 8, dy + 4), "DATE CHECK — LEFT OUT (NOT 23 NOV)",
       font=font(SANS_B, 11), fill=RED)
fdc = font(SANS, 10)
left_out = ("Democrats reach 258 (22 Nov)  ·  Sparta II fire (22 Nov)  ·  "
            "El Chapo Isidro captured (22 Nov)")
left_out2 = ("EU-Indonesia pact (21 Nov)  ·  Nigeria boat (21 Nov)  ·  "
             "ICJ Myanmar ruling (19 Nov)")
d.text((M + 8, dy + 22), left_out, font=fdc, fill=INK)
d.text((M + 8, dy + 36), left_out2, font=fdc, fill=INK)
d.text((M + 8, dy + 52), "NOT YET:",
       font=font(SANS_B, 10), fill=RED)
d.text((M + 66, dy + 52),
       "Dymer search continues (14 missing)  ·  4 House races uncalled  ·  "
       "COP32 venue not set  ·  WHO evacuating trapped Ebola staff",
       font=fdc, fill=INK)

# ---------------------------------------------------------------- footer
fy = dy + 78 + 8
d.line([M, fy, W - M, fy], fill=GOLD, width=2)
ff = font(SANS, 9)
d.text((M, fy + 6),
       "SOURCES: REUTERS · AP · BLOOMBERG · LOWY INSTITUTE · ESPN",
       font=ff, fill=GREY)
d.text((M, fy + 18),
       "REPORTED = confirmed by wires   ·   CLAIM = one side's claim, "
       "unverified", font=ff, fill=GREY)
d.text((M, fy + 30),
       "THE WORLD TODAY  ·  Monday 23 November 2026  ·  31 stories  ·  "
       "6 regions", font=font(SANS_B, 10), fill=NAVY)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.save(out, optimize=True)
print("saved", out, os.path.getsize(out), "bytes")
