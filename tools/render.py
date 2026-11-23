"""Render the front page of "THE DAY IN BRIEF" for Sunday 22 November 2026.

One 1024x1024 PNG that sums up the day's world news: a huge date nameplate, a
vertical black spine of five numbers down the right side, one big lead story
with a drawn illustration, eight identical small-story cards in a 4x2 grid, an
"ALSO TODAY" strip in three columns, and a footer.

Pillow only.  No network, no clock, no randomness: the same bytes every run.
Every string is measured with ImageDraw.textlength and wrapped to its column;
an assertion fires rather than ever drawing a line wider than its measure.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# palette and layout constants (from the brief)
# --------------------------------------------------------------------------

PALETTE = {
    "paper": "#F6F4EE",
    "ink": "#141210",
    "red": "#B22A22",
    "grey": "#6B655C",
    "hairline": "#C9C2B4",
    "navy": "#1E2A4A",
    "sky": "#CFE3EC",
    "sand": "#E8D9BC",
    "ochre": "#E3A33C",
    "peach": "#F2B183",
    "plum": "#4B3B57",
    "teal": "#2E6F6A",
}

GRID = {
    "page": 1024,
    "margin": 32,
    # top kicker line
    "kicker_y": 26,
    "kicker_size": 13,
    "kicker_track": 3,
    # nameplate
    "plate_y": 48,
    "plate_size": 56,
    # rules under the nameplate
    "bar_y": 118,
    "bar_h": 4,
    "hair_y": 126,
    "folio_y": 129,
    "folio_size": 9,
    # lead block (x, width are the brief's; the vertical stack is compacted by
    # the few pixels the 1024 canvas forces, see the note above compose())
    "lead_x": 32,
    "lead_w": 592,
    "lead_kick_y": 142,
    "lead_kick_size": 12,
    "lead_kick_track": 2,
    "lead_head_y": 160,
    "lead_head_size": 39,
    "lead_head_lead": 43,
    "lead_panel_y": 256,
    "lead_panel_h": 164,
    "lead_deck_y": 428,
    "lead_deck_size": 13,
    "lead_deck_lead": 17,
    "lead_deck_max": 5,
    # numbers spine
    "spine_x": 632,
    "spine_w": 360,
    "spine_y": 140,
    "spine_h": 384,
    "spine_pad": 14,
    "spine_head_y": 152,
    "spine_row_y": 172,
    "spine_row_h": 68,
    "spine_fig_size": 38,
    "spine_label_size": 11,
    "spine_label_lead": 14,
    "spine_label_gap": 42,
    # cards
    "card_x": [32, 277, 522, 767],
    "card_w": 225,
    "card_row_y": [528, 731],
    "card_art_h": 80,
    "card_kick_size": 10,
    "card_kick_track": 1.5,
    "card_kick_dy": 86,
    "card_head_size": 15,
    "card_head_lead": 18,
    "card_head_dy": 98,
    "card_deck_size": 11,
    "card_deck_lead": 13,
    "card_deck_dy": 139,
    "card_deck_max": 4,
    # also today
    "also_rule_y": 922,
    "also_head_y": 930,
    "also_x": [32, 361, 690],
    "also_w": 300,
    "also_kick_y": 944,
    "also_head_y2": 958,
    "also_size": 12.5,
    "also_lead": 15,
    # footer
    "footer_y": 1000,
    "footer_size": 10.5,
}

# --------------------------------------------------------------------------
# editorial content (verbatim)
# --------------------------------------------------------------------------

EDITORIAL = {
    "top_kicker": "THE DAY IN BRIEF  ·  ONE PAGE, THE WHOLE DAY",
    "nameplate": "SUNDAY 22 NOVEMBER 2026",
    "folio_left": "No. 22",
    "folio_right": "ONE PAGE · 8 STORIES",
    "lead": {
        "kicker": "ANTALYA · CLIMATE · THE LEAD",
        "headline": ["Climate talks collapse", "with no deal on fossil fuels"],
        "deck": (
            "COP31 ran two days past its deadline and ended on Sunday without an "
            "overarching agreement. The final draft, the Antalya Pact, never named "
            "fossil fuels; the EU, Britain, Panama and vulnerable states refused it, "
            "and the presidency put the decisions to no vote. Nearly 200 countries "
            "leave Antalya with no new joint plan as 2026 heads for the warmest year "
            "on record."
        ),
        "panel": "lead",
    },
    "numbers_header": "THE DAY IN NUMBERS",
    "numbers": [
        ("212", "countries at COP31, which closed with no deal"),
        ("258", "House seats won by the Democrats, their most since 1992"),
        ("7", "Ukrainian sea drones that sank the corvette Merkury"),
        ("1,300", "guests at the Pope's World Day of the Poor lunch"),
        ("3", "killed when a strike wrecked flats in Dymer"),
    ],
    "cards": [
        {
            "panel": "libya",
            "kicker": "BENGHAZI · WAR",
            "headline": "Sea drones sink a Russian corvette in Libya",
            "deck": (
                "Seven Ukrainian naval drones hit the Merkury at Benghazi on Sunday, "
                "destroying a Ka-27 helicopter; the cargo ship Angara was struck too."
            ),
        },
        {
            "panel": "dymer",
            "kicker": "KYIV REGION · WAR",
            "headline": "Strike wrecks flats in Dymer",
            "deck": (
                "At least three people were killed when an apartment block was hit; "
                "rescuers searched the rubble through Sunday."
            ),
        },
        {
            "panel": "house",
            "kicker": "WASHINGTON · POLITICS",
            "headline": "Democrats win 258 House seats",
            "deck": (
                "Their largest majority since 1992, with the Senate too, against a "
                "Republican president: divided government."
            ),
        },
        {
            "panel": "cartel",
            "kicker": "SINALOA · CRIME",
            "headline": "Cartel boss 'Chapo Isidro' held",
            "deck": (
                "Fausto Isidro Meza Flores, on the FBI's ten-most-wanted list, was "
                "seized in Guasave; 11 died in the fallout."
            ),
        },
        {
            "panel": "factory",
            "kicker": "INDONESIA · DISASTER",
            "headline": "Candy factory fire kills three",
            "deck": (
                "Dozens of workers were unaccounted for after the blaze at the plant; "
                "investigators are on the site."
            ),
        },
        {
            "panel": "lebanon",
            "kicker": "SOUTH LEBANON · MIDEAST",
            "headline": "Israel pulls back; houses razed",
            "deck": (
                "Troops left a border village and villagers walked back to wrecked "
                "homes as demolitions went on."
            ),
        },
        {
            "panel": "vatican",
            "kicker": "VATICAN · SOCIETY",
            "headline": "Pope dines with 1,300 poor",
            "deck": (
                "For the tenth World Day of the Poor, Pope Leo XIV shared a lunch in "
                "Rome with 1,300 guests."
            ),
        },
        {
            "panel": "india",
            "kicker": "INDIA · TECH",
            "headline": "Congress youth protest Meta",
            "deck": (
                "The party's youth wing marched against the platform over alleged "
                "removals of accounts."
            ),
        },
    ],
    "also_header": "ALSO TODAY",
    "also": [
        ("SPORT", "UCLA's first loss shakes up the Top 25"),
        ("CULTURE", "Princess Catherine on life after cancer, in a new documentary"),
        ("AMERICAS", "Rio's Pride parade fills Copacabana"),
    ],
    "footer": "Compiled from the day's reporting  ·  22 November 2026",
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_FILES = {
    "serif": "DejaVuSerif.ttf",
    "serif-bold": "DejaVuSerif-Bold.ttf",
    "sans": "DejaVuSans.ttf",
    "sans-bold": "DejaVuSans-Bold.ttf",
}

# every column measured, for the overflow report printed by main()
WIDTH_LOG = []


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

_FONTS = {}


def font(kind, size):
    """Load one of the four DejaVu faces at an integer size."""
    key = (kind, int(round(size)))
    if key not in _FONTS:
        path = os.path.join(FONT_DIR, FONT_FILES[kind])
        _FONTS[key] = ImageFont.truetype(path, int(round(size)))
    return _FONTS[key]


def advance(draw, text, face, tracking=0.0):
    """Width of a string, letter-spacing included."""
    if not tracking:
        return draw.textlength(text, font=face)
    total = 0.0
    for ch in text:
        total += draw.textlength(ch, font=face)
    return total + tracking * max(len(text) - 1, 0)


def wrap(draw, text, face, width, tracking=0.0):
    """Wrap on spaces; every returned line measures <= width."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        if advance(draw, word, face, tracking) > width:
            raise AssertionError("word wider than column: %r" % word)
        trial = (cur + " " + word).strip()
        if not cur or advance(draw, trial, face, tracking) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    for line in lines:
        w = advance(draw, line, face, tracking)
        if w > width + 1e-6:
            raise AssertionError("line overflows: %r %.1f > %.1f" % (line, w, width))
    return lines


