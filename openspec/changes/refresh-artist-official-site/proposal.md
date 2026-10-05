## Why

Concert and ticket-sale discovery ground every search on the artist's official site, but the site is looked up only once, when the artist is first followed, and the lookup picks the first catalog link it finds. On 2026-10-05, 107 of the 133 followed artists had a stored site. A check of those 107 against the music catalog found:

- 5 artists stored with a label page although the catalog also lists the artist's own domain: ヨルシカ, あいみょん, 04 Limited Sazabys, ILLIT and SPYAIR.
- 1 artist (羊文学) stored with a site the catalog has since marked as ended, while it now lists the new one.

The first case is a selection problem, and the second is a refresh problem. Discovery reads the wrong page in both.

## What Changes

- Artist.ResolveOfficialSiteURL prefers links that point at a site's top page (no path) over deeper links, such as `/artist/<name>` pages on label sites. It does this before the existing credit-based priority. On the 2026-10-05 data this picks the artist's own domain for all five label-page cases and changes none of the other 25 artists with several active links.
- An artist records when its official site was last checked in the music catalog (`official_site_check_time`).
- A new daily job, at 04:00 Japan time, refreshes the official sites of followed artists whose site was never checked or was checked more than 7 days ago, oldest first.
  - Each run handles at most the number of followed artists divided by 7, rounded up, so the whole set is refreshed in about 7 days. Calls to the music catalog stay small, because the catalog limits requests per source address.
  - It creates the site when none is stored, replaces it when the catalog now resolves to a different URL, and keeps the stored site when the catalog lists no active homepage.
  - A catalog failure leaves the artist due for the next run.
- The follow-time lookup and the daily image sync stay as they are.

Out of scope:

- Catalog entries that are themselves outdated or list only label pages (TOTALFAT's former domain, WurtS, レキシ). These are fixed by editing the catalog; the refresh then picks the fix up.
- The 26 followed artists with no stored site. For none of them did the catalog list an active homepage on 2026-10-05; the list includes Ado, Aimer and Tyler, The Creator, which suggests some are matched to the wrong catalog entry. The refresh stores a site for them as soon as the catalog lists one. Checking their catalog identity is a follow-up.

## Capabilities

### New Capabilities

- `components/entity/artist/list-stale-official-site`: returns the followed artists whose official site is due for a check: never checked, or checked longer ago than a given age. Never-checked artists come first, then the oldest checks, up to a limit.
- `components/entity/artist/update-official-site-url`: replaces the URL of an artist's stored official site and keeps its id.
- `components/entity/artist/mark-official-site-checked`: records when an artist's official site was last checked.
- `components/usecase/artist/refresh-official-site`: refreshes one artist's official site from the music catalog, and the daily run that drives it.

### Modified Capabilities

- `components/entity/artist` (Purpose): a new `official_site_check_time` attribute, edited directly in the main spec.
- `components/entity/artist`: a new artist also starts without an `official_site_check_time`.
- `components/entity/artist/resolve-official-site-url`: links to a site's top page are preferred before the credit-based priority.

The other entity operations the new usecase relies on stay unchanged:

- Artist.GetOfficialSite, Artist.CreateOfficialSite and Artist.ResolveOfficialSiteURL keep their current contracts, apart from the selection change above.
- Follow.ListAll keeps its contract; the daily run uses it to size the batch.
- The OfficialSite entity is unchanged: replacing the URL keeps the site's id, and an artist still has at most one site.
- FollowUseCase.Follow (`components/usecase/follow/follow`) keeps resolving a missing site in the background; the daily refresh is separate from it.

## Impact

- backend:
  - `internal/infrastructure/music/musicbrainz`: selection rule.
  - `internal/entity` and `internal/infrastructure/database/rdb`: the new Artist operations and the `official_site_check_time` field.
  - A new usecase.
  - A new job entrypoint under `cmd/job/` and its DI wiring.
  - An Atlas migration that adds a nullable `artists.official_site_check_time` column.
- cloud-provisioning: a new CronJob (04:00 JST daily) with its ConfigMap, image pin and the usual Spot patch, in dev and prod.
- No proto change: like `fanart_sync_time`, the check time is not part of the Artist message.
- External: the job calls the music catalog at most ceil(followed artists / 7) times a day, about 20 with 133 followed artists.
