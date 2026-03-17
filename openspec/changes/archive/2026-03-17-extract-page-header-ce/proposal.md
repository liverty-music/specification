## Why

The `.page-header` pattern (HTML structure + CSS) is duplicated across 3 route pages (my-artists, settings, tickets) with identical base styles (~17 lines of CSS each). Extracting it into a shared Custom Element improves maintainability and ensures visual consistency when the header design evolves.

## What Changes

- Create a `page-header` Custom Element (CE) that encapsulates the shared header layout, typography, and border styling.
- The CE accepts a `title-key` bindable (i18n translation key) and an `<au-slot>` for optional trailing actions (e.g., count badge, view-toggle button).
- Replace inline `<header class="[ page-header ]">` markup in my-artists, settings, and tickets routes with `<page-header>`.
- Remove duplicated `.page-header` CSS blocks from each route's stylesheet.
- Register the CE globally in `main.ts` (same pattern as `StatePlaceholder`, `SvgIcon`).

## Capabilities

### New Capabilities

- `page-header-ce`: Shared page-header Custom Element with i18n title and slot-based action area.

### Modified Capabilities

_(none — this is a refactor with no requirement-level changes to existing capabilities)_

## Impact

- **frontend/src/components/page-header/**: New CE (`.ts`, `.html`, `.css`)
- **frontend/src/main.ts**: Add `PageHeader` global registration
- **frontend/src/routes/my-artists/**: Replace header markup, remove `.page-header` CSS
- **frontend/src/routes/settings/**: Replace header markup, remove `.page-header` CSS
- **frontend/src/routes/tickets/**: Replace header markup, remove `.page-header` CSS