def note_width(name, lines, face, draw, width, tracking=0.0):
    """Record the widest measured line of a column and assert it fits."""
    widest = max((advance(draw, ln, face, tracking) for ln in lines), default=0.0)
    WIDTH_LOG.append((name, widest, width))
    assert widest <= width + 1e-6, "%s: %.1f > %.1f" % (name, widest, width)
    return widest


def text_at(draw, xy, text, face, fill, tracking=0.0):
    """Draw a string with optional letter-spacing; top-left anchored."""
    x, y = xy
    if not tracking:
        draw.text((x, y), text, font=face, fill=fill, anchor="la")
        return draw.textlength(text, font=face)
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=face, fill=fill, anchor="la")
        cx += draw.textlength(ch, font=face) + tracking
    return cx - x - tracking


def text_right(draw, x_right, y, text, face, fill, tracking=0.0):
    """Right-aligned string, measured, so it never passes x_right."""
    w = advance(draw, text, face, tracking)
    text_at(draw, (x_right - w, y), text, face, fill, tracking)
    return w


def text_centred(draw, cx, y, text, face, fill, tracking=0.0):
    w = advance(draw, text, face, tracking)
    text_at(draw, (cx - w / 2.0, y), text, face, fill, tracking)
    return w


def para(draw, x, y, lines, face, leading, fill, width, name, tracking=0.0):
    """Draw a block of pre-wrapped lines; returns the y below the last line."""
    note_width(name, lines, face, draw, width, tracking)
    for i, line in enumerate(lines):
        text_at(draw, (x, y + i * leading), line, face, fill, tracking)
    return y + len(lines) * leading


