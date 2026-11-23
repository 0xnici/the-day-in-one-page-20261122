"""Render the front page of "THE DAY IN BRIEF" for Sunday 22 November 2026.

Concept #3 — "The Fold": Single continuous scroll-like layout.
Masthead → Lead bleeds across full width → Numbers as horizontal ticker → Grid flows beneath.
Bold rule lines, generous whitespace. Accent red only on lead headline and number highlights.

Output: 1024x1024 PNG written to the path passed as argv[1].
Dependencies: Python 3.13 stdlib + Pillow. No network, no randomness, deterministic.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Palette (Concept #3)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg": "#F5F0E8",            # newsprint warm off-white
    "text_primary": "#1A1A1A",  # near-black charcoal
    "text_secondary": "#4A4A4A",
    "accent_red": "#C0392B",    # lead headline, key numbers
    "rule": "#D4C9BE",          # subtle warm grey
    "illustration": "#2C3E50",  # dark blue-grey for illustration strokes
    "tint_europe": "#E8F4F3",   # 5% opacity teal
    "tint_asia": "#FEF9E7",     # 5% opacity ochre
    "tint_americas": "#EBF5FB", # 5% opacity blue
    "tint_mideast": "#E8F8F5",  # 5% opacity green
}

# ---------------------------------------------------------------------------
# Layout Grid (1024x1024)
# ---------------------------------------------------------------------------
GRID = {
    "page": 1024,
    "margin": 48,               # content area 928x928
    # Masthead band: y=48-96
    "masthead_y": 48,
    "masthead_h": 48,
    # Lead zone: y=112-380 (full width)
    "lead_y": 112,
    "lead_h": 268,
    # Numbers ticker: y=396-452 (full width, ruled top/bottom)
    "numbers_y": 396,
    "numbers_h": 56,
    # Grid: y=468-976, 4 columns x 2 rows, gutter 16px
    "grid_y": 468,
    "grid_h": 508,
    "grid_cols": 4,
    "grid_rows": 2,
    "grid_gutter": 16,
    # Footer: y=992-1024
    "footer_y": 992,
    "footer_h": 32,
}

# ---------------------------------------------------------------------------
# Typography Scale
# ---------------------------------------------------------------------------
TYPO = {
    "masthead": {"size": 28, "weight": "bold", "tracking": 20},
    "date_edition": {"size": 16, "weight": "medium", "tracking": 0},
    "lead_headline": {"size": 42, "weight": "bold", "leading": 1.1},
    "lead_dek": {"size": 18, "weight": "regular", "leading": 1.4},
    "numbers_label": {"size": 13, "weight": "medium", "tracking": 50, "uppercase": True},
    "numbers_value": {"size": 28, "weight": "bold"},
    "grid_kicker": {"size": 11, "weight": "bold", "tracking": 30, "uppercase": True},
    "grid_headline": {"size": 16, "weight": "bold", "leading": 1.25},
    "grid_body": {"size": 13, "weight": "regular", "leading": 1.5},
    "footer": {"size": 11, "weight": "regular"},
}

# ---------------------------------------------------------------------------
# Editorial Content (verbatim from BRIEF.md)
# ---------------------------------------------------------------------------
EDITORIAL = {
    "masthead": "THE DAY IN BRIEF",
    "date_edition": "SUNDAY 22 NOVEMBER 2026  ·  EDITION 22",
    "lead": {
        "kicker": "ANTALYA  ·  CLIMATE  ·  THE LEAD",
        "headline": [
            "COP31 climate talks collapse",
            "in Antalya — no deal on fossil fuels"
        ],
        "dek": (
            "The two-week summit of 212 nations ended in deadlock on Sunday. "
            "The final draft, the Antalya Pact, never named fossil fuels; the EU, "
            "Britain, Panama and vulnerable states refused it, and the presidency "
            "put the decisions to no vote. Nearly 200 countries leave Antalya with "
            "no new joint plan as 2026 heads for the warmest year on record."
        ),
    },
    "numbers_header": "THE DAY IN NUMBERS",
    "numbers": [
        ("212", "nations at COP31"),
        ("258", "House seats won by Democrats"),
        ("7", "Ukrainian naval drones in Black Sea"),
        ("1,300", "guests at Pope's lunch"),
        ("3", "killed in Dymer cargo ship blast"),
    ],
    "grid": [
        # Row 1
        {
            "region": "Europe",
            "tint": "tint_europe",
            "kicker": "BLACK SEA  ·  WAR",
            "headline": "7 naval drones hit Russian logistics",
            "body": "Port of Sevastopol disrupted after Ukrainian sea drones struck Russian supply vessels overnight.",
        },
        {
            "region": "Europe",
            "tint": "tint_europe",
            "kicker": "DYMER  ·  WAR",
            "headline": "Cargo ship explosion kills 3",
            "body": "Grain corridor shaken after blast wrecks vessel near Kyiv; rescuers search rubble through Sunday.",
        },
        {
            "region": "Americas",
            "tint": "tint_americas",
            "kicker": "WASHINGTON  ·  POLITICS",
            "headline": "Democrats flip 4 seats, take narrow House majority",
            "body": "218–217 split gives Democrats first House control since 2022; divided government with GOP president.",
        },
        {
            "region": "Americas",
            "tint": "tint_americas",
            "kicker": "PERU  ·  CRIME",
            "headline": "Castillo ally 'Chapo Isidro' arrested in Lima",
            "body": "Fausto Isidro Meza Flores, former president's associate, seized in Guasave operation.",
        },
        # Row 2
        {
            "region": "Asia",
            "tint": "tint_asia",
            "kicker": "INDONESIA  ·  DISASTER",
            "headline": "Candy factory fire in Bekasi kills 5",
            "body": "12 injured; investigators cite safety violations at the plant. Dozens unaccounted for initially.",
        },
        {
            "region": "Mideast",
            "tint": "tint_mideast",
            "kicker": "SOUTH LEBANON  ·  MIDEAST",
            "headline": "Israel withdraws from 3 villages per ceasefire",
            "body": "UNIFIL verifies pullback; villagers return to wrecked homes as demolitions continue nearby.",
        },
        {
            "region": "Europe",
            "tint": "tint_europe",
            "kicker": "VATICAN  ·  SOCIETY",
            "headline": "Pope Francis hosts lunch for 1,300 poor",
            "body": "Tenth World Day of the Poor marked in Paul VI Hall with homeless and vulnerable guests.",
        },
        {
            "region": "Americas",
            "tint": "tint_americas",
            "kicker": "ARGENTINA  ·  ECONOMY",
            "headline": "Inflation dips to 190% YoY",
            "body": "Monthly easing continues but annual rate remains among world's highest; peso stabilizes.",
        },
    ],
    "also_today": [
        ("SPORT", "ATP Finals semis set"),
        ("CULTURE", "MoMA opens AI art wing"),
        ("AMERICAS", "Argentina inflation dips to 190% YoY"),
    ],
    "footer": "Compiled from the day's reporting  ·  22 November 2026",
}

# ---------------------------------------------------------------------------
# Font loading
# ---------------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
FONT_FILES = {
    "regular": "DejaVuSans.ttf",
    "bold": "DejaVuSans-Bold.ttf",
    "serif": "DejaVuSerif.ttf",
    "serif_bold": "DejaVuSerif-Bold.ttf",
}

_FONT_CACHE = {}

def get_font(face: str, size: int) -> ImageFont.FreeTypeFont:
    """Load and cache a font."""
    key = (face, int(round(size)))
    if key not in _FONT_CACHE:
        path = os.path.join(FONT_DIR, FONT_FILES[face])
        _FONT_CACHE[key] = ImageFont.truetype(path, int(round(size)))
    return _FONT_CACHE[key]

# ---------------------------------------------------------------------------
# Text measurement and drawing helpers
# ---------------------------------------------------------------------------
def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, tracking: float = 0.0) -> float:
    """Measure text width with optional letter-spacing (tracking)."""
    if tracking == 0.0:
        return draw.textlength(text, font=font)
    total = 0.0
    for ch in text:
        total += draw.textlength(ch, font=font)
    return total + tracking * max(len(text) - 1, 0)

def draw_text(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, font: ImageFont.FreeTypeFont,
              fill: str, tracking: float = 0.0, anchor: str = "la") -> float:
    """Draw text with optional tracking. Returns width drawn."""
    if tracking == 0.0:
        draw.text((x, y), text, font=font, fill=fill, anchor=anchor)
        return draw.textlength(text, font=font)
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill, anchor=anchor)
        cx += draw.textlength(ch, font=font) + tracking
    return cx - x - tracking

def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
              max_width: float, tracking: float = 0.0) -> list[str]:
    """Wrap text to fit within max_width. Returns list of lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        word_w = measure_text(draw, word, font, tracking)
        if word_w > max_width:
            # Word too long - force it anyway (shouldn't happen with our content)
            if current:
                lines.append(current)
            lines.append(word)
            current = ""
            continue
        trial = (current + " " + word).strip()
        if not current or measure_text(draw, trial, font, tracking) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

