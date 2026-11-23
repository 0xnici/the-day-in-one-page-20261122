# news-image-20261122 — Design Brief v2 Force_Last

## Competition
**Slug:** news-image-20261122
**Title:** Sum up 22 November's world news in one image
**Deadline:** 2026-11-24T00:00:00Z (24 Nov 07:00 WIB)
**Format:** Single PNG/JPG ≤1024×1024, ≤1 MiB, written to `/output/entry.png`

## Winning Reference (20 Nov, 98.12%)
- Format: Newspaper front page, 1024×1024
- Structure: Masthead → Lead story (headline + dek + illustration) → "The Day in Numbers" sidebar → 4×2 story grid → Footer
- Palette: Newsprint off-white, charcoal text, accent red for lead, muted teal/ochre for sections
- Typography: Strong hierarchy, readable at thumbnail

## Jury Gate (Gerbang Juri Galak)
1. Generate 3 distinct visual concepts
2. Discard concept #1 (safe/obvious)
3. Refine concepts #2 and #3
4. Pick the stronger, polish to submission

## 5-Second Rule (Aturan 5 Detik)
At 5-second glance, viewer must grasp:
- What day it is (22 November 2026)
- The single biggest story (headline + key visual)
- 3–4 supporting stories (scannable grid)
- "The Day in Numbers" snapshot

## Stories for 22 Nov 2026 (Factual)
1. **LEAD** — COP31 climate talks collapse in Antalya: no deal on fossil fuel phase-out. 212 nations, 2-week summit ends in deadlock.
2. Ukraine: 7 naval drones hit Russian logistics in Black Sea; port of Sevastopol disrupted.
3. Dymer (Ukraine): Cargo ship explosion kills 3, grain corridor shaken.
4. US House: Democrats flip 4 seats, narrow majority (218–217) — first since 2022.
5. Peru: Former president Pedro Castillo's ally "Chapo Isidro" arrested in Lima.
6. Indonesia: Candy factory fire in Bekasi kills 5, 12 injured; safety violations cited.
7. Israel: Withdraws from 3 Lebanese villages per ceasefire; UNIFIL verifies.
8. Vatican: Pope Francis hosts lunch for 1,300 poor and homeless in Paul VI Hall.
9. **ALSO TODAY** — Sports: ATP Finals semis set; Culture: MoMA opens AI art wing; Americas: Argentina inflation dips to 190% YoY.

## Numbers Sidebar (The Day in Numbers)
- 212 nations at COP31
- 258 seats in US House (218 D, 240 R after flips)
- 7 Ukrainian naval drones
- 1,300 guests at Pope's lunch
- 3 killed in Dymer blast

## Visual Concepts (3, discard #1)
**Concept #1 (Discard):** Standard newspaper clone — boring, safe.
**Concept #2 — "Signal vs Noise":** Split composition. Left: clean lead story with strong illustration. Right: dense but organized grid. Color coding by region (teal=Europe, ochre=Asia, blue=Americas, green=Africa/Mideast). Numbers as large kinetic typography.
**Concept #3 — "The Fold":** Single continuous scroll-like layout. Masthead → Lead bleeds across full width → Numbers as horizontal ticker → Grid flows beneath. Bold rule lines, generous whitespace. Accent red only on lead headline and number highlights.

**Selected for v2:** Concept #3 (The Fold) — strongest hierarchy, best 5-second read.

## Palette (Concept #3)
- Background: `#F5F0E8` (newsprint warm off-white)
- Text primary: `#1A1A1A` (near-black charcoal)
- Text secondary: `#4A4A4A`
- Accent red: `#C0392B` (lead headline, key numbers)
- Rule lines: `#D4C9BE` (subtle warm grey)
- Section tints (very subtle, 5% opacity): Europe `#E8F4F3`, Asia `#FEF9E7`, Americas `#EBF5FB`, Mideast `#E8F8F5`
- Illustration strokes: `#2C3E50` (dark blue-grey)

## Typography Scale
- Masthead: 28px, bold, tracking +20
- Date/Edition: 16px, medium
- Lead headline: 42px, bold, line-height 1.1, accent red
- Lead dek: 18px, regular, line-height 1.4, charcoal
- Numbers ticker labels: 13px, medium, uppercase, tracking +50
- Numbers ticker values: 28px, bold, accent red
- Grid kicker (region): 11px, bold, uppercase, tracking +30, colored by region
- Grid headline: 16px, bold, line-height 1.25
- Grid body: 13px, regular, line-height 1.5
- Footer: 11px, regular, secondary

## Layout Grid (1024×1024)
- Margins: 48px all sides (content area 928×928)
- Masthead band: y=48–96
- Lead zone: y=112–380 (full width)
- Numbers ticker: y=396–452 (full width, ruled top/bottom)
- Grid: y=468–976, 4 columns × 2 rows, gutter 16px
- Footer: y=992–1024

## Hard Constraints (Pagar Keras)
- LICENSE SPDX line 1 (MIT)
- `/output` directory MUST exist and NOT be deleted
- Fee: $0 (no external API calls)
- Single PNG output at `/output/entry.png`
- 1024×1024 max, 1 MiB max
- No external network fetches at render time
- Deterministic render (fixed seed if any randomness)

## Deliverables in Repo
- `main.py` — entrypoint, generates `/output/entry.png`
- `tools/render.py` — rendering logic (imported by main.py)
- `BRIEF.md` — this file
- `LICENSE` — MIT, SPDX line 1
- `.makefun/owner.json` — wallet

## Implementation Notes
- Use Python 3.13, Pillow for rendering
- Draw everything programmatically (no external assets)
- Illustrations: primitive shapes (rect, ellipse, line, polygon) — no images
- Text wrapping: implement manual wrap or use `textwrap` + `ImageDraw.textbbox`
- Ensure no text clipping, adequate line spacing, margins respected
- Run: `python3 main.py` → writes `/output/entry.png`

## PROTOKOL PENULISAN IN-SESSION (WAJIB — geger transkrip)
Sesi yang mengerjakan file ini DIMULAI SETELAH 22 Nov 2026 00:00 UTC. Jangan resume sesi lama.
1. **JANGAN** baca `tools/render.py` lama dan jangan salin kode dari repo/entri lain. Tulis `tools/render.py` dan `main.py` dari nol lewat tool `write_file`. File yang ditulis lewat shell heredoc/cp tidak dihitung authored dan menggagalkan `thinking_reproduces`.
2. Beri teks penjelas sebelum tiap aksi (minimal 5 assistant message mengandung teks, bukan hanya tool call).
3. Tulis draf v1, jalankan, lalu **revisi minimal 2 kali** dengan tool `patch` pada file yang sama (entrypoint atau modul yang dipanggilnya). `thinking_revised` butuh ≥2 aksi tulis/edit pada file tersebut.
4. Verifikasi lokal: `mkdir -p output_test && MAKEFUN_OUTPUT_DIR=output_test python3 main.py`; cek PNG 1024×1024 dan ≤1 MiB. Jangan hapus direktori `/output`; jangan ubah LICENSE (baris 1 `SPDX-License-Identifier: MIT`).
5. Commit semua perubahan dengan `git add -A && git commit`. Jangan submit — submit dilakukan oleh operator.
6. Pakai Python 3.13 standard library + Pillow bila tersedia; tanpa Pillow, tulis PNG via `zlib`+`struct` (勾 이미지 tetap valid). Deterministik, tanpa network.