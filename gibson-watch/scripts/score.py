#!/usr/bin/env python3
"""Deterministic scorer for the Gibson Watch database.

Rescores every guitar in database.json in place and regenerates reports/master.csv.
Weights: weight 30%, shoulder profile 25%, neck measurements 20%, rolled edges 10%,
condition 10%, price 5%.
(Shoulders raised from 20% and depths cut from 35% on 2026-08-13: the buyer said slim
shoulders are a big part of what he is after, and shape decides feel more than depth does.)
Run from the gibson-watch/ directory: python3 scripts/score.py
"""
import csv
import json
import os
import re

_re_bridge = re.compile(r"bridge(?:\s+pickup)?\s*[:\-]\s*([^|;\n]{0,60})")

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
    # Buyer signal 2026-08-13: vibratos are wanted on SEMI-HOLLOWS ONLY, not on a Les Paul.
    # So the +0.5 lb allowance applies to the ES family alone; a Bigsby-equipped LP is
    # excluded outright at sweep/ingest time rather than given extra weight headroom.
    vib = 0.5 if (has_vibrato(g) and g["category"] != "les_paul") else 0.0
    if g["category"] == "les_paul":
        s = band_score(g.get("weight_lbs"), 8.0, 9.0, 8.3, 8.8, falloff=1.2)
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


# Gibson Custom's named carves, with their published 1st/12th depths. Many listings
# name the carve but publish no numbers, so the name IS the measurement.
# V3 (Skinny C) -> V2 -> V1 (a.k.a. "Carmelita") runs slim to medium; the buyer's stated
# ideal is V3, and on 2026-08-13 he confirmed a V1/Carmelita neck also appeals.
NAMED_CARVES = {
    "v3": (0.800, 0.890), "skinny c": (0.800, 0.890),
    "v2": (0.830, 0.940),
    "v1": (0.860, 0.975), "carmelita": (0.860, 0.975),
    "1960 slimtaper": (0.840, 0.960), "60s slim taper": (0.840, 0.960),
    "authentic '59": (0.900, 1.000), "'58 profile": (0.920, 1.010),
}


def carve_depths(g):
    """(f1, f12) implied by a named carve, or (None, None)."""
    text = " ".join(str(g.get(k) or "") for k in
                    ("neck_profile", "shoulder_description", "model", "notes")).lower()
    for name, dims in NAMED_CARVES.items():
        if name in text:
            return dims
    return (None, None)


def neck_component(g):
    """Nut width, fret depths, and whether measurements exist at all."""
    parts, notes = [], []
    imputed = False
    if g["category"] == "les_paul":
        nut = band_score(g.get("nut_width_in"), 1.68, 1.71, 1.69, 1.70, falloff=0.05)
        # Depth targets are the buyer's stated ones (2026-07-19, reaffirmed 2026-08-13:
        # he did NOT ask for deeper necks). The falloff is gentler than the original 0.06
        # so a neck .04" outside target degrades smoothly instead of falling off a cliff
        # from 100 to 27 — a scoring-quality fix, not a change of target.
        d1, d12 = g.get("fret1_depth_in"), g.get("fret12_depth_in")
        if d1 is None and d12 is None:
            cd1, cd12 = carve_depths(g)
            if cd1 is not None:
                d1, d12, imputed = cd1, cd12, True
        f1 = band_score(d1, 0.79, 0.82, 0.79, 0.82, falloff=0.12)
        f12 = band_score(d12, 0.89, 0.92, 0.89, 0.92, falloff=0.14)
    else:
        nut = band_score(g.get("nut_width_in"), 1.56, 1.60, 1.5625, 1.5625, falloff=0.05)
        # Buyer signal 2026-08-16: for ES-335s he prefers a 1st fret UNDER .80".
        # Ideal tightened to .76-.80; .80-.82 stays acceptable but no longer scores 100.
        f1 = band_score(g.get("fret1_depth_in"), 0.76, 0.82, 0.76, 0.80, falloff=0.06)
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
    if imputed:
        notes.append("depths inferred from the named carve, not measured — confirm with dealer")
    if slim_shouldered(g) and score < 75.0:
        # Depth alone under-rates a fast-feeling neck; the shoulders carry the feel.
        notes.append("floored at 75 — documented slim shoulders (feel beats raw depth)")
        score = 75.0
    return max(score, 0.0), "; ".join(notes)


