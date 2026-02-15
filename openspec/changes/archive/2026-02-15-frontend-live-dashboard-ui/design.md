## Context

The dashboard route (`/dashboard`) currently renders a placeholder. The frontend is an Aurelia 2 SPA using Tailwind CSS, with existing Connect-RPC service clients for concert and artist data. The backend already exposes `ConcertService` and `ArtistService` via Connect-RPC. This design adds the "Live Highway" dashboard UI that consumes these APIs and presents live events in a typography-focused, three-lane layout.

## Goals / Non-Goals

**Goals:**
- Implement the three-lane Live Highway layout as new Aurelia 2 components
- Generate deterministic colors from artist name strings for visual variety
- Provide a bottom sheet detail modal for event information
- Mobile-first, portrait-optimized, vertical-scroll layout
- Consume existing backend APIs (concert listing, artist data) with no backend changes

**Non-Goals:**
- Building a new backend API specifically for the dashboard (use existing services)
- User location/GPS-based proximity (use registered prefecture from user profile)
- Real-time event updates via WebSocket/SSE (standard request-response is sufficient for MVP)
- Desktop-optimized multi-column layouts (mobile-first only)
- Image/asset handling for artists (explicitly avoided by design)

## Decisions

### 1. Component Architecture

**Decision:** Create a `live-highway` component directory under `src/components/` containing the lane components, card components, and bottom sheet.

**Rationale:** Keeps the dashboard route thin (orchestration only) while encapsulating all highway UI in reusable components. Follows the existing pattern of `src/components/<feature>/` seen in `dna-orb` and `toast-notification`.

**Structure:**
```
src/components/live-highway/
  live-highway.ts / .html          # Main three-lane container
  highway-lane.ts / .html          # Generic lane component (receives lane config)
  event-card.ts / .html            # Typography card (adapts size by lane type)
  event-detail-sheet.ts / .html    # Bottom sheet modal
  color-generator.ts               # Deterministic artist name → HSL color utility
```

**Alternatives considered:**
- Inline everything in the dashboard route: rejected, too monolithic
- Separate components per lane type: rejected, the lanes differ only in sizing/density which can be driven by configuration props

### 2. Color Generation Algorithm

**Decision:** Use a simple string hash → HSL mapping. Hash the artist name to a hue (0-360), fix saturation at 65-75% and lightness at 40-50% for sufficient contrast with white text.

**Rationale:** Deterministic (same artist always gets same color), cheap to compute, no external dependencies. HSL gives predictable perceptual results. Fixed saturation/lightness ensures all generated colors are vibrant enough to serve as card backgrounds with readable white text.

**Implementation:**
```typescript
function artistColor(name: string): string {
  let hash = 0
  for (const char of name) hash = ((hash << 5) - hash + char.charCodeAt(0)) | 0
  const hue = ((hash % 360) + 360) % 360
  return `hsl(${hue}, 70%, 45%)`
}
```

**Alternatives considered:**
- MD5/SHA hash: overkill for a visual-only purpose
- Pre-assigned color palette: doesn't scale, requires server-side mapping

### 3. Layout Strategy

**Decision:** CSS Grid with `grid-template-columns: 50% 30% 20%` for the three lanes. Each lane scrolls as part of a single vertical scroll container.

**Rationale:** CSS Grid provides precise column sizing. A single scroll container (vs. independent lane scrolling) keeps the timeline aligned across lanes and enables the shared Y-axis date markers. Tailwind utility classes handle responsive breakpoints.

**Alternatives considered:**
- Flexbox: less precise for fixed-ratio columns
- Independent scroll per lane: breaks timeline alignment, confusing UX

### 4. Bottom Sheet Implementation

**Decision:** Custom CSS-based bottom sheet using `transform: translateY()` with CSS transitions. No external library.

**Rationale:** The interaction is simple (slide up/down), and adding a library for one modal is unnecessary. CSS transitions easily achieve 60fps on mobile. The sheet is triggered by a custom event from card click.

**Alternatives considered:**
- Dialog element: doesn't provide bottom-sheet slide animation natively
- Third-party modal library: adds dependency for minimal benefit

### 5. Data Fetching

**Decision:** Extend the existing `ConcertServiceClient` to add a `listConcerts` method that fetches upcoming concerts. Group/filter results client-side by user's registered prefecture for lane assignment.

**Rationale:** Reuses the existing Connect-RPC transport and service client pattern. Client-side grouping is acceptable for MVP scale (dozens to low hundreds of events). The user's prefecture comes from the existing `UserService`.

**Alternatives considered:**
- Server-side lane grouping: requires backend changes, out of scope
- Separate API per lane: over-engineered for MVP

### 6. Date/Time Markers

**Decision:** Sticky date headers rendered as separator rows within the single scroll container, spanning all three lanes.

**Rationale:** Sticky positioning keeps the current date visible during scroll. Full-width separators maintain timeline alignment across lanes. Events are sorted chronologically and grouped by date before rendering.

## Risks / Trade-offs

- **[Limited concert data at launch]** → The highway may look sparse initially. Mitigation: show a helpful empty state per lane ("No events yet in your city").
- **[Client-side filtering by prefecture]** → Won't scale beyond hundreds of events. Mitigation: acceptable for MVP; add server-side filtering if volume grows.
- **[Color collisions]** → Two different artists could generate similar colors. Mitigation: acceptable since names provide the primary distinction; colors are supplementary.
- **[No existing ListConcerts RPC]** → The concert service may not yet expose a list endpoint suitable for the dashboard. Mitigation: check available RPCs; if missing, the dashboard can use mock/stub data for initial UI development.
