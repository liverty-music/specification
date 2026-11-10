## Context

See proposal.md - Why. The audit compared every port doc comment in `backend/internal/entity` and the UseCase interfaces in `backend/internal/usecase` with their implementations and with the living specs. Each finding falls in one of three groups:

| Group | What is wrong | Fix |
|---|---|---|
| Stale doc comment | The spec and the code agree; the Go doc says something else or leaves the behaviour out | Rewrite the doc comment from the spec |
| Code breaks a spec | The spec states a rule the code does not keep | Change the code; add the missing scenario |
| Spec silent | Neither the spec nor the doc says what happens | Not in this change; listed under Open Questions |
| Project rule broken | No spec is broken, but the code breaks a rule of the backend's AGENTS.md "Review criteria" | Change the code to follow the rule |

Code that breaks a spec today:

- `users.email` is `TEXT UNIQUE`, which compares letter case. `UserRepository.GetByEmail` matches with `lower(email) = lower($1)` and already returns Internal when two rows match ("more than one user has the email when letter case is ignored"). `components/entity/user/get-by-email` and `components/entity/user/create` together mean one User per address with letter case ignored.
- `seriesUseCase.Publish` calls `SeriesRepository.PublishEvents` (its own transaction) and then `SeriesRepository.SetUnlistedToken` (a separate statement). The Series spec allows a share token only on a published UNLISTED Series, and the Publish spec says an UNLISTED publish leaves the Series with a share token. When the second call fails, the Series is published without a token, and a repeated Publish fails with FailedPrecondition because no DRAFT Event is left.

A second audit (the re-audit) read every usecase, adapter and infrastructure file and added these:

- **Code breaks a spec:**
  - `adapter/pb/order.go` (`FromOrder`, lines 50-55) maps the source as "the Checkout, otherwise the LotteryEntry". An Order whose source is a ResaleEntry is therefore announced as paid with `lottery_entry_id` set to an empty id, although `entity/v1` has `resale_entry_id`. `entity/order/issue` says the paid announcement carries the Order. The confirmation email and push read the Order again by id, so they are not affected; the analytics consumer records no source for such an Order (see Open Questions).
  - `organizerUseCase.AssociateArtist` reads the Organizer, checks that it is not deactivated, and then calls `OrganizerRepository.AssociateArtist` in a separate transaction. A Deactivate that commits in between lets a deactivated Organizer gain an Artist, which `usecase/organizer/associate-artist` forbids ("the Organizer's roster is fixed because it is deactivated"). The AGENTS.md rule for a write that checks a condition requires the check and the write in one transaction.
- **A promise kept only by luck:** `UserRepository.UpdateHome` reads the User without a lock, then inserts a Home when the User has none. Two concurrent first calls both insert, and one Home row is left unreferenced. The User still ends with one Home, so no spec is broken, but the same AGENTS.md rule applies.
- **Project rules broken** (AGENTS.md "Review criteria"):
  - `ConcertRepository.ListByArtist(ctx, artistID, upcomingOnly bool)`: "A different filter is a different method".
  - `UserRepository.UpdatePersonalDetails` and the User entity store an absent full name or phone number as `""` (`nullStringFromEmpty`): "an optional value is a pointer, never `""`".
  - `infrastructure/geo` `CentroidResolverImpl.ResolveCentroid` returns bare `fmt.Errorf` to the usecase: "A bare `fmt.Errorf` across a boundary is a violation". Its port `usecase.CentroidResolver` has no doc comment.
  - The check-then-act rule cites `checkout_repo.go` `checkoutLockTicketTypeQuery`, which no longer exists; the lock it means is `checkoutUserLockQuery`, the User row lock every creation of an Order takes first.

Checked in the re-audit and found not to be defects:

