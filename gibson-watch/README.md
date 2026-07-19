# Gibson Watch Agent — Persistent Database

Long-running sourcing agent for a Gibson Les Paul and an ES-335. Runs every 24 hours.

## Layout

- `database.json` — historical database of every guitar ever found. Never delete entries; mark status instead (`ACTIVE`, `SOLD`, `PRICE DROP`, `PRICE INCREASE`). Each entry keeps full specs, score breakdown, price history, and discovery/confirmation dates.
- `preferences.md` — learned buyer preferences. Updated whenever the buyer rejects or favorites a guitar. Treat as training data for scoring adjustments.
- `dealers.md` — dealer roster, including dealers discovered during runs (searched on every subsequent run).
- `scripts/score.py` — deterministic scorer (weight 30%, neck 35%, shoulders 20%, condition 10%, price 5%). Run: `python3 scripts/score.py` from `gibson-watch/` to rescore `database.json` in place.
- `reports/master.csv` — master spreadsheet regenerated each run from the database.
- `reports/YYYY-MM-DD-report.md` — daily run report: full ranking, NEW TODAY, BETTER THAN CURRENT BEST, WATCHLIST (top 10 per category).

## Run procedure (each 24h cycle)

1. Re-confirm every ACTIVE listing's URL. Missing/sold → mark `SOLD` (keep in database). Price changed → mark `PRICE DROP`/`PRICE INCREASE` and append to `price_history`.
2. Sweep all dealers in `dealers.md` for new listings (individual product pages only — never category/search pages).
3. Dedupe against database by serial number, URL, and dealer inventory ID.
4. Score new entries with `scripts/score.py`; do forum research (Reddit, The Gear Page, MyLesPaul) for each genuinely new listing and store a 5-bullet summary in the entry's `research` field.
5. Regenerate `reports/master.csv` and write the dated report.
6. Notify immediately if: any score > 95; price ≥15% under market; new Norlin ES-335; lightweight R0; Ebony Standard 60s under 8.8 lbs.
