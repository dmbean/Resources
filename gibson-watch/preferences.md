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
| 2026-08-13 | g525 (CME Spec '59, Carmelita neck, $7,199) | "I don't know the neck on that one, I'm just interested in these necks that address more than depth measurements in a highly regarded way." + "I like how the Carmelita is described as feeling fast because of the slimmer shoulders" | CORRECTION of an over-read: this is NOT "V1/Carmelita depths are acceptable". The real signal is that the buyer values necks characterised by SHAPE — documented, well-regarded carves whose SHOULDERS make them feel fast — over raw depth numbers. Depth targets stay as originally stated. Encoded as: (a) named carves infer depths (flagged inferred); (b) a documented/replicated carve scores 90 on shoulders; (c) a documented SLIM-SHOULDERED carve floors the neck component at 75, so a fast-feeling neck is not dragged down by a few thousandths of depth. Collector's Choice models are the purest example of this category — each replicates one specific, documented neck.
| 2026-08-13 | g140 (1973 LP Deluxe), g145 (1977 LP Deluxe) | "No mini humbuckers. Looks like at least one made it back on there." | Full-size humbuckers only for LPs. LP Deluxes excluded by default; verified each against the dealer page first, which mattered: g142 is a Deluxe converted to '57 Classics (KEPT) and g392 "Historic Makeovers Deluxe Package" is an upgrade tier, not a Deluxe (KEPT). Sweeps must record pickups and check for conversions rather than rejecting on the model name. |
| 2026-08-13 | — | "I don't want a Bigsby on a Les Paul, just semi hollows" + "I would very much like a P90 in the neck of an LP, so let's not exclude those" + "humbucker in the bridge is a requirement still" | TWO REVERSALS. (1) Vibrato allowance is now SEMI-HOLLOW ONLY; vibrato-equipped Les Pauls are excluded (8 removed). (2) The blanket P-90 LP ban of 2026-08-09 is REVERSED — 54 guitars restored. New rule: humbucker in the BRIDGE is required, P-90 in the NECK is a positive (+6 on condition). Dual-P-90 guitars fail on the bridge. Also learned: the year-based P-90 inference was wrong in both directions — Willcutt builds '54 Goldtops with Custombuckers and '56 Goldtops with P-90s, so only STATED pickups may be used. |
| 2026-07-20 | — | "Open to trying Japanese options available in NYC" | Scope expansion: MIJ LP-style (Tokai, Greco, Burny, Edwards, Navigator, Momose) and 335-style (Yamaha SA-2200, Greco SA, Tokai ES, Ibanez JSM/AS) now in scope **when located in the NYC area** (buyer wants to try in person). Same spec targets and weight/measurement rules apply. Epiphone remains excluded. |
| 2026-08-13 | — | "Let's do dealer-first runs with a light reverb pass" + "add a filter for unpotted pickups, we can remove the plek'd filter" | Run shape changed: all 18 dealer sites every run, then ONE budgeted Reverb pass (~250 calls: 200 verification via scripts/reverb_plan.py, ~50 sweep, single agent, >=1.5s pacing, no retry loops on 403). Board filter swapped from PLEK'd (2 live matches) to Unpotted (52 live matches); PLEK scoring bonus retained. |
| 2026-08-16 | — | "Add a filter for a first fret depth of < .80\" — that would be my preference for 335s" | ES-335 ideal 1st-fret band tightened from .76-.82 to .76-.80 (.80-.82 still acceptable, no longer scores 100). Board gets a `1st < .80\"` toggle. COVERAGE PROBLEM: only 64 of 188 live ES listings publish a 1st-fret figure at all, and just 8 are under .80\" — so the filter shows a real but small slice, and a guitar with no published depth is invisible to it rather than excluded. Sweeps should ask dealers for 1st-fret depth on ES-335s the way they already do for weight. |