| Finding | Why it is not a defect | Where it goes |
|---|---|---|
| The cancellation notice prices a Ticket as the Order's amount divided by its ticket count; `Refund` divides by the number of the Order's Ticket rows | Both specs (`usecase/order/refund`, `usecase/notification/send-event-cancelled`) say amount divided by the number of Tickets. `Ticket.ListByUser` returns Issued and Voided Tickets alike, so the row count equals the ticket count and both give the same price | The duplicated formula moves to one entity method in `move-decisions-into-entities` |
| `stripeWebhookService.ApplyOnce` checks `IsProcessed` before applying and marks after | The processed row is only a fast path; the applied handlers are idempotent, which the code documents, so a second delivery applies nothing twice | None |
| `OrganizerRepository.SetStatus` sets the status with no compare-and-set | Its only caller is Deactivate, which may move an Organizer to Deactivated from any state; Provisioning to Active already uses `CompareAndSetStatus` | None |
| The cancellation and refund emails have no "send time" guard, unlike the confirmation and lottery-loss emails | Each is sent in a recorded workflow step of a workflow named after the Order (`orderNoticeWorkflowID`), so a rerun sends nothing a second time, as `send-event-cancelled` requires | None |
| `gemini.EventDraft.Country` is parsed and never read | The discovered event has no country attribute in its spec; the admin area code carries the country. Dead code, not a broken contract | Removal in `move-decisions-into-entities`, with the other Concert.Search code it touches |
| Concert.Search removes repeated events by a symmetric key, and two events with no start time collapse to one, while `DiscoveredSeries.FilterNewSeries` treats an unknown start time asymmetrically | Each follows its own spec (`entity/concert/search` "Search removes repeated events", `entity/discovered-series/filter-new-series`) | None; the normalization differences are an Open Question |

## Goals / Non-Goals

**Goals:**

- Every port doc comment in `internal/entity` and every UseCase interface comment touched here states what the implementation does, in the spec's terms, including every apperr code it returns under `# Possible errors`.
- The spec violations are fixed and covered by tests annotated with the new scenarios, and the code follows the AGENTS.md rules listed above.

**Non-Goals:**

- Moving rules between layers, splitting functions or changing test infrastructure: those belong to `restructure-backend-responsibilities` (layers, errors and the clock), `move-decisions-into-entities` (rules moved into entities, function size) and `speed-up-and-fill-backend-tests`. This change edits comments, the behaviour fixes and the rule fixes above, so it can merge before them and they rebase on correct comments and signatures.
- Deciding behaviour the specs leave open (Open Questions).

## Decisions

### Doc comments are rewritten from the spec, not from the code

Where the spec and the code agree, the spec wording is the reference and the Go doc paraphrases it, keeping the project's `# Possible errors` and `# Announces` headings. Writing from the code would copy implementation detail (index names, COALESCE) into the contract; the spec already states the promise at the right level. The SQL detail stays in the query constants' own comments, where it is today.

The findings to fix, each confirmed against the spec named:

| Port method | Spec | What the doc gets wrong |
|---|---|---|
| `ConcertRepository.Create` | `entity/concert/create` | Names the natural key `(series_id, local_event_date, venue_id)`; the slot is Venue, date and start time, an unknown start matching only an unknown start, and same-slot Concerts in one call are stored once |
| `ConcertRepository.ListByArtist`, `ListByArtists`, `ListByFollower`, `ListByLocation` | `entity/concert/list-by-*` | Omit that Concerts not visible to fans are left out; `ListByArtist` says "all concerts" |
| `ConcertRepository.ListEventsBySeries`, `FillEventStartTimes`, `FindEventsByVenueAndDate`, `FindEventsByArtistAndDate`, `Delete`, `ListByIDs` | `entity/concert` "A draft event is not a concert" | Omit that a DRAFT Event's id matches no Concert; `Delete` says only "an id that no longer exists" is a no-op |
| `ArtistRepository.UpdateFanart` | `entity/artist/update-fanart` | Says no fanart updates only the sync time; it removes the earlier images |
| `ConcertUseCase.ListByArtist`, `ListFollowed` | `usecase/concert/list-by-artist`, `list-followed` | List NotFound; an unknown Artist gives an empty list, and an unknown User gives no Concerts |
| `OrderUseCase.Refund` | `usecase/order/refund` | Describes the refund as "face + system fee; processor fee retained" and Dispute as "always allowed"; the amount is the price of the Tickets still Issued, and only a Paid Order is refunded |
| 16 announcing methods: `ArtistRepository.Create`, `CheckoutRepository.Release`, `ConcertRepository.Create`, `FollowRepository.Follow`, `LotteryEntryRepository.PersistDrawOutcome`, `IssuanceRepository.Issue`, `OrganizerRepository.CompareAndSetStatus`, `OrganizerRepository.AssociateArtist`, `PasskeyRepository.Create`, `PasskeyRepository.Delete`, `PushSubscriptionRepository.Create`, `PushSubscriptionRepository.Delete`, `ResaleListingRepository.RecordRefund`, `SeriesRepository.PublishEvents`, `TicketRepository.Admit`, `TicketSaleRepository.UpsertDiscovered` | each method's spec | `# Possible errors` omits Unavailable (a failure to record the announcement); `CompareAndSetStatus` has no `# Possible errors` at all |

