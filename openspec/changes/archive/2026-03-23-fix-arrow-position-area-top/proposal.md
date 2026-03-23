## Why

The coach-mark tooltip arrow (`::before` + `clip-path`) could not be made to reliably flip direction when the tooltip flips position (via `position-try-fallbacks: flip-block`). Multiple approaches were attempted:

1. `margin: inherit` trick (css-tip.com pattern) — requires `position-area: top` + physical `margin-top`, which broke tooltip positioning
2. `@container anchored (fallback: flip-block)` — not firing in current Chrome for `::before` pseudo-elements
3. `margin-block: inherit` — logical properties don't flip with `position-area: block-end`

The arrow added visual complexity with no reliable CSS-only solution for direction control. Removing it simplifies the component while maintaining the core UX (spotlight + tooltip message).

## What Changes

- Remove `::before` arrow (clip-path, z-index, anchor positioning)
- Remove arrow-related CSS custom properties (`--arrow-size`, `--arrow-gap`)
- Restore tooltip to proven `0d7d6cf` positioning pattern (`position: fixed` + `position-area: block-end` + `margin-block: var(--space-s) 0`)
- Update E2E tests: replace arrow-specific assertions with tooltip-near-target proximity checks

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

(none — CSS bug fix and simplification, no spec-level behavior changes)

## Impact

- `frontend/src/components/coach-mark/coach-mark.css` — tooltip rules simplified
- `frontend/e2e/css-antipattern-verification.spec.ts` — arrow tests replaced with proximity tests
- `frontend/e2e/onboarding-flow.spec.ts` — tooltip background assertion updated
