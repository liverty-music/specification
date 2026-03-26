## Context

The dashboard route currently owns all rendering logic for the 3-column concert lane grid: stage headers, date separators, event cards, and laser beam effects. This prevents reuse on the Welcome page, which needs the identical UI in readonly mode with preview data.

`dashboard-service.ts` aggregates three unrelated concerns (follows, concerts, journeys) into a single orchestrator. The `protoGroupToDateGroup()` conversion is private, blocking Welcome from using the same `ProximityGroup → DateGroup` pipeline.

The Welcome page currently has a broken inline implementation that hard-codes all concerts into the `away` lane and lacks the grid CSS entirely.

## Goals / Non-Goals

**Goals:**
- Extract a `<concert-highway>` CE that both `dashboard-route` and `welcome-route` consume
- Decompose `dashboard-service` by moving methods to their domain services
- Rewrite `welcome-route` to use `ListWithProximity` RPC with tokyo-fixed home, rendering via `<concert-highway readonly>`
- Apply Sticky CTA + Peek Preview layout to the Welcome page

**Non-Goals:**
- Changing the backend `ListWithProximity` RPC or proximity calculation
- Modifying event-card internals (already a standalone CE)
- Adding new onboarding flows or changing the lane intro state machine
- Staging/prod preview artist configuration (handled by existing `.env` mechanism)

## Decisions

### Decision: `<concert-highway>` CE location — `components/live-highway/`

Place the new CE alongside `event-card` in the existing `live-highway` directory, since it composes event-cards into a highway grid.

**Alternatives considered:**
- Separate `components/concert-highway/` directory: Rejected — the highway and event-card are tightly coupled, and co-location simplifies imports.
- Keep in `routes/dashboard/`: Rejected — defeats the purpose of extraction.

### Decision: Bindable API for `<concert-highway>`

```typescript
@bindable dateGroups: DateGroup[] = []
@bindable readonly: boolean = false
@bindable showBeams: boolean = true
```

Data loading stays in the consuming route. The CE is a pure presentation component that receives fully-formed `DateGroup[]`. This keeps the CE framework-agnostic regarding data source (dashboard service, preview RPC, mock data, etc.).

**Alternatives considered:**
- CE loads its own data via injected service: Rejected — tightly couples CE to a specific data source, breaks reuse for different contexts.

### Decision: Decompose `dashboard-service` into domain services

| Method | Current Location | New Location |
|---|---|---|
| `protoGroupToDateGroup()` | `dashboard-service` (private) | `concert-service.toDateGroups()` (public) |
| `fetchFollowedArtistMap()` | `dashboard-service` (private) | `follow-service.getFollowedArtistMap()` (public) |
| `fetchJourneyMap()` | `dashboard-service` (private) | `journey-service.getJourneyMap()` (public) |
| `loadDashboardEvents()` | `dashboard-service` (public) | `dashboard-route.loadData()` (inline orchestration) |

After migration, `dashboard-service.ts` is deleted.

**Alternatives considered:**
- Keep `dashboard-service` and just export `protoGroupToDateGroup`: Rejected — the service is an unnecessary orchestration layer; each method belongs to its domain.

### Decision: Welcome preview data flow via `listWithProximity`

```
welcome-route.ts
  attached()
  └── loadPreviewData()
      ├── concertService.listWithProximity(
      │     PREVIEW_ARTIST_IDS,
      │     'JP',       // countryCode
      │     'JP-13'     // level1 (Tokyo)
      │   )
      └── concertService.toDateGroups(proximityGroups, artistMap)
          → this.dateGroups = result
```

This reuses the existing guest flow in `concert-service` and the same `ProximityGroup → DateGroup` conversion that the dashboard uses. No new RPC calls or mappers needed.

### Decision: Peek Preview layout for Welcome

The preview section uses a fixed-height scrollable container (`~55svh`) with a bottom fade-out mask. CTA buttons are positioned below the preview with sticky behavior so they remain visible while the user scrolls the preview.

```
┌─ viewport ──────────────┐
│  Hero copy              │
│  ┌─ preview (55svh) ──┐ │
│  │ <concert-highway    │ │
│  │   readonly>         │ │
│  │   (internal scroll) │ │
│  └─ fade mask ─────────┘ │
│  Guest-friendly copy     │
│  [Get Started] sticky    │
│  [Log In]                │
└──────────────────────────┘
```

## Risks / Trade-offs

- **CSS extraction complexity**: Moving grid/beam CSS from `dashboard-route.css` to the CE requires careful `@scope` boundary management. The CE must not leak styles to parent, and parent must not override CE internals.
  → Mitigation: Use Aurelia 2 shadow DOM-like `@scope` isolation (already the project pattern).

- **Beam tracking scroll context change**: In `dashboard-route`, the scroll container is the route itself. In `welcome-route`, the scroll container is the `.welcome-preview` wrapper (not the full page).
  → Mitigation: The CE accepts a scroll container reference or uses its own root element for intersection/scroll observation.

- **`dashboard-route` regression**: Refactoring a working route carries risk of breaking the authenticated dashboard.
  → Mitigation: Ensure existing E2E tests pass. The template change is mechanical (replace inline HTML with CE tag).

## Open Questions

- Should the laser beams animate on Welcome page load, or start static and animate on first scroll interaction? (UX preference — can be decided during implementation.)
