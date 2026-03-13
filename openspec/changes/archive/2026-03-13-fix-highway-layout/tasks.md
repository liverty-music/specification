## 1. Restructure live-highway DOM

- [x] 1.1 Move `.stage-header` out of `.highway-scroll` to be a direct child of `.highway-layout` (before `.highway-scroll`) in `live-highway.html`

## 2. Update live-highway CSS

- [x] 2.1 Convert `.highway-layout` from `display: flex; flex-direction: column` to `display: grid; grid-template-rows: auto 1fr`
- [x] 2.2 Remove `position: sticky` and `inset-block-start: 0` from `.stage-header`
- [x] 2.3 Remove `isolation: isolate` from `.highway-scroll`
- [x] 2.4 Add `scrollbar-gutter: stable` to `.highway-scroll`
- [x] 2.5 Change `.date-separator` `inset-block-start` from `41px` to `0`

## 3. Fix global.css prefers-contrast rule

- [x] 3.1 Remove `a` from the `:where(button, a, input, textarea, select)` selector in the `prefers-contrast: more` media query in `global.css`

## 4. Correct css-cleanup design and spec

- [x] 4.1 Rewrite Decision 1 in `openspec/changes/css-cleanup/design.md` to describe DOM restructuring instead of `isolation: isolate`
- [x] 4.2 Update the stacking context management requirement in `openspec/changes/css-cleanup/specs/css-linting/spec.md` to reference proper DOM structure instead of `isolation: isolate`

## 5. Update css-state-separation tasks

- [x] 5.1 Remove section 6 from `openspec/changes/css-state-separation/tasks.md` and ensure sections 1-4 tasks are fully atomic (both TS/HTML and CSS changes in each task)

## 6. Verification

- [x] 6.1 Run `make check` in frontend — zero stylelint errors, zero biome errors, all unit tests pass
- [x] 6.2 Grep for `z-index` in frontend CSS — zero occurrences
- [x] 6.3 Grep for `41px` in frontend CSS — zero occurrences
- [x] 6.4 Grep for `stylelint-disable` in frontend CSS — zero occurrences
