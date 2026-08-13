# Gibson Watch Agent — Persistent Database

Long-running sourcing agent for a Gibson Les Paul and an ES-335. Runs every 24 hours.

## Layout

- `database.json` — historical database of every guitar ever found. Never delete entries; mark status instead (`ACTIVE`, `SOLD`, `PRICE DROP`, `PRICE INCREASE`). Each entry keeps full specs, score breakdown, price history, and discovery/confirmation dates.
- `preferences.md` — learned buyer preferences. Updated whenever the buyer rejects or favorites a guitar. Treat as training data for scoring adjustments.
- `dealers.md` — dealer roster, including dealers discovered during runs (searched on every subsequent run).
- `scripts/score.py` — deterministic scorer (weight 30%, **shoulders 30%**, neck depths 25%, condition 10%, price 5%; shoulders raised from 20% and depths cut from 35% on 2026-08-13 — the buyer said slim shoulders are a big part of what he is after, and a documented slim-shouldered carve floors the neck component at 75 so a fast-feeling neck is not dragged down by a few thousandths of depth). Run: `python3 scripts/score.py` from `gibson-watch/` to rescore `database.json` in place.
- `reports/master.csv` — master spreadsheet regenerated each run from the database.
- `reports/YYYY-MM-DD-report.md` — daily run report: full ranking, NEW TODAY, BETTER THAN CURRENT BEST, WATCHLIST (top 10 per category).

## Operational notes (read before each run)

- **WebFetch is broken in this environment** (its fetch path 403s for every URL even with open
  egress). Fetch pages with Bash curl + a browser user agent; append `.js` to Shopify product
  URLs for availability JSON. Reverb HTML blocks curl — use the public API instead:
  `https://api.reverb.com/api/listings/<id>` (and `?query=` for search) with headers
  `Accept: application/hal+json` and `Accept-Version: 3.0`; only `state: "live"` counts.
- **Fresh container?** Run `pip install pillow` before `scripts/images.py`.
- **Reverb rate-limiting is real.** After the very large sweeps of 2026-08-09 (~20k listings in a
  day), api.reverb.com returned a 403 anti-bot wall to this environment for hours — every endpoint,
  every header variation. Dealer sites were unaffected. Keep per-run Reverb volume moderate, pace
  at >=1.5s between calls, and NEVER run two Reverb-fetching agents concurrently.
- **Give each sweep agent its OWN scratch directory.** On 2026-08-13 two agents wrote to the same
  path and one picked up the other's script, doubling load against an already-blocked endpoint.
- **Always date a run from the system clock** (`date -u +%F`) — never infer today's date from
  the previous run or from conversation context. On 2026-08-09 a run was mis-stamped 2026-08-05,
  so the board's "last sweep" line read as stale to the buyer even though the data was fresh.
- **Pipeline order matters**: update `meta.last_run`/`run_count` BEFORE running `scripts/site.py`,
  otherwise the board embeds a stale run number (site.py snapshots meta at generation time).
- **On-demand runs (2026-08-01)**: the daily Routine is PAUSED at the buyer's request. The board
  header has a "↻ Refresh" button that deep-links into this agent session; any buyer message like
  "run" triggers a full cycle. (A page-side button cannot fire the agent directly — the artifact
  runtime has no channel back into the session — so the button opens the chat instead.)
- The board must be republished with the **Artifact tool from this session** using file path
  `gibson-watch/site/index.html` — same path keeps the buyer's pinned URL. If the Artifact tool
  is ever unavailable in a run, say so in the run summary instead of skipping silently.

- **Run summaries must include direct listing links** for every guitar mentioned (buyer
  request 2026-07-29) — never make the buyer hunt for a URL on the board. Pull the `url`
  field from database.json for each id referenced.

## Run procedure (each 24h cycle)