P90_WORDS = ("p-90", "p90", "soapbar", "soap bar", "dog ear", "dogear")
MINI_WORDS = ("mini humbucker", "mini-humbucker", "minibucker", "mini hum", "mini bucker")


def is_mini_hb_lp(g):
    """Mini-humbucker Les Paul (buyer signal 2026-08-13: full-size humbuckers only).
    LP Deluxes shipped minis — but a Deluxe CONVERTED to full-size humbuckers is fine,
    so check for a conversion before excluding, and never judge on the model name alone.
    Note 'Historic Makeovers Deluxe Package' is an upgrade tier, not an LP Deluxe."""
    if g.get("category") != "les_paul":
        return False
    txt = " ".join(str(g.get(k) or "") for k in
                   ("pickups", "model", "notes", "modifications")).lower()
    converted = any(w in txt for w in ("replacing the original mini", "replaced the mini",
                                       "converted", "full-size humbucker", "full size humbucker"))
    if converted:
        return False
    return any(w in txt for w in MINI_WORDS)


def has_p90(g):
    """P-90s on a Les Paul. NOT an exclusion — buyer signal 2026-08-13 reversed that:
    he wants a P-90 in the NECK position. '54/'56 Standard reissues (R4/R6) are dual-P-90;
    LP Customs of those years are not."""
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


HB_WORDS = ("humbucker", "custombucker", "burstbucker", "paf", "t-top", "throbak",
            "57 classic", "'57 classic", "s bucker", "\"s\" bucker", "cloudbucker",
            "490", "498", "mhs", "alnico ii", "alnico iii", "alnico 3")


def bridge_is_p90(g):
    """True when the BRIDGE pickup is a P-90/soapbar. Buyer signal 2026-08-13: a P-90 in
    the NECK is wanted, but a humbucker in the BRIDGE is a hard requirement.

    Judge only on stated pickups — never on the model year. Willcutt sells 1954 Goldtops
    built with Custombuckers ("instead of the traditional P-90s") alongside '56 Goldtops
    with Soapbar P-90s, so year predicts nothing. An unstated pickup set returns False
    here and is flagged separately rather than guessed at."""
    if g.get("category") != "les_paul":
        return False
    txt = " ".join(str(g.get(k) or "") for k in ("pickups", "model", "notes")).lower()
    m = _re_bridge.search(txt)
    if m:                                  # explicit "bridge pickup: X"
        return any(w in m.group(1) for w in P90_WORDS)
    has_p90_word = any(w in txt for w in P90_WORDS)
    has_hb_word = any(w in txt for w in HB_WORDS)
    return has_p90_word and not has_hb_word     # P-90s named, no humbucker anywhere


def p90_neck(g):
    """A P-90 specifically in the NECK position — the configuration the buyer asked for
    (2026-08-13). Catches a stated neck P-90 and the common P-90-neck/humbucker-bridge
    pairing, as well as dual-P-90 guitars (which have one in the neck by definition)."""
    if not has_p90(g):
        return False
    txt = " ".join(str(g.get(k) or "") for k in ("pickups", "model", "notes")).lower()
    for w in P90_WORDS:
        i = txt.find(w)
        while i != -1:
            window = txt[max(0, i - 40):i + 40]
            if "neck" in window:
                return True
            i = txt.find(w, i + 1)
    return True   # dual-P-90 guitar: a P-90 is in the neck by construction


SLIM_WORDS = ("slimtaper", "slim taper", "slim", "1960", "60s", "fast c", "fast d",
              "medium c", "medium-slim", "thin", "skinny")
FAT_WORDS = ("baseball", "chunky", "50s", "fat", "huge", "boat", "clubby")
V3_WORDS = ("v3", "skinny c")   # buyer signal 2026-07-29: V3 / late-1960 Skinny C preferred


# Carves documented as SLIM-SHOULDERED / fast-feeling. Buyer signal 2026-08-13: what he
# values is how a neck feels, and a slim-shouldered carve feels fast even at moderate depth
# (the Carmelita measures ~.860" yet is described as fast because of its shoulders). So a
# documented slim-shouldered carve must not be dragged down by depth figures alone.
SLIM_SHOULDER_CARVES = ("carmelita", "v1 neck", "v2 neck", "v3 neck", "skinny c",
                        "slimtaper", "slim taper", "1960 slim", "60s slim", "fast c",
                        "fast d", "asymmetric")


