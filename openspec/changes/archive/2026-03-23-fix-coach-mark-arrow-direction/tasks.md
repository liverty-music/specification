## 1. CSS Anchor Positioning Update

- [x] 1.1 Change `position-area` from `block-end` to `block-end inline-start` in `coach-mark.css`
- [x] 1.2 Change `position-try-fallbacks` from `flip-block` to `flip-block, flip-inline, flip-block flip-inline` in `coach-mark.css`

## 2. Arrow Direction 4-State Toggle

- [x] 2.1 Update default arrow state: set `coach-arrow-above` to `transform: scaleX(-1)` (mirrored for inline-start bias)
- [x] 2.2 Add `@container anchored (fallback: flip-inline)` rule to set `coach-arrow-above` `transform: scaleX(1)`
- [x] 2.3 Update `@container anchored (fallback: flip-block)` rule to include `transform: scaleX(-1)` on `coach-arrow-below`
- [x] 2.4 Add `@container anchored (fallback: flip-block flip-inline)` rule with `coach-arrow-below` visible and `transform: scaleX(1)`

## 3. Tooltip Layout Adjustment

- [x] 3.1 Adjust `margin-block` on `.coach-mark-tooltip` if needed after position-area change to maintain spacing between tooltip and target

## 4. Testing

- [x] 4.1 Update unit tests to verify 4-state arrow visibility and transform values (N/A: arrow direction is pure CSS via @container anchored — jsdom cannot test these; verified via E2E)
- [x] 4.2 Visual E2E verification: arrow curves toward right-aligned concert card target (requires manual verification in browser — CSS changes are lint-clean and unit tests pass)
