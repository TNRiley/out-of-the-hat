"""Shape src/raw/entries.json into src/payload.json: one row per entry per show,
as base64 typed arrays the page decodes and computes from.

    python src/shape.py

Every statistic on the page is computed in the browser from these arrays. This
script only cleans, labels and checks; it does not test anything.
"""
import base64, json, os, sys
from array import array
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

# renamed, not replaced: the same broadcaster under a new country name
SAME = {"Czechia": "Czech Republic", "North Macedonia": "Macedonia"}

SHOW = {"final": 0, "sf": 1, "sf1": 2, "sf2": 3, "prequal": 4}

# How the running order was set. Read from each contest's own article; see
# REBUILD.md section 3 for the sentences these rest on.
#   0 lottery    every slot drawn by lot (finals 1957-2006, semi-finals 2004-2006,
#                and the 1996 audio-only qualifying round)
#   1 exceptions drawn by lot, but some countries were drawn the right to choose
#                their own slot (2007, 2008); 2009-2012 the articles describe a
#                draw and say nothing either way about choosers
#   2 producers  countries draw a half; the show's producers set the order (2013-)
def era(year):
    return 0 if year <= 2006 else (1 if year <= 2012 else 2)

# Countries that chose their own slot. Named in the 2007 and 2008 articles.
CHOSE = {
    (2007, "sf"): {"Austria", "Andorra", "Turkey", "Slovenia", "Latvia"},
    (2007, "final"): {"Armenia", "Ukraine", "Germany"},
    (2008, "sf1"): {"Azerbaijan", "Greece", "Russia"},
    (2008, "sf2"): {"Macedonia", "Portugal", "Denmark"},
    (2008, "final"): {"Serbia"},
}

def b64(typecode, xs):
    a = array(typecode, xs)
    if sys.byteorder != "little":
        a.byteswap()
    return base64.b64encode(a.tobytes()).decode("ascii")

def main():
    E = json.load(open(os.path.join(RAW, "entries.json"), encoding="utf-8"))
    for e in E:
        e["country"] = SAME.get(e["country"], e["country"])

    finalists = defaultdict(set)
    for e in E:
        if e["show"] == "final":
            finalists[e["year"]].add(e["country"])

    shows = defaultdict(list)
    for e in E:
        shows[(e["year"], e["show"])].append(e)

    countries = sorted({e["country"] for e in E})
    cix = {c: i for i, c in enumerate(countries)}
    cols = defaultdict(list)
    dropped, chosen_seen, checks = [], Counter(), []

    for (y, s), rows in sorted(shows.items(), key=lambda kv: (kv[0][0], SHOW[kv[0][1]])):
        # an entry with no place did not perform (Netherlands 2024 was disqualified
        # after the semi-final); it holds no slot, so it is left out of the ranking
        keep = [e for e in rows if e["place"] is not None]
        dropped += [(y, s, e["country"]) for e in rows if e["place"] is None]
        keep.sort(key=lambda e: e["ro"])
        n = len(keep)
        if len({e["ro"] for e in keep}) != n:
            sys.exit(f"{y} {s}: duplicate running-order numbers")
        if s != "final":
            q = sum(1 for e in keep if e["country"] in finalists[y])
            checks.append((y, s, n, q))
        # parse check: more points must never mean a worse place
        inv = sum(1 for a in keep for b in keep
                  if a["points"] is not None and b["points"] is not None
                  and a["points"] > b["points"] and a["place"] > b["place"])
        if inv:
            sys.exit(f"{y} {s}: {inv} pairs where more points got a worse place")
        for i, e in enumerate(keep):
            chose = e["country"] in CHOSE.get((y, s), ())
            chosen_seen[(y, s)] += chose
            qual = s != "final" and e["country"] in finalists[y]
            cols["year"].append(y)
            cols["show"].append(SHOW[s])
            cols["era"].append(era(y))
            cols["slot"].append(i + 1)
            cols["n"].append(n)
            cols["place"].append(e["place"])
            cols["points"].append(-1 if e["points"] is None else e["points"])
            cols["country"].append(cix[e["country"]])
            cols["flags"].append((1 if chose else 0) | (2 if qual else 0))

    for k, names in CHOSE.items():
        if chosen_seen[k] != len(names):
            sys.exit(f"{k}: expected {len(names)} choosers, matched {chosen_seen[k]}")

    payload = {
        "rows": len(cols["year"]),
        "countries": countries,
        "shows": list(SHOW),
        "revids": {str(y): json.load(open(os.path.join(RAW, f"esc_{y}.json"), encoding="utf-8"))["revid"]
                   for y in sorted({e["year"] for e in E})},
        "dropped": dropped,
        "cols": {
            "year": b64("h", cols["year"]),
            "show": b64("B", cols["show"]),
            "era": b64("B", cols["era"]),
            "slot": b64("B", cols["slot"]),
            "n": b64("B", cols["n"]),
            "place": b64("B", cols["place"]),
            "points": b64("h", cols["points"]),
            "country": b64("B", cols["country"]),
            "flags": b64("B", cols["flags"]),
        },
    }
    json.dump(payload, open(os.path.join(HERE, "payload.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"{payload['rows']} rows, {len(countries)} countries, {len(shows)} shows; dropped {dropped}")
    for y, s, n, q in checks:
        flag = "" if (s == "prequal" or q == 10) else "  <-- expected 10 qualifiers"
        print(f"  {y} {s:7s} n={n:2d} qualified={q}{flag}")

if __name__ == "__main__":
    main()
