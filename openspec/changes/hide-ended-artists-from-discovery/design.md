## Context

- The Discovery bubbles are filled from `ArtistService.ListTop` and `ArtistService.ListSimilar`. The backend usecases (`backend/internal/usecase/artist_uc.go`) take the Last.fm chart or similar-artist list, register each artist by MBID and cache the result in process memory for 6 hours. Last.fm returns only a name and an MBID; it has no notion of an artist's activity.
- MusicBrainz, already used for canonical names and official sites, returns `life-span: {begin, end, ended}` on every artist lookup (`/ws/2/artist/<mbid>?fmt=json`). Checked on 2026-11-09: SMAP, チャットモンチー, BiSH, 嵐, The Beatles and Michael Jackson have `ended: true`; ELLEGARDEN and 東京事変, which re-formed, have `ended: null`; Queen has `ended: true` with no end date. MusicBrainz has no field for a hiatus.
- MusicBrainz allows about 1 request per second; the client throttles to that (`musicbrainz/client.go`, `rateLimitInterval`). Looking 50 chart artists up during a ListTop call would take about 50 seconds, so the status must be stored ahead of time.
- The bubble field never shows an artist the fan follows (`frontend/src/services/artist-bubble-store.ts`), and it tops itself up with more chart artists when a fetch leaves it short.
- The number of registered artists in prod is not known: on 2026-11-09 the read-only prod login of the `cloud-sql-access.md` runbook was refused because the developer's Cloud SQL IAM user is missing, so the count could not be read.

## Goals / Non-Goals

**Goals:**
- Store one fact per artist, whether MusicBrainz marks its activity as ended, with no other new column.
- Keep it current for every registered artist, followed or not, with no state beyond that fact.

**Non-Goals:**
- Hiatus. MusicBrainz cannot express it, and "no upcoming concerts" would also hide active artists whose concerts we have not found.
- Hiding ended artists anywhere other than ListTop and ListSimilar (name search, My Artists, concert pages).
- Checking a new artist at the moment it is registered (see Decision 3).

## Decisions

### 1. One column, `artists.activity_ended BOOLEAN NOT NULL DEFAULT false`

`false` covers both "not ended" and "not checked yet"; both mean "suggest it", so no third state is needed. A positive name (`active`, `is_activated`) was rejected: it would claim that unchecked artists and artists on hiatus are active, and "active" already means "currently valid" elsewhere in the backend (an active Organizer, an active IdentityVerification). A begin/end date was rejected: nothing reads it, and some ended records (Queen) have no end date. Adding a `NOT NULL` column with a constant default is a metadata-only change in PostgreSQL 18, so the migration does not rewrite the table.

`entity.Artist` gets `ActivityEnded bool`. `ArtistRepository` gets `UpdateActivityEnded(ctx, id, ended)` and `ListActivityCheckDue(ctx, slots, slot, since)`; the existing scan of an artist row reads the new column, so `ListByMBIDs` returns it without a signature change.

### 2. A stateless 30-day rotation instead of a check time

Each daily run checks `slot = (days since 1970-01-01 in Asia/Tokyo) mod 30`. An artist's slot is derived from its UUID's two last bytes, which UUIDv7 fills with random bits: `((get_byte(uuid_send(id), 14) << 8) | get_byte(uuid_send(id), 15)) % 30`. Every artist is checked once every 30 days, and the first 30 runs fill in the artists registered before this change.

Alternatives:
- An `activity_checked_at` column, selected oldest-first like `official_site_checked_at`. It retries a failed artist the next day and fills the backlog in fewer days, at the cost of a second column; the user chose not to add one.
- A check time kept in Redis (Memorystore). The project runs no Redis today, so this adds a paid managed service, its connection settings and its failure handling for one timestamp, while `activity_ended` must still live in Postgres for the ListTop filter. Rejected.
- `hashtext(id::text)`. It is an internal PostgreSQL function whose output is not guaranteed across major versions, so the slots could move on an upgrade; the UUID bytes cannot. Rejected.

### 3. New artists are checked by the next daily run, not on registration

`ListActivityCheckDue` also returns artists registered after `run start - 25h`, read from the UUIDv7 timestamp with `uuid_extract_timestamp(id)` (PostgreSQL 17+; prod runs `POSTGRES_18`, `cloud-provisioning/src/gcp/components/postgres.ts`). The extra hour covers a run that starts late. An ended artist newly registered by a discovery call can therefore appear for at most a day.

