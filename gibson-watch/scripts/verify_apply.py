#!/usr/bin/env python3
"""Apply a verification pass to database.json.

Usage: python3 scripts/verify_apply.py results.json --date YYYY-MM-DD
results.json maps guitar id -> {"state": "live"|"sold"|"gone"|"unknown"|..., "price": <usd|null>}.
live: refresh last_confirmed_active, track price changes; sold/gone: mark SOLD.
unknown/fetch errors leave the entry untouched (retry next run).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")


def main():
    args = sys.argv[1:]
    date = args[args.index("--date") + 1]
    results = {}
    for path in args:
        if path.startswith("--") or path == date:
            continue
        with open(path) as f:
            results.update(json.load(f))

    with open(DB) as f:
        db = json.load(f)
    confirmed = sold = repriced = 0
    for g in db["guitars"]:
        r = results.get(g["id"])
        if not r or g["status"] in ("SOLD", "EXCLUDED"):
            continue
        state = (r.get("state") or "").lower()
        if state in ("sold", "gone", "ended"):
            g["status"] = "SOLD"
            g["notes"] = (g.get("notes") or "") + " | Marked SOLD %s." % date
            sold += 1
        elif state == "live":
            g["last_confirmed_active"] = date
            new = r.get("price")
            old = g.get("price_usd")
            if new and old and round(new) != round(old):
                g.setdefault("price_history", []).append({"date": date, "price_usd": new})
                g["status"] = "PRICE DROP" if new < old else "PRICE INCREASE"
                g["price_usd"] = new
                repriced += 1
            else:
                g["status"] = "ACTIVE"
            confirmed += 1
    with open(DB, "w") as f:
        json.dump(db, f, indent=2)
    print("confirmed %d, sold %d, repriced %d" % (confirmed, sold, repriced))


if __name__ == "__main__":
    main()