def slim_shouldered(g):
    text = " ".join(str(g.get(k) or "") for k in
                    ("neck_profile", "shoulder_description", "model", "notes")).lower()
    return any(w in _strip_negated(text) for w in SLIM_SHOULDER_CARVES)


# Named carves that replicate a specific, documented guitar. The buyer's interest is in
# necks described this way — the shape is on record and vouched for — rather than in any
# one carve's depth figures.
DOCUMENTED_CARVES = ("carmelita", "v1 neck", "v2 neck", "v3 neck", "skinny c",
                     "collector's choice", "collectors choice", "cc#", "cc #",
                     "true historic", "cme spec", "wildwood spec", "psl", "m2m",
                     "made to measure", "dealer select", "botb", "beauty of the burst")


# Gibson Custom names its Les Paul carves V1/V2/V3, and listings phrase them freely:
# "'60 V2 Neck", "V2 profile", "V1 (Carmelita)". Match the bare token on word boundaries
# so the carve is recognised however the dealer wrote it. Caught 2026-08-18 on g404, whose
# spec block reads "Neck Profile : '60 V2 Neck".
V_CARVE_RE = re.compile(r"\bv[123]\b")


NEGATORS = (" vs ", " vs. ", "instead of", "rather than", "not a ", "not the ",
            "unlike", "no longer", "as opposed to")


def _strip_negated(text):
    """Drop the clause after a negator so 'Carmelita (vs stock baseball bat)' isn't
    read as a baseball-bat neck. Caught 2026-08-13 on g318."""
    for neg in NEGATORS:
        if neg in text:
            text = text.split(neg)[0]
    return text


def shoulder_component(g):
    text = " ".join(filter(None, [g.get("neck_profile"), g.get("shoulder_description")])).lower()
    if not text:
        return 40.0, "no shoulder/profile info"
    text = _strip_negated(text)
    fat = any(w in text for w in FAT_WORDS)
    slim = any(w in text for w in SLIM_WORDS)
    if g["category"] == "les_paul":
        if any(w in text for w in V3_WORDS):
            return 100.0, "V3/Skinny C — buyer-preferred carve: '%s'" % text[:60]
        # Buyer signal 2026-08-13: he values necks characterised beyond raw depth numbers —
        # named carves replicating a specific, well-regarded guitar, where the shoulders and
        # taper are documented rather than guessed. That is exactly what this component
        # measures, so a documented carve scores high even when depths are unstated. A carve
        # that is BOTH documented and described as slim keeps the 95 slim wording earns on
        # its own — being named must never cost a guitar points (caught 2026-08-18).
        if any(w in text for w in DOCUMENTED_CARVES) or V_CARVE_RE.search(text):
            if slim and not fat:
                return 95.0, "documented carve, slim-described: '%s'" % text[:60]
            return 90.0, "documented/replicated carve (shape known, not just depths): '%s'" % text[:60]
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
    if p90_neck(g):
        score = min(100.0, score + 6.0)
        note += " (+P-90 in neck — buyer-requested)"
    if is_plekd(g):
        score = min(100.0, score + 10.0)
        note += " (+PLEK'd)"
    return score, note


ORIGINAL_WORDS = ("all original", "100% original", "fully original", "original pickups",
                  "original electronics", "original pots", "untouched")
REPLACED_PU_WORDS = ("pickups changed", "pickups replaced", "pickup swap", "replaced pickups",
                     "non-original electronics", "non original electronics", "aftermarket pickup",
                     "seymour duncan", "duncans", "dimarzio", "bare knuckle", "fralin",
                     "replacement pickups", "pickups swapped", "rewound")


ROLLED_WORDS = ("rolled binding", "rolled fingerboard", "rolled fretboard",
                "rolled neck binding", "rolled board", "rolled edges", "rolled edge",
                "hand-rolled", "hand rolled", "eased binding", "eased edges",
                "broken-in binding", "played-in binding")

# Eras and lines where rolled binding is a documented factory spec rather than wear.
ROLLED_SPEC_MARKERS = ("murphy lab", "gibson custom 1959 es", "1959 es-335 reissue",
                       "1961 es-335 reissue", "1963 es-335 reissue", "1964 es-335 reissue",
                       "'59 es-335 reissue", "'63 es-335 reissue", "'64 es-335 reissue")