def rule(draw, x0, y0, x1, thickness, fill):
    draw.rectangle([x0, y0, x1, y0 + thickness - 1], fill=fill)


def frame(draw, box, fill, thickness=1):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1 - 1, y1 - 1], outline=fill, width=thickness)


def panel_layer(width, height, background):
    """A fresh RGB panel of exactly the illustration box, with its own draw."""
    img = Image.new("RGB", (int(width), int(height)), background)
    return img, ImageDraw.Draw(img)


# --------------------------------------------------------------------------
# illustrations: each paints only inside its own box (a local layer of that
# exact size, pasted by compose), in palette colours, bold flat shapes
# --------------------------------------------------------------------------


def panel_lead(d, box):
    """Globe with a dark flame over it, red circle-and-slash, an ANTALYA pin."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["sky"])
    # sand coastline sweeping across the bottom
    d.polygon([(0, h - 26), (w * 0.22, h - 44), (w * 0.48, h - 30),
               (w * 0.74, h - 46), (w, h - 28), (w, h), (0, h)], fill=P["sand"])
    d.polygon([(0, h - 12), (w * 0.30, h - 24), (w * 0.62, h - 14),
               (w, h - 22), (w, h), (0, h)], fill=P["ochre"])
    # globe
    cx, cy, r = 132, h * 0.52, 74
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P["paper"])
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=P["navy"], width=4)
    # landmasses, kept well inside the disc
    d.ellipse([cx - 52, cy - 46, cx - 6, cy - 6], fill=P["sand"])
    d.ellipse([cx - 40, cy - 6, cx + 6, cy + 22], fill=P["sand"])
    d.polygon([(cx + 10, cy - 40), (cx + 54, cy - 24), (cx + 36, cy + 6),
               (cx + 12, cy - 2)], fill=P["sand"])
    d.polygon([(cx - 30, cy + 26), (cx + 14, cy + 30), (cx + 2, cy + 54),
               (cx - 26, cy + 46)], fill=P["sand"])
    # meridian and equator lines
    d.ellipse([cx - 30, cy - r + 4, cx + 30, cy + r - 4], outline=P["teal"], width=2)
    d.line([(cx - r + 4, cy), (cx + r - 4, cy)], fill=P["teal"], width=2)
    # dark flame over the globe
    fx, fb = cx + 44, cy + 30
    d.polygon([(fx, fb), (fx - 26, fb - 44), (fx - 12, fb - 62), (fx - 4, fb - 40),
               (fx + 12, fb - 78), (fx + 26, fb - 46), (fx + 30, fb - 20)],
              fill=P["ink"])
    d.polygon([(fx - 2, fb - 6), (fx - 12, fb - 34), (fx - 2, fb - 46),
               (fx + 6, fb - 28), (fx + 14, fb - 44), (fx + 18, fb - 22),
               (fx + 12, fb - 4)], fill=P["red"])
    d.polygon([(fx + 2, fb - 8), (fx - 2, fb - 24), (fx + 6, fb - 30),
               (fx + 12, fb - 14)], fill=P["ochre"])
    # red circle-and-slash over the flame: no deal on fossil fuels
    rx, ry, rr = fx + 2, fb - 40, 33
    d.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], outline=P["red"], width=7)
    d.line([(rx - 24, ry + 24), (rx + 24, ry - 24)], fill=P["red"], width=7)
    # ANTALYA pin on the coast
    px, py = w - 118, h - 74
    d.polygon([(px - 16, py + 20), (px + 16, py + 20), (px, py + 44)],
              fill=P["red"])
    d.ellipse([px - 19, py - 19, px + 19, py + 19], fill=P["red"])
    d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=P["paper"])
    face = font("sans-bold", 11)
    label = "ANTALYA"
    lw = advance(d, label, face, 2)
    d.rectangle([px - lw / 2 - 8, py + 48, px + lw / 2 + 8, py + 68], fill=P["ink"])
    text_at(d, (px - lw / 2, py + 51), label, face, P["paper"], 2)
    # a few delegates' markers on the sand, keeping the right side alive
    for i, col in enumerate((P["navy"], P["plum"], P["teal"])):
        bx = w - 250 + i * 26
        d.rectangle([bx, h - 44, bx + 14, h - 14], fill=col)
        d.ellipse([bx + 2, h - 56, bx + 12, h - 46], fill=col)
    return box


def panel_libya(d, box):
    """Dark navy water, a grey hull tipped half under, flame, a drone boat."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["sky"])
    d.rectangle([0, int(h * 0.34), w, h], fill=P["navy"])
    d.polygon([(0, int(h * 0.34)), (w * 0.3, int(h * 0.30)), (w * 0.62, int(h * 0.35)),
               (w, int(h * 0.31)), (w, int(h * 0.42)), (0, int(h * 0.42))],
              fill=P["teal"])
    # tipped hull, half under the waterline
    hull = [(26, 56), (128, 48), (150, 62), (140, 74), (38, 74)]
    d.polygon(hull, fill=P["grey"])
    d.polygon([(26, 56), (128, 48), (150, 62), (146, 66), (34, 62)], fill=P["paper"])
    d.polygon([(60, 50), (86, 46), (90, 52), (64, 55)], fill=P["ink"])
    d.polygon([(96, 46), (104, 28), (110, 30), (108, 47)], fill=P["grey"])
    # red flame burst at the hull
    d.polygon([(120, 58), (132, 30), (142, 44), (152, 20), (162, 46), (170, 38),
               (170, 64)], fill=P["red"])
    d.polygon([(134, 58), (140, 42), (148, 52), (154, 44), (156, 60)],
              fill=P["ochre"])
    # water line over the hull
    d.rectangle([0, 62, w, 66], fill=P["navy"])
    # small drone boat silhouette, right side
    bx = w - 62
    d.polygon([(bx, 40), (bx + 40, 40), (bx + 32, 48), (bx + 6, 48)], fill=P["ink"])
    d.line([(bx + 18, 40), (bx + 18, 24)], fill=P["ink"], width=3)
    d.polygon([(bx + 4, 22), (bx + 20, 22), (bx + 12, 30)], fill=P["red"])
    d.line([(bx - 16, 48), (bx, 47)], fill=P["paper"], width=3)
    # gulls
    for gx, gy in ((36, 18), (58, 24)):
        d.line([(gx, gy), (gx + 7, gy - 5)], fill=P["grey"], width=2)
        d.line([(gx + 7, gy - 5), (gx + 14, gy)], fill=P["grey"], width=2)
    return box


