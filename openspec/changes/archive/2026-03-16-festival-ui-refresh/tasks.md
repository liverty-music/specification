## 1. Design Tokens & Fonts

- [x] 1.1 Update `index.html`: add Righteous + Poppins Google Fonts `<link>` tags (retain existing Outfit link as fallback), update `theme-color` meta to deep navy
- [x] 1.2 Update `tokens.css`: replace brand color values (primary → hot pink, secondary → electric blue, accent → lime green)
- [x] 1.3 Update `tokens.css`: add stage color tokens (`--color-stage-home`, `--color-stage-near`, `--color-stage-away`)
- [x] 1.4 Update `tokens.css`: replace surface color values (base/raised/overlay → deep navy with hue)
- [x] 1.5 Update `tokens.css`: update text color values (secondary/muted → warm-tinted gray)
- [x] 1.6 Update `tokens.css`: update border color opacity values (subtle → 12%, muted → 22%)
- [x] 1.7 Update `tokens.css`: replace `--font-display` to Righteous-first stack, `--font-body` to Poppins-first stack
- [x] 1.8 Update `tokens.css`: update shadow tokens to use relative color syntax (`oklch(from var(--color-brand-primary) l c h / N%)`)

## 2. Global Styles Verification

- [x] 2.1 Verify `global.css` body/link styles reference tokens correctly (no hardcoded colors to update)
- [x] 2.2 Verify `compositions.css` requires no changes (compositions are layout-only, no visual treatment)

## 3. Dashboard Festival Timetable (Block Layer)

- [x] 3.1 Update `dashboard-route.css`: apply per-stage colors to `.stage-header > span` via `[data-stage]` attribute selectors within `@scope` (exception pattern)
- [x] 3.2 Update `dashboard-route.css`: change `font-weight: 700` to `font-weight: normal` on stage header spans (Righteous single-weight constraint)
- [x] 3.3 Update `dashboard-route.css`: lane columns get subtle stage-colored `border-block-start` accents
- [x] 3.4 Update `dashboard-route.css`: date separator background uses stage-color gradient at low opacity

## 4. Navigation & Headers (Block Layer)

- [x] 4.1 Update `bottom-nav-bar.css`: replace `border-block-start` with `::before` pseudo-element gradient (primary → secondary → accent)
- [x] 4.2 Update `bottom-nav-bar.css`: add active tab glow effect via `box-shadow` on `[data-active="true"]`
- [x] 4.3 Update `page-header.css`: subtle gradient background and change `font-weight: 700` to `font-weight: normal`

## 5. Event Card Adjustments (Block Layer)

- [x] 5.1 Review `event-card.css`: verify glow/shadow effects work with new brand colors (token references should auto-propagate)
- [x] 5.2 Update `event-card.css`: change `.artist-name` `font-weight: 800` to `font-weight: normal` (Righteous single-weight constraint)

## 6. Verification

- [x] 6.1 Run `make check` in frontend to verify lint + test pass
- [x] 6.2 Verify WCAG AA contrast: stage header text (`--color-surface-base`) on each stage color background
- [x] 6.3 Verify WCAG AA contrast: body text (`--color-text-primary`) on new surface-base background
- [x] 6.4 Verify no `font-weight` values > 400 remain on elements using `--font-display`
