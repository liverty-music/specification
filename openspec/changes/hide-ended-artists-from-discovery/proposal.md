## Why

The Discovery bubbles suggest artists from the music catalog's popular and similar-artist charts, and those charts include groups that have dissolved and solo artists who have died (in the Japan chart on 2026-11-09: Queen, The Beatles and Michael Jackson). Liverty Music exists to bring fans to live shows, so suggesting an artist who will never perform again wastes a bubble, and searching such an artist's concerts and ticket sales with the external grounded search costs money for nothing.

## What Changes

- An Artist gets a new attribute, `activity_ended`: true when the music catalog marks the artist's activity as ended (a group dissolved, a solo artist died), false otherwise or when not yet read.
- `ArtistUseCase.Refresh` replaces `ArtistNameResolutionUseCase.ResolveCanonicalName`. From one catalog lookup it adopts the canonical name, as before, and records `activity_ended`. It runs on the artist-created announcement, as the name resolution did, and once a day for one thirtieth of all artists, chosen by their id, so every artist is read again every 30 days without storing a check time. **BREAKING** (internal): the usecase, its spec and the event consumer are renamed; a catalog NotFound now succeeds instead of being retried.
- `ArtistUseCase.ListTop` and `ArtistUseCase.ListSimilar` leave out artists whose activity has ended, also when they reuse a result from the last 6 hours.
- `ConcertUseCase.SearchNewConcerts` and `TicketSaleDiscoveryUseCase.DiscoverForArtist` do not search artists whose activity has ended.
- `ArtistUseCase.Search` is unchanged: a fan who types a name still finds the artist, ended or not.
- Out of scope: hiatus (活動休止). The catalog only records that an activity ended, not that it paused; an artist on hiatus stays suggested and searched.

## Capabilities

### New Capabilities
- `components/usecase/artist/refresh`: reads an artist again from the catalog (name and activity status), on registration and in a daily 30-day rotation.
- `components/entity/artist/update-activity-ended`: stores whether an artist's activity has ended.
- `components/entity/artist/list-refresh-due`: lists one rotation slot of all artists for the daily run.

### Modified Capabilities
- `components/entity/artist` (Purpose): adds the `activity_ended` attribute to the attribute table. Its requirement "A new artist starts without images" changes so that a new artist also starts with `activity_ended` false.
- `components/entity/artist/get-artist` (and its Purpose): GetArtist also returns whether the catalog marks the artist's activity as ended.
- `components/usecase/artist/resolve-canonical-name`: every requirement is removed and the capability is retired (`retire_capabilities: true`); its rules move to `components/usecase/artist/refresh`.
- `components/usecase/artist/list-top`: leaves out artists whose activity has ended.
- `components/usecase/artist/list-similar`: leaves out artists whose activity has ended before cutting the result to the requested limit.
- `components/usecase/concert/search-new-concerts`: does not search artists whose activity has ended.
- `components/usecase/ticket-sale/discover-for-artist`: does not search artists whose activity has ended.
- `components/entity/follow/list-all`: also returns each followed artist's `activity_ended`, which DiscoverForArtist reads.
- `stories/discover-artists` (Purpose and requirements): the usecase diagram adds `ArtistUseCase.Refresh` now and drops `ArtistNameResolutionUseCase.ResolveCanonicalName` at archive, once the modified requirement no longer names it (`scripts/check-story-diagrams.py` checks main specs only); the enrichment requirement names Refresh; a new requirement states that charts and similar artists do not suggest artists whose activity has ended, while a name search still finds them.

Entity operations the modified usecases rely on and that stay unchanged: `Artist.ListTop`, `Artist.ListSimilar` (catalog lookups; the catalog does not filter), `Artist.FilterArtistsByMBID`, `Artist.Create`, `Artist.Get` (SearchNewConcerts now reads the artist with it), `Artist.UpdateName` and `Artist.ListByMBIDs` (their promises do not change; the artists they return now carry `activity_ended` as an attribute of the entity).

## Impact

- backend: `artists` gets one column; the MusicBrainz client reads `life-span.ended`; `ArtistNameResolutionUseCase` is folded into `ArtistUseCase.Refresh`; ListTop, ListSimilar, SearchNewConcerts and DiscoverForArtist skip ended artists; a new job binary `artist-refresh`.
- cloud-provisioning: the JetStream durable `resolve-artist-name` is replaced by `refresh-artist` (Consumer resource and KEDA trigger); a new CronJob `artist-refresh` with its ConfigMap, prod image override and an entry in the prod image pin list. The old durable is deleted from the NATS server once by hand.
- frontend: no change. The bubble field already tops itself up when a fetch returns fewer artists.
- MusicBrainz traffic: unchanged per new artist (still one lookup); plus about 175 lookups (about 3 minutes) once a day for the 5,261 artists registered on 2026-11-09.
- External grounded search: no more daily concert and ticket-sale searches for followed artists whose activity has ended.