1. Re-confirm every ACTIVE listing's URL. Missing/sold → mark `SOLD` (keep in database). Price changed → mark `PRICE DROP`/`PRICE INCREASE` and append to `price_history`.
2. Sweep all dealers in `dealers.md` for new listings (individual product pages only — never category/search pages).
   **NYC shops first (buyer signal 2026-07-29)**: start every sweep with the NYC-area shops —
   TR Crandall, Southside, Rudy's, Rivington, Retrofret, 30th Street, Main Drag, Ludlow
   (Reverb shop only — domain hijacked), plus Reverb searches filtered/checked for NYC-area
   seller locations. Sweep them every run without fail (national dealers may rotate if time
   is short, NYC may not), and lead the run summary's NEW TODAY section with NYC finds. **Continental-US availability is required**: exclude listings located outside the lower 48 (international, Alaska, Hawaii, PR). Existing entries found to violate this get status `EXCLUDED` (kept in the database, hidden from live views).
   **Price cap from buyer signal (2026-07-19): $10,000** — do not ingest listings priced above
   $10k; existing entries above the cap are EXCLUDED (re-include if a price drop brings one under).
   **Finish exclusions for LPs (buyer signal 2026-07-29, generalized same day)**: Wine Red and ALL blue-family finishes (Pelham Blue, Blueberry Burst, Ocean Blue, Cobalt, etc.) — do not ingest Les Pauls in these finishes. Buyer's LP palette is warm/dark: Ebony, Unburst, Dirty Lemon, Bourbon Burst, Iced Tea, classic bursts. ES-335s unaffected.
   **Mini-humbucker exclusion (buyer signal 2026-08-13)**: no mini-humbucker Les Pauls.
   That means LP Deluxes (1969-84) are OUT by default — but a Deluxe CONVERTED to full-size
   humbuckers is acceptable, so read the listing before rejecting or ingesting one. Do not
   judge from the model name: "Historic Makeovers Deluxe Package" is an upgrade tier, not a
   Les Paul Deluxe. Always record the pickups.
   **P-90 exclusion (buyer signal 2026-08-09)**: Les Pauls with P-90/soapbar pickups are OUT —
   the buyer's LP spec is humbucker-equipped (Standard 60s, R0, PAF-style). This means '54 and
   '56 Standard reissues (R4/R6) and Goldtops of those years do NOT qualify, however good the
   weight or neck. '57+ reissues (R7/R8/R9/R0) are humbucker guitars and remain in scope.
   Check the PICKUPS before scoring a Goldtop — this rule was missed once and put six P-90
   guitars at the top of the board.
   **Model exclusions from buyer signals**: Les Paul Standard 60s Plain Top (rejected 2026-07-19)
   — do not ingest; existing entries are EXCLUDED. Figured-top Standard 60s remain in scope.
   **Standing MIJ/NYC hunt (added 2026-07-20)**: Japanese-made LP-style (Tokai LS/Love Rock,
   Greco EG, Burny RLG, Edwards E-LP, Navigator, Momose) and 335-style (Yamaha SA-2200,
   Greco SA, Tokai ES, Ibanez JSM/AS) are in scope ONLY when the listing is in the NYC area
   (five boroughs + close NJ/CT/Long Island — buyer wants to play before buying). Same weight,
   measurement, and price rules. Epiphone still excluded. NYC shops to sweep: TR Crandall,
   Southside, Rudy's, Rivington Guitars, Retrofret (Brooklyn), 30th Street Guitars,
   Main Drag Music (Brooklyn), Ludlow Guitars, plus Reverb listings with NYC-area shops.
   **Named carves (buyer signal 2026-08-13)**: Gibson Custom's carves run V3/"Skinny C"
   (.800"/.890") -> V2 (.830/.940) -> V1, a.k.a. "Carmelita" (.860/.975). The buyer's ideal is
   V3; V1/Carmelita is CONFIRMED acceptable. Sweeps must record the carve NAME even when no
   depths are published — the scorer infers depths from the name (and flags them as inferred).
   Search dealer text for: carmelita, V1/V2/V3 neck, skinny C, CME Spec, PSL, M2M, Dealer Select.
   **V3 neck priority (buyer signal 2026-07-29)**: Les Pauls with the V3 / late-1960 "Skinny C"
   carve (≈.80" 1st / .89" 12th — 60th Anniversary V3, some M2M/Wildwood Spec V3 orders) rank
   highest on neck feel; add "V3", "skinny C", and "60th anniversary v3" to LP sweep queries.
   Weight floors are SOFT as of 2026-07-29 (LP 8.0, ES 7.2) — do not reject light guitars.
   **Vibrato allowance (buyer signal 2026-08-09)**: ceilings are LP 9.0 / ES 8.0, but rise to
   LP 9.5 / ES 8.5 when a vibrato (Bigsby, Maestro, Vibrola, sideways) is fitted — the buyer
   likes vibratos and accepts their weight. Ideal bands unchanged, so lighter still ranks higher.
   Every sweep must record the vibrato type when present, or the allowance cannot be applied.
   **Model priority (buyer signal 2026-08-09)**: ES-335s and Les Pauls are the CORE targets.
   ES-345/355/347/340 stay in scope but carry a -6 score adjustment so they never outrank an
   equivalent 335. Sweeps should spend effort on 335s and LPs first, other ES models second.
   **ES-family note (2026-08-09)**: sweeps cover ES-345/355/347/340 on the same rules as the 335. Always record Varitone (intact/bypassed/removed), stereo-vs-mono wiring, and weight-adding hardware (Bigsby/Maestro/TP-6/gold). ES-347s ship Dirty Fingers (hot ceramic, not PAF-style) — flag that explicitly.
   **Standing narrow-nut hunt**: every sweep must include dedicated queries for 1-9/16" nut ES-335s — the buyer's ideal nut, found only on 1965–1981 vintage examples (modern reissues are all 1-11/16"). Reverb API queries: "es-335 1 9/16", "es-335 narrow nut", "es-335 1.56", plus year-specific searches 1968–1980; also sweep dealers that publish nut widths (Carter, CME used, Gruhn).
