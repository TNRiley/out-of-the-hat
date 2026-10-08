# src

The pipeline that builds `../index.html`. Run from the repository root, in order:

```bash
python src/fetch.py     # 69 Wikipedia articles -> src/raw/esc_<year>.json   (~43 MB, ~2 min)
python src/extract.py   # every result table     -> src/raw/entries.json
python src/shape.py     # clean, label, check    -> src/payload.json
python src/inject.py    # splice into template   -> index.html (+ Pages wrapper, breadcrumb)
```

`src/raw/` and `payload.json` are not committed; the scripts regenerate them. `shape.py` stops
the build if a parse check fails (more points with a worse place, duplicate running-order
numbers, or a named slot-chooser that cannot be matched) and prints the qualifier count for
every semi-final, which should be ten each.

`inject.py` expects to sit inside the Quick Projects workspace (it calls the catalog's
`wrap_for_pages.py` and `add_catalog_link.py`). Outside it, splice `payload.json` into
`template.html` at `__PAYLOAD__` by hand.

Needs Python 3.11+ and `beautifulsoup4`. Nothing else.

See `../REBUILD.md` for the reasoning and the expected values.
