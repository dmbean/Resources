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
    "mij lp": 2000,
    "mij 335": 2200,
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


NYC_MARKERS = ("new york", "brooklyn", "queens", "manhattan", "bronx",
               "long island city", "astoria", "ridgewood, ny")
NYC_SHOP_URLS = ("rivingtonguitars", "rudysmusic", "retrofret", "trcrandall",
                 "southsideguitars", "maindragmusic", "30thstreetguitars")


def is_nyc(g):
    """NYC-area listing the buyer could play before buying (weigh-in-person allowance)."""
    if any(s in (g.get("url") or "").lower() for s in NYC_SHOP_URLS):
        return True
    loc = str(g.get("city_state") or "").lower().split("(")[0]
    return any(m in loc for m in NYC_MARKERS)


VIBRATO_WORDS = ("bigsby", "maestro", "vibrola", "vibrato", "trapeze vibrato",
                 "whammy", "tremolo arm", "sideways")


def has_vibrato(g):
    """Factory/period vibrato tailpiece (buyer signal 2026-08-09: likes vibratos and
    accepts the weight they add — a Bigsby or Maestro runs roughly half a pound)."""
    text = " ".join(str(g.get(k) or "") for k in
                    ("model", "notes", "modifications", "hardware", "condition")).lower()
    return any(w in text for w in VIBRATO_WORDS)


def weight_component(g):
    # Buyer signal 2026-07-29: soft floors — light guitars are fine, heavy ones are not.
    # Buyer signal 2026-08-09: a vibrato's weight is accepted, so the ceiling gets a
    # +0.5 lb allowance when one is fitted; lighter is still preferred, so the ideal
    # band does NOT move — a vibrato guitar simply isn't punished for the hardware.
    vib = 0.5 if has_vibrato(g) else 0.0
    if g["category"] == "les_paul":
        s = band_score(g.get("weight_lbs"), 8.0, 9.0 + vib, 8.3, 8.8, falloff=1.2)
    else:
        s = band_score(g.get("weight_lbs"), 7.2, 8.0 + vib, 7.4, 7.8, falloff=1.0)
    if s is None:
        # Buyer signal 2026-08-09: a NYC listing with no published weight is one the buyer
        # can put on a scale in person, so an unknown weight is neutral here, not a zero.
        # Scoring it 0 capped every playable NYC guitar near 70 (avg 33.5 vs 64.7 board-wide).
        if is_nyc(g):
            return 65.0, "weight unpublished — NYC, weigh in person (neutral)"
        return 0.0, "no exact weight stated"
    note = "weight %s lbs" % g.get("weight_lbs")
    if vib:
        note += " (vibrato allowance +0.5)"
    return s, note


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


P90_WORDS = ("p-90", "p90", "soapbar", "soap bar", "dog ear", "dogear")


def is_p90_lp(g):
    """P-90 Les Paul (buyer signal 2026-08-09: spec is humbucker LPs only).
    '54/'56 Standard reissues (R4/R6) ship P-90s; LP Customs of those years do not."""
    import re as _re
    if g.get("category") != "les_paul":
        return False
    txt = " ".join(str(g.get(k) or "") for k in ("pickups", "model", "notes")).lower()
    if any(w in txt for w in P90_WORDS):
        return True
    m = str(g.get("model") or "").lower()
    if "les paul custom" in m or "black beauty" in m:
        return False
    return bool(_re.search(r"(1954|'54|\br4\b|1956|'56|\br6\b)", m))


SLIM_WORDS = ("slimtaper", "slim taper", "slim", "1960", "60s", "fast c", "fast d",
              "medium c", "medium-slim", "thin", "skinny")
FAT_WORDS = ("baseball", "chunky", "50s", "fat", "huge", "boat", "clubby")
V3_WORDS = ("v3", "skinny c")   # buyer signal 2026-07-29: V3 / late-1960 Skinny C preferred


def shoulder_component(g):
    text = " ".join(filter(None, [g.get("neck_profile"), g.get("shoulder_description")])).lower()
    if not text:
        return 40.0, "no shoulder/profile info"
    if g["category"] == "les_paul" and any(w in text for w in V3_WORDS):
        return 100.0, "V3/Skinny C — buyer-preferred carve: '%s'" % text[:60]
    fat = any(w in text for w in FAT_WORDS)
    slim = any(w in text for w in SLIM_WORDS)
    if fat and slim:
        return 60.0, "mixed slim/fat signals: '%s'" % text[:60]
    if fat:
        return 20.0, "fat/50s-style profile: '%s'" % text[:60]
    if slim:
        return 95.0, "slim/fast profile: '%s'" % text[:60]
    return 60.0, "profile unclear: '%s'" % text[:60]


COND_MAP = [
    ("new", 100), ("mint", 98), ("excellent", 92), ("very good", 82),
    ("good", 70), ("fair", 50), ("player", 55), ("poor", 30),
]


def is_plekd(g):
    """Stated PLEK work anywhere in the listing text (buyer signal 2026-07-29)."""
    text = " ".join(str(g.get(k) or "") for k in ("condition", "modifications", "notes")).lower()
    return "plek" in text


def condition_component(g):
    c = (g.get("condition") or "").lower()
    score = 70.0
    for key, s in COND_MAP:
        if key in c:
            score = float(s)
            break
    note = c or "condition unstated"
    if is_plekd(g):
        score = min(100.0, score + 10.0)
        note += " (+PLEK'd)"
    return score, note


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


ES_SECONDARY = ("345", "355", "347", "340", "339", "336", "356")


def family_penalty(g):
    """Buyer signal 2026-08-09: prioritize ES-335s and Les Pauls over the other ES
    models. The 345/355/347/340 stay in scope (same nut era, same construction) but
    rank below an equivalent 335, so they never displace a core target."""
    if g.get("category") != "es_335":
        return 0.0, None
    m = str(g.get("model") or "").lower()
    if "335" in m:
        return 0.0, None
    if any(k in m for k in ES_SECONDARY):
        return 6.0, "secondary ES model (-6: 335s and Les Pauls rank first)"
    return 0.0, None


def score(g):
    w, wn = weight_component(g)
    n, nn = neck_component(g)
    s, sn = shoulder_component(g)
    c, cn = condition_component(g)
    p, pn = price_component(g)
    total = 0.30 * w + 0.35 * n + 0.20 * s + 0.10 * c + 0.05 * p
    pen, pen_note = family_penalty(g)
    total = max(0.0, total - pen)
    g["score"] = round(total, 1)
    g["score_breakdown"] = {
        "weight_30pct": {"score": round(w, 1), "note": wn},
        "neck_35pct": {"score": round(n, 1), "note": nn},
        "shoulders_20pct": {"score": round(s, 1), "note": sn},
        "condition_10pct": {"score": round(c, 1), "note": cn},
        "price_5pct": {"score": round(p, 1), "note": pn},
    }
    if pen_note:
        g["score_breakdown"]["model_priority"] = {"score": -pen, "note": pen_note}
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
