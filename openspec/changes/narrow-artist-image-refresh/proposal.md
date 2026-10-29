## Why

The daily image run re-checks every registered artist whose images are older than 7 days, and it cannot keep up. Prod on 2026-10-29: 5,137 artists, 1,301 of them past the 7-day age, the oldest check 10 days old; the run has stopped at its 500-artist limit every day for the last 30 days. Only 164 artists (3%) are followed by a fan or perform in a concert, which are the artists fans see again and again; the other 4,973 were registered by a search, a chart or a similar-artist lookup and are rarely shown again. Re-checking them costs one image catalog lookup, a logo download and a write each, and it accounts for about 1,100 of the backend's spans every day.

## What Changes

- The daily image run re-checks an artist's images only while at least one fan follows the artist or the artist performs in a concert.
- An artist that is never checked is still checked by the daily run, whoever registered it. After that, an artist nobody follows and with no concert keeps the images of its first check.
- An artist that a fan follows later, or that gets a concert later, is re-checked by the next daily run once its last check is more than 7 days old.
- The 500-artist limit, the 7-day age and the order (never checked first, then oldest check first) stay.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/artist/list-stale-or-missing-fanart`: an artist past the age is returned only when a fan follows it or it performs in a concert; a never-checked artist is returned either way.
- `stories/discover-artists`: "Artist images are kept current" applies to followed and performing artists.

Unchanged and why: `components/usecase/artist/sync-artist-image` ("SyncArtistImage runs daily for due artists") names Artist.ListStaleOrMissingFanart as the source of due artists and states no rule of its own about which artists are due, so the narrowing is the operation's. `components/entity/artist` keeps its attributes; follows and concerts are read, not changed.

## Impact

- backend: `listStaleOrMissingFanartQuery` in `internal/infrastructure/database/rdb/artist_repo.go`, its contract test, and the doc comment of `ListStaleOrMissingFanart` in `internal/entity/artist.go`.
- No proto, frontend or cloud-provisioning change. No migration.
- At today's data the daily run checks about 24 artists a day instead of 500, after the backlog of never-checked artists (none today) is cleared.