3. Dedupe against database by serial number, URL, and dealer inventory ID.
4. Score new entries with `scripts/score.py`; do forum research (Reddit, The Gear Page, MyLesPaul) for each genuinely new listing and store a 5-bullet summary in the entry's `research` field.
   Terminology: "NEW TODAY" = newly *discovered* by the watch (sweeps are query samples, not full
   crawls, so older listings surface as coverage grows). True market age comes from offer intel's
   `days_listed` and is shown on the board ("on market Nd" + a "Fresh listing" chip when ≤7 days).
5. Regenerate `reports/master.csv` and write the dated report.
6. Notify immediately if: any score > 95; price ≥15% under market; new Norlin ES-335; lightweight R0; Ebony Standard 60s under 8.8 lbs.
6b. Offer intelligence: `python3 scripts/offers.py --date YYYY-MM-DD` — refreshes, for every
   live Reverb listing, the offers_enabled flag, days on market, over-market %, and a suggested
   opening offer (heuristic documented in the script header). Shown on the board as an amber
   "Offers" chip + dashed suggestion box. Surface standout negotiation targets (long-listed,
   well over anchor) in the run summary.
7. Fetch photos for new listings: `python3 scripts/images.py` (Reverb photos via API,
   dealer pages via og:image; thumbs cached in `site/thumbs/`, needs `pip install pillow`).
   Then regenerate the listings board and republish it: `python3 scripts/site.py`, then publish
   `site/index.html` with the Artifact tool (same file path keeps the same URL). The buyer's
   pinned board: https://claude.ai/code/artifact/5767f4d9-f871-41fc-833a-02ca59e472f3
   (favicon 🎸 — keep it, and pass a dated version label like "run-N-YYYY-MM-DD").
   The buyer prefers this board over spreadsheets; a one-off Google Sheet from 2026-07-19
   exists in their Drive but is not maintained.