The list was produced by a script that reads each interface method's doc and flags a `# Announces` section without Unavailable under `# Possible errors`. The implementer re-runs the same check when done, and also compares every `apperr.New`/`toAppErr` code each listed implementation returns with its `# Possible errors` (known misses: InvalidArgument on `ConcertRepository.Create`, `LotteryEntryRepository.Create`, `ResaleEntryRepository.Create`, `IssuanceRepository.Issue`, `ArtistRepository.Create`, `UserRepository.Create`).

### Email uniqueness: a unique index on `lower(email)`

The rule "two emails are the same when equal with letter case ignored" is enforced where the existing uniqueness is enforced, in the database, so two concurrent Creates cannot both pass. Replace the column constraint `email TEXT UNIQUE` with `CREATE UNIQUE INDEX uq_users_email_lower ON users (lower(email))`, which also replaces the plain `idx_users_email_lower` (same expression). `idx_users_email` is dropped too: no query in `internal/infrastructure/database/rdb` matches `users.email` exactly (the only email lookup is `lower(u.email) = lower($1)` in `user_repo.go`). A unique violation on the new index maps to AlreadyExists through `toAppErr`, as the old constraint did.

The email is stored as given; normalising it to lower case on write was rejected because the announcement and the confirmation emails carry the address as the identity provider gave it, and nothing in the specs asks for a canonical form.

The Internal branch of `GetByEmail` for two matching rows becomes unreachable once the index exists. It is kept: removing it would turn a data-integrity breach into a silent first-match.

Alternatives considered: a `citext` column (needs an extension and changes every comparison on the column, more than the rule needs); a check in `UserRepository.Create` before the insert (a race between two Creates passes it).

### Share token travels with `Series.PublishEvents`

`SeriesRepository.PublishEvents` gains an optional token parameter (`token *string`, following the "optional value is a pointer" review rule). Inside its existing transaction, after the series row is locked (`lockSeriesForWrite`), it checks that the Series is UNLISTED and has no token, then sets it in the same transaction as the publish. `seriesUseCase.Publish` generates the token before the call only when the loaded Series is UNLISTED and has none, and no longer calls `SetUnlistedToken`. `SetUnlistedToken` stays for `RegenerateShareUrl`.

The check and the write run under the series row lock that `RegenerateShareUrl`'s path (`SetUnlistedToken` on the same row) and `Update` (which can change visibility, also locking the series row through `lockSeriesForWrite`) take, so a visibility change or a rotation between the check and the write cannot interleave. The implementer confirms that `SetUnlistedToken` takes the row lock (an `UPDATE` on the row does); if it does not, it must.

Alternatives considered: setting the token before publishing (breaks the Series spec rule that only a published UNLISTED Series has a token, and a token on a draft would open nothing yet still be live); a compensating clear of the token after a failed publish (a second write that can itself fail); a usecase-level transaction spanning two repository calls (no such seam exists in the project, and it would be the only one).

### The Order's source comes from the entity, all three cases

`pb.FromOrder` sets exactly one of `checkout_id`, `lottery_entry_id` and `resale_entry_id`, from the one of `CheckoutID`, `LotteryEntryID` and `ResaleEntryID` that is set, as `Order.ValidateSource` already decides. The announcement consumers that decode the source (`analytics_consumer.go`, `entity.OrderPaidData`) read the third case too. Moving the choice into one entity method (`Order.Source()`) is left to `move-decisions-into-entities`; this change fixes the mapping with a table test over the three sources.

### AssociateArtist checks the status under the Organizer's row lock

`OrganizerRepository.AssociateArtist` already runs in a transaction (it records the announcement there). It first takes the Organizer's row with `SELECT status FROM organizers WHERE id = $1 FOR SHARE` and fails with FailedPrecondition when the status is Deactivated. `SetStatus` updates that row, so a Deactivate waits for the link to commit, or the link sees Deactivated. The usecase keeps its own early check: it gives the same answer without a write in the common case, and its spec still describes it.

### UpdateHome locks the User row first

`UserRepository.UpdateHome` reads the User with `FOR UPDATE` in its transaction, so a second concurrent call waits and then sees the Home the first one stored. No migration: an unreferenced Home row left by an earlier race is harmless, and the read-only check in the Migration Plan counts them.

### Upcoming concerts are their own operation

`Concert.ListUpcomingByArtist(ctx, artistID)` is added and `ListByArtist` loses its flag; its three callers (`concertUseCase.ListByArtist`, `SearchNewConcerts`, `ticketSaleDiscoveryUseCase.DiscoverForArtist`) call the one they mean. The SQL keeps its two queries. Which day "the current date" is stays as today; see Open Questions.

