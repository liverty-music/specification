## 1. Token foundation (m3-design-tokens)

- [ ] 1.1 Add M3 color role aliases to `src/styles/tokens.css`: `primary`/`on-primary`,
      `secondary`/`on-secondary`, `tertiary`/`on-tertiary` (map `brand-accent` → tertiary), plus
      `*-container`/`on-*-container` and `outline`/`outline-variant`, as oklch aliases/derivations over
      existing brand tokens.
- [ ] 1.2 Expand surface tiers from 3 to 5 (`surface-container-lowest` → `-highest`) aliased over
      base/raised/overlay + two derived tiers; document the physical↔semantic mapping inline.
- [ ] 1.3 Add state-layer opacity tokens (hover 8% / focus 12% / press 12% / drag 16% / selected 12%).
- [ ] 1.4 Add motion tokens: standard + emphasized easing curves, duration scale, and spring cubic-bezier
      approximations split into `*-spatial` (overshoot) and `*-effects` (no overshoot). Verify values against
      m3.material.io.
- [ ] 1.5 Add shape role aliases over existing radius tokens incl. Expressive `-increased` steps; confirm
      logical radius usage.
- [ ] 1.6 Run `make lint` (stylelint token/oklch/logical rules) and confirm zero hex/hsl and no regressions.

## 2. Shared feedback primitives

- [ ] 2.1 Standardize state layers: refactor the shared hover/focus/press feedback to consume the 1.3 tokens
      via `color-mix`/oklch-relative; ensure `:focus-visible` (not bare `:focus`) everywhere.
- [ ] 2.2 Build the `press-feedback` custom attribute (ripple at contact point + `:active` round↔squircle
      radius morph using a spatial spring); zero-specificity base so component `:active` keeps precedence;
      stable hit area; reduced-motion fallback to a non-motion acknowledgement.
- [ ] 2.3 Add a `.skeleton` CUBE utility (layout-preserving blocks, shimmer via effects token, static under
      reduced motion) and a loading/skeleton variant of `state-placeholder`.
- [ ] 2.4 Extract a `HapticService` (DI singleton) from the orb `vibrate()`, feature-detected, no-op where
      unsupported; define tap vs confirm pulse durations.
- [ ] 2.5 Add list enter/exit transition helpers (`@starting-style` + `transition-behavior: allow-discrete`)
      as a shared utility/attribute with reduced-motion fallback.
- [ ] 2.6 Add a selection spring-morph treatment (color + rounder shape morph, driven by selected/aria state,
      spatial spring, reduced-motion fallback) as a shared style.

## 3. Rollout — content & loading

- [ ] 3.1 Dashboard: replace `<p>loading</p>` / all-nearby loading text with content-shaped skeletons; verify
      no layout shift on resolve (reference screen for the no-CLS scenario).
- [ ] 3.2 my-artists: replace the centered spinner loading with skeletons; animate follow(enter)/
      unfollow(exit) list items via 2.5.
- [ ] 3.3 Other content lists/routes (import-ticket-email, concert lists) adopt skeleton + list transitions
      where a loading/spinner state exists today.

## 4. Rollout — controls & selection

- [ ] 4.1 Apply `press-feedback` (2.2) app-wide to buttons and tappable cards (dashboard cards, event-card,
      CTAs); confirm bespoke components (orb) are unaffected.
- [ ] 4.2 bottom-nav-bar: convert the selected-tab treatment to the selection spring-morph (2.6).
- [ ] 4.3 artist-filter-bar chips: convert selected state to selection spring-morph (2.6).
- [ ] 4.4 Wire `HapticService` (2.4) to confirm actions (follow/unfollow confirmation, and other meaningful
      confirmations), alongside existing visual feedback.
- [ ] 4.5 Migrate remaining scattered raw-ms / one-off cubic-bezier transitions (snack-bar, pwa-install-banner,
      welcome, celebration-overlay) to the motion tokens from 1.4.

## 5. Accessibility & expression-budget verification

- [ ] 5.1 Audit each flow for the expression budget (1–2 hero moments); demote any over-expressive siblings to
      foundational.
- [ ] 5.2 Verify every new animation has a `prefers-reduced-motion: reduce` path that lands the end state
      (grep + manual toggle).
- [ ] 5.3 Verify `forced-colors: active` / high-contrast: surfaces distinguishable by tonal tier, controls
      operable, focus visible.
- [ ] 5.4 Verify contrast on dynamic-hue surfaces (artist-hue cards) across the hue range with the new
      on-color roles.
- [ ] 5.5 Confirm touch targets remain ≥ 44–48px and labels retained after press-morph rollout.

## 6. Gate & manual verification

- [ ] 6.1 `make check` (lint + typecheck + tests) green; add/adjust component smoke tests where feedback
      changes rendered output.
- [ ] 6.2 Drive the app (dashboard + my-artists + discovery) to confirm skeletons, ripple/press-morph,
      list transitions, selection morph, and haptics (on a supporting device) behave and degrade correctly.
