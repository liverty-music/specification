## Context

See proposal.md for why. The code paths, verified at backend `d13fe418`:

- `ConcertUseCase.SearchNewConcerts` drops already-known events (`FilterNewSeries`, keyed by listed venue name) and starts `create-from-discovered` with what is left.
- `CreateFromDiscovered` (`internal/usecase/concert_creation_uc.go`) chooses the series first (`resolveSeriesForGroup`: the Artist's Events on the batch's dates with the same listed name), then per event either takes the re-discovery fast path (`eventsAtSameVenue` by listed name, then `resolveExistingEvent` and `FillEventStartTimes`) or resolves the venue with Places and runs the shared collision gate (`detectDuplicateEvent` / `duplicateEventAmong` in `concert_candidate_uc.go`, also used by `Approve`).
- The DB identity of an event is `uq_events_natural_key (venue_id, local_event_date, local_start_time) NULLS NOT DISTINCT WHERE publish_state IS DISTINCT FROM 'DRAFT'`. `Concert.Create` upserts on it and links performers by joining on it (`insertEventPerformersQuery`), returning newly linked events so `Concert.Created` is announced per newly listed Artist. A second performer is therefore already supported by the store; only the usecases never route a found event there.
- `FillEventStartTimes` is a single `UPDATE ... FROM unnest(...)`, so a 23505 on the natural key fails the whole statement; `toAppErr` maps 23505 to `already_exists`.
- Tables referencing `events`: `concerts`, `concert_artists`, `ticket_journeys` (PK `user_id, event_id`), `ticket_sale_events` (PK `ticket_sale_id, event_id`) all `ON DELETE CASCADE`; first-party tables (tickets, settlements, scanners, admissions, ticket stocks) are `RESTRICT` or only reference first-party events.

## Goals / Non-Goals

**Goals:**
- One decision procedure for "is this the same concert" shared by discovery and approval.
- No failure of a whole batch because of one slot.

**Non-Goals:**
- Merging Venue rows, changing `uq_events_natural_key`, or changing `FilterNewSeries` (it stays a best-effort pre-filter; the creation path decides).

## Decisions

### D1. Other listed venue names are a column on `events`
`events.other_listed_venue_names TEXT[] NOT NULL DEFAULT '{}'`, holding normalized names. `entity.Event` gains `OtherListedVenueNames []string` and `ListedUnder(name string) bool` (Event, "Listed under a name"), built on `entity.SameListedVenue`, which already defines name equality. The names are read with the event by `FindEventsByArtistAndDate` and `FindEventsByVenueAndDate`.
Alternative: a separate `event_listed_venue_names (event_id, name)` table. Rejected: a handful of names per event, always read with the event, never queried on their own.
Alternative: suppress through RejectedConcert. Rejected: the RejectedConcert is append-only analysis data that never suppresses (entity spec), and its rows are not tied to an Event.

### D2. `AddOtherListedVenueName` decides in Go under a row lock
The repository reads the event `FOR UPDATE`, asks `ListedUnder`, and appends only when false, in one transaction. A plain `array_append ... WHERE NOT name = ANY(...)` would compare exact strings, not `SameListedVenue` keys.

### D3. `Concert.Merge` is one transaction that locks both events
`ConcertRepository.Merge(ctx, sourceID, targetID)`: `SELECT ... FROM events WHERE id IN (source, target) ORDER BY id FOR UPDATE` (fixed order, so two merges cannot deadlock), check same venue and date and `publish_state IS NULL` on both events, then `INSERT INTO concert_artists ... SELECT target ... ON CONFLICT DO NOTHING`, `INSERT INTO ticket_journeys ... SELECT target ... ON CONFLICT (user_id, event_id) DO NOTHING` (the fan's journey on the target wins), the same for `ticket_sale_events`, append the source's names to the target's `other_listed_venue_names` (deduplicated with `SameListedVenue` in Go before the write), `DELETE FROM events WHERE id = source` (cascades the source's remaining rows), and leave the Series (see D6b). No outbox row is written, so nothing is announced. `Series.DeleteOrphaned` keeps a Series that has a TicketSale, so a sale stored after a merge emptied the Series survives the sweep. Merge refuses (FailedPrecondition) a source that is the last Event of a Series with a TicketSale, since the Series sweep would remove the sales with it; discovery then stages the event and Approve adds the Artist with `Concert.Create`, keeping the source.
The refusal for a source that sells alone reads the Series' other Events and its TicketSales, so Merge then locks the source's Series row `FOR UPDATE` (after the events, always in that order) before evaluating it. That serializes two Merges out of one Series, and conflicts with the `FOR KEY SHARE` that inserting a sale or an event into the Series takes.
Check-then-act: the other checks read the two locked rows; any writer that could change them (`FillEventStartTimes`, `UpdateEventListedVenueName`, `Concert.Create`'s upsert on the target's natural key, another `Merge`) updates the same rows and waits on these locks. A ticket journey or sale link written for the source cannot slip in between the copy and the delete: inserting a row that references `events` takes `FOR KEY SHARE` on the event row for the foreign key check, which conflicts with the `FOR UPDATE` taken first. A writer that committed earlier is seen by the copy; a later one waits for the merge to commit and then fails its foreign key check, so the fan's action fails visibly instead of being cascaded away.

