## Context

See proposal.md - Why. The data-model, per-event publish and edit rules were decided with the product owner on 2026-10-10. This design records how they are built.

Current state (verified on backend, frontend and specification `main`, 2026-10-10):

- **Schema** (`backend/internal/infrastructure/database/rdb/schema/schema.sql`):
  - `events` has the full constraint `uq_events_natural_key UNIQUE NULLS NOT DISTINCT (venue_id, local_event_date, start_at)` (:177).
  - Drafts live in `draft_events` (:218) and `draft_series_performers` (:242). Commit 21d8b04 says they exist only so that drafts stay out of the natural key and claim no discovered slot before publish.
  - `series.publish_state` (:141), `published_at` and `cancelled_at` are stored, and `chk_series_first_party_state` (:149) ties them to `organizer_id`.
- **Database**: Cloud SQL runs `POSTGRES_18` (`cloud-provisioning/src/gcp/components/postgres.ts:209`). Partial unique indexes with `NULLS NOT DISTINCT` are available (PostgreSQL 15+).
- **Editing a published concert today**:
  - The usecase rejects only CANCELLED (`backend/internal/usecase/concert_authoring_uc.go:303`).
  - The repository's update matches only DRAFT rows (`rdb/series_repo.go:99-103`) and returns FailedPrecondition when no row matched (`series_repo.go:579`). That happens before the draft rows are rewritten, inside a transaction that rolls back.
  - So a save of a published concert fails. It does not silently lose edits.
  - The proto promises the opposite. `Update` is "a correction" once published (`specification/proto/liverty_music/rpc/organizer/series/v1/series_service.proto:64-77`), and `Publish` can add later dates (`:79-96`).
  - The organizer editor lets the operator edit and then shows "Published concerts only allow correction edits; this change was rejected." (`frontend/organizer/concert-editor/concert-editor-route.ts:308-309`).
  - `PublishDraft` rejects a Series that is not DRAFT (`series_repo.go:886`), so a published Series can never gain a date.
- **Fan-facing filters**:
  - One fragment, `firstPartyVisibilityGuard` (`rdb/concert_repo.go:129-132`), is appended to the five fan list queries and reads `s.publish_state` and `s.visibility`.
  - `IsEventPublished` reads the Series' state (`rdb/event_publish_state_repo.go:37-44`).
  - The event page uses `Series.HasEventPage` (`entity/series.go:171`, called at `usecase/concert_uc.go:291`).
  - Non-test references to `publish_state` in rdb: 8 in `concert_repo.go`, 3 in `event_publish_state_repo.go`, 9 in `series_repo.go`.
- **Upserts that name the constraint**: `concert_repo.go:27` (discovery) and `series_repo.go:988` (publish).
- **Cancellation announcement**: `CONCERT.cancelled` is published by `ConcertAuthoringUseCase.Cancel` (`concert_authoring_uc.go:462`) and has no consumer. Changing its payload to the cancelled Events only breaks nobody.
- **Frontend readers of the Series state**:
  - organizer concert list (`organizer/concerts/concerts-route.ts:130-144`);
  - organizer editor (`concert-editor-route.ts:214`);
  - reception links screen (`organizer/reception-links/reception-links-route.ts:170`);
  - fan event page (`src/routes/event/event-page.ts:68`).
- **Discovery**: artists represented by an active Organizer are not searched (archived `2026-08-28-organizer-event-authoring` design, D5). So a discovered Event at an organizer's slot exists only when it was found before the artist was represented.

## Goals / Non-Goals

**Goals:**
- One `events` table and one natural key for every performance. A draft is a row in a state.
- Each fan-facing read decides by the Event's state through one shared condition, and a test proves that draft and cancelled dates never leak.
- A published concert can be corrected and can gain dates.

**Non-Goals:**
- The console redesign: per-date publish confirmation, per-date cancel control and state badges in the list. They belong to `redesign-organizer-console`. Here the existing screens only keep working (route deltas).
- Refunding tickets of a cancelled Event. It stays the existing operator refund flow, as for a cancelled Series today.
- Scheduled publish (`organizer-event-authoring-extensions`).
- Changing the claim rule at publish. It is kept as it is, with one addition: a CANCELLED Event blocks its slot (see "Assumptions to confirm").

## Decisions

### D1 — One `events` table with a nullable `publish_state`

