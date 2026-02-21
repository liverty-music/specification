## Context

The dashboard (live-highway) fetches concerts via `ConcertService.List` and displays them in a three-lane layout (My City / My Region / Others). Currently:

- `Concert` proto carries only `venue_id` — no venue name or admin area reaches the frontend
- Frontend hardcodes `venueName: 'Venue TBD'` and `locationLabel: ''`
- All events are placed in the `main` lane; `region` and `other` lanes are always empty
- Tapping a concert card opens `EventDetailSheet` (bottom sheet) with no URL change — the detail is not shareable or directly linkable
- Go `entity.Event` has `LocalEventDate` but proto uses inconsistent raw types (`google.type.Date`, `google.type.TimeOfDay`, plain `string`) instead of VO wrapper messages

The Go entity layer is the source of truth. The proto layer needs to catch up.

## Goals / Non-Goals

**Goals:**
- Surface venue name (`listed_venue_name`) and admin area (`venue.admin_area`) in the `Concert` proto
- VO-ify all raw-typed fields in `Concert` and `Event` proto to match Go entity conventions
- Rename `LocalEventDate` → `LocalDate` in Go `entity.Event` and propagate
- JOIN venues in `ListByArtist` SQL so each concert carries a resolved `Venue`
- Enable dashboard lane assignment using `venue.admin_area` vs user's localStorage region
- Add Concert Detail UI: hybrid bottom-sheet with URL sync at `/concerts/:id`

**Non-Goals:**
- `GetConcert` RPC — not needed; dashboard pre-fetches all concerts via `List`
- Share action / Web Share API — deferred to post-MVP
- Storing user region in DB (`users.admin_area`) — separate issue
- Unifying `Event.start_at` Timestamp type with Concert's TimeOfDay — separate refactor

## Decisions

### 1. VO wrapper messages for all primitive fields

**Decision:** Introduce shared VO messages (`LocalDate`, `StartTime`, `OpenTime`, `Title`, `SourceUrl`, `ListedVenueName`) in the proto entity layer, replacing raw `google.type.*` and `string` fields.

**Rationale:** Go entity already uses named types with clear semantics. Proto should mirror this. VO wrappers enable per-field validation via protovalidate and make the schema self-documenting. Consistent with existing pattern (`ArtistId`, `VenueName`, `ConcertTitle`, etc.).

**Alternatives considered:**
- Keep raw types, add only new fields → leaves existing inconsistency, tech debt grows
- Use `google.type.TimeOfDay` for `StartTime`/`OpenTime` → contradicts Go entity which uses `*time.Time` (full timestamp); mapper already converts `time.Time → TimeOfDay` as a lossy transform

### 2. Embed `Venue` in `Concert` (not a sidecar map in `ListResponse`)

**Decision:** Add `Venue venue = 9` directly on the `Concert` message, server-populated on every `List` call.

**Rationale:** Venue data is always needed when displaying a concert (name, Maps link, lane assignment). Embedding follows the AIP principle: always-needed related resources should be inlined. The `venue_id` field is retained for backward compatibility.

**Alternatives considered:**
- `map<string, Venue> venues` in `ListResponse` → gRPC/Connect anti-pattern; client must join; not idiomatic
- Separate `GetVenue` call from frontend → N+1 problem; unnecessary round-trips

### 3. Embed `Venue` in `Event` (replace `venue_id`)

**Decision:** Replace `VenueId venue_id` with `Venue venue` in `Event` proto, consistent with `Concert`.

**Rationale:** `Event` (ticket/ZK domain) needs the same venue information. Inconsistency between `Concert` (embedded `Venue`) and `Event` (only `venue_id`) would create cognitive overhead. Go entity has `VenueID string` on `Event` — the proto should embed the full object since that's always resolved server-side.

### 4. Remove `create_time` / `update_time` from `Event`

**Decision:** Delete these fields from the `Event` proto.

**Rationale:** Go `entity.Event` does not have these fields. They were in the proto but unused by any handler or mapper. Removing them aligns proto with the domain model and reduces noise.

### 5. Hybrid Concert Detail: bottom-sheet + URL sync

**Decision:** Retain the existing `EventDetailSheet` bottom-sheet UX, but sync the URL to `/concerts/:id` when the sheet opens and restore it on close.

**Rationale:** Preserves the native app-like feel (slide-up animation, swipe-to-dismiss) while enabling linkability for future share features. A full-page navigation would break the dashboard scroll state. Aurelia Router supports programmatic URL updates without full navigation.

**Alternatives considered:**
- Full page navigation to `/concerts/:id` → loses scroll position, feels less native
- No URL change → sheet is not linkable; share feature (future) would have no URL to share

### 6. `LocalEventDate` → `LocalDate` rename in Go entity

**Decision:** Rename `entity.Event.LocalEventDate` to `entity.LocalDate` and update all call sites.

**Rationale:** Aligns Go entity field name with the new proto VO name `LocalDate`. Reduces the mapping mental model: same concept, same name across layers.

## Risks / Trade-offs

- **BSR breaking change** → `concert.proto` and `event.proto` field renames/type changes require a semver major bump on the BSR schema. All generated clients (Go backend, TypeScript frontend) must be regenerated. → Mitigation: coordinate proto change and client regeneration in a single PR.
- **SQL JOIN on every List call** → `ListByArtist` now JOINs `venues`. For users following many artists this is N JOINs (one per artist). → Mitigation: the existing query already JOINs `events`; adding `venues` is one more indexed JOIN on `venue_id` (UUID PK). Acceptable at current scale.
- **`TimeToTimeOfDayProto` becomes dead code** → mapper function that converts `*time.Time → TimeOfDay` will be unused after VO type change. → Remove it as part of the mapper update.

## Migration Plan

1. Update proto files (`concert.proto`, `event.proto`) with new VO messages and field changes
2. Bump BSR schema version (breaking change)
3. Regenerate Go and TypeScript clients from BSR
4. Update Go backend: rename `LocalEventDate` in `entity.Event`, update SQL query, update mapper
5. Update frontend: map new proto fields in `dashboard-service.ts`, implement lane assignment, add URL sync to `EventDetailSheet`
6. Deploy backend before frontend (frontend is backward-compatible with old proto during rollout window)
