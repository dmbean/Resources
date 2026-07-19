#!/usr/bin/env python3
"""Deterministic scorer for the Gibson Watch database.

Rescores every guitar in database.json in place and regenerates reports/master.csv.
Weights: weight 30%, neck measurements 35%, shoulder profile 20%, condition 10%, price 5%.
Run from the gibson-watch/ directory: python3 scripts/score.py
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")
CSV_OUT = os.path.join(HERE, "reports", "master.csv")

# Rough market anchors (USD) used only for the 5% price component.
MARKET_ANCHORS = {
    "standard 60s": 2800,
    "plain top": 2600,
    "r0": 6800,
    "1960 reissue": 6800,
    "custom shop": 5500,
    "murphy lab": 7500,
    "wildwood spec": 7000,
    "norlin lp": 5500,
    "es-335 modern": 3500,
    "es-335 61 reissue": 4000,
    "es-335 memphis": 3500,
    "es-335 norlin": 5000,
    "es-335 vintage": 8000,
}


def band_score(value, lo, hi, ideal_lo=None, ideal_hi=None, falloff=1.0):
    """100 inside ideal band, linear-ish decay outside acceptable band."""
    if value is None:
        return None
    ideal_lo = ideal_lo if ideal_lo is not None else lo
    ideal_hi = ideal_hi if ideal_hi is not None else hi
    if ideal_lo <= value <= ideal_hi:
        return 100.0
    if lo <= value <= hi:
        # inside acceptable band but outside ideal: 80-99
        edge = min(abs(value - ideal_lo), abs(value - ideal_hi))
        span = max(ideal_lo - lo, hi - ideal_hi) or 1
        return 100.0 - 20.0 * min(edge / span, 1.0)
    # outside acceptable band: decay
    edge = lo - value if value < lo else value - hi
    return max(0.0, 80.0 - 80.0 * edge / falloff)


def weight_component(g):
    if g["category"] == "les_paul":
        s = band_score(g.get("weight_lbs"), 8.3, 9.0, 8.4, 8.8, falloff=1.2)
    else:
        s = band_score(g.get("weight_lbs"), 7.4, 8.0, 7.5, 7.8, falloff=1.0)
    return (s if s is not None else 0.0, "weight %s lbs" % g.get("weight_lbs"))


def neck_component(g):
    """Nut width, fret depths, and whether measurements exist at all."""
    parts, notes = [], []
    if g["category"] == "les_paul":
        nut = band_score(g.get("nut_width_in"), 1.68, 1.71, 1.69, 1.70, falloff=0.05)
        f1 = band_score(g.get("fret1_depth_in"), 0.79, 0.82, 0.79, 0.82, falloff=0.06)
        f12 = band_score(g.get("fret12_depth_in"), 0.89, 0.92, 0.89, 0.92, falloff=0.06)
    else:
        nut = band_score(g.get("nut_width_in"), 1.56, 1.60, 1.5625, 1.5625, falloff=0.05)
        f1 = band_score(g.get("fret1_depth_in"), 0.76, 0.82, 0.76, 0.82, falloff=0.06)
        f12 = band_score(g.get("fret12_depth_in"), 0.86, 0.94, 0.87, 0.92, falloff=0.08)
    for label, s in (("nut", nut), ("1st fret", f1), ("12th fret", f12)):
        if s is not None:
            parts.append(s)
            notes.append("%s ok (%.0f)" % (label, s))
        else:
            notes.append("%s unmeasured" % label)
    if not parts:
        # no hard measurements; profile-name-only necks cap low
        return 35.0, "no neck measurements (capped)"
    score = sum(parts) / len(parts)
    # penalty for missing measurements: -8 per missing datum
    score -= 8.0 * (3 - len(parts))
    return max(score, 0.0), "; ".join(notes)


SLIM_WORDS = ("slimtaper", "slim taper", "slim", "1960", "60s", "fast c", "fast d",
              "medium c", "medium-slim", "thin")
FAT_WORDS = ("baseball", "chunky", "50s", "fat", "huge", "boat", "clubby")


def shoulder_component(g):
    text = " ".join(filter(None, [g.get("neck_profile"), g.get("shoulder_description")])).lower()
    if not text:
        return 40.0, "no shoulder/profile info"
    if any(w in text for w in FAT_WORDS):
        return 20.0, "fat/50s-style profile: '%s'" % text[:60]
    if any(w in text for w in SLIM_WORDS):
        return 95.0, "slim/fast profile: '%s'" % text[:60]
    return 60.0, "profile unclear: '%s'" % text[:60]


COND_MAP = [
    ("new", 100), ("mint", 98), ("excellent", 92), ("very good", 82),
    ("good", 70), ("fair", 50), ("player", 55), ("poor", 30),
]


def condition_component(g):
    c = (g.get("condition") or "").lower()
    for key, s in COND_MAP:
        if key in c:
            return float(s), c
    return 70.0, c or "condition unstated"


def price_component(g):
    price = g.get("price_usd")
    anchor = MARKET_ANCHORS.get(g.get("market_bucket") or "", None)
    if not price or not anchor:
        return 60.0, "no market anchor"
    ratio = price / anchor
    if ratio <= 0.85:
        return 100.0, "%.0f%% under anchor" % ((1 - ratio) * 100)
    if ratio <= 1.0:
        return 90.0, "at/under anchor"
    if ratio <= 1.15:
        return 70.0, "slightly above anchor"
    return max(0.0, 70.0 - (ratio - 1.15) * 200), "well above anchor"


def score(g):
    w, wn = weight_component(g)
    n, nn = neck_component(g)
    s, sn = shoulder_component(g)
    c, cn = condition_component(g)
    p, pn = price_component(g)
    total = 0.30 * w + 0.35 * n + 0.20 * s + 0.10 * c + 0.05 * p
    g["score"] = round(total, 1)
    g["score_breakdown"] = {
        "weight_30pct": {"score": round(w, 1), "note": wn},
        "neck_35pct": {"score": round(n, 1), "note": nn},
        "shoulders_20pct": {"score": round(s, 1), "note": sn},
        "condition_10pct": {"score": round(c, 1), "note": cn},
        "price_5pct": {"score": round(p, 1), "note": pn},
    }
    return g


CSV_FIELDS = [
    "id", "category", "score", "status", "dealer", "url", "price_usd", "condition",
    "city_state", "year", "model", "finish", "serial", "weight_lbs", "nut_width_in",
    "fret1_depth_in", "fret12_depth_in", "neck_profile", "shoulder_description",
    "fingerboard_radius", "pickups", "case_included", "modifications",
    "measurements_source", "date_discovered", "last_confirmed_active",
]


def main():
    with open(DB) as f:
        db = json.load(f)
    for g in db["guitars"]:
        score(g)
    db["guitars"].sort(key=lambda g: g["score"], reverse=True)
    with open(DB, "w") as f:
        json.dump(db, f, indent=2)
    os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        for g in db["guitars"]:
            w.writerow(g)
    print("scored %d guitars -> %s" % (len(db["guitars"]), CSV_OUT))


if __name__ == "__main__":
    main()