- Add an enum type `event_publish_state` (`DRAFT`, `PUBLISHED`, `CANCELLED`) and a nullable column `events.publish_state`. NULL marks a discovered Event.
- A DRAFT Event gets its `concerts` row and `concert_artists` rows when it is created, like any Event. So publish only flips the state.
- The rule "NULL exactly when the Series is discovered" spans two tables, so a CHECK cannot enforce it. The Series repository is the only writer of first-party Events, and it always sets the state. The migration test and the leakage test cover the rule.
- **Why one table:** a published Series must hold draft dates (decision 3). The draft tables are keyed on a Series that is entirely DRAFT. Keeping them would mean a second copy step and a second performer model for published Series.
- **Rejected — keep `draft_events` and allow rows for published Series:** every read of "the Series' dates" would union two tables, and the claim logic would stay a copy step.

### D2 — The natural key becomes a partial unique index

- Drop the constraint. Create `uq_events_natural_key` as `UNIQUE INDEX ... (venue_id, local_event_date, start_at) NULLS NOT DISTINCT WHERE publish_state IS DISTINCT FROM 'DRAFT'`.
- DRAFT rows never collide. PUBLISHED, CANCELLED and discovered rows share one key space.
- The two upserts move from `ON CONFLICT ON CONSTRAINT uq_events_natural_key` to index inference: `ON CONFLICT (venue_id, local_event_date, start_at) WHERE publish_state IS DISTINCT FROM 'DRAFT'`. PostgreSQL infers a partial unique index when the conflict clause's predicate implies the index predicate. The same expression is used in both places.
- **CANCELLED keeps its slot.** A cancelled performance is still that performance (`components/entity/event` identity). This also stops discovery from bringing back a cancelled show at the same slot, which is the same reason suppression exists.

### D3 — The Series state is derived, not stored

- Drop `series.publish_state`, `published_at`, `cancelled_at` and the type `series_publish_state`. `chk_series_first_party_state` keeps only `visibility` tied to `organizer_id`.
- The timestamps go because no spec reads them. The specification review criteria allow a timestamp field only when a spec requirement reads it (`specification/CLAUDE.md`, review criteria).
- Series reads compute the state with one aggregate over the Series' events: `PUBLISHED` if any is published, else `CANCELLED` if any is cancelled, else `DRAFT`. In Go, `entity.Series.PublishState` stays a field and is filled by the repository from that aggregate. No caller recomputes it.
- Proto: `Series.publish_state` stays, with the same number. It becomes `OUTPUT_ONLY` and is documented as derived. The console list and the reception links screen keep reading it.
- **Rejected — keep a stored Series state in sync:** two sources of truth for one fact. Every event transition would have to update the Series too.

### D4 — Two shared conditions and one leakage test

- `rdb` gets two SQL fragments and no other copies of the predicate:
  - `catalogEventCondition` = `e.publish_state IS DISTINCT FROM 'DRAFT'`. Every Concert operation that reads `events` uses it: the list queries, `ListByIDs`, `ListEventsBySeries`, `FindEventsByVenueAndDate`, `FindEventsByArtistAndDate`, `FillEventStartTimes`, `DeleteAndSuppress`. It realizes the spec's "A draft event is not a concert".
  - `fanVisibleCondition` = `(s.organizer_id IS NULL OR (e.publish_state = 'PUBLISHED' AND s.visibility = 'PUBLIC'))`. It replaces `firstPartyVisibilityGuard` in the five fan lists.
- `IsEventPublished` reads `e.publish_state = 'PUBLISHED'`.
- In Go, `Series.IsPubliclyVisible` and `Series.HasEventPage` become `Event.IsPubliclyVisible(series)` and `Event.HasEventPage(series)`. `ConcertUseCase.Get` checks the event page on the Concert's Event. `ListBySeries` keeps its Series-level check: a Series has an event page when one of its Events has one, and `ListEventsBySeries` already leaves drafts out.
- **Leakage test** (rdb integration, Postgres):
  - The fixture holds a discovered Event, a PUBLISHED Event of a PUBLIC Series, a PUBLISHED Event of an UNLISTED Series, a DRAFT and a CANCELLED Event in that published PUBLIC Series, and a DRAFT Event at the slot of the discovered Event.
  - A table-driven test runs every read method of `entity.ConcertRepository` and of the event-publish port against the fixture and asserts the exact id set.
  - A reflection check fails when the interface gains a `List*`/`Find*`/`Get*` method that is not in the table. A new read cannot skip the test.
- **Rejected — a SQL view `catalog_events`:** the fan-visibility rule would still be a second predicate. We also did not check that the Atlas setup (`atlas.hcl`, `scripts/lint-schema.sh`) handles views (unverified). The reflection-guarded test gives the same protection with no new schema object.

### D5 — Lifecycle operations stay on `SeriesRepository`

