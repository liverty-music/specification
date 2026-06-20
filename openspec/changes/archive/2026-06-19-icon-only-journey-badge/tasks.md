## 1. Card badge markup (icon-only)

- [x] 1.1 In `frontend/src/components/live-highway/event-card.html`, replace the icon-wrapper + label `<span>` inside `.journey-badge` with the icon emoji only (`${journeyConfig.icon}`)
- [x] 1.2 Add `role="img"` + `aria-label.bind="journeyConfig.labelKey | t"` to the badge so assistive tech announces the canonical label (a bare `<span>` with implicit `generic` role would not reliably expose the name)

## 2. Card badge styling (corner-bleed bare emoji)

- [x] 2.1 In `frontend/src/components/live-highway/event-card.css`, anchor the badge to the top-right corner (`inset-block-start` + `inset-inline-end`) and add `translate: 40% -40%` so it bleeds half outside the card; keep `position: absolute`
- [x] 2.2 Remove the redundant `overflow: hidden` from `.event-card` so the badge can bleed past the corner without a wrapper (clipping is already handled by `border-radius`, the noise `::after` `border-radius: inherit`, and the matched beam `::before` mask)
- [x] 2.3 Render the badge as the bare emoji (no background pill or hue): keep only position + `translate` + `font-size` + `line-height`; remove label-only rules (`gap`, `font-weight`, `text-transform`, `letter-spacing`, `color`) and the now-dead `background`, `padding`, `border-radius`, and flex-centering
- [x] 2.4 Remove the now-unused per-status `--_journey-text` AND `--_journey-bg` custom properties (the card badge no longer paints a hue; chips and the detail control keep their own hue)

## 3. Verification

- [x] 3.1 `npx stylelint` on `event-card.css` and `tsc --noEmit` for the changed files pass (admin-area TS errors are pre-existing and unrelated)
- [x] 3.2 Confirm on the dashboard timetable that each of the five statuses renders as a bare corner-bleed emoji (no background) with no artist-name overlap — verified via a throwaway Playwright run (authenticated, mocked follow/user/concert/journey RPCs) across HOME (no venue label) and AWAY (rightmost) lanes with short/medium/very-long names; emojis 👀📝💔💰🎟️ sit on the top-right corner, short/medium names fully clear, AWAY-lane badges not clipped by `concert-scroll` (`clipped:false`), and removing `overflow:hidden` left corners/gradient/noise/matched glow+beam visually intact
- [x] 3.3 Confirm the dashboard filter chips and concert-detail status control still show icon + label — verified statically: only `event-card.{html,css}` changed; `artist-filter-bar.html` and `event-detail-sheet.html` still render `config.icon` + `t.bind` label
- [x] 3.4 Visual baselines — no regeneration needed for this change. The card-layout baseline (`dashboard-data-loaded.png`, `mobile-visual` project) is guest-mode with no journey data, so the badge does not appear in it; the `overflow: hidden` removal was pixel-inert there (#456 Visual Regression passed unchanged). The journey badge has no active CI visual spec (`ticket-journey.visual.spec.ts` is `.fixme`) — adding that coverage is tracked separately in frontend#459, out of scope here.
