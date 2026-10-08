# 🎤 Out of the Hat

**In the fifty Eurovision finals whose running order was drawn by lot, songs drawn into the last third finished about one and a half places higher than songs drawn into the first.**

→ **[Open it](https://tnriley.github.io/out-of-the-hat/)**

From 1957 to 2006 Eurovision drew its running order out of a hat, which makes half a century of finals an experiment nobody had to design. Every result table was extracted from each contest's own Wikipedia article, and the late-slot advantage shows up twice, on two measures kept apart: finishing place in the drawn finals, and qualification from the drawn semi-finals (38% of the first third got through, 66% of the last). A control checks that the draw was clean by testing slot against each country's earlier results, and the page withholds its headline if that ever drifts. The famous curse of slot two turns out to be chance: replay history with random winners and some regular slot goes winless two times in three, and slot sixteen has never won either.

## Running it

One self-contained HTML file. No build step, no server, no network access at runtime — open `index.html` in a browser, or serve the directory with any static host.

```bash
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Rebuilding it from scratch

[REBUILD.md](REBUILD.md) is written for an LLM with a shell and nothing else: the data sources and their quirks, the processing decisions, the page's structure and interactions, and a table of expected values to check the result against.

## Source

The full build pipeline is in [`src/`](src/), with a README describing how to regenerate the page from scratch.

## Data

- **[English Wikipedia, the articles Eurovision Song Contest 1957 to Eurovision Song Contest 2025: result tables and each article's account of how its running order was set, read through the MediaWiki parse API on 2026-10-07 with revision ids recorded](https://en.wikipedia.org/wiki/Eurovision_Song_Contest)** — CC BY-SA 4.0

Every figure on the page is computed from the data shipped with it. Check the page's own methods panel for how each number is derived and where it should not be pushed.

## Built with

Python, BeautifulSoup, MediaWiki parse API, vanilla JS, SVG, base64 typed-array payload, in-page permutation tests.

## Licence

Code is MIT (see [LICENSE](LICENSE)). Data keeps the licence of its source, listed above.

---

Part of [Quick Projects](https://github.com/TNRiley/quick-projects) — one self-contained thing, built in one session. First published 2026-10-07.
