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
2. Sweep all dealers in `dealers.md` for new listings (individual product pages only — never category/search pages). **Continental-US availability is required**: exclude listings located outside the lower 48 (international, Alaska, Hawaii, PR). Existing entries found to violate this get status `EXCLUDED` (kept in the database, hidden from live views).
   **Model exclusions from buyer signals**: Les Paul Standard 60s Plain Top (rejected 2026-07-19)
   — do not ingest; existing entries are EXCLUDED. Figured-top Standard 60s remain in scope.
   **Standing narrow-nut hunt**: every sweep must include dedicated queries for 1-9/16" nut ES-335s — the buyer's ideal nut, found only on 1965–1981 vintage examples (modern reissues are all 1-11/16"). Reverb API queries: "es-335 1 9/16", "es-335 narrow nut", "es-335 1.56", plus year-specific searches 1968–1980; also sweep dealers that publish nut widths (Carter, CME used, Gruhn).
3. Dedupe against database by serial number, URL, and dealer inventory ID.
4. Score new entries with `scripts/score.py`; do forum research (Reddit, The Gear Page, MyLesPaul) for each genuinely new listing and store a 5-bullet summary in the entry's `research` field.
5. Regenerate `reports/master.csv` and write the dated report.
6. Notify immediately if: any score > 95; price ≥15% under market; new Norlin ES-335; lightweight R0; Ebony Standard 60s under 8.8 lbs.
7. Fetch photos for new listings: `python3 scripts/images.py` (Reverb photos via API,
   dealer pages via og:image; thumbs cached in `site/thumbs/`, needs `pip install pillow`).
   Then regenerate the listings board and republish it: `python3 scripts/site.py`, then publish
   `site/index.html` with the Artifact tool (same file path keeps the same URL). The buyer's
   pinned board: https://claude.ai/code/artifact/5767f4d9-f871-41fc-833a-02ca59e472f3
   (favicon 🎸 — keep it, and pass a dated version label like "run-N-YYYY-MM-DD").
   The buyer prefers this board over spreadsheets; a one-off Google Sheet from 2026-07-19
   exists in their Drive but is not maintained.