- `CreateDraft` (rewritten), `Update` (new), `PublishEvents` (new), `CancelEvents` (new) and `GetAuthored` (rewritten) each run in one transaction.
- `UpdateDraft`, `PublishDraft`, `MarkPublished`, `MarkCancelled`, `LoadDraft` and `entity.DraftEvent` are deleted.
- The usecase method `UpdateDraft` is renamed `Update`, matching the RPC.
- **Why on the Series:** each operation is scoped to one Series. The claim rule needs the Series' Organizer. Splitting writes across an event repository would split the transaction.
- `CancelEvents` deletes a Series left with no Event. `series_media` cascades. The `media` row and its objects stay, as for any hard-deleted Series today (comment at the end of `ConcertAuthoringUseCase.Cancel`).

### D6 — RPC surface: optional event lists, no new methods

- `EventDraft` gains an optional `event_id`. An entry without it is a new date.
- `PublishRequest` and `CancelRequest` gain `repeated EventId event_ids`. Empty means every DRAFT Event (Publish), or every PUBLISHED and DRAFT Event (Cancel).
- `entity.v1.Event` and `entity.v1.Concert` gain `PublishState publish_state` (`OUTPUT_ONLY`). The enum in `series.proto` gets new comments, because it now describes an Event.
- The doc comments of `Update`, `Publish` and `Cancel` are rewritten to the specs. Today's comments promise behavior that the code rejects.
- **Why:** the existing console calls (series id only) keep their meaning. `redesign-organizer-console` sends one id for a per-date publish or cancel.
- **Rejected — new `PublishEvent` / `CancelEvent` methods:** two more methods with the same rules and errors as the Series-level ones.
- Breaking changes go in with the `buf skip breaking` label.

### D7 — Claim at publish keeps the discovered id

- When a DRAFT Event's slot holds a discovered Event (or one of another Series of the same Organizer), `PublishEvents`:
  - re-points that row to the Series and sets it `PUBLISHED`;
  - adds the draft's performers;
  - deletes the DRAFT row.
- Fan references to the discovered id survive (decision 7). No sale, reception link or event page can reference a draft id: sales and reception links require `IsEventPublished`, and drafts have no event page.
- The draft's open time is not copied onto the claimed Event. This is today's behavior (`series_repo.go` claim branch), unchanged.

### D8 — A new start time takes its slot inside `Series.Update`

