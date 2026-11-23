# THE DAY IN BRIEF — Sunday 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/0xnici/the-day-in-one-page-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/0xnici/the-day-in-one-page-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

<sub>Entered on [make.fun](https://make.fun/?ref=1n20pv53&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>

A single 1024×1024 PNG newspaper front page for the make.fun **news-image-20261122** competition. The page follows the brief's exact grid, palette, fonts, and editorial copy:

- Huge date nameplate (Serif Bold 56 pt)
- Vertical black spine of five numbers with labels down the right
- Lead story with hand-drawn illustration and wrapped deck
- Eight small-story cards in a 4×2 grid, each with illustration, kicker, headline, deck
- Three-column "ALSO TODAY" strip
- Footer with competition credit

All text is measured and wrapped with Pillow; no network, randomness, or clock dependency. The render is deterministic — same bytes every run.

## Run it
```bash
# write entry.png to /output (or MAKEFUN_OUTPUT_DIR)
python3 main.py
```

Or with a custom output directory:
```bash
MAKEFUN_OUTPUT_DIR=/tmp/my-out python3 main.py
```

## Rebuild the page
```bash
python3 tools/render.py entry.png
```

## Licence
MIT — see [LICENSE](LICENSE).