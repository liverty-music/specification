## Context

See proposal.md for the motivation. The current state that shapes the approach (origin/main on 2026-10-10):

- **Proto.**
  - `entity.v1.Concert` (concert.proto) has `id`, `venue_id`, `local_date`, `start_time`, `open_time`, `venue`, `listed_venue_name`, `series` and `performers`.
  - `entity.v1.Event` (event.proto) has `id`, `venue`, `local_date`, `start_time`, `open_time` and `series_id`. It has no `listed_venue_name`.
  - The organizer `ConcertService` returns `AuthoredConcert { series, events: [Event], performers }`.
  - The admin `ConcertService.List` returns `entity.v1.Concert`.
- **Backend.**
  - The Go entity `Concert` already embeds `Event` and adds `Series` and `Performers` (`internal/entity/concert.go`).
  - The Concert reads (`concert_repo.go`) join the Series columns, including the first-party ones since `public-event-page`, but not the cover image. `Get` and `ListBySeries` replace the Series with `Series.Get` to add it.
  - `Concert.Create` learns which Events are new from `INSERT INTO concerts ... RETURNING event_id` (`concert_repo.go:784`), plus the `event_performers` insert for newly linked Artists. Both stay.
- **DB.**
  - `concerts (event_id PK → events)` is an otherwise empty extension table.
  - `event_performers (event_id → events, artist_id → artists)` links Artists to the generic Event.
  - `organizer-console-api` holds `INSERT` on `concerts` (migration `20261008020000:109`). `migration_grants_integration_test.go:70` pins it.
- **Fan RPC `SearchNewConcerts`.**
  - It has no caller in any repository.
  - It is listed in `auth.FanPublicProcedures()` (`public_procedures.go:19-24`).
  - The 120-second `SERVER_CONCERT_HANDLER_TIMEOUT` (`provider.go:620`) exists for it.
- **Frontend.**
  - The fan app reads Concerts in `src/services/concert-store.ts` (dashboard and welcome), `src/routes/event/event-page.ts` (event page) and `src/routes/tickets/tickets-route.ts`.
  - The admin app reads them in `admin/approved-concerts`, and the organizer console reads `AuthoredConcert`.
  - Nothing persists a Concert proto. The tickets page's IndexedDB snapshot holds the derived `EventPageEvent`.
- **Spec moves.** Per the spec-tree rules, moving a main spec is a direct commit on the main specs with a mapping table, not part of a change.

## Goals / Non-Goals

**Goals:**
- One wire rule for every response that carries Concerts, on all three audiences.
- An Event message free of music data, so a later kind of event extends it the way Concert does.

**Non-Goals:**
- Renaming the discovery pipeline, NATS subjects, the `concert-discovery` job, metrics, analytics events, notification types or the `/concerts/:id` URL (proposal: naming rule).
- The organizer console route names (`concerts`, `concert-editor`). `redesign-organizer-console` aligns them.
- `draft_series_performers`. `restructure-event-publishing` removes the draft tables.
- Fixing the sales notification link `/concerts/<id>`, which cannot reach an event that is not in the fan's dashboard list. This is tracked as a separate issue (task 1.2).
- A fan club event type.

## Decisions

### D1 — `Concert { event, artist_ids }` composes the generic Event

```proto
message Event {            // entity/v1/event.proto
  EventId id = 1;
  Venue venue = 2;
  LocalDate local_date = 4;
  StartTime start_time = 5;
  OpenTime open_time = 6;
  SeriesId series_id = 8;
  ListedVenueName listed_venue_name = 9;   // new
}

message Concert {          // entity/v1/concert.proto
  Event event = 13;                        // fields 1-12 reserved
  repeated ArtistId artist_ids = 14;       // min 1, unique
}
```

- **Composition over a `oneof` inside Event.** Each kind is its own message holding an Event, so a reader of `Concert` gets typed music data without inspecting a variant.
  - A mixed list (concerts and fan club events) would put a `oneof` around the kinds in the list response. That is decided when the second kind arrives.
  - Rejected: `Event { oneof details { ConcertDetails ... } }`. Every reader would branch on the variant, even where only concerts exist, which is every reader today.
- **Old field numbers.** The old Concert field numbers 1–12 are reserved, not reused, so a stale client fails loudly instead of misreading.
- **Go types.** `entity.Concert` already embeds `Event`; only its `Performers` field is renamed `Artists`.

### D2 — Responses carry each referenced Series and Artist once

