## Why

The onboarding guide flow has 4 interconnected bugs that create a progression-blocking experience on the Dashboard page. Two root causes are responsible: (1) the Popover API's top-layer rendering breaks CSS color inheritance, making help text unreadable; (2) `document.querySelector('[data-stage="home"]')` matches an invisible element inside `page-help` instead of the intended `concert-highway` stage header, causing the spotlight to anchor to a 0×0 ghost element — which breaks click blockers, mispositions tooltips, and ultimately prevents the celebration overlay from appearing.

## What Changes

- Fix top-layer color inheritance: popover/dialog elements currently inherit `color: black` from `<html>` instead of `color: white` from `<body>`, making all bottom-sheet text invisible on dark backgrounds.
- Eliminate `data-stage` attribute collision between `page-help` (decorative color labels) and `concert-highway` (structural lane headers) so the coach-mark targets the correct element.
- Redesign the lane intro spotlight activation to use Aurelia 2's `@watch` + `queueTask` instead of premature `activateSpotlight()` calls that fire before data loads and DOM renders.
- Scope coach-mark target selectors to `concert-highway` to prevent cross-component selector collisions.

## Capabilities

### New Capabilities

_(none — all changes are fixes to existing capabilities)_

### Modified Capabilities

- `onboarding-spotlight`: Coach-mark target resolution must be scoped to the correct component context; `findAndHighlight` must skip invisible (0×0) elements.
- `dashboard-lane-introduction`: Spotlight activation must wait for data load + DOM render instead of firing in `attached()`; the `needsRegion` flow must not activate the spotlight until stage headers exist in the DOM.
- `onboarding-page-help`: Decorative stage-color labels must not use the same `data-stage` attribute as `concert-highway` headers to avoid selector collisions.

## Impact

- **frontend**: `global.css`, `bottom-sheet.css`, `page-help.html`, `page-help.css`, `coach-mark.ts`, `dashboard-route.ts`
- No backend, proto, or infrastructure changes.
- No breaking API changes.