### Optional personal details are pointers

`User.FullName` and `User.PhoneNumber` become `*string`, and `UserRepository.UpdatePersonalDetails` takes `*string` for each. The rdb layer maps nil to NULL and NULL to nil. `adapter/pb` and the usecases that read the two fields check nil instead of `""`. The time zone is left out: no spec names it (see Open Questions).

## Risks / Trade-offs

- [Production already holds two Users whose emails differ only in letter case] → The migration's `CREATE UNIQUE INDEX` fails and the Atlas Operator stops. Mitigation: before writing the migration, run a read-only query through the cloud-provisioning runbook `docs/runbooks/cloud-sql-access.md` (`db-proxy`, personal IAM login): `SELECT count(*) FROM (SELECT lower(email) FROM users GROUP BY 1 HAVING count(*) > 1) d`, which returns only the number of duplicated addresses and never prints one. Report only that count (the specification repository is public). If any pair exists, stop and ask the user how to merge or remove the duplicates; the migration ships only on a clean result.
- [Building the unique index locks `users` against writes while it builds] → The table is small (the product has no users beyond the owner and one tester). A plain `CREATE UNIQUE INDEX` is used; `CONCURRENTLY` is not needed at this size.
- [Changing `PublishEvents`' signature touches every caller and mock] → It has one production caller (`seriesUseCase.Publish`); `make mocks` regenerates the mock.

## Migration Plan

1. Run the read-only duplicate check in production and record the count in the PR.
2. Update `schema.sql` and generate the migration with `atlas migrate diff --env local` (the `db-migration-workflow` skill). The migration drops the column's unique constraint, drops `idx_users_email` and `idx_users_email_lower`, and creates `uq_users_email_lower`.
3. Deploy through the Atlas Operator; confirm the AtlasMigration status in production read-only.

4. Read-only, through the same runbook: `SELECT count(*) FROM homes h WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.home_id = h.id)`, to record how many unreferenced Homes an earlier race left. Report only the count.

Rollback: a new forward migration restores `UNIQUE (email)` and the two plain indexes; the share-token change has no data to roll back.

## Open Questions

None that change this plan. The behaviours below are left open by the specs; the code keeps them as they are, and each is reported to the user for a separate decision.

- `Order.CommitRefund` on an Order that is Pending or Void, or on an id with no Order: it changes nothing and returns success. The spec covers only an Order already Refunded.
- `Series.CreateDraft` with an id an existing Series already has: the Series row is not inserted (`ON CONFLICT (id) DO NOTHING`) and the DRAFT Events are added to the existing Series. The spec does not cover a taken id.
- `ResaleEntry.Create` for an Event whose start time is unknown: it fails with FailedPrecondition because no resale deadline can be computed. The spec does not say whether such an Event has resale at all.

The re-audit added these:

- **Which day is "the current date".** `Concert.Search` leaves out events dated before the search date, and `Concert.ListByArtist` with upcoming only (after this change, `Concert.ListUpcomingByArtist`) keeps Concerts dated on or after the current date. Neither spec names a time zone. The code cuts the day at UTC midnight: the searcher truncates the search time with `Truncate(24 * time.Hour)` (`searcher.go:911`), and the upcoming query uses the database's `CURRENT_DATE`. Between 00:00 and 09:00 Japan time, a concert of the previous Japanese day still counts as upcoming. `ticket-sale/discover-for-artist` already counts days in Japan time. Recommended: state Japan time in both specs and use `entity.JapanDate`.
- **What a not-yet-announced venue is.** The specs keep a venue name as the source wrote it (`entity/concert/search`) and drop only a blank one (`entity/discovered-series/filter-new-series`). The searcher's repeat-removal key also maps "TBA", "未定", "某所" and similar markers to empty, lower-cases, strips a prefecture in parentheses, and maps "日本ガイシ" and "クロコくん" to one name; none of these is in the spec's list of notation differences. An event whose venue is "TBA" is therefore kept, and creating a Concert from it makes a Venue named "TBA". The two normalizations also differ: Search removes whitespace, the Venue spec collapses it to one space. Recommended: decide whether an unannounced venue is dropped at Search, and whether the two normalizations should be one.
- **The analytics source of a resale Order.** After the mapping fix, the "order paid" signal can tell a resale Order apart, but no spec names the signal's properties; the analytics consumer records `lottery_entry` or `checkout` only.
- **The User's time zone.** `users.time_zone` and `User.TimeZone` exist, but no spec names a time zone attribute of a User. AGENTS.md treats a column no spec uses as a violation. Recommended: decide whether to specify it or remove it.
