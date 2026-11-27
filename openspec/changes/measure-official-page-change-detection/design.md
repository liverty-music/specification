## Context

See proposal.md for why. The current state this design builds on:

- The daily concert search is the `concert-discovery` CronJob (18:00 JST). It lists followed Artists (`FollowRepo.ListAll`) and calls `ConcertUseCase.SearchNewConcerts` with trigger `daily_run`; a ConcertSearch completed less than 96h ago skips the external search.
- Before each Gemini call the concert searcher fetches the OfficialSite's top page with `NewOfficialPageClient` (public addresses only, at most 3 redirects within the site's registrable domain, 5 s timeout, 2 MiB cap) and lists up to 60 of its links in the prompt, after dropping social, streaming, shop, ticket-vendor and site-information links (`officialPageLinks` in `internal/infrastructure/gcp/gemini/official_pages.go`).
- Each search that reached Gemini sends a PostHog `concert.search.completed` event with `artist_id`, `trigger` and `outcome` (`found`, `nothing_new` or `failed`) and `event_count`.
- Change `move-concert-search-to-flex-tier` is live (backend v1.156.0, 2026-11-27). The `concert-discovery` CronJob (18:00 JST) now only records each due search and starts a `search-concerts` workflow, and ends within minutes without calling Gemini. The workflow worker runs the search in attempts: the page read and the Gemini call happen at the successful attempt, from 18:00 JST up to 20 hours later (no attempt starts at or after 20 hours; a call can end up to 15 minutes after that), and the search's `concert.search.completed` event is sent when it ends, so always before the next 18:00 JST. A search ends as failed (error kind unavailable) when the service stays busy for the whole window. A search whose Artist is found ended or represented by the first attempt sends no event.
- `pkg/analyticslog` marks a log line for the analytics log bucket, with exactly one topic from the list the structured-logging spec fixes (`job_result`, `notification_delivery`, `catalog_review`, `catalog_sync`, `payment`). An unmarked line stays in the operational logs, which Cloud Logging keeps for 30 days.

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

The job's code path for the search is gone (it starts workflows), so this mode shares only the binary, the image and the database wiring with the daily run. The check needs no Gemini key and no workflow client.

The CronJob carries the pod label `app: concert-discovery`, the label of the binary it runs, so the existing per-workload ERROR-log alert in cloud-provisioning (`src/gcp/components/monitoring.ts`, one entry per `app` label under `k8s/namespaces/backend/base`) covers its failures with no new entry. A label of its own would need a new alert entry, a Pulumi change applied to prod by the owner, for a workload that lives 8 days. The CronJob name tells the two apart in logs.

Alternative: run the check inside the daily job. The job now ends within minutes, so a check of about 1,900 pages (D3) would stretch it by an order of magnitude and put its failures into the job's 3-failure stop, which this measurement must not do.

### D2. Hash the normalized visible text, not the raw HTML

The page is parsed with `golang.org/x/net/html` (already used for the link list). The text is the concatenation of text nodes outside `script`, `style`, `noscript`, `template` and `svg`, with entities decoded by the parser and runs of whitespace collapsed to one space. The log line carries its SHA-256 (hex) and its length in characters.

Evidence: on 2026-11-27, 12 official top pages fetched twice 20 seconds apart gave a different raw-HTML SHA-256 on 6 pages and the same text SHA-256 on all 12. `ETag` was present on 4 pages and `Last-Modified` on 2, so neither can serve as the signal.

### D3. The pages checked are exactly the pages a search lists

The mode reads the top page through the same client and the same link selection as the searcher, so the measured pages are the ones Gemini is pointed at. The top-page fetch is refactored to return the parsed document once, from which both the links and the text are taken; the searcher's behavior and its link list do not change (its existing tests pin that). Each listed link is then fetched with the same client and hashed the same way. A link that leaves the site's registrable domain is still fetched (tour sites live on other domains), with the same address guard.

Load: around 80 sites with a median of 22 listed links (2026-11-21). Artists are processed 4 at a time and the pages of one site one after another, so no site gets parallel requests.

### D4. One operational log line per page, and a `job_result` summary

Each page gets one INFO line with the message `official page checked` and the fields `artist_id`, `page_url` (the URL requested), `page_kind` (`top` or `linked`), `status` (`ok`, `http_error`, `fetch_error` or `not_html`), `http_status`, `text_sha256` and `text_length`. The line is **not** marked for the analytics bucket:
- the structured-logging spec allows only its listed topics, and none fits a per-page measurement;
- adding a topic would be a spec change made only to remove it again after 8 days;
- the operational logs keep the lines for 30 days, longer than the at most 16 runs. The analysis reads them with `gcloud logging read` filtered on that message.

The run ends with the summary line the structured-logging spec requires ("Job summary lines report how far the run got"), on the existing `job_result` topic:
- processed: Artists reached;
- failed: Artists whose top page was not `ok`;
- succeeded: processed minus failed;
- stopped early: always false, because this mode has no consecutive-failure stop. A site that fails says nothing about the next one.

