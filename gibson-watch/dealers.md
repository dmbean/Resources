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
- Tone Wolf (Brooklyn, NY) — added to the roster 2026-08-09. Publishes exact weights AND 1st/12th-fret
  depths, which is rare. CORRECTION 2026-08-13: their inventory was NOT previously being missed —
  ~503 of their listings already appear in earlier Reverb sweep caches. Adding them to the roster
  gains a direct Shopify source (tonewolf.com, ~489 in stock), not new inventory.
- Ludlow Guitars — CORRECTION 2026-08-09: their Reverb shop (slug `ludlowguitars`, id 20485) now
  lists a Kirkland WA address and carries only 11 parts/amp listings. Treat as no longer an NYC
  source until that changes.
- Main Drag / 30th Street — 30th Street's Shopify is pedals-only and their guitars go to Reverb;
  neither had in-scope guitars on 2026-08-09. Keep sweeping, but expect thin results.
- Ludlow Guitars — DROPPED 2026-08-13. The domain now redirects to a parked site
  (kaksetosurabaya.com), and their Reverb shop moved to a Kirkland WA address with only ~11
  parts/amp listings. No longer an NYC source; stop sweeping unless it comes back.
- Sweetwater (sweetwater.com) — **BLOCKED, never swept** (checked 2026-08-09). Publishes an exact
  weight for every individual serial, so it is the single best structural fit for the exact-weight
  rule — but the site sits behind PerimeterX bot detection: every route (search, product detail,
  sitemap, robots.txt, homepage, media subdomain) returns a px-captcha 403 regardless of headers.
  Headless Chromium/Playwright is installed here but cannot reach ANY site through this
  environment's proxy (control fetch of reverb.com also returns ERR_CONNECTION_RESET), so the
  browser workaround is unavailable too. Do NOT record Sweetwater as swept. Re-test occasionally;
  reaching it needs a browser-capable or residential-proxy fetch path.

