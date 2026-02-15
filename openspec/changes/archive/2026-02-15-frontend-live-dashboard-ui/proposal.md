## Why

The current dashboard route (`/dashboard`) lacks a dedicated live events view. Users need a way to discover upcoming concerts organized by geographic proximity, with a design that avoids artist images entirely to eliminate copyright concerns and reduce operational costs. A typography-focused "Live Highway" layout provides visual variety through deterministic color generation while keeping the UI lightweight for mobile PWA usage.

## What Changes

- Add a new three-lane "Live Highway" dashboard layout displaying live events organized by geographic proximity (My City / My Region / Others)
- Implement deterministic color generation from artist name strings for card backgrounds
- Add mega-typography event cards for the primary lane, compressed cards for secondary lanes, and text-only list items for the tertiary lane
- Implement a bottom sheet detail modal with event info, Google Maps link, and calendar export
- Add date/time markers along the Y-axis timeline for temporal context
- Optimize the layout for mobile-first portrait orientation with one-handed scrolling

## Capabilities

### New Capabilities
- `typography-focused-dashboard`: Three-lane live event dashboard with typography-first card design, deterministic color generation, bottom sheet details, and mobile-optimized layout

### Modified Capabilities

_(none)_

## Impact

- **Frontend**: New Aurelia 2 components under `src/components/` and a new route or sub-route under `src/routes/`
- **Backend**: Requires live event data API (concert search or live-events service) - consumed via existing Connect-RPC client
- **Dependencies**: No new external dependencies expected; CSS Grid/Flexbox for layout, native Web Animations API or CSS transitions for bottom sheet
- **Existing routes**: Dashboard route may need updated navigation to include the live highway view
