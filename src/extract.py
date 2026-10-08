"""Pull every result table (running order, country, points, place) out of the
downloaded Wikipedia articles and write src/raw/entries.json, one row per entry
per show.

    python src/extract.py

A result table is any table whose first header row starts R/O and which also has
a Place column. Its caption says which show it is. Rows that are not entries
(footnotes, spanning notes) are dropped by requiring an integer running order.
"""
import json, os, re, sys
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

def clean(s):
    s = re.sub(r"\[[^\]]*\]", "", s)              # footnote markers like [a] or [ 12 ]
    return re.sub(r"\s+", " ", s).strip()

def show_of(caption, year):
    c = caption.lower()
    if "pre-qualif" in c or "qualifying round" in c or "kvalifikacija" in c or "preselection" in c:
        return "prequal"
    if "semi" in c:
        if "second" in c or "semi-final 2" in c: return "sf2"
        if "first" in c or "semi-final 1" in c: return "sf1"
        return "sf"                                # 2004-2007 had one semi-final
    return "final"

def num(s):
    m = re.match(r"^\s*(\d+)", s)
    return int(m.group(1)) if m else None

def tables(year):
    d = json.load(open(os.path.join(RAW, f"esc_{year}.json"), encoding="utf-8"))
    soup = BeautifulSoup(d["html"], "html.parser")
    for t in soup.find_all("table"):
        rows = t.find_all("tr")
        if not rows: continue
        hdr = [clean(c.get_text(" ", strip=True)) for c in rows[0].find_all(["th", "td"])]
        if not hdr or hdr[0] != "R/O" or "Place" not in hdr: continue
        cap = t.find("caption")
        cap = clean(cap.get_text(" ", strip=True)) if cap else ""
        ix = {h: i for i, h in enumerate(hdr)}
        pts_col = "Points" if "Points" in ix else ("Votes" if "Votes" in ix else None)
        out = []
        for r in rows[1:]:
            cells = r.find_all(["th", "td"])
            if len(cells) < len(hdr): continue
            txt = [clean(c.get_text(" ", strip=True)) for c in cells]
            ro = num(txt[ix["R/O"]])
            if ro is None: continue
            out.append({"ro": ro, "country": txt[ix["Country"]],
                        "points": num(txt[ix[pts_col]]) if pts_col else None,
                        "place": num(txt[ix["Place"]]),
                        "place_raw": txt[ix["Place"]]})
        yield cap, show_of(cap, year), out, d["revid"]

def main():
    years = [y for y in range(1956, 2026) if y != 2020]
    entries, log = [], []
    for y in years:
        for cap, show, rows, rev in tables(y):
            log.append((y, show, len(rows), cap[:60]))
            for r in rows:
                entries.append(dict(year=y, show=show, revid=rev, **r))
    json.dump(entries, open(os.path.join(RAW, "entries.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=0)
    for l in log: print(*l, sep=" | ")
    print(len(entries), "entry rows")

if __name__ == "__main__":
    main()