def draw_wrapped(draw: ImageDraw.ImageDraw, x: float, y: float, lines: list[str],
                 font: ImageFont.FreeTypeFont, leading: float, fill: str,
                 tracking: float = 0.0) -> float:
    """Draw multiple pre-wrapped lines. Returns y after last line."""
    for i, line in enumerate(lines):
        draw_text(draw, x, y + i * leading, line, font, fill, tracking)
    return y + len(lines) * leading

def draw_rule(draw: ImageDraw.ImageDraw, x0: float, y: float, x1: float,
              thickness: float, fill: str) -> None:
    """Draw a horizontal rule."""
    draw.rectangle([x0, y, x1, y + thickness - 1], fill=fill)

# ---------------------------------------------------------------------------
# Illustration primitives (Concept #3 style: bold rule lines, generous whitespace)
# ---------------------------------------------------------------------------
def draw_lead_illustration(draw: ImageDraw.ImageDraw, x: float, y: float,
                           width: float, height: float) -> None:
    """Draw lead story illustration: globe with flame, red circle-slash, ANTALYA pin."""
    P = PALETTE
    # Background wash
    draw.rectangle([x, y, x + width, y + height], fill=PALETTE["tint_europe"])

    # Globe center
    cx = x + 130
    cy = y + height * 0.5
    r = 70

    # Globe circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=P["illustration"], width=3)
    # Meridian and equator
    draw.line([cx - r, cy, cx + r, cy], fill=P["illustration"], width=2)
    draw.line([cx, cy - r, cx, cy + r], fill=P["illustration"], width=2)

    # Landmass suggestion (simple ellipses)
    draw.ellipse([cx - 45, cy - 40, cx - 5, cy - 5], fill=P["illustration"])
    draw.ellipse([cx - 35, cy + 5, cx + 10, cy + 30], fill=P["illustration"])
    draw.ellipse([cx + 15, cy - 35, cx + 50, cy - 10], fill=P["illustration"])

    # Dark flame over globe
    fx, fy = cx + 45, cy + 25
    draw.polygon([
        (fx, fy), (fx - 24, fy - 40), (fx - 10, fy - 58),
        (fx, fy - 38), (fx + 12, fy - 74), (fx + 26, fy - 44),
        (fx + 30, fy - 18)
    ], fill=P["text_primary"])
    draw.polygon([
        (fx, fy - 6), (fx - 10, fy - 30), (fx - 2, fy - 42),
        (fx + 8, fy - 24), (fx + 14, fy - 40), (fx + 18, fy - 20),
        (fx + 12, fy - 4)
    ], fill=P["accent_red"])
    draw.polygon([
        (fx + 2, fy - 8), (fx - 2, fy - 22), (fx + 6, fy - 28),
        (fx + 12, fy - 12)
    ], fill="#E3A33C")

    # Red circle-and-slash (no fossil fuels)
    rx, ry, rr = fx + 2, fy - 38, 30
    draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr], outline=P["accent_red"], width=6)
    draw.line([rx - 22, ry + 22, rx + 22, ry - 22], fill=P["accent_red"], width=6)

    # ANTALYA pin on right side
    px, py = x + width - 100, y + height - 60
    draw.polygon([(px - 14, py + 18), (px + 14, py + 18), (px, py + 40)], fill=P["accent_red"])
    draw.ellipse([px - 17, py - 17, px + 17, py + 17], fill=P["accent_red"])
    draw.ellipse([px - 6, py - 6, px + 6, py + 6], fill=P["bg"])

    pin_font = get_font("bold", 10)
    label = "ANTALYA"
    lw = measure_text(draw, label, pin_font, 1.5)
    draw.rectangle([px - lw/2 - 6, py + 44, px + lw/2 + 6, py + 62], fill=P["text_primary"])
    draw_text(draw, px - lw/2, py + 46, label, pin_font, P["bg"], 1.5)

    # Delegate markers
    for i, col in enumerate((P["illustration"], "#4B3B57", P["tint_europe"])):
        bx = x + width - 230 + i * 22
        draw.rectangle([bx, y + height - 38, bx + 12, y + height - 12], fill=col)
        draw.ellipse([bx + 1, y + height - 50, bx + 11, y + height - 40], fill=col)


