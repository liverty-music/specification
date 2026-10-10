## 0. Dependency gate

- [ ] 0.1 Confirm `unify-ticket-sales` is in production, so `TicketSale.ListByEvent` exists (design D8, D10); verify `TicketSaleRepository.ListByEvent` is on backend `main` and the production rollout carrying it is healthy
- [ ] 0.2 Confirm `public-event-page` is archived, so the deltas on `entity/series` "Which series' events have an event page", `usecase/concert/get` and `route/event` have main specs to apply to (design D10); verify `openspec validate restructure-event-publishing --strict` reports no "Archive would refuse this delta" INFO lines
- [ ] 0.3 Read in production, read-only through the db-proxy runbook, the counts of design "Migration Plan" step 1: Series by state, `draft_events` per Series state, PUBLISHED Series with draft rows, CANCELLED Series with draft rows and no events. Record them in design.md "Migration Plan"; verify that only test data exists, or stop and ask the user

## 1. Specification — main specs and notes

- [ ] 1.1 Edit the main spec Purposes directly, as listed (Purpose) in proposal.md, and verify `openspec validate --specs` and `python3 scripts/check-spec-layout.py` pass:
  - `components/entity/event`: add the row `publish state | DRAFT, PUBLISHED or CANCELLED | first-party only; absent on a discovered Event` and a stateDiagram (`[*] --> DRAFT`, `DRAFT --> PUBLISHED`, `PUBLISHED --> CANCELLED`, `DRAFT --> [*]` for removal, `CANCELLED --> [*]`);
  - `components/entity/series`: remove the rows publish state, published at and cancelled at and the stateDiagram; remove `Series ||--o{ DraftEvent` and `Series }o--o{ Artist : "drafts performers"`; say in the text that a first-party Series' publish state is derived from its Events;
  - `components/entity/concert`: add the row `publish state | the Event's publish state | absent on a discovered concert`;
  - `components/entity/venue`: remove `Venue ||--o{ DraftEvent`;
  - `components/entity/series/create-draft`, `get-authored`, `components/entity/event/is-event-published`, `components/usecase/series/create-draft`, `publish`, `cancel`, `stories/publish-an-organizer-concert`: replace DraftEvent and Series-state wording with DRAFT Events and per-Event states.
- [ ] 1.2 Remove the main spec directory `components/entity/draft-event` and the other REMOVED capability directories when this change archives (proposal "Removed Capabilities"); verify `openspec validate --specs` passes after archive
- [ ] 1.3 Add a note to `organizer-event-authoring-extensions/design.md` that scheduled publish must publish chosen DRAFT Events and that `publish_at` belongs on the Event (design D10 item 5); verify `openspec validate organizer-event-authoring-extensions --strict` passes
- [ ] 1.4 Open the plan PR from a worktree cut from origin/main (README "Branch work in this repository"), staging only `openspec/changes/restructure-event-publishing`, with the `openspec show --diff` block in the body (`openspec/AGENTS.md`); verify `openspec-checks.yml` passes and the PR merges

## 2. Proto (specification → BSR)

- [ ] 2.1 Entity protos (design D3, D6):
  - `event.proto` and `concert.proto` gain `PublishState publish_state` (`OUTPUT_ONLY`, optional, unspecified on a discovered Event);
  - `series.proto` `publish_state` becomes `OUTPUT_ONLY` and is documented as derived from the Events (Series spec "Publish state is derived from the events");
  - the `PublishState` enum comments describe an Event.

  Verify `buf lint` and `buf format -d` pass
- [ ] 2.2 `rpc/organizer/concert/v1/concert_service.proto` (design D6):
  - `EventDraft.event_id` (optional `EventId`);
  - `PublishRequest.event_ids` and `CancelRequest.event_ids` (`repeated EventId`, unique items, empty meaning all);
  - rewrite the doc comments of the service, `Update`, `Publish` and `Cancel` from `components/usecase/series/{update,publish,cancel}`, including every FAILED_PRECONDITION case.

  Verify `buf lint` passes and each comment's error list matches the usecase specs
- [ ] 2.3 Open the proto PR from a worktree with the `buf skip breaking` label, merge, and cut a Release; verify `buf-release.yml` succeeds and BSR has the new version

## 3. Backend — migration (design D1–D3, "Migration Plan")

