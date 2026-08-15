#!/usr/bin/env python3
"""Pick which Reverb listings to re-verify this run, within a call budget.

Re-verifying every live Reverb listing costs one call each — over 500 on a full
board, which is what earned us a multi-hour anti-bot block on 2026-08-13. A daily
run does not need all of them: what matters is that the guitars the buyer might
actually act on are current, and that nothing goes unchecked indefinitely.

Priority order:
  1. Anything scoring >= HOT_SCORE (the buyer's real shortlist)
  2. Anything flagged as fast-moving: under market, or recently listed
  3. Oldest-checked first, to guarantee full coverage over a rolling window

Usage:
    python3 scripts/reverb_plan.py --budget 200 --date 2026-08-13
Writes the chosen ids + urls to reports/reverb-plan.json and prints a summary,
including how many live listings will go unverified and how stale the oldest is.
"""
import argparse
import json
import os
import re
from datetime import date as _date

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")
OUT = os.path.join(HERE, "reports", "reverb-plan.json")

HOT_SCORE = 80.0
DEAD = ("SOLD", "EXCLUDED", "DUPLICATE")


def days_between(a, b):
    try:
        ya, ma, da = (int(x) for x in str(a)[:10].split("-"))
        yb, mb, db_ = (int(x) for x in str(b)[:10].split("-"))
        return (_date(yb, mb, db_) - _date(ya, ma, da)).days
    except Exception:
        return 999


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=200,
                    help="max Reverb detail calls to spend on verification")
    ap.add_argument("--date", required=True, help="today's date, YYYY-MM-DD")
    args = ap.parse_args()

    with open(DB) as f:
        db = json.load(f)

    live = [g for g in db["guitars"]
            if g.get("status") not in DEAD and "reverb.com" in (g.get("url") or "")]

    def stale_days(g):
        return days_between(g.get("last_confirmed_active"), args.date)

    def priority(g):
        oi = g.get("offer_intel") or {}
        under = (oi.get("over_market_pct") or 0) <= -15
        fresh = (oi.get("days_listed") is not None and oi["days_listed"] <= 14)
        hot = (g.get("score") or 0) >= HOT_SCORE
        # lower sorts first
        return (0 if hot else 1 if (under or fresh) else 2, -stale_days(g))

    ranked = sorted(live, key=priority)
    chosen = ranked[:args.budget]
    skipped = ranked[args.budget:]

    plan = [{"id": g["id"], "url": g["url"], "score": g.get("score"),
             "stale_days": stale_days(g)} for g in chosen]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(plan, f, indent=1)

    hot = sum(1 for g in chosen if (g.get("score") or 0) >= HOT_SCORE)
    oldest = max((stale_days(g) for g in skipped), default=0)
    print("live Reverb listings: %d | verifying: %d (budget %d) | skipping: %d"
          % (len(live), len(chosen), args.budget, len(skipped)))
    print("  of those verified, %d are score >= %.0f" % (hot, HOT_SCORE))
    print("  every listing scoring >= %.0f is covered: %s"
          % (HOT_SCORE, all((g.get("score") or 0) < HOT_SCORE for g in skipped)))
    print("  oldest unverified listing will be %d days stale" % oldest)
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