```proto
// fan ConcertService
GetResponse            { Concert concert; repeated Series series; repeated Artist artists; }
ListResponse           { repeated Concert concerts; repeated Series series; repeated Artist artists; }
ListBySeriesResponse   { repeated Concert concerts; repeated Series series; repeated Artist artists; }
ListByFollowerResponse { repeated ProximityGroup groups; repeated Series series; repeated Artist artists; }
ListByArtistsResponse  { ... same ... }
ListByLocationResponse { ... same ... }
// admin ConcertService
ListResponse           { repeated Concert concerts; repeated Series series; repeated Artist artists; }
```

- **Where the lists sit.** The `series` and `artists` lists sit beside the groups, not inside `ProximityGroup`. A tour spans dates, and dates are the groups.
- **Built in the mapper, from the Go Concerts.**
  - The usecases and the entity reads keep returning Concerts with their Series and Artists.
  - The mapper (`internal/adapter/rpc/mapper/concert.go`) collects each distinct Series and Artist by id, in first-seen order.
  - No usecase or repository signature changes for this, which is why the usecase specs are unchanged.
- **New pattern.** There is no earlier response in this proto with such de-duplicated side lists. From this change on, every response that returns Concerts follows this rule.
- **Rejected: keep `series` embedded and drop only the description from lists.** That would give the Series two shapes depending on the call, and leave the repetition of the Artists.

### D3 — One Series shape on every read

- The Concert reads add the cover image with the same `LEFT JOIN series_media ... media` the Series reads use (`series_repo.go:50`).
- `ConcertUseCase.Get` and `ListBySeries` then stop replacing the Series with `Series.Get`. They still apply the event-page check to the Series they read.
- The fan `SeriesToProto` sets `media` whenever the Series has a cover. The share token stays out, as before (it has no proto field).
- **Cost.** One extra left join per Concert row, on a primary-key lookup. The lists are bounded by the follow set or the location window.

### D4 — The event page keeps `Get` then `ListBySeries`

- **Flow.** The page renders from `Get`, which now carries the Series and its cover. It then fills in the other dates from `ListBySeries`. This is the current flow, with the response shape of D2.
- **Cost.** The Series arrives twice per page, instead of once per date as today.
- **Rejected: a `SeriesService.Get(series_id) → { series, events }` for the page.**
  - It would need a second call before the title can render.
  - It would add a second response shape and mapper to the fan app.
  - It saves only one copy of the Series.
- **Rejected: `ConcertService.Get(event_id)` returning the whole Series with every date.** Every other `Get` in this proto returns only its own resource.

### D5 — The organizer `ConcertService` becomes `SeriesService`

- **Package.** `rpc/organizer/concert/v1` → `rpc/organizer/series/v1`. The service keeps the same eight RPCs: Create, Update, Publish, Cancel, CreateMediaUploadURL, AttachMedia, RegenerateToken and List.
- **Responses.** `AuthoredConcert` is removed. Create, Update, Publish, Cancel and AttachMedia return `{ series, concerts, artists }`, and List returns `{ repeated series, concerts, artists }`.
- **A DRAFT Series' dates are DraftEvents.** They are returned as Concerts whose `event.id` is the DraftEvent id. Their `artist_ids` are the Series' draft performers, which is what `AuthoredConcert` shows today. `restructure-event-publishing` later makes them real DRAFT Events.
- **Code.** The backend handler moves to `organizer_series_handler.go`, with its registration in `internal/di/provider.go`. `ConcertAuthoringUseCase` keeps its name; renaming the usecase is out of scope.
- **Organizer console.** The console groups `concerts` by `event.series_id` to rebuild one page per Series.

### D6 — `event_performers` becomes `concert_artists`, keyed by the Concert

The constraint names below are the expected defaults; task 2.1 records the actual ones from prod.

```sql
ALTER TABLE event_performers RENAME TO concert_artists;
ALTER TABLE concert_artists RENAME CONSTRAINT event_performers_pkey TO concert_artists_pkey;
ALTER TABLE concert_artists DROP CONSTRAINT event_performers_event_id_fkey;
ALTER TABLE concert_artists ADD CONSTRAINT concert_artists_event_id_fkey
  FOREIGN KEY (event_id) REFERENCES concerts(event_id) ON DELETE CASCADE;
ALTER TABLE concert_artists RENAME CONSTRAINT event_performers_artist_id_fkey TO concert_artists_artist_id_fkey;
```

