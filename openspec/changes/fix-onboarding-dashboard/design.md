## Context

The onboarding tutorial guides new users through discovery → dashboard → my-artists. On the dashboard, a lane introduction sequence spotlights three stage headers (HOME/NEAR/AWAY STAGE) and then a concert card. This sequence is broken because:

1. Coach mark CSS selectors (`[data-stage-home]`) don't match the HTML attribute format (`data-stage="home"`).
2. The client-side `groupConcertsByDate()` puts all concerts into the `away` bucket because no proximity classification exists for unauthenticated users.
3. Retry timers in `findAndHighlight()` leak when a new phase starts before the previous retry completes.

The existing `ListByFollower` RPC resolves proximity server-side but requires authentication. Onboarding users are unauthenticated.

## Goals / Non-Goals

**Goals:**
- Fix the onboarding dashboard so stage spotlights appear and concerts are correctly classified by proximity.
- Add a public RPC that provides proximity-grouped concerts for unauthenticated users who have a Home selection and a list of followed artists.
- Eliminate the N+1 RPC call pattern in onboarding (currently one `List` per followed artist).

**Non-Goals:**
- Changing the existing `List` or `ListByFollower` RPCs.
- Modifying the proximity model (thresholds, classification logic).
- Refactoring the coach mark component beyond the timer leak fix.

## Decisions

### D1: New `ListWithProximity` RPC (not extending `List` or `ListByFollower`)

Add a new RPC rather than modifying existing ones.

- `List` is a simple single-artist query; adding proximity would change its contract.
- `ListByFollower` requires authentication and resolves artists+Home from user context; adding optional guest parameters would blur its responsibility.
- `ListWithProximity` accepts explicit `repeated ArtistId` + `Home` and returns `repeated ProximityGroup`. Same response shape as `ListByFollower`.

**Alternative considered**: Extend `ListByFollower` with optional `guest_artist_ids` and `guest_home` fields. Rejected because it mixes authenticated and unauthenticated concerns in one RPC.

### D2: Repository method `ListByArtists` (plural) with coordinates

The new use case needs concerts for multiple artists with venue coordinates (for Haversine calculation). The existing `ListByArtist` (singular) fetches one artist and does not include coordinates.

New repository method: `ListByArtists(ctx, artistIDs []string) ([]*entity.Concert, error)` with SQL `WHERE c.artist_id = ANY($1)` and `v.latitude, v.longitude` in the SELECT.

### D3: Centroid resolution in the handler, not the client

The `ListWithProximity` request accepts `entity.v1.Home` (which includes `country_code` and `level_1`). The backend resolves the centroid from `level_1` using the existing `geo.ResolveCentroid()` function, then constructs `entity.Home` for `GroupByDateAndProximity()`.

The client sends only the `Home` message (country_code + level_1) it already has from the onboarding home selection step. No new client-side logic needed for centroid resolution.

### D4: Fix CSS selectors directly (no HTML changes)

The HTML template uses `data-stage="home"` (attribute with value). The TypeScript `laneIntroSelector` getter uses `[data-stage-home]` (attribute name check). Fix the getter to `[data-stage="home"]`, `[data-stage="near"]`, `[data-stage="away"]`.

**Alternative considered**: Change HTML to `data-stage-home` (boolean attributes). Rejected because `data-stage="home"` is the more standard pattern and is already in use.

### D5: Cancel retry timer at the start of `findAndHighlight()`

Call `cleanup()` at the beginning of `findAndHighlight()` to cancel any pending retry timer before starting a new retry chain. This prevents timer leaks when `targetSelectorChanged` fires while a previous retry is still running.

## Risks / Trade-offs

- **[Risk] `ListWithProximity` is public (no auth)**: An unauthenticated caller can query concerts for arbitrary artist IDs. → Mitigation: This is the same data already available via the public `List` RPC; the only addition is proximity grouping, which is not sensitive. Rate limiting applies at the gateway level.

- **[Risk] Centroid resolution may fail for unsupported country codes**: → Mitigation: `geo.ResolveCentroid()` returns nil for unknown codes. `GroupByDateAndProximity` treats nil Home centroid as AWAY — same fallback as today.

- **[Risk] Large artist list in a single RPC call**: → Mitigation: Onboarding limits follows to a small number (typically 3-10 artists). Add protovalidate constraint `repeated ... [(buf.validate.field).repeated.max_items = 50]`.