- For a PUBLISHED Event whose start time changes, the transaction:
  - checks `suppressed_concerts`;
  - looks up the slot with `catalogEventCondition`;
  - when a discovered Event is there, moves its `ticket_journeys` to the live Event (`ON CONFLICT DO NOTHING` keeps the live Event's own journey), adds its performers, and deletes it (cascading its `concerts` row);
  - when a first-party Event is there, fails with FailedPrecondition.
- The live Event keeps its id because its `/events/<id>` link may already be shared and announced. See "Assumptions to confirm".
- **Start-time lock:** `ConcertAuthoringUseCase.Update` calls `TicketSale.ListByEvent` (from `unify-ticket-sales`) for each PUBLISHED Event whose start time changes. A TicketSale requires a start time (`unify-ticket-sales`, `usecase/ticket-sale/create`). So an Event with no start time is never on sale, and setting its first start time is always allowed.
- **Race:** a sale created between the check and the update is possible in theory. There is one operator per Organizer. This is the same trade-off as `unify-ticket-sales` D4.

### D9 — Update validates against the stored Series without resolving venues

- The usecase reads `GetAuthored`, then checks "Corrections keep what publish fixed" before any write.
- A PUBLISHED Event's venue counts as unchanged when the entered venue name equals the Event's listed venue name, and the place id, when given, equals the Venue's place id. The usecase does not resolve the venue for a published Event, so a refused save creates no Venue.
- Performers compare as sets against the performers of the Series' PUBLISHED and CANCELLED Events.
- The past-date check (`validateDraftEventInputs`) runs only for new and DRAFT events. The editor already allows past dates on published concerts (`concert-editor-route.ts:255`).

### D10 — Sequencing with in-flight changes

1. **`unify-ticket-sales`** ships first. This change needs `TicketSale.ListByEvent`.
   - Its `usecase/ticket-sale/create` calls `Event.IsEventPublished`. That operation now answers per Event, and its scenario "the Series is still draft" stays true.
2. **`public-event-page`** archives before this change syncs. Three deltas here modify its specs:
   - `entity/series` "Which series' events have an event page";
   - `usecase/concert/get`;
   - `route/event` "Cancelled event".

   `openspec validate --strict` reports them as INFO until then. Its code is already on `main` (`concert_uc.go:291`).
3. **`ticket-wallet-and-checkin`**: no shared requirement.
   - Its reception-link usecase calls `IsEventPublished`, which now gives the per-Event answer it expects.
   - The reception links screen reads the Series state today (`reception-links-route.ts:170`). Task 8.3 switches it to the Event.
4. **`first-come-ticket-sales`**: its reservation and sale reads call `IsEventPublished` "as for a cancelled concert". That now also covers one cancelled date. Its `route/event` delta changes a different requirement (ticket section). Its backend tables do not read `series.publish_state`. It needs a rebase only if it touches the dropped columns.
5. **`organizer-event-authoring-extensions`**: its "Scheduled publish" (ADDED to `usecase/series/publish`) and its design's `publish_at` on the Series must become per Event when that change is scheduled. This change does not edit it; task 1.3 adds the note there.
6. **`redesign-organizer-console`**: builds the per-date publish confirmation and per-date cancel on D6's surface.

## Assumptions to confirm

The brief did not settle these. Each is the simplest option, and the specs are written to it:

1. **Cancelling a whole Series removes its DRAFT dates.** A Series left with no Event is removed. So "Cancel" on a draft-only concert discards it, where today it becomes a CANCELLED Series (`usecase/series/cancel` "Cancel a draft").
   - Alternative: keep the drafts. But that leaves a Cancelled Series whose drafts can still be published.
   - Alternative: a separate `Delete` RPC for draft concerts. That adds one more method.
2. **No terminal rule on the Series.** A Series whose dates are all CANCELLED can gain a new DRAFT date. Publishing it makes the Series Published again, for example a replacement date (振替公演) under the same tour. CANCELLED stays terminal for each Event.
3. **Type, source page and visibility are fixed after the first publish; performers stay changeable** (confirmed with the owner on 2026-10-10: a guest act is often added after the announcement). An added performer must be represented by the Organizer, as at creation. Adding a performer announces nothing to that Artist's followers; only publishing a new Event announces (`usecase/series/publish` "Public series announces new events per performer").
4. **A new start time that lands on another Event's slot:**
   - a discovered Event there is absorbed and the live Event keeps its id, to keep its shared links;
   - any first-party Event there, even of the same Organizer, fails with FailedPrecondition, so no Event with sales is ever merged away.

   This is narrower than publish's claim of same-Organizer Events.
5. **A CANCELLED Event keeps its slot.** Publishing a draft at exactly that Venue, date and start time fails with FailedPrecondition. "Undo a cancel" is not supported. A moved show has a different slot anyway.
6. **Update must list every PUBLISHED and CANCELLED Event.** Leaving one out fails with FailedPrecondition and does not silently keep it. A published date is cancelled, not removed.
7. **The fan event page marks a cancelled sibling date 中止 in its date list** (`route/event`, scenario "Other date of a partly cancelled tour").

## Risks / Trade-offs

- [A new Concert query forgets `catalogEventCondition`, and drafts leak to fans or into discovery matching] → D4's reflection-guarded leakage test fails for any new read method that is not in the fixture table.
- [Discovery's upsert (`concert_repo.go:27`) still fills an unknown start time of a PUBLISHED organizer Event (existing behavior), which bypasses D8's slot rules] → Represented artists are not searched (Context), so this needs a discovered match found before representation. The unique index still rejects a colliding fill. Not changed here.
- [A deploy window where old pods read dropped columns] → One migration plus the backend rollout. The organizer and fan lists can fail for the minutes between them. There are no users (`CLAUDE.md`, current operating state).
- [Deleting a Series in `CancelEvents` leaves its cover objects in storage] → Same as today's hard delete. The objects are private and unreferenced.
- [Partial-index inference syntax is wrong in one upsert] → Both upserts have contract tests (tasks 4.2, 5.1) that insert at an existing slot and at a draft's slot.

## Migration Plan

1. Read-only counts in production (task 0.2): Series by state, `draft_events` per Series state, PUBLISHED Series that still have draft rows (expected 0), CANCELLED Series with draft rows and no events.
2. Specification: plan PR, then proto PR, then Release, then BSR gen.
3. Backend PR with one Atlas migration, in this order:
   1. Create `event_publish_state` and add `events.publish_state`.
   2. Copy each first-party Series' state onto its events.
   3. Drop the constraint `uq_events_natural_key` and create the partial index under the same name.
   4. Insert `draft_events` of DRAFT Series into `events` as `DRAFT`, keeping their ids, with `concerts` rows. Insert their performers from `draft_series_performers` into `concert_artists`.
   5. Delete CANCELLED Series that have no events. Their draft rows cascade.
   6. Drop `draft_series_performers`, `draft_events`, `series.publish_state`, `published_at`, `cancelled_at` and the type `series_publish_state`. Rewrite `chk_series_first_party_state`.
4. Frontend PR: organizer editor, concert list, reception links and the fan event page.
5. Verify in production: the AtlasMigration status, read-only row checks against step 1, and the story tests run in CI against Postgres. No dev environment is needed.
6. Rollback: the migration is forward-only. With test data only, fix forward. If data must come back, use Cloud SQL point-in-time recovery to before the migration.
