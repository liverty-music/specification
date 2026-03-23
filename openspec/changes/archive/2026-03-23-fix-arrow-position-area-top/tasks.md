## 1. Restore tooltip to known-good positioning

- [x] 1.1 Restore `position: fixed` + `position-area: block-end` + `flip-block`
- [x] 1.2 Restore `margin-block: var(--space-s) 0`
- [x] 1.3 Remove `--arrow-size`, `--arrow-gap` custom properties

## 2. Remove arrow

- [x] 2.1 Remove `::before` pseudo-element rules (clip-path, z-index, anchor, margin)
- [x] 2.2 Remove `@container anchored` rule
- [x] 2.3 Remove `container-type: anchored` / `container-name` from tooltip

## 3. Update tests

- [x] 3.1 Replace arrow-specific E2E assertions with tooltip proximity checks
- [x] 3.2 Update tooltip background assertion in onboarding-flow.spec.ts

## 4. Verify

- [x] 4.1 E2E suite `css-antipattern-verification.spec.ts` — 6 passed
- [x] 4.2 `make check` — 0 stylelint errors
