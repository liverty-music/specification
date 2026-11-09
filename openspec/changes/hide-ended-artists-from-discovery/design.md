## Context

- The Discovery bubbles are filled from `ArtistService.ListTop` and `ArtistService.ListSimilar`. The backend usecases (`backend/internal/usecase/artist_uc.go`) take the Last.fm chart or similar-artist list, register each artist by MBID (`persistArtists`: `ListByMBIDs`, then `Create` for the missing ones) and cache the registered list in process memory for 6 hours. Last.fm returns only a name and an MBID; it has no notion of an artist's activity.
- MusicBrainz, already used for canonical names and official sites, returns `life-span: {begin, end, ended}` on every artist lookup (`/ws/2/artist/<mbid>?fmt=json`). Checked on 2026-11-09: SMAP, チャットモンチー, BiSH, 嵐, The Beatles and Michael Jackson have `ended: true`; ELLEGARDEN and 東京事変, which re-formed, have `ended: null`; Queen has `ended: true` with no end date. MusicBrainz has no field for a hiatus.
- MusicBrainz allows about 1 request per second; the client throttles to that (`musicbrainz/client.go`, `rateLimitInterval`). Looking 50 chart artists up during a ListTop call would take about 50 seconds, so the status must be stored ahead of time.
- On `ARTIST.created`, the durable `resolve-artist-name` runs `ArtistNameResolutionUseCase.ResolveCanonicalName`, which already calls `GetArtist` (`artist_name_resolution_uc.go`) and discards everything but the name.
- Prod had 5,261 registered artists on 2026-11-09 (read-only query through the `cloud-sql-access.md` runbook).
- The bubble field never shows an artist the fan follows (`frontend/src/services/artist-bubble-store.ts`), and it tops itself up with more chart artists when a fetch leaves it short.
- The concert-discovery and sales-phase-discovery jobs run a Gemini grounded search for every followed artist (`cmd/job/concert-discovery`, `cmd/job/sales-phase-discovery`).

## Goals / Non-Goals

**Goals:**
- Store one fact per artist, whether MusicBrainz marks its activity as ended, with no other new column.
- Keep it current for every registered artist, followed or not, with no state beyond that fact and no extra MusicBrainz request per new artist.

**Non-Goals:**
- Hiatus. MusicBrainz cannot express it, and "no upcoming concerts" would also hide active artists whose concerts we have not found.
- Hiding ended artists from name search, My Artists or concert pages.

## Decisions

### 1. One column, `artists.activity_ended BOOLEAN NOT NULL DEFAULT false`

`false` covers both "not ended" and "not read yet"; both mean "suggest it", so no third state is needed. A positive name (`active`, `is_activated`) was rejected: it would claim that unread artists and artists on hiatus are active, and "active" already means "currently valid" elsewhere in the backend (an active Organizer, an active IdentityVerification). A begin/end date was rejected: nothing reads it, and some ended records (Queen) have no end date. Adding a `NOT NULL` column with a constant default is a metadata-only change in PostgreSQL 18 (prod runs `POSTGRES_18`, `cloud-provisioning/src/gcp/components/postgres.ts`), so the migration does not rewrite the table.

`entity.Artist` gets `ActivityEnded bool`. `ArtistRepository` gets `UpdateActivityEnded(ctx, id, ended)` and `ListRefreshDue(ctx, slots, slot)`; the shared artist-row scan (`scanArtist`) reads the new column, so `ListByMBIDs` and `Get` return it without a signature change. `FollowRepository.ListAll` has its own query (`followListAllQuery`, id, name and MBID only) and its own scan; both get `a.activity_ended`.

### 2. `ArtistUseCase.Refresh` replaces `ArtistNameResolutionUseCase`

One MusicBrainz lookup serves both the name and the activity status, so one usecase method adopts both. It is a method of `ArtistUseCase`, the entity's usecase, rather than a new role-named interface; `ArtistNameResolutionUseCase` and its file are removed. Its spec moves from `components/usecase/artist/resolve-canonical-name` (retired with `retire_capabilities: true`; `openspec archive` refuses to empty a spec without it, checked on a scratch copy) to `components/usecase/artist/refresh`. A catalog `NotFound` now succeeds without a change: retrying it 3 times, as the announcement consumer does today, cannot succeed.

The durable is renamed from `resolve-artist-name` to `refresh-artist` so the event name says what runs. The ARTIST stream uses `retention: limits` (`k8s/namespaces/nats/base/jetstream/stream-artist.yaml`), so a durable left behind does not hold messages back; it is removed by hand because the Consumer resource has `preventDelete: true`. An announcement made while neither durable is bound is not refreshed on registration; the 30-day rotation (Decision 3) refreshes it later.

Alternatives:
- Keep `ResolveCanonicalName` and add the activity write to it. Rejected: the name would no longer say what the method does.
- A second `ARTIST.created` durable for the activity alone. Rejected: one more MusicBrainz request per new artist on the consumer's shared 1-per-second throttle, plus a Consumer resource and a KEDA trigger, for no behaviour the merged method lacks.
- Keep the durable name, as `SubjectArtistHypeChanged` does (`backend/internal/entity/event_data.go`). Rejected here: the product has no users yet, the stream retention makes the switch harmless, and a misnamed durable stays misleading in every log line and KEDA trigger.

### 3. A stateless 30-day rotation instead of a check time

The daily run refreshes `slot = (days since 1970-01-01 in Asia/Tokyo) mod 30`. An artist's slot is derived from its UUID's two last bytes, which UUIDv7 fills with random bits: `((get_byte(uuid_send(id), 14) << 8) | get_byte(uuid_send(id), 15)) % 30`. Every artist is read once every 30 days; the first 30 runs fill in the artists registered before this change. With 5,261 artists a run reads about 175 (about 3 minutes at 1 request per second).

