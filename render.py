#!/usr/bin/env python3
"""Render the news-image-20261119 front page (1024x1024 PNG).

Original work for make.fun competition news-image-20261119. Draws a newspaper
front page in code with PIL: date masthead, region/field count bars, day-in-
numbers strip, 3 illustrated leads, 10 illustrated mid cards, a world map with
numbered pins, and numbered one-line briefs. Every story was checked against
reporting published on Thursday 19 November 2026; stories first reported on
18 November are named in the DATE CHECK line instead of being shown as news.
Deterministic: no network, no randomness, no clock reads.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 241, 227)
PAPER = (250, 246, 236)
INK = (26, 26, 26)
RED = (158, 28, 28)
DARKRED = (120, 20, 20)
GREY = (90, 84, 74)
LIGHT = (233, 226, 210)
RULE = (26, 26, 26)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_O = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap to pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines):
    """Wrap text, truncating with an ellipsis if it exceeds max_lines."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    return lines


# ---------------------------------------------------------------- stories
# n, region, field, place, headline, deck, illustration key, (lat, lon) or None
LEADS = [
    (1, "ASIA", "Politics & diplomacy", "SHENZHEN",
     "Trump, Xi and Putin meet in Shenzhen",
     "First-ever trilateral of the three nuclear powers; nuclear arms on the agenda, and a Trump-Putin bilateral after the plenary.",
     "summit", (22.5, 114.0)),
    (2, "WORLD", "Culture & games", "WORLDWIDE",
     "GTA VI goes on sale at midnight",
     "Thirteen years after GTA V, the rollout runs west by time zone; New Zealand plays first, the US at midnight tonight.",
     "gta", (-41.3, 174.8)),
    (3, "ASIA", "Disasters & weather", "BAY OF BENGAL",
     "Cyclone Akvan bears down on India's east coast",
     "Severe storm due ashore at noon on Friday; 47,000 evacuated in Odisha and schools shut across the coast.",
     "cyclone", (17.0, 84.0)),
]

MIDS = [
    (4, "EUROPE", "Politics & diplomacy", "BERLIN",
     "Coalition of the Willing meets in Berlin",
     "Merz hosts Macron and Burnham for Ukraine guarantees.",
     "berlin", (52.5, 13.4)),
    (5, "MIDDLE EAST", "War & security", "GAZA",
     "IDF pushes into central Gaza despite ceasefire",
     "First ground push since the truce; Gaza rebuilding stalled.",
     "gaza", (31.5, 34.5)),
    (6, "WORLD", "Society", "WORLDWIDE",
     "Pew: Islam set to be the largest faith by 2035",
     "Muslims set to outnumber Christians within a decade.",
     "pew", (0.0, 0.0)),
    (7, "AMERICAS", "Politics & diplomacy", "WASHINGTON",
     "Democrats count biggest Senate gains in 70 years",
     "Midterm haul gives the party a 56-44 Senate majority.",
     "capitol", (38.9, -77.0)),
    (8, "AMERICAS", "Economy", "WASHINGTON",
     "Fed minutes point to more rate rises",
     "Most officials expect further hikes if inflation stays hot.",
     "chart", (38.9, -77.0)),
    (9, "AMERICAS", "Technology", "SANTA CLARA",
     "Nvidia's acting chief promises earlier pay rises",
     "Kress: raises come in December, months earlier than planned.",
     "chip", (37.4, -122.0)),
    (10, "OCEANIA", "Politics & diplomacy", "CANBERRA",
     "Australia sanctions Israeli settlers",
     "Wong targets West Bank expansion; four groups listed.",
     "scales", (-35.3, 149.1)),
    (11, "WORLD", "Science & space", "DEEP SPACE",
     "NASA briefs on Voyager 1's one-light-day mark",
     "1977 probe nears 25.9bn km; a signal sent today arrives tomorrow.",
     "voyager", (70.0, 0.0)),
    (12, "ASIA", "Politics & diplomacy", "TOKYO",
     "India and Japan review defence ties",
     "Rajnath and Jaishankar in Tokyo to deepen security links.",
     "flags", (35.7, 139.7)),
    (13, "WORLD", "Science & space", "WORLDWIDE",
     "Earth is missing a billion years of history",
     "Scientists say they may have found why the record has a gap.",
     "earth", (-10.0, -20.0)),
]