Alternatives:
- Read `life-span` in the `resolve-artist-name` consumer, which already calls `GetArtist` on `ARTIST.created`. No extra request, but `ArtistNameResolutionUseCase.ResolveCanonicalName` would then also write activity status. Renaming it to match is not cheap: the JetStream durable is a NACK resource named `resolve-artist-name` in cloud-provisioning, and this repository keeps durable names when a meaning changes (`backend/internal/entity/event_data.go`, comment on `SubjectArtistHypeChanged`). Rejected to keep each usecase doing what its name says.
- A second `ARTIST.created` durable, `resolve-artist-activity`. Correct naming, checked within seconds, but it adds a NACK Consumer, a KEDA trigger and one more MusicBrainz request per new artist on the consumer's shared 1-per-second throttle, slowing name resolution. Rejected: the gain is under a day of delay on a product that has no users yet.
- Piggybacking on the daily official-site refresh. It only covers followed artists and the rotation already covers them. Not needed.

### 4. The filter re-reads the flag on every call

`ListTop` and `ListSimilar` keep caching the registered list for 6 hours, unchanged. After taking the list from the cache or from Last.fm, each call runs `ListByMBIDs` on its MBIDs and drops the artists with `ActivityEnded`. This is one indexed query of at most 50 MBIDs per call. Filtering before caching was rejected: a newly registered artist enters the cache with `false`, and the daily run's result would then wait for the cache to expire (up to 6 hours, per process). `ListSimilar` filters before `firstN`, so a limit of 10 still returns 10 when enough remain.

`ListTop` does not ask Last.fm for extra artists to make up for the dropped ones; the bubble field tops up by itself (Context). In the Japan chart on 2026-11-09, 3 of 50 artists would be dropped.

### 5. `GetArtist` returns the status; no new catalog operation

The MusicBrainz response is already decoded in `GetArtist`; `artistResponse` gets `LifeSpan struct { Ended *bool }` and `GetArtist` returns it on `entity.Artist.ActivityEnded` (`nil` and `false` both map to false). `ArtistIdentityManager.GetArtist` keeps its signature. A separate `GetActivity` method would issue the same HTTP request.

### 6. A new job binary `artist-activity-refresh`

`cmd/job/artist-activity-refresh` mirrors `cmd/job/official-site-refresh`: build the usecase, run `RefreshDueActivity` once, exit non-zero on a circuit break. The usecase interface `ArtistActivityRefreshUseCase` has `RefreshActivity(ctx, artistID, mbid)` and `RefreshDueActivity(ctx) (Summary, error)`, the same split as `OfficialSiteRefreshUseCase`. The run logs one summary line (slot, listed, attempted, ended count, failed, circuit broken).

The CronJob runs at `0 20 * * *` (05:00 JST), an hour after `official-site-refresh` (04:00 JST), so the two MusicBrainz callers do not share the rate limit from the same cluster egress. `concurrencyPolicy: Forbid`, `backoffLimit: 0` and `ttlSecondsAfterFinished: 86400` as in `official-site-refresh`.

Folding the rotation into the `official-site-refresh` binary was rejected: it would mix two unrelated refreshes in one job and its name.

## Risks / Trade-offs

- [A MusicBrainz record is wrong, e.g. Queen is `ended: true` while Queen + Adam Lambert tours] → Accepted by the user: the catalog is the source. A wrong record can be fixed upstream in MusicBrainz and is picked up within 30 days.
- [A failed artist waits 30 days for its next check] → The run stops after 3 consecutive failures, so a MusicBrainz outage does not burn through a slot; isolated failures (a busy 503 after the client's retries) wait one cycle. Acceptable for a fact that changes rarely.
- [Run length grows with the catalog] → One run takes about (artists / 30 + artists registered per day) seconds. The count is unknown (Context); at 30,000 artists that is about 17 minutes plus new artists. The summary log shows the listed count; revisit the slot count if a run approaches an hour.
- [An ended artist registered today is suggested until tomorrow's run] → Decision 3; at most one day.
- [The first 30 days only partly cover existing artists] → Accepted: the product has no users yet.
- [The flag and the 6-hour cache disagree] → Decision 4 re-reads the flag on every call.

## Migration Plan

1. backend: Atlas migration adding the column (from `schema.sql`, `atlas migrate diff`), entity field, repository methods, MusicBrainz `life-span` decoding, the ListTop/ListSimilar filter, the new usecase and job binary, and the bake target. Merge; the AtlasMigration applies the column in prod before the new image rolls out, and the old image ignores the column.
2. cloud-provisioning: CronJob, ConfigMap and kustomization entries in base and both overlays, prod image override, and `artist-activity-refresh` in the image list of `.github/workflows/bump-prod-pin.yml`. Merge after the backend image exists in the registry.
3. Verify in prod read-only: the AtlasMigration status shows the new version; the first run's log shows its slot and counts; the next day, ListTop for Japan no longer returns an artist whose `activity_ended` was set (when the run reached one).

Rollback: suspend the CronJob; the column defaults to false, which shows every artist as before. Reverting the backend filter needs no data change.
