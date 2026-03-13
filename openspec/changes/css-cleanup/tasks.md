## 1. Remove z-index and fix stacking contexts

- [ ] 1.1 Replace `z-index: 10` in `live-highway.css` `.stage-header` with `isolation: isolate` on the parent container
- [ ] 1.2 Remove the `stylelint-disable-next-line property-disallowed-list` comment in `live-highway.css`
- [ ] 1.3 Verify sticky header renders above scrolling content without z-index

## 2. Remove Tailwind remnants from lint config

- [ ] 2.1 Remove `@theme` from `ignoreAtRules` in `stylelint.config.js` (if present)
- [ ] 2.2 Remove `theme()` from `ignoreFunctions` in `stylelint.config.js` (if present)
- [ ] 2.3 Grep codebase for any remaining `@theme` or `theme()` usage and remove

## 3. Consolidate duplicate @keyframes

- [ ] 3.1 Audit all CSS files for `@keyframes` definitions that duplicate those in `utilities.css`
- [ ] 3.2 Remove duplicate `@keyframes` from component CSS files, keeping only the `utilities.css` definitions
- [ ] 3.3 Verify component animations still reference the correct keyframes names

## 4. Add accessibility and form control enhancements

- [ ] 4.1 Add `prefers-contrast: more` styles to components with insufficient contrast in dark theme
- [ ] 4.2 Add `forced-colors: active` media query to ensure interactive elements remain visible in Windows High Contrast Mode
- [ ] 4.3 Verify existing `prefers-reduced-motion` styles are comprehensive
- [ ] 4.4 Add `accent-color: var(--color-brand-primary)` to form controls (checkbox, radio, select) in `global.css`
- [ ] 4.5 Replace standalone `clip: rect(0, 0, 0, 0)` in `discover-page.css` with `clip-path: inset(50%)` (modern syntax)

## 5. Update specification

- [ ] 5.1 Remove "Stylelint compatible with Tailwind CSS v4" requirement from `css-linting` spec
- [ ] 5.2 Add stacking context management requirement to `css-linting` spec
- [ ] 5.3 Add accessibility media query requirement to `css-linting` spec

## 6. Verification

- [ ] 6.1 Run `make check` — zero stylelint errors, zero biome errors
- [ ] 6.2 Run `make test` — all unit tests pass
- [ ] 6.3 Confirm zero `stylelint-disable` comments remain in the codebase