# n, region, field, place, one-line brief
BRIEFS = [
    (14, "AMERICAS", "War & security", "US", "Senators warn AI cyber threats are outpacing defences."),
    (15, "AMERICAS", "Politics & diplomacy", "CANADA", "Carney adjusts China ties, aims for the right deal with US."),
    (16, "MIDDLE EAST", "War & security", "SAUDI ARABIA", "Danger has passed in three southern cities after alerts."),
    (17, "AFRICA", "Justice", "LIBYA", "Cocaine and millions of pills seized in the east."),
    (18, "AMERICAS", "Justice", "US", "Tougher rules proposed for employment-based green cards."),
    (19, "EUROPE", "Justice", "UK", "McDonald's sex-abuse case can go ahead, judge rules."),
    (20, "EUROPE", "Justice", "UK", "Report finds Lynch superyacht had unknown vulnerability to high winds."),
    (21, "AFRICA", "War & security", "SOMALIA", "Accuses UAE of secretly building military bases."),
    (22, "EUROPE", "Economy", "FINANCE", "Deutsche Bank handled $582m in Epstein-linked deals, FT reports."),
    (23, "AMERICAS", "War & security", "US", "NSA's classified internal network suffers outage, reports say."),
    (24, "MIDDLE EAST", "Politics & diplomacy", "GAZA", "Peace Council warns Gaza reconstruction is stalled."),
    (25, "ASIA", "Society", "INDIA", "Modi meets Prince and Princess of Wales on UK-India ties."),
    (26, "OCEANIA", "Sport", "SPORT", "Duckett hits 133 as England press Australia in third ODI."),
    (27, "AMERICAS", "Justice", "US", "Susan Smith parole hearing held as ex-husband fights release."),
    (28, "ASIA", "Society", "INDIA", "Firms give staff a day off to play GTA VI."),
    (29, "ASIA", "War & security", "CHINA", "Security tight around the Shenzhen summit venue."),
    (30, "EUROPE", "War & security", "RUSSIA", "Accuses Europe of imposing conditions on Ukraine peace talks."),
    (31, "EUROPE", "War & security", "BLACK SEA", "LPG tanker that sank off Bulgaria was hit by projectiles."),
    (32, "ASIA", "Disasters & weather", "INDIA", "Odisha shuts schools in six districts as Akvan nears."),
    (33, "WORLD", "Economy", "MARKETS", "Oil falls as Middle East news lifts risk aversion."),
    (34, "AMERICAS", "Technology", "TECH", "Microsoft reportedly in talks to sell AI services to ByteDance."),
    (35, "AMERICAS", "War & security", "US", "Report says Trump unhappy Vance did not back Iran war."),
    (36, "ASIA", "War & security", "TAIWAN", "Draft law adds transnational repression crime."),
    (37, "AMERICAS", "Justice", "US CONGRESS", "Liu Yunping elected caucus chair, first Taiwanese American."),
    (38, "WORLD", "Health", "HEALTH", "Merck launches self-amplifying mRNA rabies vaccine for pets."),
    (39, "ASIA", "Society", "CHINA", "Electric micro-vehicles spread through cities."),
    (40, "ASIA", "Society", "INDIA", "Reporters hit back at Delhi Police affidavit to top court."),
    (41, "ASIA", "Sport", "SPORT", "India forms 14-member panel to shape professional leagues."),
    (42, "AMERICAS", "Politics & diplomacy", "CANADA", "Carney meets Pacific leaders on APEC sidelines."),
    (43, "ASIA", "Politics & diplomacy", "APEC", "Leaders back openness, innovation and cooperation."),
    (44, "ASIA", "Politics & diplomacy", "SHENZHEN", "APEC family photo and leaders' meeting held on day two."),
]

NUMBERS = [
    ("47,000", "evacuated in Odisha"),
    ("25.9bn km", "Voyager 1 out"),
    ("13 years", "since GTA V"),
    ("90-100 km/h", "Akvan winds"),
    ("56-44", "Senate split"),
    ("3", "nuclear powers meet"),
]

DATE_CHECK = ("Left out on purpose because first reported on 18 Nov, not today: "
              "Jeffries nominated House speaker 251-11; Peltola wins Alaska Senate; "
              "EU proposes \u20ac45bn Ukraine loan; Anthropic IPO raises $81.3bn; "
              "Myanmar genocide verdict at UN court; Kerch bridge span collapse; "
              "Nvidia's $115.8bn quarter.")

FOOTER = ("Every story here happened, or was first reported, on Thursday 19 November 2026. "
          "Contested claims are attributed. Sources: Reuters, AP, AFP, BBC, The Hindu, IMD, "
          "NASA, Pew Research, NDTV. Original drawings.")


# ---------------------------------------------------------------- helpers
REGION_COLORS = {
    "EUROPE": (47, 85, 151), "MIDDLE EAST": (176, 92, 20), "ASIA": (122, 54, 132),
    "AFRICA": (46, 125, 72), "AMERICAS": (158, 28, 28), "OCEANIA": (32, 120, 122),
    "WORLD": (70, 70, 70),
}
REGION_ORDER = ["EUROPE", "MIDDLE EAST", "ASIA", "AFRICA", "AMERICAS", "OCEANIA", "WORLD"]


def all_stories():
    return LEADS + MIDS + [(n, r, f, p, b, "", "", None) for (n, r, f, p, b) in BRIEFS]


def region_counts():
    counts = {r: 0 for r in REGION_ORDER}
    for s in all_stories():
        counts[s[1]] += 1
    return counts


def field_counts():
    counts = {}
    for s in all_stories():
        counts[s[2]] = counts.get(s[2], 0) + 1
    return counts


