## Why

The daily image run re-checks every registered artist whose images are older than 7 days, and it cannot keep up. Prod on 2026-10-29: 5,137 artists, 1,301 of them past the 7-day age, the oldest check 10 days old; the run has stopped at its 500-artist limit every day for the last 30 days. Only 144 artists (3%) are followed by a fan, which are the artists fans see again and again; the others were registered by a search, a chart or a similar-artist lookup and are rarely shown again. Re-checking them costs one image catalog lookup, a logo download and a write each, and it accounts for about 1,100 of the backend's spans every day.

## What Changes

- The daily image run re-checks an artist's images only while at least one fan follows the artist, as the official site check already does (`components/entity/artist/list-stale-official-site`).
- An artist that is never checked is still checked by the daily run, whoever registered it. After that, an artist nobody follows keeps the images of its last check.
- An artist that a fan follows later is re-checked by the next daily run once its last check is more than 7 days old.
- The 500-artist limit, the 7-day age and the order (never checked first, then oldest check first) stay.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/entity/artist/list-stale-or-missing-fanart`: an artist past the age is returned only when a fan follows it; a never-checked artist is returned either way. Its Purpose is edited in the main spec by archive task 4.1.
- `stories/discover-artists`: "Artist images are kept current" applies to followed artists.
- `components/usecase/artist/sync-artist-image` (Purpose, edited in the main spec by archive task 4.2): the daily run is for never-checked artists and followed artists last checked more than 7 days ago. Its requirement "SyncArtistImage runs daily for due artists" is unchanged: it takes the due artists from Artist.ListStaleOrMissingFanart and states no rule of its own about which artists are due. Both Purposes are edited at archive, not before, so the main specs do not describe behavior that has not shipped.

`components/entity/artist` keeps its attributes; follows are read, not changed.

## Impact

- backend: `listStaleOrMissingFanartQuery` and the doc comment of `ArtistRepository.ListStaleOrMissingFanart` in `internal/infrastructure/database/rdb/artist_repo.go`, the doc comment of `ListStaleOrMissingFanart` in `internal/entity/artist.go`, the contract test in `artist_repo_test.go`, and a new story test.
- No proto, frontend or cloud-provisioning change. No migration.
- At today's data the daily run checks about 21 artists a day (144 followed artists every 7 days) instead of 500, plus any never-checked artist (none today).
