## Why

The Discovery bubbles suggest artists from the music catalog's popular and similar-artist charts, and those charts include groups that have dissolved and solo artists who have died (in the Japan chart on 2026-11-09: Queen, The Beatles and Michael Jackson). Liverty Music exists to bring fans to live shows, so suggesting an artist who will never perform again wastes a bubble and teaches the fan nothing useful.

## What Changes

- An Artist gets a new attribute, `activity_ended`: true when the music catalog marks the artist's activity as ended (a group dissolved, a solo artist died), false otherwise or when not yet checked.
- `ArtistUseCase.ListTop` and `ArtistUseCase.ListSimilar` drop artists whose activity has ended. The check reads the current value on every call, also when the result itself is reused from the last 6 hours, so an artist marked later disappears from the next call.
- A new daily run, `ArtistActivityRefreshUseCase.RefreshActivity`, asks the catalog for each artist's activity status and records it. Each day it checks the artists registered in the last 25 hours and one thirtieth of all artists, chosen by their id, so every registered artist is checked once every 30 days without storing a check time. The first 30 days of runs fill in the artists registered before this change.
- `ArtistUseCase.Search` is unchanged: a fan who types a name still finds the artist, ended or not.
- Out of scope: hiatus (活動休止). The catalog only records that an activity ended, not that it paused; an artist on hiatus stays suggested.

## Capabilities

### New Capabilities
- `components/usecase/artist/refresh-activity`: checks and records an artist's activity status from the catalog, and the daily run that picks which artists to check.
- `components/entity/artist/update-activity-ended`: stores whether an artist's activity has ended.
- `components/entity/artist/list-activity-check-due`: lists the artists a daily run checks: one rotation slot of all artists plus the recently registered ones.

### Modified Capabilities
- `components/entity/artist` (Purpose): adds the `activity_ended` attribute to the attribute table. Its requirement "A new artist starts without images" changes so that a new artist also starts with `activity_ended` false.
- `components/entity/artist/get-artist`: GetArtist also returns whether the catalog marks the artist's activity as ended.
- `components/usecase/artist/list-top`: drops artists whose activity has ended, on every call.
- `components/usecase/artist/list-similar`: drops artists whose activity has ended before cutting the result to the requested limit, on every call.
- `stories/discover-artists` (Purpose and requirements): the usecase diagram adds `ArtistActivityRefreshUseCase.RefreshActivity`; a new requirement states that charts and similar artists do not suggest artists whose activity has ended, while a name search still finds them.

Entity operations the modified usecases rely on and that stay unchanged: `Artist.ListTop`, `Artist.ListSimilar` (catalog lookups, unchanged: the catalog does not filter), `Artist.FilterArtistsByMBID`, `Artist.Create` and `Artist.Get` (unchanged), and `Artist.ListByMBIDs` (its promise does not change; the artists it returns now carry `activity_ended` as an attribute of the entity).

## Impact

- backend: `artists` table gets one column; the MusicBrainz client reads `life-span.ended`; ListTop and ListSimilar re-read the activity flag before returning; a new usecase and a new job binary `artist-activity-refresh`.
- cloud-provisioning: a new CronJob, its ConfigMap, the prod image override and the prod image pin list, following `official-site-refresh`.
- frontend: no change. The bubble field already tops itself up when a fetch returns fewer artists.
- MusicBrainz traffic: about one request per second for (artists / 30 + new artists per day) seconds once a day, at an hour the other MusicBrainz jobs do not use.