def rolled_edges(g):
    """Rolled/eased fingerboard binding.

    Buyer signal 2026-08-19, on the Les Paul Custom he actually bought: "the shoulders and
    rolled fretboard edges really did it for me." He names this alongside shoulders as the
    thing that closed a purchase, so it belongs in the feel bucket rather than as a nicety.

    On a 335 the board is bound, so what gets eased is the binding, not bare wood — dealers
    write it as 'rolled binding' as often as 'rolled fingerboard edges'. Both count.

    Stated-in-the-listing only. Gibson Memphis 2015-2018 and the Custom Shop/Murphy Lab ES
    reissues carry it as a factory spec, but era alone is inferred, not documented, so it
    scores lower than a dealer saying it outright — the same rule applied to pickups.
    """
    txt = " ".join(str(g.get(k) or "") for k in
                   ("neck_profile", "shoulder_description", "modifications",
                    "note", "notes", "model")).lower()
    if any(w in txt for w in ROLLED_WORDS):
        return 100.0, "rolled/eased fingerboard binding stated in the listing"
    model = " ".join(str(g.get(k) or "") for k in ("model", "note", "notes")).lower()
    if any(m in model for m in ROLLED_SPEC_MARKERS):
        return 70.0, "rolled binding is a factory spec on this line (not stated in the listing)"
    year, dealer = g.get("year"), (g.get("model") or "").lower()
    if isinstance(year, int) and 2015 <= year <= 2018 and "memphis" in dealer:
        return 70.0, "Gibson Memphis 2015-18 — rolled neck binding was a factory spec that era"
    return 0.0, "no rolled-edge information"


def originality(g):
    """Pickup/electronics originality.

    Buyer evidence 2026-08-16, from two guitars he played back to back at the same shop:
    the ALL-ORIGINAL 1999 ES-335 Dot (g375) — "loved the sound and sustain"; the 1974
    ES-335 (g376) with Seymour Duncans, non-original electronics and a Nashville bridge
    conversion — "pickups and sustain were just ok", despite a neck he found comfortable.
    Original/period-correct electronics predict the tone he wants better than year does.
    Scope this to PICKUPS AND ELECTRONICS only — he did not object to refrets or tuners."""
    txt = " ".join(str(g.get(k) or "") for k in
                   ("pickups", "modifications", "notes", "condition")).lower()
    if any(w in txt for w in REPLACED_PU_WORDS):
        # Softened from -6 on 2026-08-19. The buyer bought a Les Paul whose pickups "weren't
        # what I was looking for" and chose to keep them, because feel decided it. Non-original
        # electronics still predict the tone he liked less well, but they must not outweigh a
        # neck that fits the hand.
        return -3.0, "pickups/electronics replaced (a real but secondary negative)"
    if any(w in txt for w in ORIGINAL_WORDS):
        return 4.0, "original pickups/electronics (buyer's favourite tone so far)"
    return 0.0, None


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
    # Buyer signal 2026-08-13: "slim shoulders are a big part of what I'm after".
    # Rebalanced from the original 35/20 depth-vs-shoulders split: shoulder profile now
    # carries nearly as much as raw depth measurements, because that is what decides feel.
    r, rn = rolled_edges(g)
    # Buyer signal 2026-08-19: shoulders and rolled edges together closed his Les Paul
    # purchase. Feel now carries 35% (shoulders 25 + rolled edges 10), taken from raw depth
    # measurements, which he has repeatedly said matter less to him than how a neck feels.
    total = 0.30 * w + 0.20 * n + 0.25 * s + 0.10 * r + 0.10 * c + 0.05 * p
    pen, pen_note = family_penalty(g)
    orig, orig_note = originality(g)
    total = max(0.0, total - pen + orig)
    g["score"] = round(total, 1)
    g["score_breakdown"] = {
        "weight_30pct": {"score": round(w, 1), "note": wn},
        "neck_20pct": {"score": round(n, 1), "note": nn},
        "shoulders_25pct": {"score": round(s, 1), "note": sn},
        "rolled_edges_10pct": {"score": round(r, 1), "note": rn},
        "condition_10pct": {"score": round(c, 1), "note": cn},
        "price_5pct": {"score": round(p, 1), "note": pn},
    }
    if pen_note:
        g["score_breakdown"]["model_priority"] = {"score": -pen, "note": pen_note}
    if orig_note:
        g["score_breakdown"]["originality"] = {"score": orig, "note": orig_note}
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
