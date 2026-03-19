## Context

The proto schema has two wrapper types for the same underlying UUID:

- `ConcertId` in `concert.proto` — used only by the `Concert` message
- `EventId` in `ticket.proto` — used by `Ticket`, `Entry`, and `TicketJourney`

Both resolve to `events.id` in the database. The Go domain model already treats them as one concept: `Concert` embeds `Event`, sharing a single `ID` field.

Additionally, `EventId` is currently defined in `ticket.proto`, which is semantically incorrect — an event identifier is a top-level domain concept, not a ticket sub-concept. The `Event` message in `event.proto` already references `EventId` via an import from `ticket.proto`.

## Goals / Non-Goals

**Goals:**

- Eliminate `ConcertId` message and unify on `EventId` as the single event identifier type
- Relocate `EventId` to `event.proto` where it semantically belongs
- Maintain wire compatibility where possible (same field numbers, same UUID format)

**Non-Goals:**

- Renaming the `Concert` message or `ConcertService` RPC — the "concert" concept remains valid as a domain-specific view of an event
- Changing database schema — `events.id` and `concerts.event_id` are already correct
- Modifying the Go `entity.Concert` / `entity.Event` structs — they already use a single `ID` field

## Decisions

### 1. Move EventId to event.proto

**Decision**: Relocate the `EventId` message from `ticket.proto` to `event.proto`.

**Why**: `EventId` is a core entity identifier. It belongs alongside the `Event` message, not nested inside ticket definitions. `ticket.proto` will import it from `event.proto`.

**Alternative considered**: Create a new `ids.proto` for all ID types. Rejected — the project convention is to co-locate ID types with their parent entity (e.g., `ArtistId` in `artist.proto`, `VenueId` in `venue.proto`).

### 2. Replace ConcertId with EventId in Concert message

**Decision**: Change `Concert.id` from `ConcertId id = 1` to `EventId id = 1`.

**Why**: The field number stays the same (1), and both types wrap `string value = 1` with UUID validation. The wire format is identical — only the generated type name changes. This aligns the proto schema with the Go entity and database where the ID has always been an event ID.

**Alternative considered**: Keep `ConcertId` as a type alias (documentation-only). Rejected — it preserves the naming confusion and adds maintenance burden.

### 3. Delete ConcertId message entirely

**Decision**: Remove the `ConcertId` message from `concert.proto` rather than deprecating it.

**Why**: `ConcertId` is only used in `concert.proto` line 15. No other proto file references it. Clean removal is simpler than maintaining a deprecated type. The `buf skip breaking` label will be applied to the PR.

### 4. Update concert.proto imports

**Decision**: Add `import "liverty_music/entity/v1/event.proto"` to `concert.proto` (if not already present) to access `EventId`.

## Risks / Trade-offs

- **[Breaking change for generated clients]** → Mitigated by the fact that `ConcertId` has zero usage outside `concert.proto`. Backend mapper changes are mechanical (`ConcertId` → `EventId`). Frontend changes are similarly straightforward. All repos will be updated in coordinated PRs after BSR regeneration.

- **[ticket.proto breaking change from removing EventId]** → `EventId` is moved, not deleted. `ticket.proto` will import it from `event.proto`. Existing fields (`Ticket.event_id`) keep the same type and field number. Wire-compatible.

- **[buf breaking check will flag removed message]** → Apply `buf skip breaking` label to the specification PR. The change is intentional and coordinated.