### D4. The fill reports AlreadyExists; the usecase stages
`FillEventStartTimes` keeps its single statement; the 23505 already surfaces as AlreadyExists. Before filling, the usecase looks for an Event holding the slot in the `FindEventsByVenueAndDate` result; if one is there it merges or stages (create-from-discovered, "Start time held by another Event") without trying the fill. The AlreadyExists branch only covers a concurrent writer.

### D5. Venues are resolved before the series is chosen
`createSeriesFromDiscovered` becomes two passes:
1. For every event: normalize the name; when one of the Artist's events on that date (one `FindEventsByArtistAndDate` call for the series' dates, as today) is `ListedUnder` it, take that event's venue; otherwise, with an admin area and a time zone, resolve the venue through the existing Places path (batch cache unchanged); otherwise mark it unresolved.
2. Choose the series (create-from-discovered, "One Series per discovered series"): an Artist's event on one of the dates that is `ListedUnder` the name or has the resolved `venue_id`; else, for TOUR, `SeriesRepository.ListUpcomingToursByArtist` filtered by `entity.SameTourTitle`; else mint and create.
Then decide each event with the series known, staging unresolved events as today.
Places calls do not increase: an event that skipped Places before still skips it; only the order changes. A Places failure still fails the batch before any write, which is safe to retry.

