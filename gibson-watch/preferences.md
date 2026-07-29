# Learned Preferences

Training data from the buyer's explicit choices. Update on every reject/favorite signal.

## Baseline spec (from initial brief, 2026-07-19)

### Les Paul
- Weight ≤9.0 lbs (soft floor 8.0; ideal 8.3–8.8; lighter is acceptable, heavier is not — revised 2026-07-29)
- Neck carve: **V3 / late-1960 "Skinny C" preferred** (revised 2026-07-29) — matches the stated depth targets
- Nut 1.695" preferred; 1st fret 0.79–0.82"; 12th fret 0.89–0.92"
- Shoulders: minimal — SlimTaper, 1960, fast C. No baseball bats, no 10-pounders.
- Finishes: Ebony, Unburst, Dirty Lemon, Bourbon Burst, Iced Tea
- Models: Standard 60s, R0, Wildwood Spec, select Custom Shop, interesting Norlins
  (~~Standard 60s Plain Top~~ — rejected 2026-07-19, see log)

### ES-335
- Weight 7.4–8.0 lbs, ideal 7.5–7.8
- Nut 1.56–1.60", ideal 1-9/16"; 1st fret 0.76–0.82"
- Shoulders: minimal, fast; D or slim C
- Years: 1972–1980, 1961 Reissue, excellent Memphis
- Pickups: T-Tops, Custombuckers, good PAF-style

## Observed signals

_None yet — no rejections or favorites recorded. Log them below as they happen:_

| Date | Guitar (id) | Signal | Inferred preference shift |
|------|-------------|--------|---------------------------|
| 2026-07-19 | g014 (1973 ES-335, UK) | Buyer requires continental-US availability | Hard constraint: only lower-48 listings qualify; international/AK/HI/PR excluded at sweep time |
| 2026-07-19 | g041 (Willcutt Ebony Plain Top) | "Not a fan of the new LP Standard 60s Plain Top" — model rejected | Remove Standard 60s Plain Top from target models; exclude at sweep time. Figured-top Standard 60s remain in scope. Possible weak signal against plain/unfigured tops generally — watch for confirmation before generalizing. |
| 2026-07-19 | g031, g067, g071 (all >$10k) | "Exclude anything over 10k" | Hard budget cap: $10,000. Applies at sweep time; re-include on price drop below cap. |
| 2026-07-29 | g025, g026 | "I don't like Pelham Blue or Wine Red — exclude from LP searches" | LP finish exclusions: Pelham Blue, Wine Red. Applied at sweep time; existing entries EXCLUDED (cost the former #1 LP). ES-335s unaffected. Watch: if blue finishes generally get rejected next, generalize. |
| 2026-07-29 | — | "Give guitars a higher rating if they've been PLEK'd" | +10 on the condition component (max +1 overall) for stated PLEK work; PLEK'd chip + filter on the board. Only credited when the listing states it. |
| 2026-07-29 | g037 | "I don't like Blueberry Burst either" | CONFIRMED generalization: all blue-family LP finishes excluded (Pelham, Blueberry, Ocean Blue, Cobalt, etc.). Buyer's palette is warm/dark only: Ebony, Unburst, Dirty Lemon, Bourbon, Iced Tea, classic bursts. ES-335s still unaffected. |
| 2026-07-29 | — | "Why do I have a weight floor?" + "I might want a V3 neck for a Les Paul — rank those higher" | Softened weight floors (LP 8.3→8.0 soft, ES 7.4→7.2 soft; ceilings unchanged). V3/Skinny C carve now scores max on the shoulder component; V3-labeled listings prioritized in sweeps. |
| 2026-07-29 | — | "Prioritize looking at NYC shops for new listings in the morning run" | NYC-area shops are swept FIRST every run, never skipped; NYC finds lead the NEW TODAY section of run summaries. Reinforces the try-before-buying preference behind the MIJ/NYC scope and the NYC spotlight on the board. |
| 2026-07-20 | — | "Open to trying Japanese options available in NYC" | Scope expansion: MIJ LP-style (Tokai, Greco, Burny, Edwards, Navigator, Momose) and 335-style (Yamaha SA-2200, Greco SA, Tokai ES, Ibanez JSM/AS) now in scope **when located in the NYC area** (buyer wants to try in person). Same spec targets and weight/measurement rules apply. Epiphone remains excluded. |
