# Rebuilding Out of the Hat

Enough to reproduce this project from nothing: a shell, Python 3.11+ with `beautifulsoup4`,
and about ten minutes, most of it a polite download.

## 1. What is being built

One self-contained HTML page about the running order of the Eurovision Song Contest.

From 1957 to 2006 the order songs were performed in was **drawn by lot**. That makes fifty
finals a randomised experiment: no producer chose who went late, so if late songs did better,
the slot did it and not the song.

**The finding the page exists to show:** in those fifty finals, songs drawn into the last third
of the night finished about one and a half places higher than songs drawn into the first
(mean place 11.4 against 9.8). A second, independent measure agrees: in the semi-finals whose order
was drawn (2004 to 2012, slot-choosers removed), 38% of the first third qualified against 66% of
the last third.

**The secondary finding:** the folk "curse of slot two" (no song performed second has ever won) is
what chance produces. If every song in every final had an equal chance of winning, slot two would
go winless about 3% of the time, but *some* regularly used slot goes winless about two times in
three. Slot sixteen has never won either, and nobody mentions it.

## 2. Data

One source. English Wikipedia, articles `Eurovision Song Contest 1957` through
`Eurovision Song Contest 2025` (2020 was cancelled, 1956 published no places), fetched as
rendered HTML through the MediaWiki parse API:

```
https://en.wikipedia.org/w/api.php?action=parse&page=Eurovision_Song_Contest_<YEAR>&prop=text|revid&format=json&formatversion=2&redirects=1
```

69 requests, about 43 MB in all, one second apart, with a descriptive User-Agent. Licence: CC BY-SA
4.0. `src/fetch.py` stores each article's `revid` so the exact version read is on record (the
2026-10-07 build read revision 1378018909 of the 2025 article, for example).

**Why not an existing dataset:** the widely used `Spijkervet/eurovision-dataset` on GitHub has no
licence and was scraped from a fan site. It was set aside before anything was computed from it.

**Why rendered HTML and not wikitext:** the result tables are built from templates, so the wikitext
is much harder to read than the HTML the templates produce.

### Quirks that will bite

- **Find the result tables by header, not by position.** A result table is any table whose first
  header row starts `R/O` and includes `Place`. Points are under `Points` from 1975 on and `Votes`
  before that. The caption names the show: `semi-final` with `first` or `second`, plain
  `semi-final` for 2004 to 2007, `qualifying round` for 1996, otherwise the final.
- **1956 has no Place column** (only the winner was announced) and drops out by itself.
- **Strip footnote markers** like `[a]` and `[ 12 ]` from every cell.
- **The Place column carries `‡`** for the 2008 and 2009 semi-final jury wild cards; take the
  leading integer.
- **Netherlands 2024** has `—` for place: it was disqualified after its semi-final and did not
  perform. Drop it and close up the slots.
- **Withdrawn countries leave gaps in R/O numbering** in some years. Use the *rank* of R/O within
  a show as the slot, never the raw number.
- **Renamed, not replaced:** treat `Czechia` as `Czech Republic` and `North Macedonia` as
  `Macedonia`. Keep `Yugoslavia`, `Serbia and Montenegro` and `Serbia` separate.
- **Qualification is derived, not read from row colour:** a semi-final entry qualified if the same
  country appears in that year's final. Every semi-final must come out at exactly ten.

## 3. Processing decisions, and why

### Which years were a lottery (the instrument)

This is the decision the whole result rests on. It was read from each article's own sentences
about the running-order draw, not assumed:

| regime | shows | basis in the articles |
|---|---|---|
| drawn by lot | finals 1957–2006, semi-finals 2004–2006, the 1996 audio round | "The draw to determine the running order took place on ..." in year after year |
| lot with exceptions | 2007–2012 | 2007: "five wild-card countries from the semi-final and three countries from the final" chose their position, and "All countries opted for spots in the second half". 2008: three countries in each semi-final and Serbia in the final "were drawn to decide their own running order positions". 2009–2012: a draw is described and choosers are not mentioned either way |
| set by producers | 2013–2025 | "Running order Malmö 2013 to be determined by producers"; from 2016 countries draw only a half |

The named choosers (2007 semi: Austria, Andorra, Turkey, Slovenia, Latvia; 2007 final: Armenia,
Ukraine, Germany; 2008 semi 1: Azerbaijan, Greece, Russia; 2008 semi 2: Macedonia, Portugal,
Denmark; 2008 final: Serbia) are flagged and excluded from every test by default.

**The headline uses only the clean lottery.** 2007–2012 is kept separate because 2009–2012
cannot be classified from the source. Folding them in makes the effect larger (r = −0.236 in
those finals), which is a reason for caution, not comfort.

### Measures

- `slot` = rank of R/O within the show; position = (slot − 1) / (field − 1), 0 opener, 1 closer.
- **Measure A**, finals: place share = (place − 1) / (field − 1), lower is better, so a 16-song
  and a 26-song final sit on one scale. Ties keep the article's place.
- **Measure B**, semi-finals: qualified, 0 or 1.
- The two are never averaged. Different nights, different songs, different voters.
- **Headline places figure:** (mean place share of the first third − that of the last third) ×
  (median field size − 1). Thirds are position < 1/3, < 2/3, and the rest.

### Significance

