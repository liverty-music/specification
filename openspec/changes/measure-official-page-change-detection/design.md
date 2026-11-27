## Context

See proposal.md for why. The current state this design builds on:

- The daily concert search is the `concert-discovery` CronJob (18:00 JST). It lists followed Artists (`FollowRepo.ListAll`) and calls `ConcertUseCase.SearchNewConcerts` with trigger `daily_run`; a ConcertSearch completed less than 96h ago skips the external search.
- Before each Gemini call the concert searcher fetches the OfficialSite's top page with `NewOfficialPageClient` (public addresses only, at most 3 redirects within the site's registrable domain, 5 s timeout, 2 MiB cap) and lists up to 60 of its links in the prompt, after dropping social, streaming, shop, ticket-vendor and site-information links (`officialPageLinks` in `internal/infrastructure/gcp/gemini/official_pages.go`).
- Each search that reached Gemini sends a PostHog `concert.search.completed` event with `artist_id`, `trigger` and `outcome` (`found`, `nothing_new` or `failed`) and `event_count`.
- Change `move-concert-search-to-flex-tier` (merged as a plan) moves the search into background attempts on the Flex tier. Once it is live, a daily search still starts at 18:00 JST but its event arrives when its last attempt ends, up to about 21 hours later, and a search may end as failed after 20 hours of a busy service. D6 reads the events so that the result is the same whether or not that change is live during the measurement.
- `pkg/analyticslog` marks a log line for the analytics log bucket; a new topic needs no change to the Log Router sink, and the bucket is readable in BigQuery through the `logs_analytics` linked dataset.

## Goals / Non-Goals

**Goals:**
- For each daily search in the measurement period, know whether the Artist's official pages changed since the search before it.
- Measure how often a change comes with new concerts, how often new concerts come without a change, and which pages (top or linked) carried the change.

**Non-Goals:**
- Triggering a search from a change. That is the next change, if the numbers support it.
- Covering first-follow searches: they run at any time, so no snapshot sits right before them.
- Reading pages that need JavaScript to render. The measurement counts them instead (text length), so the next change knows how many Artists would still need a fixed interval.

## Decisions

### D1. A mode of the concert-discovery binary, run by its own CronJob