def panel_dymer(d, box):
    """A cream apartment slab with a black bite out of it, rubble, red light."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["sky"])
    d.rectangle([0, h - 18, w, h], fill=P["grey"])
    # slab
    d.rectangle([40, 12, 186, h - 16], fill=P["sand"])
    d.rectangle([40, 12, 186, 22], fill=P["ochre"])
    # windows
    for row in range(3):
        for col in range(5):
            x = 52 + col * 26
            y = 28 + row * 14
            d.rectangle([x, y, x + 14, y + 9], fill=P["navy"])
    # black bite taken out of the top right corner
    d.polygon([(150, 12), (186, 12), (186, 52), (176, 44), (168, 56),
               (158, 40), (150, 46)], fill=P["ink"])
    d.polygon([(150, 46), (158, 40), (168, 56), (176, 44), (186, 52),
               (186, 62), (150, 62)], fill=P["plum"])
    # rubble at the base
    d.polygon([(20, h - 16), (46, h - 30), (64, h - 16)], fill=P["plum"])
    d.polygon([(56, h - 16), (78, h - 26), (96, h - 16)], fill=P["sand"])
    d.polygon([(150, h - 16), (172, h - 28), (196, h - 16)], fill=P["plum"])
    # rescue light
    d.rectangle([4, h - 56, 10, h - 16], fill=P["ink"])
    d.ellipse([0, h - 68, 16, h - 52], fill=P["red"])
    d.ellipse([4, h - 64, 12, h - 56], fill=P["peach"])
    return box


def panel_house(d, box):
    """Dome and steps in sand, 258 as a white numeral on red, seats as squares."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["sand"])
    d.rectangle([0, 0, int(w * 0.55), h], fill=P["sky"])
    # dome and steps
    d.rectangle([14, 34, 96, 52], fill=P["paper"])
    d.pieslice([26, 12, 84, 70], 180, 360, fill=P["paper"])
    d.rectangle([28, 40, 82, 50], fill=P["sand"])
    for i in range(3):
        d.rectangle([10 + i * 2, 52 + i * 6, 100 - i * 2, 58 + i * 6], fill=P["paper"])
    d.rectangle([44, 0, 66, 14], fill=P["paper"])
    # red field with the numeral
    d.rectangle([int(w * 0.55), 0, w, h], fill=P["red"])
    face = font("sans-bold", 40)
    label = "258"
    lw = advance(d, label, face)
    text_at(d, ((w + int(w * 0.55) - lw) / 2.0, 8), label, face, P["paper"])
    # seat squares
    for i in range(9):
        x = int(w * 0.55) + 8 + (i % 9) * 9
        y = h - 12
        d.rectangle([x, y, x + 5, y + 5], fill=P["paper"])
    for i in range(9):
        x = int(w * 0.55) + 8 + (i % 9) * 9
        d.rectangle([x, h - 22, x + 5, h - 17], fill=P["peach"])
    return box


