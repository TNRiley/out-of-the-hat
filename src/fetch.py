"""Download the rendered HTML of every Eurovision Song Contest article on English
Wikipedia, one per contest year, into src/raw/. Re-running skips what is there.

    python src/fetch.py

Uses the MediaWiki parse API (rendered HTML, not wikitext: the tables are built
from templates whose wikitext is far harder to read than their output). Each file
keeps the revision id, so a rebuild can say exactly which version it read.
"""
import json, os, sys, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
API = "https://en.wikipedia.org/w/api.php"
UA = "out-of-the-hat/1.0 (https://github.com/TNRiley/out-of-the-hat; one-off research build)"
YEARS = [y for y in range(1956, 2026) if y != 2020]   # 2020 was cancelled

def get(page):
    q = urllib.parse.urlencode({"action": "parse", "page": page, "prop": "text|revid",
                                "format": "json", "formatversion": 2, "redirects": 1})
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def main():
    os.makedirs(RAW, exist_ok=True)
    for y in YEARS:
        out = os.path.join(RAW, f"esc_{y}.json")
        if os.path.exists(out):
            continue
        d = get(f"Eurovision Song Contest {y}")
        if "error" in d:
            sys.exit(f"{y}: {d['error']}")
        p = d["parse"]
        json.dump({"year": y, "title": p["title"], "revid": p["revid"], "html": p["text"]},
                  open(out, "w", encoding="utf-8", newline="\n"), ensure_ascii=False)
        print(y, p["revid"], len(p["text"]))
        time.sleep(1.0)

if __name__ == "__main__":
    main()
