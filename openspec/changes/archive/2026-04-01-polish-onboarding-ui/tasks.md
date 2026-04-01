## 1. DNA Orb Sizing

- [x] 1.1 Update `stage-effects.ts` constants: `BASE_RADIUS=60`, `GROWTH_PER_FOLLOW=7.5`, `LINEAR_STEPS=4`, `MAX_RADIUS=90`
- [x] 1.2 Update `bubble-physics.ts` `orbZoneHeight` from 160 to 130
- [x] 1.3 Verify orb growth curve: follow 0→60, 1→67.5, 2→75, 3→82.5, 4→90(MAX)

## 2. Lane Intro Sequencing

- [x] 2.1 Update Home Selector description text (`userHome.description`) to convey HOME STAGE context
- [x] 2.2 Verify `startLaneIntro()` does NOT activate coach mark spotlight during `waiting-for-home` (z-index overlap)
- [x] 2.3 Improve Home Selector spacing (padding, line-height, grid gap) for readability

## 3. My Artists Header Cleanup

- [x] 3.1 Remove `<span class="artist-count">` from `my-artists-route.html`
- [x] 3.2 Remove any associated `.artist-count` CSS rules

## 4. Signup Banner Layout

- [x] 4.1 Change `.signup-banner` flex-direction from row to column in `signup-prompt-banner.css`
- [x] 4.2 Make CTA button centered, content-width with generous padding
- [x] 4.3 Reposition dismiss button (×) to top-right of banner
- [x] 4.4 Verify banner renders correctly above bottom nav bar

## 5. Validation

- [x] 5.1 Run `make check` in frontend repo
- [x] 5.2 Visual check: Discovery page orb sizing at 0, 3, and 5+ follows
- [x] 5.3 Visual check: Dashboard Home Selector shows HOME STAGE description text
- [x] 5.4 Visual check: Signup banner vertical layout on mobile viewport