def panel_cartel(d, box):
    """Red crosshair over a sand map shape, handcuff motif, badge star."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["navy"])
    d.polygon([(10, 30), (44, 12), (86, 20), (120, 10), (160, 24), (196, 16),
               (214, 40), (198, 66), (150, 74), (104, 64), (60, 72), (24, 58)],
              fill=P["sand"])
    d.polygon([(10, 30), (44, 12), (86, 20), (120, 10), (160, 24), (196, 16),
               (214, 40), (206, 46), (120, 34), (30, 42)], fill=P["ochre"])
    # handcuffs
    cx, cy = 74, 44
    d.ellipse([cx - 24, cy - 14, cx + 2, cy + 12], outline=P["navy"], width=6)
    d.ellipse([cx + 10, cy - 14, cx + 36, cy + 12], outline=P["navy"], width=6)
    d.rectangle([cx + 2, cy - 4, cx + 10, cy + 2], fill=P["navy"])
    # crosshair
    tx, ty = 158, 40
    d.ellipse([tx - 30, ty - 26, tx + 30, ty + 34], outline=P["red"], width=5)
    d.line([(tx - 40, ty + 4), (tx + 40, ty + 4)], fill=P["red"], width=5)
    d.line([(tx, ty - 36), (tx, ty + 44)], fill=P["red"], width=5)
    d.ellipse([tx - 8, ty - 4, tx + 8, ty + 12], fill=P["red"])
    # badge star
    sx, sy, sr = 200, 64, 12
    pts = []
    for i in range(10):
        import math
        ang = -math.pi / 2 + i * math.pi / 5
        rad = sr if i % 2 == 0 else sr * 0.45
        pts.append((sx + rad * math.cos(ang), sy + rad * math.sin(ang)))
    d.polygon(pts, fill=P["paper"])
    d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=P["navy"])
    return box


def panel_factory(d, box):
    """A plum factory silhouette, orange flames at the roof, grey smoke curls."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["sand"])
    d.rectangle([0, h - 14, w, h], fill=P["grey"])
    # sawtooth roof and body
    d.polygon([(24, 50), (24, h - 12), (188, h - 12), (188, 50), (166, 40),
               (166, 50), (144, 40), (144, 50), (122, 40), (122, 50), (100, 40),
               (100, 50), (78, 40), (78, 50), (56, 40), (56, 50), (34, 40)],
              fill=P["plum"])
    # chimney
    d.rectangle([34, 18, 52, 46], fill=P["plum"])
    # windows
    for i in range(4):
        x = 44 + i * 34
        d.rectangle([x, h - 34, x + 20, h - 20], fill=P["ochre"])
    # flames at the roof
    d.polygon([(96, 46), (108, 20), (118, 34), (130, 8), (140, 30), (152, 16),
               (158, 46)], fill=P["red"])
    d.polygon([(108, 46), (118, 28), (128, 40), (136, 24), (144, 44)],
              fill=P["ochre"])
    # smoke curls
    for i, (sx, sy, sr) in enumerate(((60, 12, 11), (78, 6, 9), (44, 4, 8))):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=P["grey"])
    d.ellipse([168, 14, 190, 34], fill=P["grey"])
    d.ellipse([182, 4, 200, 22], fill=P["grey"])
    return box


