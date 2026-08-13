#!/usr/bin/env python3
"""Ingest sweep results into database.json.

Usage: python3 scripts/ingest.py results1.json [results2.json ...] --date 2026-07-19
Each input file is a JSON array of listing objects from a research agent.
Dedupes by serial number, URL, and dealer inventory ID; new guitars get ids and
date_discovered; existing guitars get last_confirmed_active and price-change tracking.
Run scripts/score.py afterwards.
"""
import json
import re
import sys
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")

LP_BUCKETS = [
    ("wildwood spec", "wildwood spec"), ("murphy lab", "murphy lab"),
    ("r0", "r0"), ("1960 reissue", "1960 reissue"), ("60th", "r0"),
    ("plain top", "plain top"), ("standard 60", "standard 60s"),
    ("custom shop", "custom shop"),
]


MIJ_BRANDS = ("tokai", "greco", "burny", "edwards", "navigator", "momose",
              "yamaha", "ibanez", "seventy seven", "fgn", "fujigen")


def market_bucket(g):
    m = (str(g.get("model") or "") + " " + str(g.get("notes") or "")).lower()
    if any(b in m for b in MIJ_BRANDS):
        return "mij 335" if g["category"] == "es_335" else "mij lp"
    year = g.get("year")
    try:
        year = int(str(year)[:4])
    except (ValueError, TypeError):
        year = None
    if g["category"] == "les_paul":
        if year and year < 1985:
            return "norlin lp"
        for key, bucket in LP_BUCKETS:
            if key in m:
                return bucket
        # Thin dealer-sweep titles like "Les Paul (1959 spec)" were defaulting to the
        # Standard 60s anchor ($2,800) and scoring a $7k Custom Shop guitar 0 on price.
        if any(k in m for k in ("1959 spec", "1958 spec", "1957 spec", "1960 spec",
                                "r9", "r8", "r7", "cme spec", "reissue")):
            return "custom shop"
        return "standard 60s"
    if year and 1970 <= year <= 1984:
        return "es-335 norlin"
    if year and year < 1970:
        return "es-335 vintage"
    if "61" in m or "1961" in m:
        return "es-335 61 reissue"
    if "memphis" in m:
        return "es-335 memphis"
    return "es-335 modern"


# Sweep agents name these fields inconsistently; map to the canonical schema.
FIELD_ALIASES = {
    "dealer_shop": "dealer", "shop": "dealer", "shop_name": "dealer", "seller": "dealer",
    "location": "city_state", "loc": "city_state", "published": "published_at",
    "weight": "weight_lbs", "price": "price_usd", "nut_width": "nut_width_in",
}


def normalize_fields(g):
    for alias, canon in FIELD_ALIASES.items():
        if alias in g and not g.get(canon):
            g[canon] = g.pop(alias)
    if g.get("dealer") and "reverb.com" in (g.get("url") or "") \
            and not str(g["dealer"]).startswith("Reverb"):
        g["dealer"] = "Reverb – " + str(g["dealer"])
    g.setdefault("dealer", "unknown")
    return g


def categorize(g):
    m = (str(g.get("model") or "")).lower()
    semi_markers = ("335", "345", "355", "347", "340", "339", "336", "356",
                    "sa-2200", "sa2200", "sa-", "jsm", "as-200", "semi-hollow",
                    "semi hollow", "dot")
    if any(k in m for k in semi_markers):
        return "es_335"
    return "les_paul"


def norm_url(u):
    if not u:
        return None
    return re.sub(r"[?#].*$", "", u.strip().rstrip("/")).lower()


def norm_serial(s):
    if not s:
        return None
    s = re.sub(r"[^a-z0-9]", "", str(s).lower())
    return s or None


def keys_of(g):
    ks = set()
    if norm_serial(g.get("serial")):
        ks.add(("serial", norm_serial(g.get("serial"))))
    if norm_url(g.get("url")):
        ks.add(("url", norm_url(g.get("url"))))
    if g.get("inventory_id"):
        ks.add(("inv", str(g["inventory_id"]).lower()))
    return ks


def main():
    args = sys.argv[1:]
    date = "unknown"
    if "--date" in args:
        i = args.index("--date")
        date = args[i + 1]
        del args[i:i + 2]

    with open(DB) as f:
        db = json.load(f)

    index = {}
    for g in db["guitars"]:
        for k in keys_of(g):
            index[k] = g

    added, updated, dup_skipped = 0, 0, 0
    seen_this_run = set()
    for path in args:
        with open(path) as f:
            batch = json.load(f)
        for raw in batch:
            normalize_fields(raw)
            raw["category"] = categorize(raw)
            match = None
            ks = keys_of(raw)
            if ks & seen_this_run:
                dup_skipped += 1
                continue
            seen_this_run |= ks
            for k in ks:
                if k in index:
                    match = index[k]
                    break
            if match:
                match["last_confirmed_active"] = date
                old = match.get("price_usd")
                new = raw.get("price_usd")
                if old and new and old != new:
                    match.setdefault("price_history", []).append({"date": date, "price_usd": new})
                    match["status"] = "PRICE DROP" if new < old else "PRICE INCREASE"
                    match["price_usd"] = new
                else:
                    match["status"] = "ACTIVE"
                updated += 1
            else:
                raw["id"] = "g%03d" % (len(db["guitars"]) + 1)
                raw["status"] = "ACTIVE"
                raw["date_discovered"] = date
                raw["last_confirmed_active"] = date
                raw["market_bucket"] = market_bucket(raw)
                raw.setdefault("price_history", [{"date": date, "price_usd": raw.get("price_usd")}])
                db["guitars"].append(raw)
                for k in keys_of(raw):
                    index[k] = raw
                added += 1

    db["meta"]["last_run"] = date
    with open(DB, "w") as f:
        json.dump(db, f, indent=2)
    print("added %d, updated %d, skipped %d in-run dupes; db total %d"
          % (added, updated, dup_skipped, len(db["guitars"])))


if __name__ == "__main__":
    main()
