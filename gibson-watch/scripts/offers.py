#!/usr/bin/env python3
"""Offer intelligence for live Reverb listings.

For each live Reverb listing in database.json, pulls the public API record and
computes: whether the seller accepts offers, days on market, price vs market
anchor, and a suggested opening offer with rationale. Results stored on each
entry as `offer_intel`. Dealer-site listings get anchor comparison only
(no offers flag / listing age available).

Suggested-offer heuristic (documented so it stays stable across runs):
  base discount 8% of ask
  +4% if listed > 90 days (+2 more if > 180)
  +4% if ask >= 110% of effective anchor
  +2% if condition is below excellent, or listing has modifications
  capped at 18% (offers below ~80% of ask are commonly auto-declined on Reverb)
  rounded to the nearest $50
Effective anchor = median of (static market anchor, median live price of the
same market bucket in our database when n >= 3).

Usage: python3 scripts/offers.py --date YYYY-MM-DD
"""
import importlib.util
import json
import os
import re
import statistics
import subprocess
import sys
import time
from datetime import date as date_cls

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")

_spec = importlib.util.spec_from_file_location("gwscore", os.path.join(HERE, "scripts", "score.py"))
_score = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_score)
MARKET_ANCHORS = _score.MARKET_ANCHORS


def api_listing(item_id):
    r = subprocess.run(
        ["curl", "-sS", "--max-time", "20",
         "-H", "Authorization: Bearer anon", "-H", "Accept: application/hal+json", "-H", "Accept-Version: 3.0",
         "https://api.reverb.com/api/listings/%s" % item_id],
        capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def effective_anchor(g, bucket_medians):
    anchors = []
    a = MARKET_ANCHORS.get(g.get("market_bucket") or "")
    if a:
        anchors.append(a)
    m = bucket_medians.get(g.get("market_bucket") or "")
    if m:
        anchors.append(m)
    return statistics.median(anchors) if anchors else None


def suggest(g, days_listed, anchor, today):
    ask = g.get("price_usd")
    if not ask:
        return None
    disc = 0.08
    reasons = ["8% base"]
    if days_listed is not None and days_listed > 90:
        disc += 0.04
        reasons.append("listed %dd" % days_listed)
        if days_listed > 180:
            disc += 0.02
    if anchor and ask >= 1.10 * anchor:
        disc += 0.04
        reasons.append("%.0f%% over market anchor ($%d)" % ((ask / anchor - 1) * 100, anchor))
    cond = (g.get("condition") or "").lower()
    weak_cond = not any(w in cond for w in ("new", "mint", "excellent"))
    mods = (g.get("modifications") or "").lower()
    has_mods = mods and mods not in ("none", "null") and not mods.startswith("none")
    if weak_cond or has_mods:
        disc += 0.02
        reasons.append("condition/mods")
    disc = min(disc, 0.18)
    offer = round(ask * (1 - disc) / 50) * 50
    return {"suggested_offer_usd": offer, "discount_pct": round(disc * 100),
            "rationale": "; ".join(reasons)}


def main():
    args = sys.argv[1:]
    today_s = args[args.index("--date") + 1]
    today = date_cls.fromisoformat(today_s)

    with open(DB) as f:
        db = json.load(f)
    live = [g for g in db["guitars"] if g.get("status") not in ("SOLD", "EXCLUDED")]

    buckets = {}
    for g in live:
        if g.get("price_usd"):
            buckets.setdefault(g.get("market_bucket") or "", []).append(g["price_usd"])
    bucket_medians = {k: statistics.median(v) for k, v in buckets.items() if len(v) >= 3}

    n_offers = 0
    for g in live:
        anchor = effective_anchor(g, bucket_medians)
        intel = {"as_of": today_s, "anchor_usd": round(anchor) if anchor else None}
        if anchor and g.get("price_usd"):
            intel["over_market_pct"] = round((g["price_usd"] / anchor - 1) * 100)
        m = re.search(r"reverb\.com/item/(\d+)", g.get("url") or "")
        if m:
            j = api_listing(m.group(1))
            time.sleep(0.3)
            if j:
                intel["offers_enabled"] = bool(j.get("offers_enabled"))
                created = (j.get("published_at") or j.get("created_at") or "")[:10]
                if created:
                    try:
                        intel["days_listed"] = (today - date_cls.fromisoformat(created)).days
                    except ValueError:
                        pass
                if intel.get("offers_enabled"):
                    s = suggest(g, intel.get("days_listed"), anchor, today)
                    if s:
                        intel.update(s)
                        n_offers += 1
        g["offer_intel"] = intel

    with open(DB, "w") as f:
        json.dump(db, f, indent=2)
    print("offer intel on %d live listings; %d Reverb listings open to offers with suggestions"
          % (len(live), n_offers))


if __name__ == "__main__":
    main()
