# Dealer Roster

## Core list (from brief)

Reverb, Chicago Music Exchange, Wildwood, Willcutt, Dave's Guitar Shop, Music Emporium,
Carter Vintage, Gruhn, Elderly, Cream City, Emerald City, Southside, Rudy's, TR Crandall,
Empire Music, Music Zoo, Rainbow Guitars, CME Used, Guitar Center Used, Music Go Round

## Discovered during runs

_Add dealers found via forums/listings here; they get searched on every subsequent run._

- Mike & Mike's Guitar Bar (mmguitarbar.com) — Seattle; strong vintage 335 stock with shop-measured
  specs; cross-lists on Reverb, so dedupe against Reverb items by specs (their serials are unpublished).
  Discovered 2026-07-20.
- NYC MIJ hunting grounds (added 2026-07-20 for the Japanese-options scope expansion):
  Rivington Guitars (rivingtonguitars.com, East Village), Retrofret (retrofret.com, Brooklyn),
  30th Street Guitars (30thstreetguitars.com), Main Drag Music (maindragmusic.com, Brooklyn),
  Ludlow Guitars (ludlowguitars.com). Sweep for MIJ LP/335-style per README rules.
- Tone Wolf (Brooklyn, NY — Reverb shop) — DISCOVERED 2026-08-09 during the full NYC sweep.
  ~500 listings; publishes exact weights AND 1st/12th-fret depths, which is rare and makes them
  high-value for this buyer's spec rules. Held 6 qualifying Les Pauls on discovery. Sweep every run
  with the NYC group.
- Ludlow Guitars — CORRECTION 2026-08-09: their Reverb shop (slug `ludlowguitars`, id 20485) now
  lists a Kirkland WA address and carries only 11 parts/amp listings. Treat as no longer an NYC
  source until that changes.
- Main Drag / 30th Street — 30th Street's Shopify is pedals-only and their guitars go to Reverb;
  neither had in-scope guitars on 2026-08-09. Keep sweeping, but expect thin results.
- CAUTION (2026-07-24): ludlowguitars.com redirects to an unrelated Indonesian site (possible
  domain hijack). Do not fetch the domain; check Ludlow Guitars' Reverb shop instead until resolved.
- Sweetwater (sweetwater.com) — **BLOCKED, never swept** (checked 2026-08-09). Publishes an exact
  weight for every individual serial, so it is the single best structural fit for the exact-weight
  rule — but the site sits behind PerimeterX bot detection: every route (search, product detail,
  sitemap, robots.txt, homepage, media subdomain) returns a px-captcha 403 regardless of headers.
  Headless Chromium/Playwright is installed here but cannot reach ANY site through this
  environment's proxy (control fetch of reverb.com also returns ERR_CONNECTION_RESET), so the
  browser workaround is unavailable too. Do NOT record Sweetwater as swept. Re-test occasionally;
  reaching it needs a browser-capable or residential-proxy fetch path.

