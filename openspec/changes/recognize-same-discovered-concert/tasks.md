## 1. specification: proto comments (design D9)

- [ ] 1.1 In `proto/liverty_music/rpc/admin/concert_candidate/v1/concert_candidate_service.proto`, rewrite the comments of `Approve`, `RESOLUTION_KEEP_EXISTING` and `RESOLUTION_ADOPT_CANDIDATE` to say that both resolutions make the candidate's Artist a performer of the existing event, unless it is an Organizer's event, and keep the name not shown as one of its other listed venue names; open the PR citing `OpenSpec-Change: recognize-same-discovered-concert` and merge it (comment only, no release); verify `buf breaking` in CI reports no change

## 2. backend: schema and entities (Event, Series; design D1, D8)

- [ ] 2.1 Add `events.other_listed_venue_names TEXT[] NOT NULL DEFAULT '{}'` with a `COMMENT ON COLUMN` to `schema.sql` and generate the Atlas migration; verify the migration test applies it
- [ ] 2.2 Add `OtherListedVenueNames` and `ListedUnder` to `entity.Event`; verify one unit test per scenario of `components/entity/event` "Listed under a name"
- [ ] 2.3 Add `entity.SameTourTitle`; verify one unit test per scenario of `components/entity/series` "Same tour title"

## 3. backend: entity operations (design D2, D3, D4, D8)

- [ ] 3.1 Return other listed venue names, publish state and performers from `FindEventsByArtistAndDate`, and listed venue name, other listed venue names, publish state and performers from `FindEventsByVenueAndDate`; verify one contract test per scenario of `components/entity/concert/find-events-by-artist-and-date` and `components/entity/concert/find-events-by-venue-and-date`
- [ ] 3.2 Make `FillEventStartTimes` fail with AlreadyExists and change nothing when a filled time takes another Event's slot; verify one contract test per scenario of `components/entity/concert/fill-event-start-times`
- [ ] 3.3 Declare and implement `Concert.AddOtherListedVenueName` (read under lock, decide with `ListedUnder`, append), and make `UpdateEventListedVenueName` keep the replaced name in the same statement; verify one contract test per scenario of `components/entity/concert/add-other-listed-venue-name` and `components/entity/concert/update-event-listed-venue-name`
- [ ] 3.4 Declare and implement `Concert.Merge` as in design D3; verify one contract test per scenario of `components/entity/concert/merge`, plus one that a ticket journey inserted for the source while the merge holds its lock fails instead of being removed
- [ ] 3.5 Declare and implement `Series.ListUpcomingToursByArtist`; verify one contract test per scenario of `components/entity/series/list-upcoming-tours-by-artist`
- [ ] 3.6 Make `Concert.Create` fail when an Event with a publish state holds a slot (design D6a); verify one contract test per scenario of `components/entity/concert/create` "Create merges into an existing slot"
- [ ] 3.7 Make `Series.DeleteOrphaned` keep a Series that has a TicketSale; including one being written at that moment; verify one contract test per scenario of `components/entity/series/delete-orphaned`

## 4. backend: shared decision and CreateFromDiscovered (design D5, D6, D7)