Permutation test: shuffle slots *within each show* 2,000 times, recompute the Pearson correlation
of position with outcome, and compare. Within-show shuffling keeps field size and scoring system
fixed. A p-value is never shown below 1 / 2,000; if no shuffle reaches the observed value the
page says `p < 0.0005`. The page's RNG is seeded, so the same numbers appear on every load.

### The control

Prior strength = a country's mean place share over its previous five finals (at least two
needed, any era). Run through the same permutation test against slot, in the lottery finals.
If the draw was clean it should sit inside its chance band. The page computes this live and
**replaces the headline with a warning if it ever falls outside**. It also regresses place share
on position and prior strength together, and reports how much of the slot effect the control's
lean could account for at most.

### The curse simulation

68 finals, each with its real field size; draw one winner uniformly per final; count winners per
slot. "Regular" slots are those that existed in at least 40 of the 68 finals (slots 1 to 20).
Report P(slot 2 winless), P(any regular slot winless), P(two or more winless), mean number winless.
10,000 histories per run; the button reruns with a new seed.

## 4. The page

Single `index.html`, no build step at view time. The payload is JSON holding base64 little-endian
typed arrays (`year` Int16, `show` Uint8 with 0 final, 1 sf, 2 sf1, 3 sf2, 4 prequal, `era` Uint8,
`slot`, `n`, `place` Uint8, `points` Int16 with −1 for none, `country` Uint8 index into
`countries`, `flags` Uint8 with bit 0 chose its slot and bit 1 qualified), plus revision ids.

Sections: the hero with lottery balls (1–8 slate for early, 17–24 gold for late) and the
computed headline; *Slot by slot* (mean place share by tenth of the running order with a grey
chance band from the same shuffles, era chips, and a toggle to readmit the choosers); *Two
measures, never averaged* (thirds for A and B side by side); *The control* (dot-and-band plot of
result and control, with the drift verdict); *The curse of slot two* (wins by slot, red zeros only
for regular slots, a rerun button); *The hat kept changing* (the regime timeline and a per-regime
table); *Methods*.

Identity: stage navy in dark mode, warm paper in light; Barlow Condensed headings, Barlow body,
JetBrains Mono numerals. Gold always means drawn late, slate drawn early, grey chance.

## 5. Expected values

From the 2026-10-07 build. A later Wikipedia revision may move a figure in the third decimal;
anything bigger means the parse went wrong.

| check | expected |
|---|---|
| rows in payload / countries / shows | 2,148 / 52 / 107 |
| dropped entries | Netherlands 2024 final, only |
| every semi-final's qualifiers | 10; the 1996 audio round 22 of 29 |
| more points with a worse place, any table | 0 pairs |
| 1974 final, Sweden | slot 8 of 17, 24 points, place 1 |
| 1975 final, Netherlands | slot 1 of 19, 152 points, place 1 (an opener that won) |
| 1988 final, Switzerland | slot 9 of 21, 137 points, place 1 |
| 2008 final, Russia | slot 24 of 25, 272 points, place 1 |
| 2012 final, Sweden | slot 17 of 26, 372 points, place 1 |
| 2025 final, Austria | slot 9 of 26, 436 points, place 1 |
| 1969 winners | Spain, United Kingdom, Netherlands, France |
| lottery finals | 975 songs in 50 finals |
| Measure A, r(position, place share) | −0.110; chance band about ±0.065; p ≈ 0.002 |
| Measure A, mean place share by third | 0.539 / 0.478 / 0.457 |
| Measure A, mean place by third | 11.4 / 10.3 / 9.8 |
| headline gap | 1.55 places, shown as "one and a half" (median field 20, so × 19) |
| Measure B, drawn semis 2004–12 without choosers | 270 songs; qualified 38% / 43% / 66%; r = 0.221; p < 0.0005 |
| Measure B, pure lottery semis 2004–06 only | 70 songs; 22% → 52% |
| control, r(position, prior strength) | −0.044, inside a band of about ±0.067, p ≈ 0.20, n = 893 |
| slot slope, raw vs holding prior fixed | −0.094 vs −0.083 (at most 12% explained by the lean) |
| lot-with-exceptions finals (no choosers) | 146 songs, r = −0.236 |
| producer finals 2013–25 | 311 songs, r = −0.122 |
| producer semis 2013–25 | 402 songs, 52% → 65% |
| winless slots, all 68 finals | 2 and 16 among the regular slots (25–27 exist too rarely to count) |
| simulation | P(slot 2 winless) ≈ 3%, P(any regular slot winless) ≈ 67%, P(two or more) ≈ 26% |

## 6. What the page must say about itself

- It shows that the slot matters, not why.
- Producer-era numbers are comparison only and cannot be read causally.
- The effect is an average of about one and a half places, not a fate; three openers won in the lottery years.
- No single slot's record, slot two's included, can show much with this few finals.
- Scoring systems changed throughout; place shares keep years comparable but do not make them the same instrument.
- Wikipedia is the only source; every figure traces to a recorded revision.

And the failed half, documented on the page:

- 2009–2012 could not be classified from the source and is held out of the headline.
- The 1996 audio-only round was meant as a no-stage control (heard in order, never seen). With
  29 songs it shows 80% qualifying in both the first and last thirds, which cannot distinguish
  anything, and it is used for nothing.
- The 2007 choosers (all eight chose the second half) are evidence of belief, not data, and are
  excluded from the tests.