Alternatives:
- An `activity_checked_at` column, selected oldest-first like `official_site_checked_at`. It retries a failed artist the next day and fills the backlog sooner, at the cost of a second column; the user chose not to add one.
- A check time in Redis (Memorystore). The project runs no Redis, so this adds a paid managed service, its connection settings and its failure handling for one timestamp, while `activity_ended` must still live in Postgres for the ListTop filter. Rejected.
- `hashtext(id::text)`. An internal PostgreSQL function whose output is not guaranteed across major versions, so the slots could move on an upgrade; the UUID bytes cannot. Rejected.

### 4. The ListTop and ListSimilar filter reads the flag once per call

On a cache miss, `persistArtists` already calls `ListByMBIDs`; the registered artists it returns carry `ActivityEnded`, and the ones it creates are `false`. The filter uses that result, so a miss makes no extra query. On a cache hit, the cached list may be up to 6 hours old, so the call runs one `ListByMBIDs` on its MBIDs and filters on the result. Each call therefore makes exactly one `ListByMBIDs` query. Filtering before caching was rejected: a newly registered artist enters the cache with `false`, and the announcement's Refresh would then wait for the cache to expire (up to 6 hours, per process). `ListSimilar` filters before `firstN`, so a limit of 10 still returns 10 when enough remain.

`ListTop` does not ask Last.fm for extra artists to make up for the dropped ones; the bubble field tops up by itself (Context). In the Japan chart on 2026-11-09, 3 of 50 artists would be dropped.

### 5. `GetArtist` returns the status; no new catalog operation

`artistResponse` gets `LifeSpan struct { Ended *bool }` and `GetArtist` returns it on `entity.Artist.ActivityEnded` (`nil` and `false` both map to false). `ArtistIdentityManager.GetArtist` keeps its signature. A separate `GetActivity` method would issue the same HTTP request.

### 6. Searches skip ended artists inside the usecases

`ConcertUseCase.SearchNewConcerts` takes an artist id; it reads the artist with `artistRepo.Get` before the organizer-representation check and returns `nil, nil` when `ActivityEnded`, like the existing skips (no failure counted by the job's circuit breaker). `TicketSaleDiscoveryUseCase.DiscoverForArtist` receives the artist from `FollowRepository.ListAll`, which carries the flag after its query change (Decision 1), and returns `0, nil` first. The check sits in the usecases, not in the jobs' artist lists, so the first-follow search (`SearchNewConcertsOnFirstFollow`) is covered too.

### 7. A new job binary `artist-refresh`

`cmd/job/artist-refresh` mirrors `cmd/job/official-site-refresh`: build the usecase, run `ArtistUseCase.RefreshDue` once, exit non-zero on a circuit break. `RefreshDue(ctx) (ArtistRefreshSummary, error)` lists the slot with `ListRefreshDue` and calls `Refresh` for each artist, stopping after 3 consecutive failures or on shutdown; the run logs one summary line (slot, listed, attempted, ended count, renamed count, failed, circuit broken).

The CronJob runs at `0 20 * * *` (05:00 JST), an hour after `official-site-refresh` (04:00 JST), so the two MusicBrainz callers do not share the rate limit from the same cluster egress. `concurrencyPolicy: Forbid`, `backoffLimit: 0` and `ttlSecondsAfterFinished: 86400` as in `official-site-refresh`.

## Risks / Trade-offs

- [A MusicBrainz record is wrong, e.g. Queen is `ended: true` while Queen + Adam Lambert tours] → Accepted by the user: the catalog is the source. A record fixed upstream is picked up within 30 days.
- [A failed artist waits 30 days for its next read] → The run stops after 3 consecutive failures, so a MusicBrainz outage does not burn through a slot; isolated failures (a busy 503 after the client's retries) wait one cycle. Acceptable for facts that change rarely.
- [Run length grows with the catalog] → About artists / 30 seconds per run; 175 seconds today. The summary log shows the listed count; revisit the slot count if a run approaches an hour.
- [Announcements during the durable switch are not refreshed on registration] → They are refreshed by the rotation within 30 days; the product has no users yet.
- [The first 30 days only partly cover existing artists] → Accepted: the product has no users yet.
- [A followed artist marked ended stops getting concert and ticket-sale searches] → Intended. If the catalog later clears the end (a re-formation), the next rotation sets `activity_ended` false and the searches resume.

## Migration Plan

1. cloud-provisioning, first PR: add the Consumer `refresh-artist` (same spec as `resolve-artist-name`, `deliverPolicy: new`) and its KEDA trigger, keeping the old ones. Merge; both durables exist.
2. backend: migration, entity, repository, MusicBrainz decoding, `ArtistUseCase.Refresh` / `RefreshDue`, the consumer row renamed to `refresh-artist`, the filters and skips, the job binary and its bake target. Merge; the AtlasMigration applies the column before the new image rolls out, and the old image ignores the column.
3. cloud-provisioning, second PR, after the backend image is pinned in prod: remove the `resolve-artist-name` Consumer resource and KEDA trigger, add the `artist-refresh` CronJob, ConfigMap, overlays, prod image override and the entry in `.github/workflows/bump-prod-pin.yml`. Then delete the old durable from the NATS server by hand (one-time action; the resource has `preventDelete: true`).
4. Verify in prod read-only: AtlasMigration status shows the new version; the consumer logs show `refresh-artist` handling `ARTIST.created`; the first CronJob run logs its slot and counts without a circuit break.

Rollback: suspend the CronJob and point the consumer back at `resolve-artist-name` with the previous image; the column defaults to false, which shows and searches every artist as before.
