## Why

The frontend has accumulated significant CSS duplication and structural repetition across dialog, prompt, and state-display components. Five separate dialog implementations share nearly identical backdrop/handle-bar/slide-in CSS (~200 lines duplicated). Two prompt components have 99% identical CSS (~90 lines). Spinner and empty-state patterns are independently re-implemented in multiple route CSS files. Extracting shared Custom Elements eliminates this duplication, creates Storybook-testable primitives, and simplifies the DOM structure across the app.

## What Changes

- **New `<bottom-sheet>` CE**: Unifies all dialog/modal/sheet implementations (event-detail-sheet, user-home-selector, language-selector in settings, hype-notification-dialog, error-banner, tickets center-dialogs) into a single CE using the popover API + scroll-snap dismiss pattern from event-detail-sheet.
- **New `<toast>` CE**: Merges notification-prompt and pwa-install-prompt into a single popover="manual" top-banner CE. Replaces both existing components.
- **Rename `toast-notification` to `<snack-bar>`**: The existing auto-dismissing notification component gets a name that accurately reflects its role (snackbar pattern), freeing the "toast" name for the prompt banner CE.
- **New `<loading-spinner>` CE**: Extracts the repeated spinner block pattern (currently duplicated in tickets-route, my-artists-route, auth-callback-route) into a standalone CE with size variants. Enables independent Storybook testing.
- **Simplify `<state-placeholder>`**: Remove unused `ctaLabel` bindable and `title`/`description` bindables. Keep only `@bindable icon` and use `<au-slot>` for all content. Loading states use slotted `<loading-spinner>` instead of custom inline markup.
- **Delete redundant CSS**: ~350+ lines of duplicated CSS removed from component and route files after consolidation.

## Capabilities

### New Capabilities

- `bottom-sheet-ce`: Shared bottom-sheet Custom Element providing popover-based slide-up dialog with scroll-snap dismiss, backdrop opacity fade, and handle-bar.
- `toast-ce`: Shared toast Custom Element providing popover="manual" top-banner for user-action prompts (notification permission, PWA install).
- `loading-spinner-ce`: Shared loading-spinner Custom Element providing animated spinner with size variants (sm, md, lg).

### Modified Capabilities

- `design-system`: Addition of three new shared CEs to the component library; rename of toast-notification to snack-bar.
- `semantic-dom`: Simplified DOM structure across dialog/prompt/state components by removing redundant wrapper elements.

## Impact

- **Frontend components** (6 deleted/merged, 3 new, 1 renamed, 1 simplified):
  - Deleted: standalone dialog CSS in event-detail-sheet, user-home-selector, hype-notification-dialog, error-banner, notification-prompt, pwa-install-prompt
  - New: `components/bottom-sheet/`, `components/toast/`, `components/loading-spinner/`
  - Renamed: `components/toast-notification/` → `components/snack-bar/`
  - Simplified: `components/state-placeholder/`
- **Frontend routes** (CSS reduction):
  - settings-route.css: ~140 lines removed (language-selector sheet CSS)
  - tickets-route.css: ~35 lines removed (spinner + center-dialog CSS)
  - my-artists-route.css: ~18 lines removed (spinner + state-center CSS)
- **Import references**: All files importing renamed/deleted components need import path updates.
- **Storybook**: New stories needed for bottom-sheet, toast, loading-spinner CEs.
- **No backend or API changes**.
