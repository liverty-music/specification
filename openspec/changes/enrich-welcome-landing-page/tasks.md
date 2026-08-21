## 1. Scroll narrative + reveal foundation

- [ ] 1.1 Convert `welcome-route` layout from two-`100svh`-snap to hero (`100svh`, keeps snap) + continuous value-section column with a consistent vertical rhythm (`--space-*`), preserving the hero markup/copy/CSS unchanged (D1, D7)
- [ ] 1.2 Add a shared `IntersectionObserver`-based scroll-reveal utility that toggles a "revealed" state on first entry and unobserves after (D2)
- [ ] 1.3 Author entrance-only reveal CSS (fade + short upward slide, `transform`/`opacity` only); ensure the un-revealed state keeps content readable/reachable if the observer never fires (spec: "Content is present without motion")
- [ ] 1.4 Disable all reveal + arrival motion under `prefers-reduced-motion: reduce`, rendering final state immediately (reuse existing reduced-motion pattern)

## 2. §2 Timetable value section

- [ ] 2.1 Render the read-only `concert-highway` preview as a complete composed frame (no cropped half-peek), reusing the existing `dateGroups` preview path unchanged
- [ ] 2.2 Add section copy communicating "auto-collected from your followed artists" to `translation.json` (JA/EN); do not touch `welcome.hero.*`
- [ ] 2.3 Ensure the section renders only when preview data is available and disappears with the rest of the stack in the no-preview fallback

## 3. §3 Ticket/goods value section

- [ ] 3.1 Extract the `event-detail-sheet` inner content (`sheet-content`) into a shared read-only content view usable outside `bottom-sheet` (D3); keep the existing sheet + its tests green
- [ ] 3.2 Embed the read-only detail view in §3 surfacing official-info (`sourceUrl`), merch (`merchUrl`), venue + map, and calendar; confirm the `isAuthenticated`-gated ticket-journey stays hidden for the anonymous visitor
- [ ] 3.3 Implement Lv2 arrival motion: the detail view rises once into place on section entry (one-shot, layered on reveal, reduced-motion disabled)
- [ ] 3.4 Add §3 section copy (JA/EN)

## 4. §4 New-concert notification value section

- [ ] 4.1 Create a notification mock card component styled as a Liverty new-concert alert (bell, brand, sample artist line) (D5)
- [ ] 4.2 Implement Lv2 arrival motion: the card drops in with a single brief bell nudge on entry (one-shot, reduced-motion disabled)
- [ ] 4.3 Add §4 section copy (JA/EN)

## 5. §5 Final CTA + value-pillar scope

- [ ] 5.1 Place the commit CTAs (`Get Started` / `Log In`) in a final CTA section after the value content, preserving the two-layer intent (no commit CTAs on the hero when preview exists) and the guest-friendly copy proximity (D6)
- [ ] 5.2 Verify the no-preview fallback (inline hero CTAs, no scroll-affordance) is unchanged
- [ ] 5.3 Confirm no capability beyond the three real pillars is advertised, and no phone-frame chrome / stats / social proof is introduced

## 6. Tests

- [ ] 6.1 Update/extend `welcome-route.stories.ts` for the new sections (data-present and data-absent states)
- [ ] 6.2 Add/adjust unit tests for reveal behavior, reduced-motion no-op, and the no-preview fallback path
- [ ] 6.3 Run `make check` (lint + typecheck + unit tests) and fix issues

## 7. Post-implementation localhost verification (manual, required)

- [ ] 7.1 `npm start` and open the Welcome page (`/`) on localhost as an unauthenticated visitor
- [ ] 7.2 Scroll §1→§5 and visually confirm section scroll-reveal fires cleanly on entry
- [ ] 7.3 Visually confirm §3 (detail view rises once) and §4 (card drop-in + bell nudge) Lv2 arrival motions
- [ ] 7.4 Confirm the preview shows real curated data; then exercise the no-preview state (e.g., empty/insufficient `previewArtistIds`) and confirm graceful degradation to the hero inline-CTA fallback
- [ ] 7.5 Enable `prefers-reduced-motion` and confirm all reveal/arrival motion stops while content stays fully readable
- [ ] 7.6 Check mobile width (real device or DevTools) for layout integrity and readability (no phone-frame; UI renders full-bleed/native size)

## 8. Ship

- [ ] 8.1 Open the frontend PR (Conventional Commits, mandatory body + `Refs: #<issue>`), pass CI
- [ ] 8.2 Merge and cut the frontend release to prod; confirm the prod pin-bump reaches ArgoCD and the change is live