def draw_grid_illustration(draw: ImageDraw.ImageDraw, x: float, y: float,
                           width: float, height: float, region: str) -> None:
    """Draw a small illustrative icon for each grid card based on region/story."""
    P = PALETTE
    tint = P.get(EDITORIAL["grid"][0]["tint"], P["bg"])  # fallback
    # Use region tint as background
    draw.rectangle([x, y, x + width, y + height], fill=tint)

    cx = x + width / 2
    cy = y + height / 2

    # Simple iconic shapes per region
    if region == "Europe":
        # Naval drone silhouette
        draw.polygon([
            (cx - 20, cy + 10), (cx + 20, cy + 10),
            (cx + 15, cy - 5), (cx - 15, cy - 5)
        ], fill=P["illustration"])
        draw.line([(cx, cy - 5), (cx, cy - 20)], fill=P["illustration"], width=3)
        draw.polygon([(cx - 6, cy - 22), (cx + 6, cy - 22), (cx, cy - 30)], fill=P["accent_red"])
    elif region == "Americas":
        # Capitol dome or gavel
        draw.rectangle([cx - 18, cy - 5, cx + 18, cy + 5], fill=P["illustration"])
        draw.ellipse([cx - 10, cy - 20, cx + 10, cy + 2], fill=P["illustration"])
        draw.rectangle([cx - 4, cy - 30, cx + 4, cy - 18], fill=P["illustration"])
    elif region == "Asia":
        # Factory silhouette with smoke
        draw.polygon([(cx - 25, cy + 15), (cx - 25, cy - 10), (cx - 10, cy - 15),
                      (cx - 10, cy - 10), (cx + 5, cy - 15), (cx + 5, cy - 10),
                      (cx + 20, cy - 15), (cx + 20, cy - 10), (cx + 25, cy + 15)],
                     fill=P["illustration"])
        # Smoke
        draw.ellipse([cx - 5, cy - 30, cx + 10, cy - 15], fill="#888888")
        draw.ellipse([cx + 10, cy - 35, cx + 22, cy - 23], fill="#888888")
    elif region == "Mideast":
        # Olive branch / house row
        for i in range(4):
            hx = cx - 28 + i * 14
            draw.rectangle([hx, cy - 15, hx + 10, cy + 5], fill=P["illustration"])
            draw.rectangle([hx, cy - 19, hx + 10, cy - 15], fill="#E3A33C")
    else:
        # Generic: circle with cross
        draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=P["illustration"], width=3)
        draw.line([cx - 10, cy, cx + 10, cy], fill=P["illustration"], width=2)
        draw.line([cx, cy - 10, cx, cy + 10], fill=P["illustration"], width=2)


