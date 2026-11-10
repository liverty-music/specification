## Why

An audit of the backend found interface doc comments that no longer describe what their implementations do, and two places where the code breaks a rule the specs already state. A caller who trusts a stale comment writes the wrong code: the Go doc of `ConcertRepository.Create` names a natural key the database does not use, and `ArtistRepository.UpdateFanart` claims that passing no fanart keeps the old images, while it removes them as the spec requires. The spec violations reach users: two accounts can hold the same email address in different letter case, after which the account recovery lookup fails with Internal, and a failed share-token write during Publish leaves an UNLISTED concert published without a share link and with no way to recover by publishing again.

## What Changes

- Make one email address belong to at most one User when letter case is ignored. Create rejects an address that differs from a stored one only in letter case with AlreadyExists, and the database enforces it with a unique index on the lower-cased address. Existing production rows are checked read-only for such pairs before the migration runs.
- Give an UNLISTED Series its share token in the same transaction as the publish of its first Events. `Series.PublishEvents` takes the new token and stores it together with the publish, so a failure stores neither and a repeated Publish succeeds.
- Rewrite the Go doc comments of ports whose implementations do more or other than the comment says, with the specs as the reference:
  - `ConcertRepository`: the natural key and merge rule of `Create`; the fan-visibility filter of `ListByArtist`, `ListByArtists`, `ListByFollower` and `ListByLocation`; the rule that every Concert operation treats a DRAFT Event's id as matching no Concert (`ListEventsBySeries`, `FillEventStartTimes`, `FindEvents*`, `Delete`).
  - `ArtistRepository.UpdateFanart`: no fanart removes the earlier images.
  - `ConcertUseCase.ListByArtist` and `ListFollowed`: an unknown Artist or User gives an empty result, not NotFound.
  - `OrderUseCase.Refund`: the amount refunded for a cancellation is the price of the Tickets still Issued; the processor-fee wording is replaced.
  - `# Possible errors` of the 16 announcing repository methods that omit Unavailable, and of the methods that return InvalidArgument without listing it.
- Add the scenarios the specs lack for the two behaviour fixes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/user` (Purpose): the email attribute row states that no two Users share an address when letter case is ignored.
- `components/entity/user/create`: Create rejects an email that matches a stored one when letter case is ignored.
- `components/entity/series/publish-events`: PublishEvents stores the share token of an UNLISTED Series together with the publish.
- `components/usecase/series/publish`: Publish gives the share token through `Series.PublishEvents`, so a failure publishes nothing. `components/entity/series/set-unlisted-token` is unchanged: RegenerateShareUrl still uses it to rotate a token.

The doc-comment rewrites change no spec: in each case the spec already states the behaviour the code has.

## Impact

- backend: `internal/entity` port doc comments (concert, artist, series, user, checkout, follow, lottery_entry, order, organizer, passkey, push_subscription, resale_listing, ticket, ticket_sale), `internal/usecase` doc comments (concert_uc, order_uc), `SeriesRepository.PublishEvents` signature and its rdb implementation, `seriesUseCase.Publish`, `UserRepository.Create` error mapping, `schema.sql` and one Atlas migration for the email index.
- Production data: a read-only query on `users` before the migration; the migration fails if two rows already share an address in different letter case, so such rows must be resolved first.
- No proto or frontend change.
