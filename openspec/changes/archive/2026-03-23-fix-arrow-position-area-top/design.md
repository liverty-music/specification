## Context

Git history analysis (`0d7d6cf`) shows the tooltip worked correctly with `position: fixed` + `position-area: block-end` + `flip-block` + `margin-block: var(--space-s) 0`. The SVG arrow was replaced with `::before` + `clip-path`, but no CSS-only approach could reliably flip the arrow direction:

- `margin: inherit` trick requires `position-area: top` + physical `margin-top`, which broke tooltip positioning in the popover top layer
- `@container anchored (fallback: flip-block)` does not apply to `::before` in Chrome 145 headless or real browser
- `margin-block: inherit` does not flip with `position-area: block-end` because logical properties don't change direction on flip-block

## Goals / Non-Goals

**Goals:**
- Tooltip correctly positioned near target (proven `0d7d6cf` pattern)
- Clean, simple implementation without broken arrow artifacts

**Non-Goals:**
- Arrow indicator (removed — no reliable CSS-only solution exists)

## Decisions

### 1. Remove arrow entirely

**Chosen**: Remove `::before` pseudo-element, clip-path, and all arrow-related CSS.

**Why**: After exhaustive investigation of CSS-only approaches (margin: inherit, @container anchored, margin-block: inherit), none work reliably with `position: fixed` + `position-area: block-end` in a popover top layer. The arrow added visual noise when pointing the wrong direction. The spotlight + tooltip message already provides sufficient onboarding guidance.

**Alternative considered**: JS-based arrow direction control. Rejected — adds complexity for a minor visual element that doesn't affect UX comprehension.

### 2. Restore tooltip to known-good positioning

**Chosen**: `position: fixed` + `position-area: block-end` + `margin-block: var(--space-s) 0` + `flip-block`.

**Why**: Proven pattern from `0d7d6cf`. The `position-area: top` and `position: absolute` experiments both caused regressions (tooltip overlapping target, incorrect coordinate resolution).

## Risks / Trade-offs

- [Risk] Removing arrow reduces visual connection between tooltip and target → Mitigation: The spotlight highlight already draws attention to the target. The tooltip's proximity (via anchor positioning) provides sufficient context.
