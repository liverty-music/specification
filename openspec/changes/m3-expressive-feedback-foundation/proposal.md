## Why

The frontend already ships modern, oklch-based tokens and CUBE CSS, but interaction feedback is
**unevenly distributed**: the discovery DNA orb is rich (physics, haptics, ripple, celebration) while the
rest of the app is a "flat zone" — press feedback is a uniform `scale(0.97)`, content loading renders a bare
`<p>loading</p>` (no skeletons anywhere), lists appear/disappear instantly, and haptics exist only in the
canvas orb. Measured in the codebase: `transition: border-radius` (shape morph) = 0 occurrences, skeleton /
shimmer = 0, `navigator.vibrate` = orb-only, `@starting-style` = 3.

The root cause is the absence of a **shared M3 token + feedback-primitive layer**. Without shared
state-layer, motion (spring), skeleton, ripple, and haptic primitives, every screen would have to reinvent
feedback, so only discovery got it. This change establishes that foundation and rolls it out across the app
so every surface feels as alive as discovery — the Material 3 Expressive standard of acknowledging every
interaction (immediate → in-progress → outcome) without over-animating.

Scope note (per user direction "全てスコープに入れて"): this change includes the token foundation, all five
feedback primitives, AND their application across all primary screens — not a single pilot screen.

## What Changes

- **New M3 token layer** (semantic aliases over existing oklch tokens, non-breaking):
  - Color **roles** with guaranteed `on-*` pairings (`primary`/`on-primary`, `tertiary`,
    `*-container`/`on-*-container`, `surface-container-*` tiers, `outline`).
  - **State-layer** opacity tokens (hover 8% / focus·press 12% / drag 16% / selected 12%) replacing ad-hoc
    per-component `color-mix` opacities.
  - **Motion** tokens: standard + emphasized easing curves, and spring approximations split into
    **spatial** (bouncy: transform/size/radius) vs **effects** (non-bouncy: color/opacity), plus a duration
    scale — replacing scattered raw-ms values and one-off cubic-beziers.
  - Shape **role** aliases (incl. Expressive `-increased` steps) and shape-morph-ready radii.
  - Expanded **surface-container** tiers (3 → 5) for tonal elevation.
- **Five shared interaction-feedback primitives** (delivered as reusable CUBE utilities / Aurelia custom
  attributes / a shared service, mirroring the existing `busy-on-click` pattern):
  1. **Skeleton** loading placeholders that preserve layout (replace text/spinner loading states).
  2. **Ripple + press-morph** on tap (contact-point ripple; round↔squircle `border-radius` morph on
     `:active`) applied app-wide to buttons and tappable cards.
  3. **Haptic** feedback service (generalize the orb's `vibrate()`) wired to meaningful confirm actions.
  4. **List enter/exit** transitions (`@starting-style` + `transition-behavior: allow-discrete`) for
     follow/unfollow and content lists.
  5. **Selection spring-morph** for nav tabs and filter chips (selected segment morphs rounder with a
     spatial spring).
- **App-wide rollout**: apply the primitives across dashboard, my-artists, bottom-nav, filter bar, forms,
  and other primary surfaces, so feedback is consistent rather than siloed in discovery.
- Every animation carries a `prefers-reduced-motion: reduce` fallback that lands the end state; every
  primitive respects `forced-colors` / high-contrast.

## Capabilities

### New Capabilities
- `m3-design-tokens`: The Material 3 semantic token layer for the frontend — color roles with `on-*`
  pairings, state-layer opacities, spatial/effects motion + easing + duration, shape roles, and tonal
  surface-container tiers — expressed in the project's oklch + CUBE CSS idiom as aliases over existing
  tokens.
- `interaction-feedback`: The app's interaction-feedback contract — which interactions must acknowledge
  (press/ripple/morph/haptic), how in-progress state is communicated (skeletons), how outcomes are
  confirmed, and how lists and selections animate — plus the reduced-motion / high-contrast guarantees.

### Modified Capabilities
<!-- None. Applying feedback primitives to existing screens changes their presentation, not their
     behavioral requirements; the cross-cutting behavior (skeleton-while-loading, haptic-on-confirm,
     animated selection) is owned by the new `interaction-feedback` capability. -->

## Impact

- **Affected code (frontend)**:
  - `src/styles/tokens.css` — add M3 role/state-layer/motion/shape aliases + 2 new surface tiers.
  - `src/styles/global.css`, `src/styles/utilities.css` — press-morph baseline, ripple utility, skeleton
    utility, list-transition helpers.
  - New `src/custom-attributes/` entries (ripple, press-morph) + a shared haptic service under
    `src/services/` (generalized from `components/dna-orb/dna-orb-canvas.ts`).
  - `src/components/state-placeholder/` — add a skeleton/loading variant.
  - Rollout edits across `routes/dashboard`, `routes/my-artists`, `components/bottom-nav-bar`,
    `components/artist-filter-bar`, and other primary surfaces.
- **Dependencies**: none new (pure CSS + platform APIs — `@starting-style`, `allow-discrete`,
  Web Vibration API). iOS Safari lacks `navigator.vibrate`; haptics degrade gracefully (feature-detected).
- **Non-goals / out of scope**: no design-system component library adoption (`@material/web` rejected
  earlier — maintenance mode); no dynamic-color seed generation; no backend/proto changes.
- **Risk**: motion/haptic over-application. Mitigated by the M3 expression budget (1–2 hero moments per
  flow) and reduced-motion/forced-colors fallbacks as acceptance criteria.
