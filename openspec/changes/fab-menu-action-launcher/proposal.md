## Why

On the fan-web dashboard, three unrelated controls — filter, laser-beam toggle,
and help — plus a mode-swap button sit in the top-right corner of the header:
the hardest place to reach one-handed on a phone (a diagonal "dead zone") and a
source of visual clutter. We want to consolidate these into a single ergonomic,
thumb-reachable launcher in the bottom-right "primary zone", following the
Material 3 Expressive **FAB Menu** pattern (labeled action list, spring motion,
shape morph), so the controls are easy to reach and learn while keeping the live
music content immersive.

## What Changes

- **NEW**: A global, app-shell-resident **FAB action launcher** floating in the
  bottom-right thumb zone. Single tap expands a vertical list of
  **icon + text label** actions (labels mandatory; no icon-only items). Built on
  the Popover API (top layer), with an M3 shape-morph (round FAB ↔ rounded-rect
  panel, `+`↔`×`) and physics-based spring motion, honoring
  `prefers-reduced-motion`.
- **NEW**: A **contextual action registry** service. Route components register
  their actions on activation and dispose them on deactivation, so the launcher's
  contents adapt per page (dashboard shows the most; other pages show only what
  applies). The FAB hides itself when a page contributes zero actions.
- **NEW**: A persisted **left-handed mode** that mirrors the FAB and its panel to
  the bottom-left (settings toggle, stored like the beam preference).
- **BREAKING** — The dashboard **page header trailing cluster is emptied**: the
  filter trigger, beam toggle, help trigger, and mode-swap button are all removed
  from the header. The header becomes title-only.
- **BREAKING** — `page-help` **loses its own `?` trigger button**; the launcher
  invokes the existing per-page help sheet instead (help content stays
  page-contextual).
- **BREAKING** — `artist-filter-bar` **loses its own trigger button**; the
  launcher opens its existing bottom sheet. The filter sheet and its bindings
  stay owned by the dashboard route.
- **BREAKING** — The beam toggle moves from a header button to an **inline toggle
  item inside the FAB panel** (immediate on/off, no sheet).
- The FAB is offset above the bottom navigation bar (nav publishes its height) so
  the two never collide.

## Capabilities

### New Capabilities
- `fab-action-launcher`: A global, thumb-zone floating action button that expands
  a labeled, contextual action list in the top layer, with M3 shape-morph + spring
  motion, disclosure-pattern accessibility, per-route contextual action
  registration, FAB-panel toggle items, and a persisted left-handed placement mode.

### Modified Capabilities
- `beam-effect-toggle`: The beam on/off control is presented as a toggle item in
  the FAB panel instead of a header button; toggle behavior and persistence are
  unchanged.
- `dashboard-artist-filter`: The filter is opened from the FAB launcher instead of
  a dedicated header trigger; the filter sheet and selection behavior are
  unchanged.
- `onboarding-page-help`: The help sheet is opened from the FAB launcher instead
  of a `?` trigger button; auto-open-on-first-visit behavior and per-page content
  are unchanged.
- `app-shell-layout`: The shell hosts the global FAB launcher alongside the bottom
  nav and exposes the nav height so the FAB can offset above it; FAB visibility
  follows the same authenticated/nav-visible gating.

## Impact

- **Frontend (fan-web) only** — no proto, backend, or RPC changes.
- New: `components/fab-menu/`, `services/fab-menu-service.ts`,
  `adapter/storage/` entry for the handedness preference, M3 token additions in
  `styles/tokens.css`.
- Modified: `app-shell.html`/`.css`, `page-header` (+ `.css`),
  `dashboard-route.ts`/`.html`, `page-help` (`.ts`/`.html`),
  `artist-filter-bar` (`.ts`/`.html`), `bottom-nav-bar.css`, `settings-route`.
- Accessibility: disclosure pattern (`aria-expanded` + `aria-controls`), not an
  ARIA `menu`; focus moves into the panel on open and returns to the FAB on close.
- Verification must include real-browser/device checks of thumb reach, the
  bottom-nav offset, reduced-motion, and left-handed mirroring.
