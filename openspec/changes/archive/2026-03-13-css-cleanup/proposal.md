## Why

The `improve-css-design` change established the CUBE CSS architecture, but left behind several lint violations bypassed with `stylelint-disable` comments. The `css-linting` spec requires z-index to be rejected, yet a `stylelint-disable-next-line` override remains in `live-highway.css`. Additionally, the `css-linting` spec still references TailwindCSS compatibility requirements that no longer apply after the Tailwind removal.

## What Changes

- Remove the `z-index: 10` usage in `live-highway.css` by replacing it with `isolation: isolate` on the parent element (proper stacking context management)
- Remove all `stylelint-disable` comments that bypass CUBE CSS or anti-pattern rules
- Deduplicate `@keyframes` definitions that exist in both `utilities.css` and component CSS files — consolidate into `@layer utility`
- Remove Tailwind-specific requirements from `css-linting` spec (the `@theme`, `theme()`, and `@apply` at-rule allowances are dead code now)
- Add `prefers-contrast: more` and `forced-colors: active` media query support for accessibility

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `css-linting`: Remove Tailwind CSS v4 compatibility requirements; they are obsolete after the Tailwind removal in `improve-css-design`

## Impact

- **frontend**: CSS files (`live-highway.css`, `utilities.css`, component CSS with duplicate keyframes), `stylelint.config.js` (remove `@theme`/`theme()` allowances)
- **specification**: `openspec/specs/css-linting/spec.md` (remove Tailwind compatibility requirement)