# ---------------------------------------------------------------------------
# Main composition
# ---------------------------------------------------------------------------
def compose() -> Image.Image:
    G = GRID
    P = PALETTE
    T = TYPO
    E = EDITORIAL

    page = Image.new("RGB", (G["page"], G["page"]), P["bg"])
    draw = ImageDraw.Draw(page)

    content_left = G["margin"]
    content_right = G["page"] - G["margin"]
    content_width = content_right - content_left

    # ============================================================
    # MASTHEAD BAND (y=48-96)
    # ============================================================
    masthead_font = get_font("bold", T["masthead"]["size"])
    draw_text(draw, G["page"] / 2, G["masthead_y"] + 8, E["masthead"],
              masthead_font, P["text_primary"], T["masthead"]["tracking"], anchor="ma")

    date_font = get_font("regular", T["date_edition"]["size"])
    draw_text(draw, G["page"] / 2, G["masthead_y"] + 36, E["date_edition"],
              date_font, P["text_secondary"], anchor="ma")

    # Thin rule under masthead
    draw_rule(draw, content_left, G["masthead_y"] + G["masthead_h"],
              content_right, 1, P["rule"])

    # ============================================================
    # LEAD ZONE (y=112-380, full width)
    # ============================================================
    lead_left = content_left
    lead_right = content_right
    lead_width = lead_right - lead_left

    # Lead kicker
    kicker_font = get_font("bold", 14)
    draw_text(draw, lead_left, G["lead_y"], E["lead"]["kicker"],
              kicker_font, P["accent_red"], 2.0)

    # Lead headline (two lines, accent red, large)
    headline_font = get_font("bold", T["lead_headline"]["size"])
    headline_leading = T["lead_headline"]["size"] * T["lead_headline"]["leading"]
    for i, line in enumerate(E["lead"]["headline"]):
        draw_text(draw, lead_left, G["lead_y"] + 30 + i * headline_leading,
                  line, headline_font, P["accent_red"])

    # Lead illustration (right side of lead zone, approx 40% width)
    illus_width = lead_width * 0.38
    illus_x = lead_right - illus_width
    illus_y = G["lead_y"] + 30
    illus_h = G["lead_h"] - 40
    draw_lead_illustration(draw, illus_x, illus_y, illus_width, illus_h)

    # Lead dek (left side, wraps in remaining width)
    dek_font = get_font("regular", T["lead_dek"]["size"])
    dek_leading = T["lead_dek"]["size"] * T["lead_dek"]["leading"]
    dek_width = illus_x - lead_left - 24  # gap before illustration
    dek_lines = wrap_text(draw, E["lead"]["dek"], dek_font, dek_width)
    dek_y = G["lead_y"] + 30 + len(E["lead"]["headline"]) * headline_leading + 16
    draw_wrapped(draw, lead_left, dek_y, dek_lines, dek_font, dek_leading, P["text_primary"])

    # Thick rule under lead
    draw_rule(draw, content_left, G["lead_y"] + G["lead_h"],
              content_right, 2, P["rule"])

    # ============================================================
    # NUMBERS TICKER (y=396-452, full width, ruled top/bottom)
    # ============================================================
    ticker_top = G["numbers_y"]
    ticker_bottom = G["numbers_y"] + G["numbers_h"]

    # Top rule
    draw_rule(draw, content_left, ticker_top, content_right, 2, P["rule"])

    # Header
    num_header_font = get_font("bold", 12)
    draw_text(draw, content_left, ticker_top + 6, E["numbers_header"],
              num_header_font, P["accent_red"], 2.0)

    # Number items - horizontal layout
    num_value_font = get_font("bold", T["numbers_value"]["size"])
    num_label_font = get_font("bold", T["numbers_label"]["size"])

    num_count = len(E["numbers"])
    num_spacing = (content_width - 40) / num_count  # 20px padding each side
    start_x = content_left + 20

    for i, (value, label) in enumerate(E["numbers"]):
        cx = start_x + i * num_spacing + num_spacing / 2
        # Value (large, red, centered)
        draw_text(draw, cx, ticker_top + 18, value,
                  num_value_font, P["accent_red"], anchor="ma")
        # Label (small, uppercase, tracking, centered below)
        label_upper = label.upper() if T["numbers_label"]["uppercase"] else label
        draw_text(draw, cx, ticker_top + 18 + T["numbers_value"]["size"] + 2, label_upper,
                  num_label_font, P["text_secondary"], T["numbers_label"]["tracking"], anchor="ma")

    # Bottom rule
    draw_rule(draw, content_left, ticker_bottom, content_right, 2, P["rule"])

    # ============================================================
    # GRID (y=468-976, 4 cols x 2 rows, gutter 16px)
    # ============================================================
    grid_top = G["grid_y"]
    grid_left = content_left
    grid_right = content_right
    grid_width = grid_right - grid_left
    col_width = (grid_width - (G["grid_cols"] - 1) * G["grid_gutter"]) / G["grid_cols"]
    row_height = (G["grid_h"] - G["grid_gutter"]) / G["grid_rows"]

    kicker_font = get_font("bold", T["grid_kicker"]["size"])
    headline_font = get_font("bold", T["grid_headline"]["size"])
    body_font = get_font("regular", T["grid_body"]["size"])
    headline_leading = T["grid_headline"]["size"] * T["grid_headline"]["leading"]
    body_leading = T["grid_body"]["size"] * T["grid_body"]["leading"]

    for idx, card in enumerate(E["grid"]):
        col = idx % G["grid_cols"]
        row = idx // G["grid_cols"]

        x = grid_left + col * (col_width + G["grid_gutter"])
        y = grid_top + row * (row_height + G["grid_gutter"])

        card_width = col_width
        card_height = row_height

        # Subtle tint background for the whole card
        tint_color = P.get(card["tint"], P["bg"])
        draw.rectangle([x, y, x + card_width, y + card_height], fill=tint_color)

        # Illustration at top (fixed height ~80px)
        illus_h = 80
        draw_grid_illustration(draw, x, y, card_width, illus_h, card["region"])

        # Kicker (region label, red, uppercase, tracking)
        kicker_y = y + illus_h + 8
        draw_text(draw, x + 8, kicker_y, card["kicker"],
                  kicker_font, P["accent_red"], T["grid_kicker"]["tracking"])

        # Thin accent line under kicker
        kicker_w = measure_text(draw, card["kicker"], kicker_font, T["grid_kicker"]["tracking"])
        draw_rule(draw, x + 8, kicker_y + T["grid_kicker"]["size"] + 3,
                  x + 8 + kicker_w, 1.5, P["accent_red"])

        # Headline (wraps to 2 lines max)
        headline_y = kicker_y + T["grid_kicker"]["size"] + 12
        headline_lines = wrap_text(draw, card["headline"], headline_font, card_width - 16)
        headline_lines = headline_lines[:2]  # clamp to 2 lines
        draw_wrapped(draw, x + 8, headline_y, headline_lines, headline_font,
                     headline_leading, P["text_primary"])

        # Body (wraps to 3-4 lines)
        body_y = headline_y + len(headline_lines) * headline_leading + 4
        body_lines = wrap_text(draw, card["body"], body_font, card_width - 16)
        body_lines = body_lines[:4]  # clamp to 4 lines
        draw_wrapped(draw, x + 8, body_y, body_lines, body_font,
                     body_leading, P["text_secondary"])

        # Thin rule between cards (vertical)
        if col < G["grid_cols"] - 1:
            rule_x = x + card_width + G["grid_gutter"] / 2
            draw_rule(draw, rule_x, y + 4, rule_x + 1, card_height - 8, P["rule"])

    # Horizontal rule between rows
    mid_y = grid_top + row_height + G["grid_gutter"] / 2
    draw_rule(draw, grid_left, mid_y, grid_right, 1, P["rule"])

    # ============================================================
    # FOOTER (y=992-1024)
    # ============================================================
    footer_font = get_font("regular", T["footer"]["size"])
    draw_text(draw, G["page"] / 2, G["footer_y"] + 10, E["footer"],
              footer_font, P["text_secondary"], anchor="ma")

    return page


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: render.py OUT.png")
        return 2

    out_path = argv[1]
    page = compose()
    assert page.size == (GRID["page"], GRID["page"]), f"Wrong size: {page.size}"
    page.save(out_path, format="PNG", optimize=True)
    size = os.path.getsize(out_path)
    print(f"wrote {out_path}  {page.size[0]}x{page.size[1]}  {size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))