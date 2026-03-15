# Extract Shared Components

## Problem

Several UI patterns are duplicated across multiple pages with minor variations, violating DRY and making updates error-prone:

1. **SVG icons**: Inline SVG definitions repeated in bottom-nav-bar (5 icons via switch/case), toast-notification (3 severity icons), tickets-page, discover-page. Adding or changing an icon requires editing multiple files.

2. **Empty/error state placeholders**: The `.state-center` + icon + title + description + optional CTA pattern appears in tickets-page, my-artists-page, dashboard, and discover-page. Each implementation is slightly different, making it hard to maintain consistency.

3. **Page shell structure**: Every route page follows the same `.page-layout` > `.page-header` > content pattern with near-identical CSS. The header structure (title + optional actions) is duplicated 5+ times.

## Proposed Solution

### Component 1: `<svg-icon>`
- Custom element that renders named SVG icons
- Single source of truth for all icon definitions
- Props: `name`, `size` (sm/md/lg)
- Eliminates switch/case blocks and inline SVG duplication

### Component 2: `<state-placeholder>`
- Reusable empty/error/loading state display
- Props: `icon` (svg-icon name), `title`, `description`, `cta-label`, `cta-action`
- Slots for custom content
- Replaces 4+ duplicated implementations

### Component 3: `<page-shell>`
- Route page wrapper providing `<main>` landmark, header, and content area
- Props: `title` (i18n key), `show-header`
- Slots: `header-actions`, default (content)
- Standardizes page structure and eliminates boilerplate

## Scope

- **In scope**: New component creation, refactoring existing pages to use them, tests for new components
- **Out of scope**: New features or visual changes
- **Depends on**: `semantic-html-landmarks` and `flatten-dom-structure` (should be applied first)

## Affected Files

New files:
- `src/components/svg-icon/svg-icon.ts` + `.html` + `.css`
- `src/components/state-placeholder/state-placeholder.ts` + `.html` + `.css`
- `src/components/page-shell/page-shell.ts` + `.html` + `.css`
- Tests for each new component

Refactored files:
- bottom-nav-bar (.html) — replace inline SVGs with `<svg-icon>`
- toast-notification (.html) — replace severity SVGs with `<svg-icon>`
- tickets-page (.html) — use `<state-placeholder>` and `<page-shell>`
- my-artists-page (.html) — use `<state-placeholder>` and `<page-shell>`
- dashboard (.html) — use `<state-placeholder>` and `<page-shell>`
- discover-page (.html) — use `<state-placeholder>` and `<page-shell>`
- settings-page (.html) — use `<page-shell>`

## Risk

High. Creating new components affects the dependency graph. Existing tests that query specific DOM structures will need updating. Incremental rollout recommended: extract one component at a time, verify, then proceed.
