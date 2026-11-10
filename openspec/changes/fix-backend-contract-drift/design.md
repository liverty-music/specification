## Context

See proposal.md - Why. The audit compared every port doc comment in `backend/internal/entity` and the UseCase interfaces in `backend/internal/usecase` with their implementations and with the living specs. Each finding falls in one of three groups:

| Group | What is wrong | Fix |
|---|---|---|
| Stale doc comment | The spec and the code agree; the Go doc says something else or leaves the behaviour out | Rewrite the doc comment from the spec |
| Code breaks a spec | The spec states a rule the code does not keep | Change the code; add the missing scenario |
| Spec silent | Neither the spec nor the doc says what happens | Not in this change; listed under Open Questions |

Code that breaks a spec today:

- `users.email` is `TEXT UNIQUE`, which compares letter case. `UserRepository.GetByEmail` matches with `lower(email) = lower($1)` and already returns Internal when two rows match ("more than one user has the email when letter case is ignored"). `components/entity/user/get-by-email` and `components/entity/user/create` together mean one User per address with letter case ignored.
- `seriesUseCase.Publish` calls `SeriesRepository.PublishEvents` (its own transaction) and then `SeriesRepository.SetUnlistedToken` (a separate statement). The Series spec allows a share token only on a published UNLISTED Series, and the Publish spec says an UNLISTED publish leaves the Series with a share token. When the second call fails, the Series is published without a token, and a repeated Publish fails with FailedPrecondition because no DRAFT Event is left.

## Goals / Non-Goals

**Goals:**

- Every port doc comment in `internal/entity` and every UseCase interface comment touched here states what the implementation does, in the spec's terms, including every apperr code it returns under `# Possible errors`.
- The two spec violations are fixed and covered by tests annotated with the new scenarios.

**Non-Goals:**

- Moving rules between layers, splitting functions or changing test infrastructure: those belong to `restructure-backend-responsibilities` and `speed-up-and-fill-backend-tests`. This change edits only comments and the two behaviours, so it can merge before them and they rebase on correct comments.
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

## Risks / Trade-offs

- [Production already holds two Users whose emails differ only in letter case] → The migration's `CREATE UNIQUE INDEX` fails and the Atlas Operator stops. Mitigation: before writing the migration, run a read-only query through the cloud-provisioning runbook `docs/runbooks/cloud-sql-access.md` (`db-proxy`, personal IAM login): `SELECT count(*) FROM (SELECT lower(email) FROM users GROUP BY 1 HAVING count(*) > 1) d`, which returns only the number of duplicated addresses and never prints one. Report only that count (the specification repository is public). If any pair exists, stop and ask the user how to merge or remove the duplicates; the migration ships only on a clean result.
- [Building the unique index locks `users` against writes while it builds] → The table is small (the product has no users beyond the owner and one tester). A plain `CREATE UNIQUE INDEX` is used; `CONCURRENTLY` is not needed at this size.
- [Changing `PublishEvents`' signature touches every caller and mock] → It has one production caller (`seriesUseCase.Publish`); `make mocks` regenerates the mock.

## Migration Plan

1. Run the read-only duplicate check in production and record the count in the PR.
2. Update `schema.sql` and generate the migration with `atlas migrate diff --env local` (the `db-migration-workflow` skill). The migration drops the column's unique constraint, drops `idx_users_email` and `idx_users_email_lower`, and creates `uq_users_email_lower`.
3. Deploy through the Atlas Operator; confirm the AtlasMigration status in production read-only.

Rollback: a new forward migration restores `UNIQUE (email)` and the two plain indexes; the share-token change has no data to roll back.

## Open Questions

None that change this plan. Three behaviours the specs leave open are kept as they are and reported to the user for a separate decision:

- `Order.CommitRefund` on an Order that is Pending or Void, or on an id with no Order: it changes nothing and returns success. The spec covers only an Order already Refunded.
- `Series.CreateDraft` with an id an existing Series already has: the Series row is not inserted (`ON CONFLICT (id) DO NOTHING`) and the DRAFT Events are added to the existing Series. The spec does not cover a taken id.
- `ResaleEntry.Create` for an Event whose start time is unknown: it fails with FailedPrecondition because no resale deadline can be computed. The spec does not say whether such an Event has resale at all.