`cmd/job/concert-discovery` gets a `-mode` flag: `search` (the default, today's behavior) and `official-page-check`. A second CronJob runs the same image with `args: ["-mode=official-page-check"]` and the same ConfigMap and secrets.

Alternative: a new `cmd/job/official-page-check` binary. It needs its own Dockerfile stage, an entry in the deploy workflow's image list, a base image name and a prod image pin, all to be removed again after 8 days. The mode reuses the image, the job wiring and the prod pin of concert-discovery, so the temporary footprint is one flag and one manifest.

Alternative: run the check inside the daily search job. It would change the timing and failure behavior of the job fans depend on, which this measurement must not do.

### D2. Hash the normalized visible text, not the raw HTML

The page is parsed with `golang.org/x/net/html` (already used for the link list). The text is the concatenation of text nodes outside `script`, `style`, `noscript`, `template` and `svg`, with entities decoded by the parser and runs of whitespace collapsed to one space. The log line carries its SHA-256 (hex) and its length in characters.

Evidence: on 2026-11-27, 12 official top pages fetched twice 20 seconds apart gave a different raw-HTML SHA-256 on 6 pages and the same text SHA-256 on all 12. `ETag` was present on 4 pages and `Last-Modified` on 2, so neither can serve as the signal.

### D3. The pages checked are exactly the pages a search lists

The mode reads the top page through the same client and the same link selection as the searcher, so the measured pages are the ones Gemini is pointed at. The top-page fetch is refactored to return the parsed document once, from which both the links and the text are taken; the searcher's behavior and its link list do not change (its existing tests pin that). Each listed link is then fetched with the same client and hashed the same way. A link that leaves the site's registrable domain is still fetched (tour sites live on other domains), with the same address guard.

Load: around 80 sites with a median of 22 listed links (2026-11-21). Artists are processed 4 at a time and the pages of one site one after another, so no site gets parallel requests.

### D4. One analytics log line per page, topic `official_page_check`

Fields: `artist_id`, `page_url` (the URL requested), `page_kind` (`top` or `linked`), `status` (`ok`, `http_error`, `fetch_error` or `not_html`), `http_status`, `text_sha256`, `text_length`. Artist IDs and official URLs are catalog data, not a fan's personal data, so `analyticslog.Attrs` marks the line. One summary line per run uses the existing `job_result` topic (artists, pages, failures).

Alternative: a database table. It would need a migration, which applies to prod on merge, for data used once; the analytics bucket already keeps logs for analysis and is queryable with SQL.

### D5. Schedule and period

The CronJob runs at 17:00 JST (`0 8 * * *` UTC), one hour before the daily search, so the snapshot of a day is the state the search of that day reads. It runs 8 times. With the 96h freshness window, an Artist is searched about twice in 8 days, so most Artists have one search whose previous search also has a snapshot before it.

### D6. How the results are read

**Which searches are compared.** Each `concert.search.completed` event with `trigger = daily_run` and outcome `found` or `nothing_new` in the period is one search. Its start day is the day of the latest 18:00 JST at or before the event, which holds whether the search ran inline or in background attempts. Its **baseline** is the Artist's previous `daily_run` search with outcome `found` or `nothing_new`; a `failed` search is skipped, because it could not have found a concert the page announced. A search is **comparable** only when the snapshots of both start days exist; the others are counted as "no baseline" and left out of every rate below.

**Which pages are compared.** For a comparable search, take the 17:00 JST snapshot of its start day and that of its baseline's start day. A page is compared only when it has `status = ok` in both. When the top page is not `ok` in either snapshot, the search is counted as "unreadable" and left out, because its link list is missing too. The search is **changed** when a compared page's `text_sha256` differs, or when the set of listed URLs differs between the two `ok` top pages. The search is **found** when its outcome is `found`.

Reported, as aggregate counts only:
- the counts of searches left out (no baseline, unreadable, failed outcome);
- over comparable searches, the 2x2 table of changed and found; recall = found and changed / found; trigger rate = changed / comparable searches;
- of the changed searches, how many changed only through linked pages;
- Artists whose top page text is shorter than 200 characters, and pages that failed to fetch on more than 2 runs;
- the expected cost of change-triggered search against today's fixed interval, from the trigger rate.

If fewer than 10 comparable searches are `found` in the period, recall is not reliable: the report says so and the CronJob keeps running until 10 are reached or 16 runs have passed, whichever comes first.

## Risks / Trade-offs

- [A site rate-limits or blocks the extra GETs] → one request at a time per site, the existing User-Agent naming the service, and the 5 s timeout; a site that answers 429 or 403 is logged with its status and left out of the comparison (D6), so a refusal never reads as a change.
- [Text that changes on every load (a clock, a random banner) makes every search look changed] → the trigger rate shows it; the report lists the pages that changed on every run so the next change can decide how to handle them.
- [A concert announced only off-site (a festival site, a ticket vendor) is never visible on the official pages] → it shows up as found without change, which is exactly what recall measures.
- [The refactor of the top-page fetch changes what the searcher sends] → the searcher's existing link-list tests must pass unchanged.

## Migration Plan

1. backend PR (mode and hashing), merge, release. The release retags the images into prod and `bump-prod-pin.yml` in cloud-provisioning rewrites every backend prod pin and pushes to main (`k8s/namespaces/backend/overlays/prod/kustomization.yaml`, "Bumping on release"); there is no hand-edited pin. The daily search job runs the new image from then on, in its default mode.
2. After the prod pins carry that release: cloud-provisioning PR that adds the CronJob. It goes live on merge through ArgoCD. Merged earlier, the CronJob would run an image without the mode and fail.
3. Confirm the first run in prod (read-only): the Job completed, and `logs_analytics` holds one line per page.
4. After the 8th run (or the extension in D6), write the results below.
5. Remove the CronJob (cloud-provisioning) and the mode (backend). Removing the CronJob alone stops all traffic, so rollback at any time is deleting the manifest.

## Results

To be written after the measurement (task 4.1).