- [ ] 3.1 Write one Atlas migration in the order of design "Migration Plan" step 3, and update `schema.sql` (comments on `events.publish_state` and `uq_events_natural_key`). Verify it applies to a fresh database after every earlier migration, `make lint-schema` passes, and the prod Atlas kustomization registers it
- [ ] 3.2 Add a migration test that loads a DRAFT Series with two draft events and one draft performer, a PUBLISHED Series with one event that claimed a discovered event, a CANCELLED Series with events, a CANCELLED Series with only draft rows, and a discovered event at the slot of one draft. Apply the migration and verify:
  - the draft ids are kept as DRAFT events, each with the performer and a `concerts` row;
  - the published and cancelled events carry their state;
  - the draft-only cancelled Series is gone;
  - the discovered event keeps its slot;
  - a second PUBLISHED event at a taken slot is rejected while a second DRAFT is accepted.

## 4. Backend — entities

- [ ] 4.1 `Event` publish state and guards (`components/entity/event`), with `Event.IsPubliclyVisible(series)` and `Event.HasEventPage(series)` replacing the Series methods (design D4); verify one unit test per scenario: Matinee and evening shows are distinct, Same slot under different series is one event, Two unknown start times collapse, Unknown start does not match a known start, Draft beside a discovered event, Discovered event has no publish state, New authored event is a draft, Draft is not cancellable, Cancelled stays cancelled, Discovered event is visible, Published event of a public series is visible, Published event of an unlisted series is not visible, Draft date of a published tour is not visible, Cancelled date is not visible, Published venue is fixed, Doors-open time after publish, Start time announced after publish, Start time on sale is fixed, Cancelled event is fixed
- [ ] 4.2 `Series` derived state and after-publish guard (`components/entity/series`); verify one unit test per scenario: Published tour with a draft date, One date cancelled, Every published date cancelled, Only drafts, Discovered series has no publish state, Title corrected after publish, Visibility fixed after publish, Draft series is fully editable, Published public series, Cancelled public series, Unlisted series, Draft series, Discovered series
- [ ] 4.3 `Concert` carries the publish state (`components/entity/concert` "A concert is exactly one event", "Fan visibility follows the event"); verify unit tests: Title comes from the series, Concert id is its event id, Cancelled date of a published tour, Concert of an unlisted organizer series, Cancelled date of a public series
- [ ] 4.4 Delete `entity.DraftEvent`, the Series fields `PublishedAt` and `CancelledAt`, and the repository methods named in design D5; keep `Series.PublishState` as a field filled from the Events (design D3); verify `make check` passes

## 5. Backend — entity operations (contract tests against Postgres)

- [ ] 5.1 `Series.CreateDraft`, `GetAuthored` and `Update` (design D5, D8); verify one contract test per scenario:
  - create-draft: Draft with two events, Unknown venue;
  - get-authored: Draft series read, Published tour with a new date, Unknown series id;
  - update: Draft date removed, Date added to a published tour, Doors-open time corrected, Guest performer added after publish, Event of another series, Start time announced, Discovered event at the new slot, Suppressed new slot, First-party event at the new slot.
- [ ] 5.2 `Series.PublishEvents` and `CancelEvents` (design D2, D7); verify one contract test per scenario:
  - publish-events: New slot, Claim a discovered event, Known start next to unknown-start event, Other drafts stay drafts, Suppressed slot, Another organizer's slot, Cancelled slot, Already published, No event given;
  - cancel-events: One date of a tour cancelled, Whole draft discarded, Published and draft dates together, Already cancelled, Unknown series.
- [ ] 5.3 `Event.IsEventPublished` on the Event's own state; verify contract tests: Published organizer event, Draft date of a published series, Cancelled date of a published series, Discovered event, Unknown event id
- [ ] 5.4 Introduce `catalogEventCondition` and `fanVisibleCondition` in `rdb` (design D4), apply them to every Concert read and to the discovery upsert's conflict inference, and add the reflection-guarded leakage test. Verify the test passes for every scenario:
  - `components/entity/concert`: Draft not returned by id, Discovery ignores a draft at the same slot;
  - list: Cancelled organizer concert included, Staged concert excluded, Empty catalog, Draft event excluded;
  - list-by-artist: Past and upcoming, Upcoming only, Draft organizer concert excluded, No concerts, Draft and cancelled dates of a published tour excluded;
  - list-by-artists: Two artists, Cancelled organizer concert excluded, No concerts, Draft date of a published tour excluded;
  - list-by-follower: Default start is today, Past start date widens the range, Two followed performers at one concert, Unlisted organizer concert excluded, Follows nothing, Draft and cancelled dates of a published tour excluded;
  - list-by-location: Same admin area without coordinates, Nearby venue in range, Outside the date range, Nothing nearby, Draft and cancelled dates of a published tour excluded.

  Also verify that `grep -n "publish_state" internal/infrastructure/database/rdb/*.go` outside tests shows only the two conditions, the Series aggregate and the lifecycle writes

