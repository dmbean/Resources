#!/usr/bin/env python3
"""Generate the dated markdown report from database.json.

Usage: python3 scripts/report.py --date 2026-07-19
Sections: full ranking, NEW TODAY, BETTER THAN CURRENT BEST, WATCHLIST (top 10 per
category). Also updates meta.current_best in database.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "database.json")

CAT_LABEL = {"les_paul": "Les Paul", "es_335": "ES-335"}


def line(g):
    price = "${:,.0f}".format(g["price_usd"]) if g.get("price_usd") else "n/a"
    return ("| {score} | {id} | {year} {model} | {finish} | {weight} lbs | {price} | "
            "{dealer} | {status} | [link]({url}) |").format(
        score=g["score"], id=g["id"], year=g.get("year") or "—",
        model=(g.get("model") or "")[:48], finish=(g.get("finish") or "")[:28],
        weight=g.get("weight_lbs"), price=price, dealer=g["dealer"][:30],
        status=g.get("status", ""), url=g["url"])


HEADER = ("| Score | ID | Model | Finish | Weight | Price | Dealer | Status | URL |\n"
          "|---|---|---|---|---|---|---|---|---|")


def breakdown(g):
    b = g["score_breakdown"]
    return ("  - weight 30%: {w[score]} ({w[note]}); neck 35%: {n[score]} ({n[note]}); "
            "shoulders 20%: {s[score]} ({s[note]}); condition 10%: {c[score]} ({c[note]}); "
            "price 5%: {p[score]} ({p[note]})").format(
        w=b["weight_30pct"], n=b["neck_35pct"], s=b["shoulders_20pct"],
        c=b["condition_10pct"], p=b["price_5pct"])


def main():
    date = sys.argv[sys.argv.index("--date") + 1]
    with open(DB) as f:
        db = json.load(f)
    gs = db["guitars"]
    active = [g for g in gs if g.get("status") not in ("SOLD",)]
    prev_best = dict(db["meta"].get("current_best") or {})

    out = ["# Gibson Watch — Daily Report — %s" % date, ""]
    out.append("Database: %d guitars total, %d active. Run #%d." %
               (len(gs), len(active), db["meta"].get("run_count", 1)))
    out.append("")

    beats = {}
    for cat in ("les_paul", "es_335"):
        cat_active = [g for g in active if g["category"] == cat]
        best = cat_active[0] if cat_active else None
        pb = prev_best.get(cat)
        if best and (not pb or best["score"] > pb.get("score", 0)) :
            if pb and best["id"] != pb.get("id"):
                beats[cat] = best
        db["meta"]["current_best"][cat] = (
            {"id": best["id"], "score": best["score"], "model": best.get("model"),
             "url": best["url"]} if best else None)

    new_today = [g for g in active if g.get("date_discovered") == date]
    out.append("## NEW TODAY (%d)" % len(new_today))
    out.append("")
    if new_today:
        out.append(HEADER)
        out.extend(line(g) for g in new_today)
    else:
        out.append("_None._")
    out.append("")

    out.append("## BETTER THAN CURRENT BEST")
    out.append("")
    if beats:
        for cat, g in beats.items():
            out.append("- **%s**: %s (score %s) beats previous #1 (%s)" %
                       (CAT_LABEL[cat], g["id"], g["score"], prev_best.get(cat, {}).get("id")))
    elif not any(prev_best.values()):
        out.append("_First populated run — today's #1s set the baseline._")
    else:
        out.append("_No guitar beat the current #1 in either category._")
    out.append("")

    for cat in ("les_paul", "es_335"):
        cat_active = [g for g in active if g["category"] == cat]
        out.append("## WATCHLIST — Top 10 %ss" % CAT_LABEL[cat])
        out.append("")
        out.append(HEADER)
        out.extend(line(g) for g in cat_active[:10])
        out.append("")
        out.append("### Score explanations")
        out.append("")
        for g in cat_active[:10]:
            out.append("- **%s** — %s %s, %s:" % (g["id"], g.get("year") or "",
                       g.get("model"), g.get("finish")))
            out.append(breakdown(g))
            if g.get("research"):
                out.append("  - Research (%s):" % g.get("research_cluster", "cluster"))
                for b in g["research"]:
                    out.append("    - %s" % b)
        out.append("")

    for cat in ("les_paul", "es_335"):
        cat_all = [g for g in gs if g["category"] == cat]
        out.append("## FULL RANKING — %ss (%d)" % (CAT_LABEL[cat], len(cat_all)))
        out.append("")
        out.append(HEADER)
        out.extend(line(g) for g in cat_all)
        out.append("")

    with open(DB, "w") as f:
        json.dump(db, f, indent=2)
    path = os.path.join(HERE, "reports", "%s-report.md" % date)
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print("wrote %s" % path)


if __name__ == "__main__":
    main()
