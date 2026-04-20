## Why

The current Welcome page uses a two-screen `scroll-snap: y mandatory` layout with CTAs duplicated on both screens. This configuration undermines the intended "Promise → Proof" narrative in three ways: (1) the timetable preview on Screen 2 is effectively hidden because the only affordance hinting at its existence is a small, unlabeled floating arrow icon; (2) the `[Get Started]` button on Screen 1 lets users commit to onboarding before they ever see the timetable demo that is supposed to raise their expectations; (3) the floating arrow is absolutely positioned without a proper containing block, so it bleeds into Screen 2 as well.

The goal is to make the Welcome page deliver its strongest message first (hero copy in isolation), then reveal the timetable preview as the single proof moment, and only then present the commitment CTAs — without abandoning the two-screen narrative the design is built around.

## What Changes

- **Remove `[Get Started]` and `[Log In]` buttons from Screen 1 in the normal (preview-available) path.** Screen 1 becomes a message-only "hook" screen when Screen 2 is rendered; the CTAs live exclusively on Screen 2.
- **Preserve an inline `[Get Started]` / `[Log In]` fallback on Screen 1 only when preview data is unavailable** (no Screen 2). Without the fallback, users would have no path to onboarding or sign-in when the preview fails to load.
- **Add a `[See how it works ↓]` scroll-affordance button on Screen 1** as the only primary action when Screen 2 is present. Tapping it smooth-scrolls to Screen 2. Minimum 44×44px tap target, `<button>` element, keyboard-navigable. Hidden when no Screen 2 exists (the fallback CTAs take its place).
- **Introduce a "peek" of Screen 2 above the fold.** Screen 1 uses `block-size: ~95svh` so the top edge of Screen 2 (preview label / frame) is faintly visible at the bottom of the initial viewport, providing a constant structural hint that more content exists.
- **Relax `scroll-snap-type` from `y mandatory` to `y proximity`** so users can stop mid-scroll to read without being forced to a snap point.
- **Remove the `.welcome-scroll-hint` floating arrow element** entirely. The labeled button and peek together replace its affordance job, and removing it also fixes the positioning bug on Screen 2.
- **Keep the language switcher on Screen 1** (below the hero subtitle, above the new scroll button). Its current position is acceptable given the message-first intent — first-visit locale discovery matters.
- **Respect `prefers-reduced-motion`**: disable smooth-scroll and fade-in animations under this media query (already partially in place for hero; extend to the new button's scroll action).
- **Fix pre-existing divergence in `handleGetStarted`**: remove the `this.guest.clearAll()` call so guest follows are preserved when entering onboarding. The landing-page spec has long required "SHALL NOT clear previously stored guest artist data (guest.follows)"; the code had been wiping it. Verification surfaced this as a pre-existing gap; since this change touches `WelcomeRoute` anyway, fixing it here avoids a separate trivial PR. `handleLogin` keeps its `clearAll()` — that path has a different rationale (preventing stale guest.home from leaking into post-auth flow).
- Out of scope: making the timetable preview interactive, redesigning the timetable visuals, touching the onboarding flow after Get Started.

## Capabilities

### New Capabilities

_None. This change refines existing capabilities only._

### Modified Capabilities

- `landing-page`: CTA placement requirements change. Both `[Get Started]` and `[Log In]` CTAs are no longer rendered on Screen 1 — they are rendered only on Screen 2 alongside the preview. A new scroll-affordance button requirement is added for Screen 1. The language switcher requirement is unaffected in behavior but its positional context shifts (now adjacent to the scroll-affordance button rather than below a CTA pair).
- `welcome-dashboard-preview`: Layout requirements change. The two-screen scroll-snap layout is retained but (a) Screen 1 no longer contains CTAs, (b) Screen 1 is sized below the viewport to reveal a Screen 2 peek, (c) snap behavior relaxes from mandatory to proximity, and (d) the floating scroll-hint element is removed. The preview content itself and the data-loading behavior are unchanged.

## Impact

- **Frontend code**: `frontend/src/routes/welcome/welcome-route.{html,ts,css}` — template restructure, new `scrollToPreview()` handler, CSS layout changes (peek sizing, snap relaxation, removed scroll-hint rule).
- **i18n**: New translation keys for the `[See how it works ↓]` button label (EN + JA).
- **Tests**: `frontend/test/routes/welcome-route.spec.ts` — update expectations around button presence on Screen 1. `frontend/e2e/functional/` — new or updated E2E assertions for the scroll-affordance flow and Screen 2 CTA interactions.
- **Storybook**: `frontend/src/routes/welcome/welcome-route.stories.ts` — update story to reflect the new layout.
- **No backend, proto, or infra impact.** This is a frontend-only change; no RPC or schema modification.
- **No breaking change to public API.** Internal UX-only change.
