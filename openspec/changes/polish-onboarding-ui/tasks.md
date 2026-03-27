## 1. DNA Orb Sizing

- [x] 1.1 Update `stage-effects.ts` constants: `BASE_RADIUS=60`, `GROWTH_PER_FOLLOW=7.5`, `LINEAR_STEPS=4`, `MAX_RADIUS=90`
- [x] 1.2 Update `bubble-physics.ts` `orbZoneHeight` from 160 to 130
- [x] 1.3 Verify orb growth curve: follow 0→60, 1→67.5, 2→75, 3→82.5, 4→90(MAX)

## 2. Lane Intro Sequencing

- [x] 2.1 Modify `dashboard-route.ts` `startLaneIntro()`: when `needsRegion=true`, show HOME coach mark before opening Home Selector
- [x] 2.2 Verify the coach mark text matches spec: "ここがHOME STAGEです。あなたの地元のライブが並びます。居住エリアはどこですか？"
- [x] 2.3 Verify Home Selector opens inline alongside the coach mark (not replacing it)

## 3. My Artists Header Cleanup

- [x] 3.1 Remove `<span class="artist-count">` from `my-artists-route.html`
- [x] 3.2 Remove any associated `.artist-count` CSS rules

## 4. Signup Banner Layout

- [x] 4.1 Change `.signup-banner` flex-direction from row to column in `signup-prompt-banner.css`
- [x] 4.2 Make CTA button full-width (`inline-size: 100%`)
- [x] 4.3 Reposition dismiss button (×) to top-right of banner
- [x] 4.4 Verify banner renders correctly above bottom nav bar

## 5. Validation

- [x] 5.1 Run `make check` in frontend repo
- [ ] 5.2 Visual check: Discovery page orb sizing at 0, 3, and 5+ follows
- [ ] 5.3 Visual check: Dashboard lane intro shows coach mark before Home Selector
- [ ] 5.4 Visual check: Signup banner vertical layout on mobile viewport