## 6. Backend — usecases (unit tests with the operations mocked)

- [ ] 6.1 `ConcertAuthoringUseCase.CreateDraft` (`components/usecase/series/create-draft`); verify unit tests: Draft for a represented artist, Two showtimes, and the existing validation scenarios
- [ ] 6.2 Rename `UpdateDraft` to `Update` and implement `components/usecase/series/update` (design D9), calling `TicketSale.ListByEvent` only for PUBLISHED Events whose start time changes; verify unit tests: Another organizer's series, Unknown series, Doors after start, Correcting a past published date, Published venue changed, Published date left out, Visibility changed after publish, Start time on sale, Start time before any sale, Event removed, Published concert corrected, Additional date added as a draft
- [ ] 6.3 `ConcertAuthoringUseCase.Publish` with optional event ids (`components/usecase/series/publish`); verify unit tests: No performer, No cover image, Claims a discovered event, Suppressed slot, Already published, Additional date on a published tour, Only the named date, Unlisted publish, New date keeps the share link, Two performers, Only claimed events, Additional date announced alone, and the unchanged Another organizer's series and Unlisted publish reported
- [ ] 6.4 `ConcertAuthoringUseCase.Cancel` with optional event ids (`components/usecase/series/cancel`); verify unit tests: Unknown series, Cancel a published concert, Cancel a draft, Cancel twice, Cancel one date, Cancelled tour, Draft discarded silently
- [ ] 6.5 `ConcertUseCase.Get` checks the event page on the Event and returns its publish state (`components/usecase/concert/get`); verify unit tests: Published public concert, Cancelled series, Draft date of a published series, and the existing Unknown id, Unlisted series, Discovered concert, Store unavailable

## 7. Backend — adapter, story and release

- [ ] 7.1 Organizer concert handler: map `EventDraft.event_id`, `PublishRequest.event_ids`, `CancelRequest.event_ids` and the per-Event `publish_state` on `AuthoredConcert` events; the fan concert mapper sets `Concert.publish_state`. Verify the existing handler tests of `components/adapter/organizer/api/rpc/series` pass and a new handler test maps each field
- [ ] 7.2 Extend the story test for `stories/publish-an-organizer-concert` (rdb integration with the usecases, like `sales_phase_story_test.go`); verify it passes for: Public concert goes live, Unlisted concert stays off lists, Discovered concert claimed, Cancel after publish, Tour adds a date, Doors-open time announced after publish, Venue cannot move after publish
- [ ] 7.3 Upgrade the generated package to the 2.3 release, run `make check` and `make test-integration`, open the backend PR citing the change, and merge; verify the AtlasMigration applies in production and the rollout is healthy

## 8. Frontend

- [ ] 8.1 Organizer concert editor (`components/infrastructure/organizer/web/route/concert-editor`):
  - per-event state;
  - fixed venue and date and no remove control on PUBLISHED events;
  - read-only CANCELLED events;
  - fixed type, source page and visibility after the first publish, performers still editable;
  - `event_id` sent for existing events;
  - the start-time-on-sale message.

  Verify component tests: Published event's venue is fixed, Additional date saved as a draft, Start time already on sale, and the existing cover image scenarios
- [ ] 8.2 Organizer concert list (`components/infrastructure/organizer/web/route/concerts`): Publish offered while any event is DRAFT, Cancel while any event is PUBLISHED or DRAFT, and the lottery and ticket sale entry points gated on the event's own state; verify component tests: Published tour with a new date, Nothing left to publish, Organizer reaches lottery configuration from a published event, No lottery entry point for a draft event
- [ ] 8.3 Reception links screen: read the event's own publish state instead of the Series'; verify its existing component tests pass with a DRAFT and a CANCELLED date of a PUBLISHED Series
- [ ] 8.4 Fan event page (`components/infrastructure/fan/web/route/event`): the 中止 banner follows `Concert.publish_state`, and a cancelled sibling date is marked 中止 in the date list; verify component tests: Shared link after cancellation, Other date of a partly cancelled tour
- [ ] 8.5 Upgrade the generated clients to the 2.3 release, run `make check`, open the frontend PR citing the change, and merge; verify the production rollout is healthy

## 9. Production verification

- [ ] 9.1 Read the migrated rows in production read-only: events by `publish_state`, no `draft_events` table, and partial index `uq_events_natural_key` present (`\d events`). Verify the counts match task 0.3
- [ ] 9.2 Run `gh workflow run stripe-sandbox-e2e.yml` and verify the ticket sale stories still pass on events whose state is now stored per Event
