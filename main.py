#!/usr/bin/env python3
"""News24 v3.1 — one-page newspaper image of Tuesday 24 November 2026.

Stdlib only. Draws a 1024x1024 PNG with a pure-Python raster canvas:
a 5x7 bitmap font, a dotted world map from coarse continent outlines,
30 numbered stories (10 feature cards + 20 briefs), a UTC rail, a
numbers rail, region tabs and a DATE CHECK. Deterministic: no network,
no randomness, no timestamps, no dict/set iteration order dependence.
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (250, 246, 238)
INK = (24, 24, 22)
RULE = (120, 112, 98)
RED = (178, 34, 28)
BLUE = (38, 70, 110)
GREEN = (46, 110, 62)
AMBER = (150, 104, 20)
PALE = (232, 222, 200)
LANDDOT = (148, 132, 104)
CHIP_CONF = (214, 232, 208)
CHIP_OFF = (246, 224, 178)
CHIP_REP = (210, 222, 236)

# ---------------------------------------------------------------- font 5x7
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '~': ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}
BLANK = ("00000",) * 7


def text_width(s, scale):
    return len(s) * (6 * scale) - scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(s, max_w, scale, max_lines):
    """Wrap and clip to max_lines, adding ... to the last line if cut."""
    lines = wrap_text(s, max_w, scale)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and text_width(lines[-1] + "...", scale) > max_w:
        lines[-1] = lines[-1][:-1]
    lines[-1] = lines[-1] + "..."
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                j = base + (xx - x0) * 3
                self.px[j], self.px[j + 1], self.px[j + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def rect(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.put(xx, yy, c)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.put(xx, yy, c)

    def draw_glyph(self, x, y, ch, scale, c, serif=False):
        g = FONT.get(ch, BLANK)
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    self.fill_rect(x + col * scale, y + r * scale,
                                   scale, scale, c)
                    if serif and scale >= 3 and (r == 0 or r == 6):
                        # tiny foot ticks give the masthead a serif feel
                        self.fill_rect(x + col * scale - 1, y + r * scale,
                                       scale + 2, scale, c)

    def text(self, x, y, s, scale, c, serif=False):
        # Bitmap font is caps-only: normalise everything to capitals so
        # no lowercase letter ever renders blank.
        s = s.upper()
        s = s.replace("\u2019", "'").replace("\u2014", "-").replace("\u2013", "-")
        s = s.replace("\u00b7", "-").replace("\u00e9", "E").replace("\u00e8", "E")
        cx = x
        for ch in s:
            self.draw_glyph(cx, y, ch, scale, c, serif=serif)
            cx += 6 * scale
        return cx

    def text_c(self, x, y, w, s, scale, c):
        """Centered text inside a box of width w starting at x."""
        tw = text_width(s, scale)
        self.text(x + max(0, (w - tw) // 2), y, s, scale, c)


def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- dotted map
# Coarse continent outlines (lat, lon) drawn from memory; point-in-polygon
# rasterisation turns them into the dotted world map. No external data.
CONTINENTS = [
    # North America
    [(70, -168), (70, -140), (68, -125), (60, -125), (58, -110), (55, -95),
     (60, -85), (62, -75), (55, -65), (50, -60), (47, -55), (45, -65),
     (40, -74), (35, -76), (30, -85), (25, -80), (20, -97), (15, -95),
     (15, -85), (10, -83), (8, -78), (15, -90), (20, -105), (25, -112),
     (32, -117), (40, -125), (48, -125), (55, -130), (60, -150), (65, -168)],
    # South America
    [(10, -75), (5, -77), (0, -80), (-5, -81), (-10, -78), (-18, -70),
     (-25, -70), (-35, -72), (-40, -73), (-50, -73), (-55, -68), (-50, -65),
     (-40, -62), (-30, -58), (-20, -48), (-10, -40), (-5, -35), (0, -45),
     (5, -52), (8, -60), (10, -65)],
    # Africa
    [(35, -6), (35, 10), (32, 20), (30, 32), (25, 35), (20, 37), (15, 40),
     (10, 44), (5, 48), (0, 42), (-5, 40), (-10, 40), (-15, 40), (-20, 35),
     (-28, 32), (-35, 20), (-30, 15), (-20, 12), (-15, 12), (-10, 13),
     (-5, 12), (0, 9), (5, 8), (5, -5), (10, -15), (15, -17), (20, -16),
     (28, -15), (32, -10)],
    # Eurasia
    [(70, 30), (70, 60), (70, 100), (70, 140), (70, 170), (65, 180),
     (60, 160), (55, 140), (50, 130), (45, 135), (40, 130), (38, 122),
     (35, 120), (30, 120), (25, 110), (20, 108), (15, 105), (10, 105),
     (8, 100), (5, 100), (5, 95), (10, 92), (15, 90), (20, 88), (22, 85),
     (25, 80), (20, 75), (15, 75), (10, 77), (8, 76), (12, 72), (18, 70),
     (23, 68), (25, 60), (28, 55), (30, 50), (30, 48), (28, 48), (25, 52),
     (25, 58), (22, 60), (18, 58), (15, 55), (12, 45), (12, 42), (15, 40),
     (18, 38), (20, 38), (25, 35), (28, 33), (30, 35), (32, 36), (36, 36),
     (38, 30), (40, 28), (42, 25), (45, 28), (48, 25), (50, 28), (55, 25),
     (60, 28), (65, 30), (68, 25)],
    # Britain
    [(58, -5), (55, -3), (52, -3), (50, 0), (53, 0), (56, -2)],
    # Australia
    [(-12, 130), (-12, 140), (-15, 145), (-20, 148), (-25, 153), (-30, 153),
     (-35, 150), (-38, 145), (-38, 140), (-35, 135), (-32, 130), (-30, 125),
     (-25, 118), (-20, 115), (-15, 120), (-12, 125)],
    # New Zealand
    [(-35, 174), (-38, 177), (-41, 175), (-44, 170), (-46, 168), (-42, 172),
     (-38, 176)],
    # Japan
    [(45, 142), (42, 144), (40, 140), (36, 140), (34, 137), (32, 130),
     (30, 130), (33, 132), (36, 136), (40, 141)],
    # Indonesia / SE Asia islands (coarse)
    [(-5, 95), (-5, 105), (0, 110), (-5, 115), (-8, 115), (-10, 120),
     (-8, 125), (-5, 130), (0, 130), (-2, 135), (-5, 140), (-8, 138),
     (-5, 132), (0, 125), (2, 120), (5, 115), (0, 110)],
    # Madagascar
    [(-12, 49), (-16, 50), (-20, 48), (-25, 45), (-22, 43), (-16, 44),
     (-12, 48)],
]


def _inside(lat, lon, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        la1, lo1 = poly[i]
        la2, lo2 = poly[(i + 1) % n]
        if (lo1 > lon) != (lo2 > lon):
            x = la1 + (lon - lo1) * (la2 - la1) / (lo2 - lo1)
            if lat < x:
                inside = not inside
    return inside


def draw_dot_map(cv, x0, y0, w, h):
    """Equirectangular dotted land map; step 2 cells, 2px dots."""
    # graticule every 30 degrees, pale
    for lon in range(-180, 181, 30):
        gx = x0 + int((lon + 180) / 360.0 * w)
        cv.vline(gx, y0, h, (222, 214, 198), 1)
    for lat in range(-60, 91, 30):
        gy = y0 + int((90 - lat) / 180.0 * h)
        cv.hline(x0, gy, w, (222, 214, 198), 1)
    for cy in range(0, 90, 2):
        lat = 89 - cy
        for cx in range(0, 180, 2):
            lon = -179 + cx
            on_land = False
            for poly in CONTINENTS:
                if _inside(lat, lon, poly):
                    on_land = True
                    break
            if on_land:
                px = x0 + cx * w // 180
                py = y0 + cy * h // 90
                cv.fill_rect(px, py, 2, 2, LANDDOT)


def project(x0, y0, w, h, lat, lon):
    return (x0 + int((lon + 180) / 360.0 * w),
            y0 + int((90 - lat) / 180.0 * h))


CHIP_FILL = {"CONFIRMED": CHIP_CONF, "OFFICIALS SAY": CHIP_OFF,
             "REPORTED": CHIP_REP}
CHIP_INK = {"CONFIRMED": GREEN, "OFFICIALS SAY": AMBER, "REPORTED": BLUE}


def draw_chip(cv, x, y, label):
    """Small chip, scale-1 text; returns width used."""
    tw = text_width(label, 1) + 8
    cv.fill_rect(x, y, tw, 12, CHIP_FILL[label])
    cv.rect(x, y, tw, 12, CHIP_INK[label], 1)
    cv.text(x + 4, y + 3, label, 1, CHIP_INK[label])
    return tw


# ---------------------------------------------------------------- the 30 stories
# (num, region, headline, body, chip, sources)
FEATURES = [
    (1, "MIDDLE EAST", "HAMAS SECURITY CHIEF KILLED",
     "Gaza City strike kills Naim Abu Nahal, Hamas security chief.",
     "CONFIRMED", "Reuters / Jerusalem Post"),
    (2, "ASIA", "HUANG'S RETURN LIFTS ASIA",
     "Taiex +8.99% to 40,122.35; Kospi +6.32%; Nikkei +3.91%.",
     "CONFIRMED", "Focus Taiwan / Independent"),
    (3, "MIDDLE EAST", "RIAL HITS RECORD LOW",
     "Rate ~2.83M rials per $1; US sanctioned 22 entities Mon.",
     "CONFIRMED", "Iran Intl / Anadolu"),
    (4, "ASIA", "GAS BLAST AT HANOI EATERY KILLS 6",
     "Hotpot blast in Dong Da; 6 dead, 10 in ICU.",
     "OFFICIALS SAY", "AP / Tuoi Tre"),
    (5, "AFRICA", "GAVI LOCKS IN 1.5M EBOLA DOSES",
     "Up to 1.5M Ebola doses, pending trials.",
     "CONFIRMED", "Gavi / Reuters"),
    (6, "OCEANIA", "SOLOMONS TO END CHINA PACT",
     "No renewal of 2022 pact; PM Wale in Canberra Tue.",
     "REPORTED", "Reuters / ABC"),
    (7, "EUROPE", "ZAPORIZHZHIA STRIKE KILLS 2",
     "2 dead, 22 hurt at first; later 40-44.",
     "REPORTED", "Reuters / Ukrainska Pravda"),
    (8, "ASIA", "NEPAL-TIBET QUAKE M5.6",
     "Epicentre Olangchung Gola; felt in Sikkim, Bengal.",
     "CONFIRMED", "Kathmandu Post / Himalayan"),
    (9, "EUROPE", "POPE DIARY: VISIONS OF DEVIL",
     "'Private Diary' out Tue; 5 languages, 94 countries.",
     "CONFIRMED", "AP / Reuters"),
    (10, "EUROPE", "MAGYAR MEETS ZELENSKYY IN UZHHOROD",
     "First official visit; 1bn hryvnias (~$22.2M) in aid.",
     "CONFIRMED", "Reuters / Liga.net"),
]

BRIEFS = [
    (11, "MIDDLE EAST", "KHAN YOUNIS STRIKE KILLS 3",
     "3 dead, 5 wounded near police post", "REPORTED"),
    (12, "MIDDLE EAST", "ISRAELI STRIKES IN S. LEBANON",
     "Touline, Qabrikha hit, outside zone", "REPORTED"),
    (13, "MIDDLE EAST", "BAGHDAD SEIZES KURDISH OIL",
     "Federal control of Kirkuk fields", "CONFIRMED"),
    (14, "ASIA", "SEOUL SUMMONS RUSSIAN ATTACHE",
     "~5 warplanes in KADIZ; F-15Ks out", "CONFIRMED"),
    (15, "ASIA", "KIM YO-JONG THREATENS SWISS",
     "Swiss sanctions called 'hostile'", "CONFIRMED"),
    (16, "ASIA", "SHENZHOU-24 CREW NAMED",
     "First foreign astronaut: Zeeshan Ali", "CONFIRMED"),
    (17, "ASIA", "BJP-SAD PACT FOR PUNJAB",
     "Alliance revived; SAD gets CM post", "CONFIRMED"),
    (18, "AMERICAS", "VENEZUELA DEBT: $237.5BN",
     "Debt ~242% of GDP; restructuring", "CONFIRMED"),
    (19, "EUROPE", "US HOLDS +6 PATRIOTS FOR UKRAINE",
     "Hegseth has not approved +60", "REPORTED"),
    (20, "EUROPE", "NORWAY EXPANDS DESNA AIR DEFENCE",
     "Anti-drone system grows; Oslo talks", "CONFIRMED"),
    (21, "EUROPE", "EVS 29.8% OF EU SALES",
     "279,799 BEVs of 939,447 in October", "CONFIRMED"),
    (22, "MIDDLE EAST", "HOUTHIS HIT RIYADH TOWER",
     "11 hurt; PIF tower in KAFD hit", "CONFIRMED"),
    (23, "GLOBAL", "EU SEEKS COP REFORM",
     "UN consensus model to be reworked", "CONFIRMED"),
    (24, "GLOBAL", "LANDMINE CASUALTIES: 6,929",
     "2025 five-year high; Myanmar 1,891", "CONFIRMED"),
    (25, "GLOBAL", "47,000 WOMEN KILLED BY KIN",
     "129 a day in 2025; 60% of 78,000", "CONFIRMED"),
    (26, "AFRICA", "SENEGAL GET AFCON TITLE BACK",
     "CAS upholds appeal; Morocco to fight", "CONFIRMED"),
    (27, "AFRICA", "SOUTH SUDAN REGISTERS PRISONERS",
     "Voter sign-up at Juba prison; >1M in", "CONFIRMED"),
    (28, "AMERICAS", "MEXICO CPI 3.96%",
     "First-half Nov inflation; core 3.68%", "CONFIRMED"),
    (29, "AMERICAS", "CARTAGENA SUPERMARKET HOSTAGES",
     "~25 held at Exito after robbery fails", "CONFIRMED"),
    (30, "OCEANIA", "AUSTRALIA: 5% TECH FINES",
     "Duty of care: fines to 5% of revenue", "CONFIRMED"),
]

UTC_RAIL = [
    ("~OVERNIGHT", "Zaporizhzhia strike"),
    ("~01:00", "Hanoi blast"),
    ("~01:30", "Nepal quake"),
    ("05:30-06:30", "Asian closes"),
    ("~10:40", "Gaza strike"),
    ("~12:00", "Mexico CPI"),
]

NUMBERS = [
    ("+8.99%", "TAIEX"),
    ("+6.32%", "KOSPI"),
    ("~2.83M", "RIALS / $"),
    ("1.5M", "EBOLA DOSES"),
    ("6,929", "MINE CASUALTIES"),
    ("47,000", "WOMEN KILLED"),
]

TABS = [("MIDDLE EAST", 6), ("ASIA", 7), ("EUROPE", 6), ("AFRICA", 3),
        ("AMERICAS", 3), ("OCEANIA", 2), ("GLOBAL", 3)]

DATE_BEFORE = [
    "MON 23 TRUMP: CONVINCED NVIDIA BOARD",
    "MON 23 HUANG REINSTATED; NVIDIA +31.5%",
    "MON 23 US SANCTIONS: 22 ENTITIES + 8",
    "MON 23 IRGC: 3 TANKERS 'HIT MINES'",
    "MON 23 BELGIAN ATC STRIKE NOTICE",
    "MON 23 SOMALIA-UGANDA COMMUNIQUE",
    "SAT 21-23 NIGERIA: NIGER, DELTA",
    "SAT 23 WFP WARNING TO THE UNSC",
    "MON 23 BRAZIL FISCAL PACKAGE PASSES",
    "MON 23 VILLAVICENCIO CAR BOMB",
    "SUN 22 COP31 COLLAPSE",
    "SAT 14 S. SUDAN VOTER REG. BEGAN",
]

DATE_NOTYET = [
    "WED 25 SHENZHOU-24 LAUNCH",
    "WED 25 SOLOMON-AUSTRALIA TREATY",
    "WED 25 PHALA PHALA JUDGMENT",
    "WED 25 AUSTRALIAN SENATE VOTE",
]

PINS = {
    1: (31.50, 34.47), 2: (25.03, 121.57), 3: (35.69, 51.39),
    4: (21.03, 105.85), 5: (1.56, 30.25), 6: (-9.43, 159.95),
    7: (47.84, 35.14), 8: (27.35, 87.67), 9: (41.90, 12.45),
    10: (48.62, 22.30), 11: (31.35, 34.30), 12: (33.22, 35.45),
    13: (35.47, 44.39), 14: (37.48, 130.90), 15: (39.03, 125.75),
    16: (40.96, 100.29), 17: (28.61, 77.21), 18: (10.49, -66.88),
    19: (50.45, 30.52), 20: (59.91, 10.75), 21: (50.85, 4.35),
    22: (24.76, 46.64), 23: (50.85, 4.35), 26: (14.72, -17.47),
    27: (4.85, 31.58), 28: (19.43, -99.13), 29: (10.39, -75.51),
    30: (-35.28, 149.13),
}
# Pin label offsets (dx, dy) for crowded spots: 19 Kyiv, 21/23 Brussels.
PIN_OFF = {19: (8, -14), 21: (-30, -12), 23: (10, 8), 9: (6, -12),
           10: (8, -12), 2: (6, 8), 14: (6, -12), 30: (-34, 6)}


# ---------------------------------------------------------------- layout
def draw_feature(cv, x, y, w, h, story, head_scale):
    num, region, headline, body, chip, src = story
    cv.fill_rect(x, y, w, h, PAPER)
    cv.rect(x, y, w, h, RULE, 1)
    cv.circle(x + 15, y + 15, 10, RED, fill=True)
    ns = str(num)
    cv.text(x + 15 - text_width(ns, 1) // 2, y + 12, ns, 1, (255, 255, 255))
    cv.text(x + 30, y + 10, region, 1, RED)
    cw = draw_chip(cv, x + w - 8 - (text_width(chip, 1) + 8), y + 8, chip)
    hl = fit_lines(headline, w - 16, head_scale, 3)
    yy = y + 30
    for ln in hl:
        cv.text(x + 8, yy, ln, head_scale, INK)
        yy += 8 * head_scale
    bl = fit_lines(body, w - 16, 2, 4)
    for ln in bl:
        cv.text(x + 8, yy, ln, 2, (52, 48, 40))
        yy += 15
    cv.text(x + 8, y + h - 13, src, 1, RULE)


def draw_brief(cv, x, y, w, item):
    num, region, headline, body, chip = item
    cv.fill_rect(x, y, 7, 7, CHIP_FILL[chip])
    cv.rect(x, y, 7, 7, CHIP_INK[chip], 1)
    head = "%d. %s" % (num, headline)
    hl = fit_lines(head, w - 12, 1, 1)
    cv.text(x + 11, y, hl[0] if hl else "", 1, INK)
    bl = fit_lines(body, w - 12, 1, 1)
    cv.text(x + 11, y + 9, bl[0] if bl else "", 1, (90, 84, 70))


def build():
    cv = Canvas(W, H, PAPER)
    # strap
    cv.text(24, 8, "THE WORLD TODAY", 2, INK)
    rt = "WORLD EDITION"
    cv.text(W - 24 - text_width(rt, 2), 8, rt, 2, INK)
    cv.hline(24, 28, W - 48, INK, 2)
    # masthead: giant serif date, one line, scale 7
    mast = "TUESDAY 24 NOVEMBER 2026"
    cv.text(8, 38, mast, 7, INK, serif=True)
    cv.hline(24, 100, W - 48, INK, 3)
    cv.hline(24, 106, W - 48, INK, 1)
    # promise line
    promise = "30 STORIES - 7 REGIONS - ALL FROM TUESDAY 24 NOVEMBER 2026"
    cv.text_c(0, 114, W, promise, 2, INK)
    # UTC rail
    cv.text(24, 136, "THE DAY IN UTC", 1, RULE)
    for i, (t, lab) in enumerate(UTC_RAIL):
        nx = 150 + i * 145
        cv.text(nx, 132, t, 2, RED)
        cv.text(nx, 148, lab, 1, INK)
    cv.hline(24, 160, W - 48, RULE, 1)
    # numbers rail
    for i, (val, lab) in enumerate(NUMBERS):
        bx = 24 + i * 163
        cv.fill_rect(bx, 166, 157, 34, PALE)
        cv.rect(bx, 166, 157, 34, RULE, 1)
        cv.text_c(bx, 170, 157, val, 3, INK)
        cv.text_c(bx, 192, 157, lab, 1, RULE)
    # region tabs
    tx = 24
    for name, n in TABS:
        label = "%s %d" % (name, n)
        tw = text_width(label, 1) + 16
        cv.fill_rect(tx, 210, tw, 16, (238, 232, 218))
        cv.rect(tx, 210, tw, 16, RULE, 1)
        cv.text(tx + 8, 215, label, 1, INK)
        tx += tw + 6
    cv.hline(24, 232, W - 48, RULE, 1)
    # feature grid
    row_a = [(24, 240), (266, 240), (508, 240)]
    for (fx, fy), st in zip(row_a, FEATURES[0:3]):
        draw_feature(cv, fx, fy, 232, 178, st, 3)
    row_b = [(24, 426), (205, 426), (386, 426), (567, 426)]
    for (fx, fy), st in zip(row_b, FEATURES[3:7]):
        draw_feature(cv, fx, fy, 172, 152, st, 2)
    row_c = [(24, 586), (266, 586), (508, 586)]
    for (fx, fy), st in zip(row_c, FEATURES[7:10]):
        draw_feature(cv, fx, fy, 232, 176, st, 3)
    # right rail: map + legends
    cv.text(756, 240, "WHERE IT HAPPENED", 2, INK)
    draw_dot_map(cv, 756, 262, 244, 150)
    cv.rect(756, 262, 244, 150, RULE, 1)
    for num, (lat, lon) in sorted(PINS.items()):
        px, py = project(756, 262, 244, 150, lat, lon)
        cv.circle(px, py, 6, RED, fill=True)
        dx, dy = PIN_OFF.get(num, (7, -4))
        cv.text(px + dx, py + dy, str(num), 1, RED)
    ly = 424
    cv.text(756, ly, "REGIONS", 1, RULE)
    for i, (name, n) in enumerate(TABS):
        cv.text(756, ly + 12 + i * 11, "%s %d" % (name, n), 1, INK)
    cy = 516
    cv.text(756, cy, "HOW TO READ THE CHIPS", 1, RULE)
    for j, lab in enumerate(("CONFIRMED", "OFFICIALS SAY", "REPORTED")):
        draw_chip(cv, 756, cy + 12 + j * 16, lab)
    hy = 580
    cv.text(756, hy, "HOW TO READ", 1, RULE)
    howto = [
        "Stories are numbered 1-30.",
        "The same number marks the",
        "story, its map pin and its",
        "place in ALSO ON.",
        "CONFIRMED: officially",
        "confirmed. REPORTED:",
        "press reports, not yet",
        "confirmed. OFFICIALS SAY:",
        "police or officials cited.",
        "Everything numbered is",
        "from Tuesday 24 Nov 2026.",
        "Earlier and later events",
        "appear only in DATE CHECK.",
    ]
    for i, ln in enumerate(howto):
        cv.text(756, hy + 12 + i * 11, ln, 1, (52, 48, 40))
    # bottom bar: ALSO ON + DATE CHECK
    cv.hline(24, 770, W - 48, INK, 2)
    cv.text(24, 780, "ALSO ON", 2, INK)
    for k, item in enumerate(BRIEFS):
        col = 0 if k < 10 else 1
        row = k % 10
        bx = 24 + col * 244
        draw_brief(cv, bx, 800 + row * 17, 232, item)
    cv.vline(508, 776, 176, RULE, 1)
    cv.text(524, 780, "DATE CHECK", 2, INK)
    cv.text(524, 800, "BEFORE TUESDAY", 1, RED)
    for i, ln in enumerate(DATE_BEFORE):
        col = 0 if i < 6 else 1
        row = i % 6
        bx = 524 + col * 238
        cv.text(bx, 812 + row * 11, fit_lines(ln, 232, 1, 1)[0], 1, INK)
    cv.text(524, 886, "NOT YET", 1, RED)
    for i, ln in enumerate(DATE_NOTYET):
        col = 0 if i < 2 else 1
        row = i % 2
        bx = 524 + col * 238
        cv.text(bx, 898 + row * 11, fit_lines(ln, 232, 1, 1)[0], 1, INK)
    # footer
    cv.hline(24, 962, W - 48, INK, 2)
    cv.text(24, 972, "Sources: Reuters, AP, AFP, Yonhap, BBC Sport, UN News, Gavi, ACEA and others.", 1, RULE)
    cv.text(24, 986, "ALL EVENTS TUE 24 NOV 2026 EXCEPT AS NOTED IN DATE CHECK. DRAWN FROM CODE, NO NETWORK.", 1, RULE)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(cv, path)
    print("wrote %s (%d bytes, %dx%d)" % (path, size, W, H))


if __name__ == "__main__":
    main()