- **Why a foreign key to `concerts`.** It makes "Artists attach only to a Concert" a database guarantee. A future fan club event gets its own link table, so one column never holds two kinds of key.
- **Precondition.**
  - Every `event_performers.event_id` has a `concerts` row; task 2.1 checks it in prod, read-only.
  - Both writers already insert into `concerts` first: `concert_repo.go:35` and `series_repo.go:1004`.
  - Deleting an Event still cascades: events → concerts → concert_artists.
- **Hand-written migration.**
  - `atlas migrate diff` emits DROP and CREATE for a rename, so the migration file is hand-edited to `RENAME` (as `20260310000000_rename_passion_level_to_hype.sql` did for a column), then hashed.
  - `schema.sql`, its comments (`lint-schema.sh`) and the integration test's table cleanup list follow.
- **Grants.** `organizer-console-api` writes `event_performers` through the publish path. `ALTER TABLE ... RENAME` keeps grants, which are bound to the table's OID. Task 2.4 updates the expected-grants map in `migration_grants_integration_test.go` and runs it.
- **Release order.** The migration and the code that writes `concert_artists` ship in one backend release. The Atlas Operator applies the migration before the new pods roll.
  - The old pods write `event_performers` until they stop. Postgres resolves a table name at query time, so those writes fail once the table is renamed.
  - The window is the rollout of `fan-api`, `admin-console-api`, `organizer-console-api`, `event-consumer` and the jobs. With no users, a failed discovery write is retried by the next run; this is accepted.

### D7 — Remove the fan `SearchNewConcerts` RPC and the 120-second limit

- **Proto.** Delete the RPC and its messages from `rpc/concert/v1`.
- **Backend.**
  - Delete the handler method and its entry in `FanPublicProcedures()`.
  - Delete `ServerSettings.ConcertHandlerTimeout`, `SERVER_CONCERT_HANDLER_TIMEOUT` and the per-service timeout branch (`provider.go:620`), so the 30-second `SERVER_HANDLER_TIMEOUT` covers the concert service.
  - `ConcertUseCase.SearchNewConcerts` stays, for `cmd/job/concert-discovery` and `SearchNewConcertsOnFirstFollow`.
- **cloud-provisioning.** Removes `SERVER_CONCERT_HANDLER_TIMEOUT` from the fan-api ConfigMap after the backend release. An unknown variable is ignored by envconfig, so the order is safe.

### D8 — The organizer spec moves in its own commit

- `openspec/specs/components/adapter/organizer/api/rpc/concert/spec.md` moves to `.../rpc/series/spec.md`, together with its Purpose wording ("organizer Series service boundary").
- The move goes in a direct commit on the main specs, with the mapping table `rpc/concert → rpc/series`, landed in the plan PR before this change's delta (task 1.1).
- `redesign-organizer-console` has a delta at the old path. The same commit moves that delta directory, so the change keeps validating.

## Risks / Trade-offs

- [The old pods' writes to `event_performers` fail during the rollout (D6)] → Release outside the discovery job's schedule (09:00 JST daily). There are no fan users, and the next discovery run re-inserts what failed.
- [A breaking proto release leaves the deployed frontend reading the old shape until the frontend release] → Release the backend and frontend together. Both are pinned by the prod pin bump. The fan app shows an error state (not wrong data) while the versions differ, because the reserved Concert fields 1–12 are absent.
- [The side-list pattern is new (D2)] → It is recorded here as the rule for every response that returns Concerts. A response that returns Concerts without the lists fails the boundary tests of tasks 5.2, 7.1 and 8.1.
- [Five changes in flight still use the old names] → Task 11.1 rewrites their artifacts after this change's plan merges, before any of them is applied.

## Migration Plan

1. **specification:**
   - The plan PR, with the organizer spec move commit (D8).
   - Then the proto PR: `Event.listed_venue_name`, the new `Concert`, the response lists, organizer `SeriesService`, and the removal of `SearchNewConcerts`.
   - Release and BSR generation.
2. **backend:**
   - Consume the release, and add the mapper side lists, the cover join, the Series service handler, the `concert_artists` migration and the timeout removal.
   - Release once the frontend PR is ready (step 3).
3. **frontend:** In one PR, move the fan `ConcertStore`, event page, tickets page, admin approved-concerts and organizer console client to the new shapes. Release right after the backend.
4. **cloud-provisioning:** Remove `SERVER_CONCERT_HANDLER_TIMEOUT` from the fan-api ConfigMap.

Rollback:
- Revert the backend and frontend releases together.
- The `concert_artists` rename is reversed by a new migration (rename back and re-point the foreign key at `events`). Data is unchanged by either direction.
