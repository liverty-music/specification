## 1. Complementary hue derivation

- [x] 1.1 Update `artistHueFromColorProfile()` in `frontend/src/adapter/view/artist-color.ts` to return `(dominantHue + 180) % 360` for chromatic logos instead of `dominantHue` directly
- [x] 1.2 Update unit tests in `frontend/src/adapter/view/artist-color.spec.ts` to verify complementary hue calculation (pink 335° → 155°, red 29° → 209°, blue 260° → 80°)

## 2. Remove unmatched dimming

- [x] 2.1 Replace `.event-card:not([data-matched])` background rule in `frontend/src/components/live-highway/event-card.css` — remove the clamped `oklch(clamp(...))` calculation and use `var(--artist-color-dim)` instead
- [x] 2.2 Remove the `--_bg-l` / `--artist-bg-lightness` consumption in the unmatched rule (the CSS custom property from `artist-color` attribute can remain for potential future use)

## 3. Logo width fill

- [x] 3.1 Update `.artist-logo` in `frontend/src/components/live-highway/event-card.css` — change `max-inline-size: 80%` to `inline-size: 100%`, keep `object-fit: contain` and `max-block-size: 25cqi`

## 4. Verification

- [x] 4.1 Run `make check` in frontend to verify lint, typecheck, and tests pass