- [ ] 4.1 Replace `resolveExistingEvent` and `duplicateEventAmong` with the one decision function of design D6; verify a table test with one row per branch listed in D6 and D6a
- [ ] 4.2 Restructure `createSeriesFromDiscovered` into venue resolution then series choice (D5) and apply the decision per event (Nothing, Fill, MergeInto, Stage, and Publish or AddPerformer collected into the series' one `Concert.Create` call), staging on AlreadyExists from the fill; verify one unit test per ADDED or MODIFIED scenario of `components/usecase/concert/create-from-discovered` with the operations mocked, and that a test reproducing the 2026-11-20 shape (an unknown-start row and a timed row under another name at one venue) neither fails nor adds an event

## 5. backend: Approve (design D6, D7)

- [ ] 5.1 In `ConcertCandidateUseCase.Approve`, detect collisions with the decision function (adding the Artist's events on the date), record names with `AddOtherListedVenueName` on keep existing and adopt the candidate, and make the Artist a performer through `Concert.Merge` or `Concert.Create`; verify one unit test per ADDED or MODIFIED scenario of `components/usecase/concert-candidate/approve`
- [ ] 5.2 Add a database integration test that runs `CreateFromDiscovered` and then `Approve` against a real schema for each scenario of `stories/review-concert-candidates` "Concert candidates are reviewed through the queue", annotated with `@spec stories/review-concert-candidates`

## 6. backend: release and production check

- [ ] 6.1 Open the backend PR citing the change, merge it, cut the release, and verify read-only in prod: AtlasMigration `Ready` with the new column, the rollout finished, and the next 09:00 JST concert-discovery run logs no `create-from-discovered` ERROR and no `workflow needs an admin`

## 7. frontend: approval queue conflict dialog (design D9)

- [ ] 7.1 Rewrite the conflict dialog lede in `admin/approval-queue/approval-queue-route.html`; verify the component test for `components/infrastructure/admin/web/route/approval-queue` "Dialog explains the choices"
- [ ] 7.2 Run the approval flow with Playwright against a local build with the RPCs mocked: approve a candidate, get a conflict, read the lede, choose Keep existing, and see the row leave the queue
- [ ] 7.3 Show copy of its own when Approve refuses adopt the candidate with FailedPrecondition, keeping the dialog and the row; verify the component test for `components/infrastructure/admin/web/route/approval-queue` "Adopt refused"
- [ ] 7.4 Open the PR citing the change, merge it and release the frontend

## 8. backend: one discovery batch at a time and daily removal of empty Series (design D11, D12)

- [ ] 8.1 Start `create-from-discovered` on a queue of global concurrency 1, registered beside `ConcertSearchQueue`; verify a unit test for `components/usecase/concert/create-from-discovered` "Two Artists of one concert found together" that the workflow is started on that queue
- [ ] 8.2 Make `Series.DeleteOrphaned` take a creation time and remove the empty discovered Series created before it (`uuid_extract_timestamp(id)`), keeping the `SKIP LOCKED`; verify one contract test per scenario of `components/entity/series/delete-orphaned`
- [ ] 8.3 Add `SeriesUseCase.RemoveEmptyDiscovered` on a daily DBOS schedule, and remove the `DeleteOrphaned` calls of `CreateFromDiscovered`, `Approve` and `Reject` with the tests annotated with their removed scenarios; verify one unit test per scenario of `components/usecase/series/remove-empty-discovered` and the "Last staged row of an empty series" scenario of `components/usecase/concert-candidate/approve`
- [ ] 8.4 Open the backend PR citing the change, merge it, cut the release, and verify read-only in prod: the rollout finished, the next 09:00 JST discovery runs its batches one at a time with no `create-from-discovered` ERROR, and the first daily run of `RemoveEmptyDiscovered` succeeds

## 9. backend: data migration (design D10, after 6.1 is live)

- [ ] 9.1 Collect, with a read-only prod query, the ids of the 9 duplicate pairs (older and newer event, the agreed listed venue name) and of the 29 split discovered TOUR Series in 13 groups with their ticket sales, excluding Ayron Jones' "TOUR DATES"; record the query and its result in the PR description, not in the issue (public repository)
- [ ] 9.2 Write the Atlas data migration with those ids, a backup table, skips for rows that no longer exist, and the ticket sale steps of design D10; verify a migration test with a fixture of one duplicate pair (with a ticket journey on the newer event) and one split tour (with a discovered ticket sale on each Series, two of them on the same method and start date) shows one event with both names, the journey moved, one Series and one sale per method and start date
- [ ] 9.3 Re-run the 9.1 query against prod right before merging, merge the PR (it applies to prod), and verify read-only: AtlasMigration `Ready`, no remaining pair of one Artist's discovered events at one venue and date where only one has a start time, and no Artist with two upcoming discovered TOUR Series of the same tour title other than the excluded one
