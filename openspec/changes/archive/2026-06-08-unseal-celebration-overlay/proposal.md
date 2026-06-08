## Why

The onboarding celebration overlay is meant to be the emotional payoff for "your personal timetable is ready" — yet its backdrop (`background: oklch(0% 0 0deg / 80%)` + `backdrop-filter: blur(8px)`) covers the entire viewport, collapsing the vibrant festival-palette timetable into dark, muddy blocks at the exact moment we most want to show it off. The celebration says "あなただけのタイムテーブルが完成しました！" while hiding the very thing it is celebrating. The first impression therefore reads as flat and dull ("地味").

## What Changes

- Replace the celebration overlay's full-screen opaque veil with a **localized "text-lens"**: a feathered radial darkening sized to the heading + sub-text group, so the completed timetable stays fully colorful at the screen edges while the text retains guaranteed contrast.
- Lower the overall scrim (full-viewport dim) to a light value and drop the heavy full-screen `backdrop-filter: blur(8px)`, so the timetable behind reads as the vibrant payoff rather than a dark smudge.
- Keep the existing brand-purple glow halo behind the heading and strengthen text shadows so legibility holds even over the brightest stage cards (e.g. near-stage cyan).
- Preserve all current behavior: two-tier gating (`maybeCelebrate()`), at-most-once-per-tier, confetti flag, tap-to-dismiss, and `prefers-reduced-motion` handling are unchanged.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `onboarding-celebration`: add a requirement governing the overlay backdrop — the celebration MUST keep the completed timetable visible/legible behind the text instead of fully obscuring it, while preserving heading/sub-text contrast.

## Impact

- **Frontend only.** Affected file: `frontend/src/components/celebration-overlay/celebration-overlay.css` (backdrop / scrim / text-shadow rules).
- Potentially `frontend/src/components/celebration-overlay/celebration-overlay.spec.ts` if a contrast/backdrop assertion is added; frontend visual baselines may need regeneration (intentional UI change).
- No backend, no proto/BSR, no API, no dependency changes. Behavior (tiers, gating, dismissal, reduced-motion) is unchanged.
