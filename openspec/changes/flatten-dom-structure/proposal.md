# Flatten DOM Structure

## Problem

Multiple templates have unnecessary wrapper elements that increase DOM depth without serving a layout or styling purpose. This adds complexity to CSS selectors, increases render tree size, and makes templates harder to maintain.

Key patterns:
- Double wrappers: `.callback-layout` > `.callback-content` > actual content
- State containers: `.state-center` > `.state-content` > icon + text
- Overlay divs that could be CSS pseudo-elements: `.grid-tile-overlay`
- Coach mark uses 4 separate `.click-blocker` divs instead of a single CSS mask
- Decorative dividers using `<div>` instead of `<hr>`

## Proposed Solution

1. Remove single-purpose wrapper divs where the parent can absorb the styling
2. Replace overlay divs with CSS `::before` / `::after` pseudo-elements
3. Consolidate coach-mark blocker structure to a single element with CSS `clip-path` or mask
4. Replace `<div class="settings-divider">` with semantic `<hr>`
5. Flatten `.state-center` > `.state-content` to a single container

## Scope

- **In scope**: HTML template restructuring and corresponding CSS selector updates
- **Out of scope**: TypeScript logic changes, component extraction
- **Depends on**: `semantic-html-landmarks` (should be applied first so this change builds on semantic structure)

## Affected Files

HTML + CSS pairs:
- auth-callback (.html, .css)
- welcome-page (.html, .css)
- dashboard (.html, .css)
- tickets-page (.html, .css)
- settings-page (.html, .css)
- my-artists-page (.html, .css)
- coach-mark (.html, .css)
- notification-prompt (.html, .css)

## Risk

Medium. CSS selectors that target removed wrappers must be updated. Tests using DOM selectors may need adjustment. Visual regression testing recommended.
