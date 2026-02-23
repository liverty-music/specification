## Why

The area selection dialog on the Home screen overlaps with the bottom navigation bar, making the lower portion of the dialog and the navigation tabs inaccessible (GitHub issue: liverty-music/frontend#73). The root cause is that both the bottom sheet components (`region-setup-sheet`, `area-selector-sheet`) and `bottom-nav-bar` use `position: fixed; bottom: 0` with competing Tailwind z-index utilities (`z-30`, `z-40`, `z-50`) — a fragile "z-index war" pattern that violates the project's Web Platform Baseline 2026 standards. The correct fix is to migrate the bottom sheets to the native `<dialog>` element, which promotes content to the browser's Top Layer automatically, eliminating z-index management entirely.

## What Changes

- Replace `region-setup-sheet`'s fixed-position `<div>` + manual backdrop with a `<dialog>` element using `showModal()` / `close()`, leveraging the native `::backdrop` pseudo-element.
- Replace `area-selector-sheet`'s fixed-position `<div>` + manual backdrop with a `<dialog>` element using the same pattern.
- Remove all z-index utilities (`z-30`, `z-40`, `z-50`) from these sheet components and their backdrops.
- Retain existing slide-up animation via CSS transitions on the `<dialog>` element.
- Preserve accessibility: `<dialog>` provides native focus trapping, ESC-to-close, and `inert` on background content automatically.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `settings`: The "My Area" bottom sheet interaction now uses a native `<dialog>` element instead of a z-index-based overlay. The user-facing behavior (2-step region/prefecture selection, close on selection) is unchanged.
- `app-shell-layout`: The area setup sheet shown on first visit now renders via Top Layer (`<dialog>`) instead of competing with the bottom navigation bar's stacking context. Navigation visibility rules are unchanged.

## Impact

- **Frontend components**: `region-setup-sheet`, `area-selector-sheet` (template + logic rewrite)
- **Frontend tests**: Existing tests for these components need to update element queries (`<dialog>` instead of `<div>`)
- **No backend changes**
- **No API changes**
- **No breaking changes to user-facing behavior**