The page and failure counts go on the same line as extra fields.

Alternative: a database table. It would need a migration, which applies to prod on merge, for data used once; the operational logs already keep the lines long enough.

### D5. Schedule and period

The CronJob runs at 17:00 JST (`0 8 * * *` UTC), one hour before the daily run that starts the searches. It runs 8 times.

The checked Artists are the ones the search would search. Followed Artists are checked with their OfficialSite, except those whose activity has ended or that an active Organizer represents (the same exclusions as SearchNewConcerts).

**How many searches can be compared.** An Artist is searched at most every 96 h. After a search that finds a new concert, it is not searched again for 14 days (the discovery window). So in 8 to 16 days:
- each Artist contributes at most one `found` search, and only when its baseline is a `nothing_new` search inside the period;
- with about 80 Artists and no measured rate of finds, the number of comparable `found` searches is unknown and may be well below 10. D6's extension rule covers that case.

### D6. How the results are read

**Which searches are compared.** Each `concert.search.completed` event with `trigger = daily_run` and outcome `found` or `nothing_new` in the period is one search. Its start day is the day of the latest 18:00 JST at or before the event: a search ends within 20.25 hours of its start, so before the next 18:00 JST. Its **baseline** is the Artist's previous `daily_run` search with outcome `found` or `nothing_new`; a `failed` search is skipped, because it could not have found a concert the page announced. A search is **comparable** only when the snapshots of both start days exist; the others are counted as "no baseline" and left out of every rate below.

**Which pages are compared.** For a comparable search, take the 17:00 JST snapshot of its start day and that of its baseline's start day. A page is compared only when it has `status = ok` in both. When the top page is not `ok` in either snapshot, the search is counted as "unreadable" and left out, because its link list is missing too. A page is matched by `page_url`. When the top page's `page_url` differs between the two snapshots (the OfficialSite was replaced by the daily official-site refresh, or the www. fallback read another host), the search is counted as "site moved" and left out, because every hash would differ for a reason that says nothing about an update. The search is **changed** when a compared page's `text_sha256` differs, or when the set of listed URLs differs between the two `ok` top pages. The search is **found** when its outcome is `found`.

Reported, as aggregate counts only:
- the counts of searches left out (no baseline, unreadable, site moved, failed outcome, no event because the first attempt found the Artist ended or represented);
- over comparable searches, the 2x2 table of changed and found; recall = found and changed / found; trigger rate = changed / comparable searches;
- of the changed searches, how many changed only through linked pages;
- Artists whose top page text is shorter than 200 characters, and pages that failed to fetch on more than 2 runs;
- the expected cost of change-triggered search against today's fixed interval, from the trigger rate.

If fewer than 10 comparable searches are `found` in the period, recall is not reliable: the report says so and the CronJob keeps running until 10 are reached or 16 runs have passed, whichever comes first.

## Risks / Trade-offs

- [A site rate-limits or blocks the extra GETs] → one request at a time per site, the existing User-Agent naming the service, and the 5 s timeout; a site that answers 429 or 403 is logged with its status and left out of the comparison (D6), so a refusal never reads as a change.
- [A concert announced after the 17:00 snapshot and before the search reads the page counts as found without change] → measured recall is a lower bound. The search reads the page when its successful attempt runs, from 18:00 JST up to 20 hours later (a busy Flex tier delays it), so the snapshot predates the read by 1 to 21 hours. The report states the share of `found` searches whose event came more than 2 hours after 18:00 JST, the ones for which a change in that gap is most likely.
- [Text that changes on every load (a clock, a random banner) makes every search look changed] → the trigger rate shows it; the report lists the pages that changed on every run so the next change can decide how to handle them.
- [A concert announced only off-site (a festival site, a ticket vendor) is never visible on the official pages] → it shows up as found without change, which is exactly what recall measures.
- [The refactor of the top-page fetch changes what the searcher sends] → the searcher's existing link-list tests must pass unchanged.

## Migration Plan

1. backend PR (mode and hashing), merge, release. The release retags the images into prod and `bump-prod-pin.yml` in cloud-provisioning rewrites every backend prod pin and pushes to main (`k8s/namespaces/backend/overlays/prod/kustomization.yaml`, "Bumping on release"); there is no hand-edited pin. The daily search job runs the new image from then on, in its default mode.
2. After the prod pins carry that release: cloud-provisioning PR that adds the CronJob. It goes live on merge through ArgoCD. Merged earlier, the CronJob would run an image without the mode and fail.
3. Confirm the first run in prod (read-only): the Job completed, and the operational logs hold one `official page checked` line per page.
4. After the 8th run (or the extension in D6), write the results below.
5. Remove the CronJob (cloud-provisioning) and the mode (backend). Removing the CronJob alone stops all traffic, so rollback at any time is deleting the manifest.

## Results

To be written after the measurement (task 4.1).