def sky(d, box, top, bottom):
    d.rectangle(box, fill=top)
    x0, y0, x1, y1 = box
    steps = max(1, y1 - y0)
    for i in range(steps):
        t = i / steps
        c = tuple(int(top[j] + (bottom[j] - top[j]) * t) for j in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def flag(d, x, y, w, h, colors, horizontal=True):
    """Tiny striped flag on a pole at (x, y) top-left of the cloth."""
    d.line([(x, y), (x, y + h + 14)], fill=INK, width=2)
    n = len(colors)
    for i, c in enumerate(colors):
        if horizontal:
            d.rectangle([x + 2, y + i * h // n, x + 2 + w, y + (i + 1) * h // n], fill=c)
        else:
            d.rectangle([x + 2 + i * w // n, y, x + 2 + (i + 1) * w // n, y + h], fill=c)
    d.rectangle([x + 2, y, x + 2 + w, y + h], outline=INK)


def draw_illustration(key, size):
    """Flat vector-style scene for one story. Drawn at a fixed reference size
    then resized to the target box, so lead and mid cards share the same art."""
    tw, th = int(size[0]), int(size[1])
    w, h = 320, 110
    img = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(img)
    if key == "summit":
        sky(d, (0, 0, w, h), (168, 196, 222), (226, 232, 238))
        d.rectangle([0, h - 26, w, h], fill=(120, 122, 110))
        for bx, bw, bh in [(6, 34, 52), (46, 26, 70), (78, 40, 44), (124, 30, 62), (160, 34, 48), (200, 28, 58), (234, 36, 40), (276, 30, 54)]:
            d.rectangle([bx, h - 26 - bh, bx + bw, h - 26], fill=(88, 96, 110))
            for wy in range(h - 26 - bh + 6, h - 30, 10):
                for wx in range(bx + 4, bx + bw - 4, 9):
                    d.rectangle([wx, wy, wx + 5, wy + 5], fill=(240, 220, 130))
        d.ellipse([w - 52, 8, w - 18, 42], fill=(242, 214, 120))
        # US flag: horizontal red/white stripes with a blue canton
        fx, fy, fw, fh = 20, h - 78, 30, 20
        d.line([(fx, fy), (fx, fy + fh + 14)], fill=INK, width=2)
        for i in range(7):
            c = (178, 34, 34) if i % 2 == 0 else (255, 255, 255)
            d.rectangle([fx + 2, fy + i * fh // 7, fx + 2 + fw, fy + (i + 1) * fh // 7], fill=c)
        d.rectangle([fx + 2, fy, fx + 2 + 12, fy + 10], fill=(47, 85, 151))
        d.rectangle([fx + 2, fy, fx + 2 + fw, fy + fh], outline=INK)
        flag(d, 58, h - 78, 30, 20, [(222, 41, 16), (255, 222, 0)], horizontal=True)
        flag(d, 96, h - 78, 30, 20, [(255, 255, 255), (0, 57, 166), (213, 0, 50)], horizontal=True)
        # long table with a white cloth, three chairs behind it
        d.rectangle([w // 2 - 58, h - 46, w // 2 + 58, h - 28], fill=(245, 245, 240), outline=(90, 80, 70))
        d.rectangle([w // 2 - 58, h - 46, w // 2 + 58, h - 42], fill=(140, 100, 60))
        for cx in (w // 2 - 25, w // 2 + 5, w // 2 + 35):
            d.rectangle([cx - 8, h - 62, cx + 8, h - 46], fill=(60, 60, 66))
    elif key == "gta":
        d.rectangle([0, 0, w, h], fill=(18, 22, 44))
        for sx, sy, sr in [(20, 14, 2), (70, 8, 1), (120, 20, 2), (180, 10, 1), (240, 16, 2), (290, 8, 1), (40, 34, 1), (150, 30, 1), (220, 34, 2), (270, 26, 1)]:
            d.ellipse([sx, sy, sx + sr * 2, sy + sr * 2], fill=(255, 255, 255))
        d.ellipse([w - 62, 6, w - 22, 46], fill=(240, 238, 210))
        for bx, bw, bh in [(4, 30, 46), (38, 24, 64), (66, 34, 40), (104, 26, 72), (134, 32, 50), (170, 24, 66), (198, 34, 44), (236, 26, 58), (266, 30, 48), (300, 22, 60)]:
            d.rectangle([bx, h - 34 - bh, bx + bw, h - 34], fill=(40, 46, 78))
            for wy in range(h - 34 - bh + 6, h - 38, 11):
                for wx in range(bx + 4, bx + bw - 4, 10):
                    d.rectangle([wx, wy, wx + 5, wy + 6], fill=(250, 210, 90))
        d.rectangle([0, h - 34, w, h], fill=(10, 12, 26))
        d.rounded_rectangle([w // 2 - 52, h - 30, w // 2 + 52, h - 6], radius=8, fill=(60, 60, 66), outline=(200, 200, 200))
        d.ellipse([w // 2 - 38, h - 24, w // 2 - 22, h - 12], fill=(30, 30, 34), outline=(220, 220, 220))
        d.ellipse([w // 2 + 22, h - 24, w // 2 + 38, h - 12], fill=(30, 30, 34), outline=(220, 220, 220))
        d.text((w // 2 - 8, h - 30), "+", fill=(255, 255, 255), font=font(SANS_B, 12))
        d.text((8, 10), "00:00", fill=(255, 255, 255), font=font(SANS_B, 16))
    elif key == "cyclone":
        sky(d, (0, 0, w, h), (120, 150, 190), (200, 214, 228))
        d.rectangle([0, h - 30, w, h], fill=(44, 92, 130))
        for cx, cy, r, col in [(w // 2, h // 2 - 6, 58, (255, 255, 255)), (w // 2, h // 2 - 6, 44, (210, 226, 240)), (w // 2, h // 2 - 6, 30, (255, 255, 255)), (w // 2, h // 2 - 6, 16, (158, 28, 28))]:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=4)
        d.ellipse([w // 2 - 7, h // 2 - 13, w // 2 + 7, h // 2 + 1], fill=(158, 28, 28))
        for ax, ay in [(w - 60, 12), (w - 90, 26), (24, 18), (52, 8)]:
            d.line([(ax, ay), (ax - 6, ay + 12)], fill=(255, 255, 255), width=2)
            d.line([(ax + 8, ay), (ax + 2, ay + 12)], fill=(255, 255, 255), width=2)
        d.polygon([(14, h - 30), (60, h - 30), (46, h - 64), (30, h - 52)], fill=(120, 150, 90))
        d.polygon([(w - 70, h - 30), (w - 16, h - 30), (w - 30, h - 58), (w - 52, h - 46)], fill=(120, 150, 90))
    elif key == "berlin":
        sky(d, (0, 0, w, h), (190, 205, 220), (232, 236, 240))
        d.rectangle([w // 2 - 62, 30, w // 2 + 62, h - 20], fill=(196, 188, 168))
        d.polygon([(w // 2 - 70, 30), (w // 2 + 70, 30), (w // 2, 10)], fill=(150, 140, 120))
        for i in range(6):
            x = w // 2 - 52 + i * 18
            d.rectangle([x, 48, x + 10, h - 20], fill=(150, 140, 120))
        d.rectangle([w // 2 - 62, h - 20, w // 2 + 62, h - 12], fill=(150, 140, 120))
        flag(d, 14, 26, 26, 17, [(0, 0, 0), (221, 0, 0), (255, 206, 0)], horizontal=True)
        flag(d, w - 44, 26, 26, 17, [(0, 85, 164), (255, 255, 255), (239, 65, 53)], horizontal=False)
        d.rectangle([0, h - 12, w, h], fill=(96, 110, 96))
    elif key == "gaza":
        sky(d, (0, 0, w, h), (214, 226, 214), (240, 240, 228))
        d.rectangle([0, h - 22, w, h], fill=(150, 140, 110))
        d.polygon([(10, h - 22), (w - 10, h - 22), (w - 40, 40), (40, 40)], fill=(226, 220, 200))
        d.line([(w // 2, 40), (w // 2, h - 22)], fill=(158, 28, 28), width=3)
        d.ellipse([w // 2 - 26, 52, w // 2 + 26, 84], fill=(255, 255, 255))
        d.ellipse([w // 2 - 40, 66, w // 2 - 8, 84], fill=(255, 255, 255))
        d.polygon([(w // 2 + 22, 62), (w // 2 + 52, 54), (w // 2 + 24, 72)], fill=(255, 255, 255))
        d.ellipse([w // 2 + 40, 58, w // 2 + 44, 62], fill=(26, 26, 26))
        d.line([(w // 2 - 30, 84), (w // 2 - 52, 96)], fill=(46, 125, 72), width=3)
        d.ellipse([w // 2 - 58, 90, w // 2 - 44, 100], fill=(46, 125, 72))
        d.ellipse([w // 2 - 48, 96, w // 2 - 34, 106], fill=(46, 125, 72))
    elif key == "pew":
        d.rectangle([0, 0, w, h], fill=(238, 232, 214))
        d.ellipse([14, 12, w // 2 + 6, h - 12], fill=(96, 150, 200))
        d.ellipse([30, 26, 70, 48], fill=(120, 170, 110))
        d.ellipse([w // 2 - 30, h - 44, w // 2 + 6, h - 22], fill=(120, 170, 110))
        d.rectangle([w // 2 + 16, h - 52, w // 2 + 46, h - 12], fill=(47, 85, 151))
        d.rectangle([w // 2 + 52, h - 76, w // 2 + 82, h - 12], fill=(158, 28, 28))
        d.rectangle([w // 2 + 88, h - 92, w // 2 + 118, h - 12], fill=(46, 125, 72))
        d.rectangle([w // 2 + 16, h - 12, w // 2 + 118, h - 8], fill=INK)
    elif key == "capitol":
        sky(d, (0, 0, w, h), (168, 196, 222), (232, 238, 242))
        d.rectangle([0, h - 18, w, h], fill=(120, 140, 110))
        d.rectangle([w // 2 - 56, 44, w // 2 + 56, h - 18], fill=(236, 232, 220))
        d.ellipse([w // 2 - 26, 8, w // 2 + 26, 52], fill=(236, 232, 220))
        d.rectangle([w // 2 - 2, 2, w // 2 + 2, 14], fill=(26, 26, 26))
        for i in range(5):
            x = w // 2 - 46 + i * 18
            d.rectangle([x, 60, x + 9, h - 18], fill=(200, 194, 178))
        d.rectangle([w - 62, 12, w - 10, 34], fill=(47, 85, 151))
        d.text((w - 60, 14), "56-44", fill=(255, 255, 255), font=font(SANS_B, 13))
    elif key == "chart":
        d.rectangle([0, 0, w, h], fill=(238, 232, 214))
        d.line([(14, h - 16), (w - 10, h - 16)], fill=INK, width=2)
        d.line([(14, 10), (14, h - 16)], fill=INK, width=2)
        bars = [(26, 34), (58, 52), (90, 44), (122, 70), (154, 62)]
        for bx, bh in bars:
            d.rectangle([bx, h - 16 - bh, bx + 24, h - 16], fill=(158, 28, 28))
        d.line([(14, 30), (w - 12, 14)], fill=(47, 85, 151), width=3)
        d.text((w - 44, 18), "%", fill=(47, 85, 151), font=font(SANS_B, 16))
    elif key == "chip":
        d.rectangle([0, 0, w, h], fill=(238, 232, 214))
        d.rectangle([w // 2 - 34, h // 2 - 34, w // 2 + 34, h // 2 + 34], fill=(26, 26, 26))
        d.rectangle([w // 2 - 20, h // 2 - 20, w // 2 + 20, h // 2 + 20], outline=(120, 200, 120), width=3)
        for i in range(5):
            x = w // 2 - 28 + i * 14
            d.line([(x, h // 2 - 44), (x, h // 2 - 34)], fill=(120, 120, 120), width=3)
            d.line([(x, h // 2 + 34), (x, h // 2 + 44)], fill=(120, 120, 120), width=3)
            y = h // 2 - 28 + i * 14
            d.line([(w // 2 - 44, y), (w // 2 - 34, y)], fill=(120, 120, 120), width=3)
            d.line([(w // 2 + 34, y), (w // 2 + 44, y)], fill=(120, 120, 120), width=3)
        d.polygon([(w - 52, 14), (w - 28, 14), (w - 40, 34)], fill=(46, 125, 72))
    elif key == "scales":
        d.rectangle([0, 0, w, h], fill=(238, 232, 214))
        d.line([(w // 2, 14), (w // 2, h - 14)], fill=INK, width=3)
        d.line([(w // 2 - 44, 24), (w // 2 + 44, 24)], fill=INK, width=3)
        d.ellipse([w // 2 - 6, 10, w // 2 + 6, 22], fill=(200, 170, 60))
        for sx, drop in [(w // 2 - 44, 0), (w // 2 + 44, 6)]:
            d.line([(sx, 24), (sx, 44 + drop)], fill=INK, width=2)
            d.polygon([(sx - 20, 44 + drop), (sx + 20, 44 + drop), (sx, 62 + drop)], fill=(176, 92, 20))
        d.rectangle([w // 2 - 30, h - 14, w // 2 + 30, h - 10], fill=INK)
    elif key == "voyager":
        d.rectangle([0, 0, w, h], fill=(10, 14, 34))
        for sx, sy, sr in [(16, 12, 2), (60, 22, 1), (110, 10, 2), (150, 26, 1), (190, 12, 1), (30, 44, 1), (90, 40, 2), (170, 46, 1), (140, 8, 1)]:
            d.ellipse([sx, sy, sx + sr * 2, sy + sr * 2], fill=(255, 255, 255))
        d.ellipse([16, h - 34, 40, h - 10], fill=(96, 150, 200))
        for i in range(7):
            x = 44 + i * 18
            d.ellipse([x, h - 28 + (i % 2) * 2, x + 3, h - 25 + (i % 2) * 2], fill=(200, 200, 200))
        d.polygon([(150, h // 2 - 10), (176, h // 2 - 4), (176, h // 2 + 8), (150, h // 2 + 2)], fill=(200, 200, 210))
        d.rectangle([132, h // 2 - 8, 152, h // 2 + 6], fill=(150, 150, 160))
        d.line([(132, h // 2 - 2), (112, h // 2 - 16)], fill=(200, 200, 210), width=3)
        d.line([(132, h // 2 + 4), (112, h // 2 + 18)], fill=(200, 200, 210), width=3)
    elif key == "flags":
        sky(d, (0, 0, w, h), (168, 196, 222), (232, 238, 242))
        d.rectangle([0, h - 20, w, h], fill=(140, 130, 110))
        d.polygon([(w // 2 - 60, h - 20), (w // 2 + 60, h - 20), (w // 2 + 30, h - 56), (w // 2 - 30, h - 56)], fill=(178, 34, 34))
        d.rectangle([w // 2 - 14, h - 56, w // 2 + 14, h - 20], fill=(120, 20, 20))
        flag(d, 18, 18, 30, 20, [(255, 153, 51), (255, 255, 255), (19, 136, 8)], horizontal=True)
        flag(d, w - 52, 18, 30, 20, [(255, 255, 255), (188, 0, 45)], horizontal=True)
    elif key == "earth":
        d.rectangle([0, 0, w, h], fill=(238, 232, 214))
        d.ellipse([w // 2 - 44, 8, w // 2 + 44, 96], fill=(96, 150, 200))
        d.ellipse([w // 2 - 30, 22, w // 2 + 4, 46], fill=(120, 170, 110))
        d.ellipse([w // 2 - 6, 52, w // 2 + 34, 78], fill=(120, 170, 110))
        d.ellipse([w // 2 - 44, 8, w // 2 + 44, 96], outline=(26, 26, 26), width=2)
        d.line([(w // 2 - 44, 52), (w // 2 + 44, 52)], fill=(158, 28, 28), width=3)
        d.text((12, h - 20), "1bn yrs missing", fill=(26, 26, 26), font=font(SANS_B, 12))
    if (tw, th) != (w, h):
        return img.resize((tw, th), Image.LANCZOS)
    return img


# Simplified continent outlines in equirectangular (lon, lat) coordinates.
# Each polygon is traced once around its coastline, in order, no jumps.
CONTINENTS = [
    # North America
    [(-168, 66), (-155, 58), (-145, 60), (-135, 58), (-130, 54), (-125, 49), (-124, 42), (-122, 37), (-117, 33), (-112, 29), (-108, 25), (-105, 22), (-97, 26), (-93, 18), (-90, 15), (-87, 13), (-83, 9), (-79, 9), (-80, 8), (-83, 9), (-87, 13), (-90, 14), (-92, 15), (-97, 16), (-102, 18), (-105, 20), (-110, 23), (-114, 28), (-117, 32), (-122, 37), (-124, 43), (-125, 49), (-130, 55), (-140, 60), (-152, 58), (-160, 55), (-165, 60), (-168, 66)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18), (-70, -23), (-70, -33), (-73, -44), (-71, -54), (-66, -55), (-65, -48), (-62, -41), (-58, -34), (-48, -28), (-41, -23), (-35, -9), (-35, -6), (-42, -3), (-50, 0), (-53, 5), (-58, 8), (-62, 10), (-68, 11), (-72, 12), (-76, 10), (-79, 9)],
    # Africa
    [(-17, 15), (-16, 21), (-13, 27), (-10, 31), (-6, 34), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (35, 28), (37, 22), (39, 15), (43, 12), (46, 11), (51, 11), (48, 10), (44, 0), (42, -5), (40, -11), (40, -16), (36, -20), (33, -26), (31, -29), (28, -33), (25, -34), (20, -35), (18, -32), (16, -28), (14, -22), (12, -17), (13, -10), (12, -5), (9, 0), (9, 4), (6, 4), (4, 6), (0, 6), (-3, 5), (-7, 4), (-8, 5), (-12, 8), (-15, 12), (-17, 15)],
    # Eurasia (Europe + Asia + Arabia as one landmass)
    [(-9, 37), (-9, 43), (-2, 48), (-5, 50), (0, 52), (5, 53), (8, 57), (10, 59), (6, 62), (13, 68), (18, 69), (25, 71), (32, 70), (40, 68), (50, 69), (60, 69), (68, 73), (75, 72), (80, 73), (90, 75), (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (158, 69), (162, 66), (170, 66), (178, 65), (178, 64), (170, 60), (162, 60), (158, 53), (150, 60), (142, 59), (142, 55), (140, 50), (141, 45), (138, 39), (135, 35), (130, 32), (127, 34), (122, 38), (120, 35), (121, 31), (120, 27), (116, 23), (110, 21), (108, 18), (105, 10), (103, 8), (100, 7), (98, 10), (95, 15), (92, 21), (89, 22), (86, 20), (82, 17), (80, 13), (77, 8), (75, 10), (73, 16), (70, 21), (66, 25), (62, 25), (58, 25), (57, 26), (54, 27), (51, 28), (49, 30), (48, 30), (44, 29), (40, 30), (36, 36), (33, 36), (30, 36), (27, 37), (23, 36), (19, 32), (15, 32), (12, 34), (10, 37), (3, 37), (-2, 35), (-6, 34), (-9, 37)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (124, -33), (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27), (150, -22), (146, -19), (142, -11), (142, -15), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14), (122, -17), (118, -20), (114, -22), (113, -22)],
    # Japan (rough chain)
    [(130, 31), (132, 33), (134, 34), (137, 35), (139, 36), (140, 38), (141, 40), (141, 42), (143, 42), (144, 44), (142, 44), (140, 41), (139, 38), (137, 35), (134, 33), (131, 32), (130, 31)],
    # Great Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51), (-2, 50), (-5, 50)],
    # New Zealand
    [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38), (175, -40), (172, -43), (168, -46), (167, -45)],
    # Borneo
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -4), (110, -2), (109, 1)],
    # Sumatra
    [(95, 5), (98, 3), (101, 0), (104, -3), (106, -6), (104, -5), (101, -1), (97, 3), (95, 5)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (45, -25), (43, -21), (44, -16)],
]


def draw_map(d, box):
    """Simplified world map with numbered pins for stories 1-13."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(214, 228, 232))
    mw, mh = x1 - x0, y1 - y0

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360 * mw, y0 + (75 - lat) / 155 * mh)

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(178, 198, 138), outline=(120, 140, 100))
    # pin offsets to separate close pins (story n -> dx, dy)
    offsets = {1: (0, 0), 2: (0, 0), 3: (0, 0), 4: (0, 0), 5: (-2, 6), 6: (0, 0),
               7: (-8, 6), 8: (16, -12), 9: (0, 0), 10: (0, 0), 11: (0, 0), 12: (0, 0), 13: (0, 0)}
    for story in LEADS + MIDS:
        n, _, _, _, _, _, _, ll = story
        if ll is None:
            continue
        lat, lon = ll
        px, py = proj(lon, lat)
        dx, dy = offsets.get(n, (0, 0))
        px, py = px + dx, py + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        fnt = font(SANS_B, 9)
        tw = d.textlength(str(n), font=fnt)
        d.text((px - tw / 2, py - 6), str(n), fill=(255, 255, 255), font=fnt)


# ---------------------------------------------------------------- layouts
def header(d, y=8):
    f_kick = font(SANS_B, 11)
    d.text((14, y), "THE WORLD'S NEWS IN ONE PICTURE", fill=RED, font=f_kick)
    right = "44 STORIES \u00b7 7 REGIONS \u00b7 11 FIELDS \u00b7 13 ILLUSTRATED \u00b7 ALL FROM THURSDAY"
    tw = d.textlength(right, font=f_kick)
    d.text((W - 14 - tw, y), right, fill=RED, font=f_kick)
    f_mast = font(SERIF, 62)
    d.text((14, y + 16), "Thursday 19 November 2026", fill=INK, font=f_mast)
    d.line([(14, y + 88), (W - 14, y + 88)], fill=RULE, width=3)
    return y + 94


REGION_SHORT = {"EUROPE": "EUROPE", "MIDDLE EAST": "MID EAST", "ASIA": "ASIA",
                "AFRICA": "AFRICA", "AMERICAS": "AMERICAS", "OCEANIA": "OCEANIA",
                "WORLD": "WORLD"}
FIELD_SHORT = {"Politics & diplomacy": "POLITICS", "War & security": "WAR",
               "Economy": "ECONOMY", "Technology": "TECH",
               "Science & space": "SPACE", "Culture & games": "GAMES",
               "Disasters & weather": "WEATHER", "Health": "HEALTH",
               "Sport": "SPORT", "Society": "SOCIETY", "Justice": "JUSTICE"}


def count_bars(d, y):
    counts = region_counts()
    f_lab = font(SANS_B, 10)
    total_w = W - 28
    x = 14
    segs = []
    for r in REGION_ORDER:
        wseg = total_w * counts[r] / 44
        d.rectangle([x, y, x + wseg, y + 20], fill=REGION_COLORS[r])
        segs.append((x, wseg, r))
        x += wseg
    # Labels drawn in a second pass: narrow segments (AFRICA 2, OCEANIA 2)
    # are ~45px wide but their labels are ~55-62px, so drawing a label
    # before the next segment's rectangle overpaints its tail.
    for x, wseg, r in segs:
        label = "%s %d" % (REGION_SHORT[r], counts[r])
        tw = d.textlength(label, font=f_lab)
        d.text((x + max(1, (wseg - tw) / 2), y + 4), label, fill=(255, 255, 255), font=f_lab)
    fields = field_counts()
    parts = ["BY FIELD:"] + ["%s %d" % (k, v) for k, v in sorted(fields.items(), key=lambda kv: -kv[1])]
    line = "  ".join(parts)
    for size in (10, 9.5, 9, 8.5, 8):
        f_field = font(SANS_B, size)
        if d.textlength(line, font=f_field) <= total_w - 8:
            break
    d.rectangle([14, y + 24, W - 14, y + 42], fill=INK)
    tw = d.textlength(line, font=f_field)
    d.text((14 + (total_w - tw) / 2, y + 27), line, fill=(255, 255, 255), font=f_field)
    return y + 46


def numbers_strip(d, y):
    f_lab = font(SANS_B, 11)
    for nsize, tsize in ((15, 10), (14, 10), (13, 9), (12, 9)):
        f_num = font(SERIF, nsize)
        f_txt = font(SANS, tsize)
        x = 14 + d.textlength("THE DAY IN NUMBERS:  ", font=f_lab)
        for num, txt in NUMBERS:
            x += d.textlength(num + " ", font=f_num)
            x += d.textlength(txt + "   \u00b7   ", font=f_txt)
        if x <= W - 14:
            break
    d.text((14, y + 3), "THE DAY IN NUMBERS:", fill=INK, font=f_lab)
    x = 14 + d.textlength("THE DAY IN NUMBERS:  ", font=f_lab)
    for num, txt in NUMBERS:
        d.text((x, y + 2), num, fill=RED, font=f_num)
        x += d.textlength(num + " ", font=f_num)
        d.text((x, y + 4), txt, fill=INK, font=f_txt)
        x += d.textlength(txt + "   \u00b7   ", font=f_txt)
    d.line([(14, y + 22), (W - 14, y + 22)], fill=GREY, width=1)
    return y + 26


def story_card(d, img, story, box, big):
    n, region, field, place, headline, deck, key, ll = story
    x0, y0, x1, y1 = box
    col = REGION_COLORS[region]
    d.rectangle([x0, y0, x1, y1], fill=PAPER, outline=(180, 172, 156))
    if big:
        ill_h, head_size, deck_size, kick_size = 96, 19, 11, 10
    else:
        ill_h, head_size, deck_size, kick_size = 56, 12, 10, 9
    ill = draw_illustration(key, (x1 - x0 - 2, ill_h))
    img.paste(ill, (int(x0) + 1, int(y0) + 1))
    ty = y0 + ill_h + 4
    f_num = font(SANS_B, 12 if big else 10)
    d.rectangle([x0 + 4, ty - 1, x0 + 4 + d.textlength(str(n), font=f_num) + 8, ty + 14], fill=RED)
    d.text((x0 + 8, ty), str(n), fill=(255, 255, 255), font=f_num)
    f_kick = font(SANS_B, kick_size)
    kick = "%s \u00b7 %s" % (region, FIELD_SHORT[field])
    d.text((x0 + 12 + d.textlength(str(n), font=f_num) + 8, ty + 1), kick, fill=col, font=f_kick)
    ty += 17
    f_head = font(SERIF, head_size)
    lines = fit_lines(d, headline, f_head, x1 - x0 - 10, 2)
    for ln in lines:
        d.text((x0 + 5, ty), ln, fill=INK, font=f_head)
        ty += head_size + 3
    f_deck = font(SANS, deck_size)
    for ln in fit_lines(d, deck, f_deck, x1 - x0 - 10, 3 if big else 2):
        d.text((x0 + 5, ty), ln, fill=(60, 56, 48), font=f_deck)
        ty += deck_size + 3


def briefs_block(d, box, cols=3):
    x0, y0, x1, y1 = box
    f_head = font(SANS_B, 12)
    d.text((x0, y0), "ALSO ON THURSDAY 19 NOVEMBER", fill=DARKRED, font=f_head)
    d.line([(x0, y0 + 17), (x1, y0 + 17)], fill=RULE, width=2)
    col_w = (x1 - x0 - (cols - 1) * 12) / cols
    per = (len(BRIEFS) + cols - 1) // cols
    avail = y1 - (y0 + 23)
    # pick the largest font size whose tallest column fits the available height
    chosen = None
    for size in (10, 9.5, 9, 8.5, 8):
        f_b = font(SANS, size)
        f_bn = font(SANS_B, size)
        lh = size + 2.5
        col_heights = []
        for c in range(cols):
            ch = 0
            for story in BRIEFS[c * per:(c + 1) * per]:
                n, _, _, place, text = story
                wnum = d.textlength(str(n) + " ", font=f_bn)
                lines = fit_lines(d, "%s: %s" % (place, text), f_b, col_w - wnum, 2)
                ch += len(lines) * lh + 2
            col_heights.append(ch)
        if max(col_heights) <= avail:
            chosen = (size, f_b, f_bn, lh)
            break
    if chosen is None:
        size = 8
        f_b = font(SANS, size)
        f_bn = font(SANS_B, size)
        lh = size + 2.5
        chosen = (size, f_b, f_bn, lh)
    _, f_b, f_bn, lh = chosen
    y = y0 + 23
    for c in range(cols):
        cx = x0 + c * (col_w + 12)
        cy = y
        for story in BRIEFS[c * per:(c + 1) * per]:
            n, _, _, place, text = story
            d.text((cx, cy), str(n), fill=RED, font=f_bn)
            nx = cx + d.textlength(str(n) + " ", font=f_bn)
            line = "%s: %s" % (place, text)
            for ln in fit_lines(d, line, f_b, col_w - (nx - cx), 2):
                d.text((nx, cy), ln, fill=INK, font=f_b)
                cy += lh
            cy += 2
    return y1


def footer_block(d, y):
    f_lab = font(SANS_B, 10)
    f_txt = font(SANS, 10)
    d.rectangle([14, y, W - 14, y + 38], outline=RED, width=1)
    d.text((18, y + 4), "DATE CHECK", fill=RED, font=f_lab)
    dx = 18 + d.textlength("DATE CHECK  ", font=f_lab)
    ly = y + 4
    for ln in fit_lines(d, DATE_CHECK, f_txt, W - 14 - dx - 4, 3):
        d.text((dx, ly), ln, fill=INK, font=f_txt)
        ly += 13
    return y + 40


def footer_line(d, y):
    f_txt = font(SANS_O, 9)
    for ln in fit_lines(d, FOOTER, f_txt, W - 28, 2):
        d.text((14, y), ln, fill=GREY, font=f_txt)
        y += 12
    return y


def layout_a():
    """Variant A: 3 leads, 10 mid cards, map + briefs. The target pattern."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    y = header(d)
    y = count_bars(d, y + 2)
    y = numbers_strip(d, y + 2)
    # leads row
    lead_w = (W - 28 - 2 * 8) / 3
    lead_y, lead_h = y + 4, 204
    for i, story in enumerate(LEADS):
        x0 = 14 + i * (lead_w + 8)
        story_card(d, img, story, (x0, lead_y, x0 + lead_w, lead_y + lead_h), big=True)
    # mid grid 5 x 2
    mid_w = (W - 28 - 4 * 6) / 5
    mid_y, mid_h = lead_y + lead_h + 6, 132
    for i, story in enumerate(MIDS):
        r, c = divmod(i, 5)
        x0 = 14 + c * (mid_w + 6)
        y0 = mid_y + r * (mid_h + 6)
        story_card(d, img, story, (x0, y0, x0 + mid_w, y0 + mid_h), big=False)
    # bottom: map left, briefs right
    bot_y = mid_y + 2 * mid_h + 6 + 6
    map_w = 330
    f_head = font(SANS_B, 12)
    d.text((14, bot_y), "WHERE IT HAPPENED", fill=DARKRED, font=f_head)
    d.text((14, bot_y + 16), "numbered pins = stories 1-13 above", fill=GREY, font=font(SANS, 9))
    draw_map(d, (14, bot_y + 32, 14 + map_w, bot_y + 32 + 210))
    d.text((14, bot_y + 246), "Pins 7 and 8 both sit in Washington; 8 is offset.",
           fill=GREY, font=font(SANS, 9))
    d.text((14, bot_y + 258), "11 rides with Voyager 1, in deep space.",
           fill=GREY, font=font(SANS, 9))
    briefs_block(d, (14 + map_w + 14, bot_y, W - 14, H - 78), cols=2)
    fy = footer_block(d, H - 74)
    footer_line(d, H - 30)
    return img


def layout_b():
    """Variant B: Daily Globe style, 2 leads, continent columns, briefs."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    y = header(d)
    y = count_bars(d, y + 2)
    lead_w = (W - 28 - 8) / 2
    lead_y, lead_h = y + 4, 204
    for i, story in enumerate(LEADS[:2]):
        x0 = 14 + i * (lead_w + 8)
        story_card(d, img, story, (x0, lead_y, x0 + lead_w, lead_y + lead_h), big=True)
    # continent columns
    col_y = lead_y + lead_h + 8
    f_head = font(SANS_B, 12)
    d.text((14, col_y), "SIX CONTINENTS, ONE DAY", fill=DARKRED, font=f_head)
    d.line([(14, col_y + 17), (W - 14, col_y + 17)], fill=RULE, width=2)
    conts = ["ASIA", "EUROPE", "AMERICAS", "MIDDLE EAST", "AFRICA", "OCEANIA"]
    col_w = (W - 28 - 5 * 8) / 6
    pick = {}
    for s in LEADS + MIDS:
        pick.setdefault(s[1], s)
    for i, r in enumerate(conts):
        x0 = 14 + i * (col_w + 8)
        s = pick.get(r)
        if s is None:
            continue
        d.rectangle([x0, col_y + 22, x0 + col_w, col_y + 150], fill=PAPER, outline=(180, 172, 156))
        d.rectangle([x0, col_y + 22, x0 + col_w, col_y + 42], fill=REGION_COLORS[r])
        d.text((x0 + 6, col_y + 26), r, fill=(255, 255, 255), font=font(SANS_B, 11))
        ty = col_y + 48
        f_h = font(SERIF, 12)
        for ln in fit_lines(d, s[4], f_h, col_w - 10, 3):
            d.text((x0 + 5, ty), ln, fill=INK, font=f_h)
            ty += 15
        f_de = font(SANS, 10)
        for ln in fit_lines(d, s[5], f_de, col_w - 10, 3):
            d.text((x0 + 5, ty), ln, fill=(60, 56, 48), font=f_de)
            ty += 13
    briefs_block(d, (14, col_y + 162, W - 14, H - 60), cols=3)
    footer_block(d, H - 74)
    footer_line(d, H - 30)
    return img


def layout_c():
    """Variant C: one big lead, 3 mids, brief-card grid."""
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    y = header(d)
    y = count_bars(d, y + 2)
    lead_y = y + 4
    story_card(d, img, LEADS[0], (14, lead_y, W - 14, lead_y + 210), big=True)
    mid_y = lead_y + 216
    mid_w = (W - 28 - 2 * 8) / 3
    for i, story in enumerate(MIDS[:3]):
        x0 = 14 + i * (mid_w + 8)
        story_card(d, img, story, (x0, mid_y, x0 + mid_w, mid_y + 150), big=False)
    briefs_block(d, (14, mid_y + 160, W - 14, H - 60), cols=3)
    footer_block(d, H - 74)
    footer_line(d, H - 30)
    return img


LAYOUTS = {"a": layout_a, "b": layout_b, "c": layout_c}

if __name__ == "__main__":
    variant = sys.argv[1] if len(sys.argv) > 1 else "a"
    out = sys.argv[2] if len(sys.argv) > 2 else "entry.png"
    img = LAYOUTS[variant]()
    img.save(out, "PNG")
    print("wrote", out, img.size)
