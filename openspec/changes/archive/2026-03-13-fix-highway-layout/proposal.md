## Why

The `live-highway` component has a structural anti-pattern: the stage header (`HOME STAGE / NEAR STAGE / AWAY STAGE`) is placed inside the scroll container as a `position: sticky` sibling of date-separator elements. This forces a `z-index: 10` hack (violating the `property-disallowed-list` stylelint rule), a hardcoded `inset-block-start: 41px` magic number on date separators (violating design token conventions), and an unnecessary `isolation: isolate` on the scroll container. Additionally, the parent layout uses `flex-direction: column` for what is a 2D structure-first layout, violating the web-design-specialist layout engine selection principle.

## What Changes

- Move `.stage-header` out of `.highway-scroll` to be a sibling in `.highway-layout`, eliminating the sticky stacking conflict entirely
- Convert `.highway-layout` from `display: flex; flex-direction: column` to `display: grid; grid-template-rows: auto 1fr` (2D structure-first layout)
- Remove `position: sticky` and `inset-block-start: 0` from `.stage-header` (no longer needed outside the scroll container)
- Change `.date-separator` from `inset-block-start: 41px` to `inset-block-start: 0` (no more magic number)
- Remove `isolation: isolate` from `.highway-scroll` (no longer needed without z-index conflicts)
- Add `scrollbar-gutter: stable` to `.highway-scroll` to prevent column misalignment between the header and the scroll content

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `css-linting`: Remove the incorrect stacking context management rule ("Components SHALL manage stacking via `isolation: isolate` on parent containers instead of arbitrary z-index values") added by the `css-cleanup` change. The correct approach is structural — elements that need different stacking should not be sticky siblings in the same scroll container.

## Impact

- `frontend/src/components/live-highway/live-highway.html` — DOM restructure (move stage-header out of scroll container)
- `frontend/src/components/live-highway/live-highway.css` — Layout engine change (flex → grid), remove sticky/z-index/isolation hacks, fix magic number
- `specification/openspec/changes/css-cleanup/design.md` — Correct the flawed Decision 1 reasoning about `isolation: isolate`
- `specification/openspec/changes/css-cleanup/specs/css-linting/spec.md` — Remove incorrect stacking context rule
- No backend or API changes
