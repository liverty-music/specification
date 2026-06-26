## Context

The frontend (Aurelia 2, CUBE CSS, `@layer` cascade) is a touch-first PWA. An audit of ~22 files with interactive elements found only 7 defined any `:active` rule (`welcome`, `settings`, `discovery`, `consent`, `signup-prompt-banner`, `pwa-install-fab`, `event-card`). The global `:where(button)` base style in `src/styles/global.css` had no `:active` feedback, and the bottom-nav tabs (the primary navigation) had none. Because the reset sets `-webkit-tap-highlight-color: transparent` and `:hover` is inert on touch, taps feel dead.

The existing press convention across the 7 components is `transform: scale(...)` (values 0.92–0.98) + a fast `~50ms ease-in` press-in. The cascade order is `reset, tokens, global, composition, utility, block, exception` (`src/styles/main.css`), so `@layer block` overrides `@layer global`.

A coverage audit of the remaining tappables found that the high-traffic interaction surfaces (`artist-filter-bar`, `discovery`, `event-detail-sheet`, `page-help`) are all `<button>` elements, so a single `<button>` baseline reaches them. The genuine non-`<button>` exceptions are the nav tabs and the dashboard `.discover-cta` (both `<a>`), plus settings list rows.

## Goals / Non-Goals

**Goals:**
- Every native `<button>` gets press feedback from one baseline rule, with zero per-component edits.
- The primary `<a>`-based tappables (nav tabs, discover CTA) and settings rows get explicit press feedback.
- All cues honor `prefers-reduced-motion: reduce`.
- Reuse the existing scale + fast-ease-in convention; introduce no new visual language.
- Components with their own `:active` are untouched.

**Non-Goals:**
- Restoring `-webkit-tap-highlight-color` (rejected below).
- Adding press feedback to plain text links (`not-found-link`, "back to dashboard" links).
- Haptic or sonic feedback (covered separately by `discovery-tap-sonic-feedback`).
- Any proto/backend/API change.

## Decisions

### `:active` press cues over restoring `-webkit-tap-highlight-color`
The default tap highlight is a rectangular flash that ignores `border-radius` and is not on-brand. A `:active` scale respects component shape, matches the app's existing motion language, and is controllable per element. Cost is slightly more CSS, accepted for the UX gain. Alternative (restore the highlight) rejected.

### Button baseline in `@layer global`, not per component
Placing `:where(button):active:not(:disabled)` in `@layer global` covers all 20 button-bearing templates at once while staying below `@layer block`, so the 7 components that already define `:active` automatically win with no conflict. `:not(:disabled)` keeps disabled controls inert.

### Explicit `:active` for the two `<a>`-based primary tappables
The `<button>` baseline cannot reach `<a>` elements. The nav tabs (`.nav-tab`) and the dashboard `.discover-cta` are styled and used as primary buttons, so each gets a dedicated `:active`. `.discover-cta` lives in `@layer utility` (`src/styles/utilities.css`); its `:active` is added there. The remaining bare `<a>` elements are plain text links and are intentionally excluded.

### Scale magnitude follows existing per-element precedent
Large tap targets use a stronger scale (FAB `0.92`), standard buttons cluster at `0.97–0.98`. The button baseline uses a standard-button magnitude; the nav tab uses the large-target magnitude (matching the FAB). This keeps the cue proportional to control size rather than applying one global value.

### List rows deepen background instead of scaling
A full-width row reads better with a background-deepen than a scale. `.settings-row` (a `<button>`) sets `transform: none` to suppress the global scale and applies a deeper `:active` background, so button-rows and anchor-rows feel identical.

### iOS activation rule is a hard constraint, not an afterthought
iOS Safari only applies `:active` when the element (or an ancestor) has `cursor: pointer` or is an `<a href>`. All targets satisfy this: `<button>` inherits `cursor: pointer` from the reset; `.nav-tab` and `.discover-cta` are `<a href>`; `.settings-row` is a `<button>`. This is an implementation constraint baked into the selectors, not a verification step.

## Risks / Trade-offs

- [A future `<a>`- or `<div>`-based primary control is added without `:active`] → The baseline only covers `<button>`; new non-button primary controls must add their own `:active` (captured as a spec requirement so reviewers catch it).
- [`transform` on a press establishes a containing block / paint layer] → Targets are leaf controls with no fixed-position descendants; effect is negligible.
- [Inconsistent reduced-motion fallbacks per element (opacity vs background)] → Acceptable: each fallback fits its element type; the single rule "drop motion, keep a non-motion cue" is captured in the spec.

## Migration Plan

1. Implement the four CSS edits on the existing branch `claude/ui-feedback-tap-effects-wtcgzt`.
2. Run `make lint` (Biome + stylelint + typecheck) and `brand-vocabulary` check.
3. Open the frontend PR; merge after CI is green.
4. Ship to prod via the standard frontend release (GitHub Release → AR retag → pin bump → ArgoCD).
5. Rollback is trivial: revert the CSS-only commit; no data or API surface is affected.

## Open Questions

- None blocking. Whether to retrofit `.discover-cta`-style anchor CTAs with a shared utility `:active` (rather than per-class) can be a later cleanup if more anchor-CTAs appear.
