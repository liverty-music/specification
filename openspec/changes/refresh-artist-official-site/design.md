## Context

See proposal.md - Why. The official site is resolved from MusicBrainz url-rels by `musicbrainz.client.ResolveOfficialSiteURL` (`selectOfficialSiteURL`) and stored in `artist_official_site` (one row per artist, `url NOT NULL`). Today the only writer is `followUseCase.resolveAndPersistOfficialSite`: it runs in a goroutine after a follow, only when no row exists. The row is never revisited.

The MusicBrainz client throttles to 1 request per second per process (`throttle.New(1s, 100)`) and retries 429/503/504. MusicBrainz enforces its limit per source IP. Prod has no Cloud NAT today, so a pod egresses through its node's IP. Pods on the same node share the limit, and enabling NAT (planned in `network.ts`) would make every pod share one IP.

Measured MusicBrainz traffic in prod over the 30 days to 2026-10-05:

| call | count | caller |
|---|---|---|
| `GetArtist` | 55 | event-consumer, artist-created |
| place search | 2 | event-consumer |
| official-site lookup | 1 | fan-api, async after a follow |
| 503 retry | 1 | — |

The existing `artist-image-sync` CronJob (19:00 JST) syncs fanart.tv images for up to 500 stale artists. It calls fanart.tv, not MusicBrainz.

## Goals / Non-Goals

**Goals:**
- Keep the MusicBrainz load of the refresh bounded and predictable, independent of how small today's traffic is.
- Reuse the existing selection, persistence and job patterns, and add no new external dependency.

**Non-Goals:**
- Manual overrides of an artist's site, or a second source such as Wikidata.
- Changing the follow-time lookup or the fanart sync.
- Fixing MusicBrainz data or the catalog identity of the 26 followed artists without a site.

## Decisions

**D1. Top-page preference by URL shape, not by a domain list.** `selectOfficialSiteURL` first narrows the active `official homepage` relations to those whose parsed URL has an empty or `/` path, no query and no fragment, when any exist, and then applies the existing credit priority.

On the 2026-10-05 data (30 followed artists with several active links):
- 21 artists get a single top page, and each is the artist's own site.
- 8 artists have several top pages; their result is unchanged.
- 1 artist (レキシ) has no top page; its result is unchanged.

Alternative considered: a list of label, agency and store domains to demote. It needs maintenance, misses new labels, and a label's own top page (for example `55mth.com` for マキシマム ザ ホルモン, which does carry ticket news) would be wrongly demoted.

**D2. The check time lives on `artists`, not on `artist_official_site`.** Add `artists.official_site_checked_at TIMESTAMPTZ NULL`. The Go entity gets `Artist.OfficialSiteCheckTime *time.Time`, mirroring `fanart_synced_at` / `FanartSyncTime`. A check that finds no URL for an artist without a site has no `artist_official_site` row to stamp, so the time cannot live there. Without a stamp, such artists would come back as never-checked on every run and take the batch.

Alternative considered: a column on `artist_official_site` (the earlier plan). Rejected for the reason above.

The column is not added to the proto Artist message, as with `fanart_synced_at`.

**D3. Entity operations on `ArtistRepository`, realized in `rdb.ArtistRepository`.**
- `ListStaleOfficialSite(ctx, age, limit)`: a SELECT over `artists` joined to `followed_artists` (DISTINCT), filtered by `official_site_checked_at IS NULL OR official_site_checked_at < now - age`, ordered `NULLS FIRST, ASC`, with a LIMIT.
- `UpdateOfficialSiteURL(ctx, artistID, url)`: `UPDATE artist_official_site SET url = $2 WHERE artist_id = $1`. Zero rows affected returns NotFound. The URL is validated with the existing OfficialSite URL rule before the update.
- `MarkOfficialSiteChecked(ctx, artistID, t)`: `UPDATE artists SET official_site_checked_at = $2 WHERE id = $1`. Zero rows affected returns NotFound.

Alternative considered: one upsert operation on `artist_official_site`. Rejected: Create (fresh id, AlreadyExists) and Update (keep id, NotFound) keep the existing Create contract intact and make each branch testable.

**D4. A separate usecase and CronJob.**
- `usecase.OfficialSiteRefreshUseCase` with `RefreshOfficialSite(ctx, artistID, mbid)` depends on `ArtistRepository` and `OfficialSiteResolver`.
- A new entrypoint `cmd/job/official-site-refresh` with `di.InitializeOfficialSiteRefreshJobApp` copies the `artist-image-sync` main loop: the circuit breaker of 3 consecutive failures, graceful shutdown, and a final summary log.
- The batch size is `ceil(len(Follow.ListAll)/7)`.
- The CronJob `official-site-refresh-app` runs at `0 19 * * *` UTC, which is 04:00 JST, with `concurrencyPolicy: Forbid`.

Alternative considered: adding the work to `artist-image-sync`. Rejected: that job runs at 19:00 JST, overlapping concert-discovery's ingestion, when event-consumer calls MusicBrainz for place searches. It also targets all 4,619 artists with a batch of 500, not only the followed ones.

**D5. Load bound.** About 20 calls a day at 1 per second is about 20 seconds of MusicBrainz use, at the hour with no observed traffic. The client's 429/503 retries are kept. Even with a shared IP, the job can only make user-path calls wait for that short window.

**D6. The follow path is unchanged.** A newly followed artist's site is created by Follow, and its first refresh comes on the next run (it is never-checked). That costs one extra call per new artist. It avoids changing `components/usecase/follow/follow` or stamping a time there.

## Risks / Trade-offs

- [The top-page rule picks a store or SNS top page listed as an official homepage, such as `https://example.bandcamp.com/` or a subdomain profile] → It only applies among `official homepage` relations, where such entries are rare. Every replacement is logged with old and new URL, so a wrong pick is visible and fixable in MusicBrainz.
- [The refresh overwrites a URL someone corrected by hand in the database] → There is no manual-override path today; adding one is a non-goal. Corrections belong in MusicBrainz.
- [Replacing the URL changes what concert and sales-phase discovery read] → This is intended. Search caches key on the artist, not on the URL, so no cache needs invalidating.
- [The followed set grows faster than the batch catches up] → The batch is recomputed every run from the current followed count, so the cycle stays about 7 days.
- [A MusicBrainz outage] → After 3 consecutive failures the run stops. Unchecked artists stay due and are taken first the next day.

## Migration Plan

1. backend:
   - The Atlas migration `ALTER TABLE artists ADD COLUMN official_site_checked_at TIMESTAMPTZ`. It is nullable with no backfill, so every followed artist starts as never-checked.
   - The selection change, the repository methods, the usecase, the job entrypoint, the Dockerfile target and the deploy workflow matrix entry.
   - Merge and release.
2. cloud-provisioning:
   - The `cronjob/official-site-refresh` base (CronJob, kustomization, configmap.env), dev and prod overlays (config, image, Spot patch), the prod image pin and `bump-prod-pin` coverage.
   - After ArgoCD sync, confirm the first run's summary log and the replacements it logs.
3. The first runs work through the 133 followed artists in about 7 days. The 5 label-page artists and 羊文学 are corrected as they come up.

Rollback: suspend the CronJob. The selection change can be reverted with the image pin. The new column is unused by the other workloads, so it can stay.

## Open Questions

- Whether to move the follow-time lookup onto the same usecase later, so a single code path writes official sites. It is deferred because it changes the Follow spec and is not needed for the refresh.
