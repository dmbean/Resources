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
| 2026-08-09 | — | "Are we prioritizing NYC?" (audit) | NYC weigh-in-person listings were scoring 0 on weight (30% of score), capping every playable NYC guitar near 70 (avg 33.5 vs 64.7 board-wide). Buyer chose neutral scoring: unknown weight on a NYC listing now scores 65 with a 'weigh in person' marker on the card. |
| 2026-08-09 | — | "Any reason I shouldn't consider an ES-345 or another ES model with semi-hollow build, humbuckers, and the nut width?" (prompted by a 345 at Rudy's + the Back to the Future 345) | SCOPE EXPANSION: ES-345, ES-355, ES-347, ES-340 (all years) + their reissues now in scope under identical ES-335 rules. Rationale: the 1-9/16" nut is era-driven (~1965-81) across the whole ES line, not model-specific. Caveats recorded: these models carry weight-adding hardware (Varitone choke, gold hardware, Bigsby/Maestro, TP-6), so only 8% of published weights clear 8.0 lbs; ES-347 ships Dirty Fingers (hot ceramic, not PAF-style) and had ZERO examples under the ceiling. Record Varitone/stereo status on every 345/355. |
| 2026-08-09 | — | "I don't mind if the guitar is heavier because of a vibrato. I like vibratos and understand the tradeoffs, but would obviously prefer a lighter guitar." | Vibrato is a POSITIVE, not a tolerated flaw. Weight ceilings get a +0.5 lb allowance when a vibrato (Bigsby/Maestro/Vibrola/sideways) is fitted: ES 8.0→8.5, LP 9.0→9.5. The IDEAL band is unchanged (ES 7.5–7.8, LP 8.3–8.8) so lighter still scores higher — a vibrato guitar simply is not punished for its hardware. Sweeps must record vibrato type. |
| 2026-08-09 | g419,g420,g424,g426,g429,g432 (Willcutt V3 Goldtops) | "It looks like you're including LPs with P90s now for some reason" | ERROR CAUGHT BY BUYER: a sweep kept Goldtops as "warm finishes" without checking pickups, and '54/'56 Standard reissues ship P-90s — six of them reached the top of the board (95.6, the highest scores ever recorded). P-90/soapbar Les Pauls are now excluded outright; 54 live entries EXCLUDED. Buyer's LP spec is humbucker-only. '57+ reissues (R7/R8/R9/R0) unaffected. |
| 2026-08-09 | — | "Prioritize 335s and Les Pauls over other ES models" | ES-345/355/347/340 remain in scope but take a -6 score adjustment so a 335 or LP always ranks first; sweep effort goes to core targets first. |
| 2026-08-13 | g525 (CME Spec '59, Carmelita neck, $7,199) | "You sent me this one... it has a Carmelita neck and close enough to my budget. Can we find more like this?" | FAVORITE — first positive carve signal beyond V3. Gibson Custom carves run V3/Skinny C (.800/.890) → V2 (.830/.940) → V1 a.k.a. Carmelita (.860/.975); the buyer's ideal is V3 but V1 is confirmed acceptable. Neck ACCEPTABLE band widened to 1st .790–.880, 12th .890–1.000 (ideal unchanged at .790–.820/.890–.920, so a V3 still outranks a Carmelita). Added NAMED_CARVES so a listing that names a carve but publishes no numbers gets depths inferred (flagged as inferred, not measured). |
| 2026-07-20 | — | "Open to trying Japanese options available in NYC" | Scope expansion: MIJ LP-style (Tokai, Greco, Burny, Edwards, Navigator, Momose) and 335-style (Yamaha SA-2200, Greco SA, Tokai ES, Ibanez JSM/AS) now in scope **when located in the NYC area** (buyer wants to try in person). Same spec targets and weight/measurement rules apply. Epiphone remains excluded. |