### D6. One decision function for discovery and approval
Replace `duplicateEventAmong`/`resolveExistingEvent` with a pure function in `internal/usecase` (or `internal/entity` if it needs no repository) taking the found event (name, venue, date, start), the Artist, the Artist's events on the date and the events at the venue and date, and returning one outcome: `Nothing`, `Fill(eventID)`, `MergeInto(sourceID, targetID)`, `AddPerformer(targetEvent)`, `Stage(conflictEventID)`, `Publish`. Discovery maps `Stage` to `ConcertCandidate.Upsert` and stores nothing for `Nothing`; Approve maps every outcome but `Fill` and `Publish` to a conflict and applies the resolution. The rules are the ordered list in the create-from-discovered spec: own events at the venue (same start or both unknown, listed under the name → Nothing; found start unknown, own event timed and listed under the name → Nothing; the same two under another name → Stage; fill, unless the slot is held → MergeInto or Stage, or the own event is an Organizer's and the slot is free → Nothing when listed under the name, Stage otherwise, see D6a), own event at another venue with the same known start → Stage (checked before the fill, against the Artist's events kept current with what the series filled, merged and plans to publish), other events at the venue (no publish state, same known start and listed under the name → AddPerformer; same start, both unknown, or unknown next to known → Stage), else Publish.

### D6a. Organizer's Events are never merged or given a performer by these rules
`FindEventsByVenueAndDate` and `FindEventsByArtistAndDate` return Events with a publish state too (`catalogEventCondition` excludes only DRAFT); both now select `publish_state` and the performers, which they did not before. The decision function treats an Event with a publish state as a plain collision (Stage), never as a target of Fill, AddPerformer or MergeInto, and never as a source of MergeInto; the one exception is the Artist's own unknown-start Organizer's Event already listed under the found name (an admin kept it), which is `Nothing`, so discovery does not stage it again and Approve still reports the collision; `Concert.Merge` refuses either side with a publish state, and `Concert.Create` fails with FailedPrecondition when an Event with one holds a slot, as backstops for an Organizer publishing between the decision and the write: the batch fails and is decided again, and an approval keeps its candidate. Create's upsert (`DO UPDATE`) locks the conflicting row whether or not it updates it (PostgreSQL, [INSERT](https://www.postgresql.org/docs/current/sql-insert.html): "all conflicting rows will be locked when ON CONFLICT DO UPDATE ... is specified"), so the publish-state check that follows in the same transaction cannot race a publish. Approve with adopt the candidate against an Organizer's Event fails with FailedPrecondition and changes nothing, since adopting would replace its listed venue name and fill its times; keep existing and reject remain.

### D6b. Series choice skips shared bills, and merged-away Series are swept at the end
Series choice rule 1 only looks at Events where the Artist is the only performer and that have no publish state, so an Event in another Artist's Series that the Artist joined, or an Organizer's Event, does not pull the Artist's tour into it. `Concert.Merge` leaves the source's Series; CreateFromDiscovered adds that Series to the set it passes to `Series.DeleteOrphaned` after the whole batch is stored, because the batch may still publish or stage events under it.

### D7. Adding a performer reuses `Concert.Create`
`AddPerformer` adds a Concert at the target's venue, date and start time, with the Artist as performer and under the target's Series, to the series' one `Concert.Create` call (create-from-discovered, "The published events of a series are created together"); `Concert.Create` already takes Concerts of several Series in one call and announces once per Series and Artist. Approve, which handles one candidate, makes its own call. The natural-key upsert keeps the target row and `insertEventPerformersQuery` links the Artist and returns the event, which announces `Concert.Created` for that Artist only. No new operation is needed.

### D8. Same tour title is a pure function
`entity.SameTourTitle(a, b string) bool`: `golang.org/x/text/width.Fold`, then `norm.NFC` (width.Fold turns "ｶﾞ" into カ plus a combining U+3099, which NFC composes into ガ; verified with x/text v0.44.0), then `unicode.ToLower` on runes in `unicode.Latin`, keep only `unicode.IsLetter || unicode.IsNumber` runes, compare. NFKC is not used, since it would make "Ⅱ" equal "II"; `IsNumber` keeps Ⅰ, Ⅱ, ① and ② so a numbered sequel stays a different tour. `ListUpcomingToursByArtist` filters in SQL on `series.organizer_id IS NULL AND series.type = 'TOUR'` and an event of the Artist on or after the current date at its venue, with the same date expression as `ListUpcomingByArtist`; the title comparison is done in Go.

### D9. Approval screen
The lede in `admin/approval-queue/approval-queue-route.html` is rewritten (approval-queue, "The conflict dialog says what each choice keeps"), and a refused adopt (FailedPrecondition, an Organizer's event) shows copy of its own ("Adopt refused for an Organizer's event"). It shows static text from no RPC field, so no proto change. The proto comments of `Approve`, `RESOLUTION_KEEP_EXISTING` and `RESOLUTION_ADOPT_CANDIDATE` say "drop it" and "overwrite"; they are updated to say the Artist becomes a performer, except of an Organizer's event, and the replaced name is kept. Comment only, no type change, so backend and frontend do not wait for a release.

### D10. Data migration after the code
An Atlas data migration in backend (`k8s/atlas/base/migrations`), applied only after the release carrying D1 to D8 runs in prod, so the old code cannot recreate duplicates. It lists ids explicitly (no title or name matching) and skips any listed row that no longer exists:
- 9 duplicate pairs (the table in the approved plan, issue liverty-music/backend#926): keep the older event, set its listed venue name to the agreed one, copy start and open time from the other, add the other's name to `other_listed_venue_names`, copy performers, ticket journeys and ticket sale links as in D3, delete the newer event.
- 29 discovered TOUR Series of 13 Artists into 13: re-point `events.series_id`, `concert_candidates.series_id` and discovered `ticket_sales.series_id` to the oldest Series of each group. Before re-pointing sales, drop the later-found of two sales that would collide on `uq_ticket_sales_discovered_convergence (series_id, method, sale_start_local_date)`, after copying its reminder log rows to the kept sale where the kept one has none; keep the oldest `ticket_sale_searches` row of the group on the canonical Series. Then delete the emptied Series. The 2026-11-27 count found no ticket sale on these Series; the steps still guard a sale found before the migration runs. Ayron Jones' "TOUR DATES" Series are left alone.
The ids are collected by a read-only query right before writing the migration and re-checked against prod right before merging it. A backup table like `_series_consolidation_backup` keeps the old `series_id` of every re-pointed row and copies of every deleted event, ticket sale and reminder log row for rollback.

## Risks / Trade-offs

- [A wrong automatic shared bill notifies another Artist's followers] → automatic only when the listed name matches and the start time is known; everything else goes to an admin.
- [Two Artists' tours with the same title by the same Artist years apart join] → only Series with an upcoming event are joined; a finished tour is never joined.
- [Notifications already sent reference a merged-away event id] → the notification record is history; a stale id in it opens no page today. Accepted.
- [The 153 pending candidates that differ only by name stay in the queue] → each approval records the name, so they do not come back; bulk clearing is out of scope.
- [The migration's ids go stale between writing and applying] → it skips missing rows; the prod check after deploy counts what remains.

## Migration Plan

1. specification: proto comment PR (D9), merged; no release required.
2. backend: schema migration (D1) and code (D2 to D8), merged, released, rolled out; the schema migration applies on merge.
3. frontend: dialog lede (D9), released.
4. backend: data migration (D10), merged after step 2 is live; it applies to prod on merge.
5. Read-only prod check: AtlasMigration `Ready`, no remaining pair of the Artist's discovered events at one venue and date where one has no start time and the other has one, and no Artist with two upcoming discovered TOUR Series of the same tour title (except the excluded one).
Rollback: the code is a plain revert; the schema column stays; the data migration's backup table restores series ids and the deleted rows.