def panel_lebanon(d, box):
    """A row of small square houses, two collapsed, under a navy sky."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["navy"])
    d.rectangle([0, h - 16, w, h], fill=P["grey"])
    d.ellipse([w - 46, 8, w - 16, 34], fill=P["sand"])
    houses = [(8, 26), (50, 20), (92, 30), (134, 22), (176, 26)]
    for i, (x, top) in enumerate(houses):
        d.rectangle([x, top, x + 36, h - 16], fill=P["sand"])
        d.rectangle([x, top, x + 36, top + 6], fill=P["ochre"])
        d.rectangle([x + 8, top + 14, x + 16, top + 24], fill=P["navy"])
        d.rectangle([x + 22, top + 14, x + 30, top + 24], fill=P["navy"])
    # two collapsed: jagged outlines instead of roofs
    d.polygon([(50, h - 16), (50, 44), (58, 56), (64, 34), (72, 50), (78, 30),
               (86, h - 16)], fill=P["plum"])
    d.polygon([(134, h - 16), (134, 48), (142, 60), (150, 38), (160, 54),
               (170, h - 16)], fill=P["plum"])
    # rubble
    d.polygon([(44, h - 16), (60, h - 26), (74, h - 16)], fill=P["sand"])
    d.polygon([(126, h - 16), (144, h - 28), (162, h - 16)], fill=P["sand"])
    # tear of smoke
    d.ellipse([96, 6, 122, 24], fill=P["grey"])
    return box


def panel_vatican(d, box):
    """A long table side-on, cream cloth, figures as rounded bars, ochre plates."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["sand"])
    d.rectangle([0, 0, w, 14], fill=P["ochre"])
    # figures behind the table
    cols = (P["plum"], P["navy"], P["red"], P["teal"], P["plum"], P["navy"])
    for i in range(7):
        x = 14 + i * 29
        col = cols[i % len(cols)]
        d.rounded_rectangle([x, 16, x + 16, 50], radius=6, fill=col)
        d.ellipse([x + 3, 6, x + 13, 18], fill=P["peach"])
    # table
    d.rectangle([6, 48, w - 6, 62], fill=P["paper"])
    d.rectangle([6, 62, w - 6, 70], fill=P["grey"])
    # plates
    for i in range(8):
        x = 16 + i * 25
        d.ellipse([x, 44, x + 16, 52], fill=P["ochre"])
    return box


def panel_india(d, box):
    """A raised fist inside a red ring over three grey phone screens."""
    w, h = box[2], box[3]
    P = PALETTE
    d.rectangle([0, 0, w, h], fill=P["sky"])
    # phone screens
    for i, x in enumerate((20, 88, 156)):
        d.rounded_rectangle([x, 40, x + 50, h - 6], radius=5, fill=P["grey"])
        d.rounded_rectangle([x + 5, 46, x + 45, h - 14], radius=3, fill=P["sand"])
        d.rectangle([x + 5, 46, x + 45, 54], fill=P["plum"])
    # red ring
    cx, cy = w / 2.0, 34
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=P["red"], width=6)
    # fist
    d.rounded_rectangle([cx - 12, cy - 4, cx + 12, cy + 22], radius=4, fill=P["ink"])
    d.rounded_rectangle([cx - 15, cy - 16, cx + 15, cy + 2], radius=5, fill=P["ink"])
    d.rectangle([cx + 12, cy - 8, cx + 18, cy + 4], fill=P["ink"])
    d.rectangle([cx - 6, cy - 22, cx + 8, cy - 12], fill=P["ink"])
    return box


PANELS = {
    "lead": panel_lead,
    "libya": panel_libya,
    "dymer": panel_dymer,
    "house": panel_house,
    "cartel": panel_cartel,
    "factory": panel_factory,
    "lebanon": panel_lebanon,
    "vatican": panel_vatican,
    "india": panel_india,
}

PANEL_BG = {
    "lead": "sky",
    "libya": "sky",
    "dymer": "sky",
    "house": "sand",
    "cartel": "navy",
    "factory": "sand",
    "lebanon": "navy",
    "vatican": "sand",
    "india": "sky",
}


def paste_panel(page, name, x, y, width, height):
    """Draw a panel into its own layer and paste it, so it cannot leak out."""
    img, d = panel_layer(width, height, PALETTE[PANEL_BG[name]])
    PANELS[name](d, (0, 0, int(width), int(height)))
    page.paste(img, (int(x), int(y)))


# --------------------------------------------------------------------------
# the page
# --------------------------------------------------------------------------


def compose():
    G = GRID
    P = PALETTE
    E = EDITORIAL
    page = Image.new("RGB", (G["page"], G["page"]), P["paper"])
    d = ImageDraw.Draw(page)

    # top kicker, centred, red, letter-spaced
    text_centred(d, G["page"] / 2.0, G["kicker_y"], E["top_kicker"],
                 font("sans-bold", G["kicker_size"]), P["red"], G["kicker_track"])

    # nameplate
    plate_face = font("serif-bold", G["plate_size"])
    plate_w = advance(d, E["nameplate"], plate_face)
    assert plate_w <= G["page"] - 2 * G["margin"], "nameplate too wide"
    text_centred(d, G["page"] / 2.0, G["plate_y"], E["nameplate"], plate_face, P["ink"])

    # double rule
    rule(d, G["margin"], G["bar_y"], G["page"] - G["margin"], G["bar_h"], P["ink"])
    rule(d, G["margin"], G["hair_y"], G["page"] - G["margin"], 1, P["hairline"])

    # folio line
    folio_face = font("sans-bold", G["folio_size"])
    text_at(d, (G["margin"], G["folio_y"]), E["folio_left"], folio_face, P["grey"], 1.5)
    text_right(d, G["page"] - G["margin"], G["folio_y"], E["folio_right"],
               folio_face, P["grey"], 1.5)

    # ---- lead
    lead = E["lead"]
    lx, lw = G["lead_x"], G["lead_w"]
    text_at(d, (lx, G["lead_kick_y"]), lead["kicker"],
            font("sans-bold", G["lead_kick_size"]), P["red"], G["lead_kick_track"])
    head_face = font("serif-bold", G["lead_head_size"])
    for i, line in enumerate(lead["headline"]):
        assert advance(d, line, head_face) <= lw, "lead headline overflows: %r" % line
        text_at(d, (lx, G["lead_head_y"] + i * G["lead_head_lead"]), line,
                head_face, P["ink"])
    WIDTH_LOG.append(("lead-headline",
                      max(advance(d, l, head_face) for l in lead["headline"]), lw))
    paste_panel(page, lead["panel"], lx, G["lead_panel_y"], lw, G["lead_panel_h"])
    frame(d, (lx, G["lead_panel_y"], lx + lw, G["lead_panel_y"] + G["lead_panel_h"]),
          P["hairline"])
    deck_face = font("sans", G["lead_deck_size"])
    deck_lines = wrap(d, lead["deck"], deck_face, lw)
    assert len(deck_lines) <= 5, "lead deck needs %d lines" % len(deck_lines)
    para(d, lx, G["lead_deck_y"], deck_lines, deck_face, G["lead_deck_lead"],
         P["ink"], lw, "lead-deck")

    # ---- numbers spine
    sx, sw, sy, sh = G["spine_x"], G["spine_w"], G["spine_y"], G["spine_h"]
    d.rectangle([sx, sy, sx + sw - 1, sy + sh - 1], fill=P["ink"])
    d.rectangle([sx, sy, sx + 1, sy + sh - 1], fill=P["red"])
    text_at(d, (sx + G["spine_pad"], G["spine_head_y"]), E["numbers_header"],
            font("sans-bold", 11), P["paper"], 2)
    fig_face = font("sans-bold", G["spine_fig_size"])
    lab_face = font("sans", G["spine_label_size"])
    lab_w = sw - 2 * G["spine_pad"]
    # rows are as tall as their figure's ink plus their label; measure first so
    # the separators sit exactly where the stack puts them
    rows = []
    top = G["spine_row_y"]
    for fig, label in E["numbers"]:
        gap = max(G["spine_label_gap"], int(fig_face.getbbox(fig)[3]) + 4)
        labs = wrap(d, label, lab_face, lab_w)
        assert len(labs) <= 2, "number label needs %d lines" % len(labs)
        height = max(G["spine_row_h"], gap + len(labs) * G["spine_label_lead"] + 6)
        rows.append((fig, labs, top, gap, height))
        top += height
    assert top <= sy + sh + 2, "numbers spine overruns: %d" % top
    for i, (fig, labs, row_top, gap, height) in enumerate(rows):
        if i:
            rule(d, sx + 4, row_top - 8, sx + sw - 4, 1, "#3A342C")
        text_at(d, (sx + G["spine_pad"], row_top), fig, fig_face, P["paper"])
        para(d, sx + G["spine_pad"], row_top + gap, labs, lab_face,
             G["spine_label_lead"], "#CFC8BA", lab_w, "spine-label-%d" % i)
    assert rows[-1][2] + rows[-1][4] <= sy + sh

    # ---- cards
    kick_face = font("sans-bold", G["card_kick_size"])
    head_face = font("serif-bold", G["card_head_size"])
    deck_face = font("sans", G["card_deck_size"])
    for i, card in enumerate(E["cards"]):
        col = i % 4
        row = i // 4
        x = G["card_x"][col]
        y = G["card_row_y"][row]
        cw = G["card_w"]
        paste_panel(page, card["panel"], x, y, cw, G["card_art_h"])
        frame(d, (x, y, x + cw, y + G["card_art_h"]), P["hairline"])
        text_at(d, (x, y + G["card_kick_dy"]), card["kicker"],
                kick_face, P["red"], G["card_kick_track"])
        assert advance(d, card["kicker"], kick_face, G["card_kick_track"]) <= cw, \
            "card kicker overflows: %r" % card["kicker"]
        heads = wrap(d, card["headline"], head_face, cw)
        assert len(heads) <= 2, "card headline needs %d lines: %r" % (len(heads), card["headline"])
        para(d, x, y + G["card_head_dy"], heads, head_face, G["card_head_lead"],
             P["ink"], cw, "card-head-%d" % (i + 1))
        decks = wrap(d, card["deck"], deck_face, cw)
        assert len(decks) <= 4, "card deck needs %d lines: %r" % (len(decks), card["deck"])
        para(d, x, y + G["card_deck_dy"], decks, deck_face, G["card_deck_lead"],
             P["grey"], cw, "card-deck-%d" % (i + 1))

    # ---- also today
    rule(d, G["margin"], G["also_rule_y"], G["page"] - G["margin"], 1, P["hairline"])
    text_at(d, (G["margin"], G["also_head_y"]), E["also_header"],
            font("sans-bold", 12), P["red"], 2)
    ak_face = font("sans-bold", 10)
    ah_face = font("serif-bold", G["also_size"])
    for i, (kick, head) in enumerate(E["also"]):
        x = G["also_x"][i]
        aw = G["also_w"]
        text_at(d, (x, G["also_kick_y"]), kick, ak_face, P["red"], 1.5)
        assert advance(d, kick, ak_face, 1.5) <= aw, "also kicker overflows"
        lines = wrap(d, head, ah_face, aw)
        assert len(lines) <= 2, "also headline needs %d lines" % len(lines)
        para(d, x, G["also_head_y2"], lines, ah_face, G["also_lead"], P["ink"],
             aw, "also-head-%d" % (i + 1))

    # ---- footer
    text_centred(d, G["page"] / 2.0, G["footer_y"], E["footer"],
                 font("sans", G["footer_size"]), P["grey"])

    return page


def main(argv):
    if len(argv) < 2:
        print("usage: render.py OUT.png")
        return 2
    out = argv[1]
    page = compose()
    assert page.size == (GRID["page"], GRID["page"])
    page.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s  %dx%d  %d bytes" % (out, page.size[0], page.size[1], size))
    worst = sorted(WIDTH_LOG, key=lambda r: r[1] - r[2], reverse=True)[:4]
    for name, widest, width in worst:
        print("  column %-14s widest line %6.1f px of %6.1f px" % (name, widest, width))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
