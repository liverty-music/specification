## Why

The concert search runs Gemini for each followed Artist at most once every 4 days (the prod freshness window is 96h), so a concert announced on an official site can reach fans up to 4 days late. Since the release of 2026-11-21 the search makes almost no Google Search queries (0 to 28 a day, inside the 5,000 free queries a month), so tokens are now nearly the whole cost, and every search we avoid saves money.

If a plain HTTP fetch of the official site can tell that its content changed, a search could run when a page changed and be skipped when nothing changed, instead of running on a fixed interval. A probe on 2026-11-27 fetched 12 official top pages twice, 20 seconds apart: the SHA-256 of the raw HTML differed on 6 of 12 pages (per-request tokens), while the SHA-256 of the visible text (script, style and tags removed, whitespace collapsed) matched on all 12. Two pages are JavaScript shells with almost no text (11 and 93 characters), so the pages the top page links to matter too.

What the probe cannot show is whether a text change predicts a new concert, and whether new concerts appear without any text change. This change measures that in production for 8 days, without calling Gemini and without changing what fans see, so the next change can decide between change-triggered search and a shorter fixed interval on evidence.

## What Changes

- The backend concert-discovery job gains a second mode, official-page-check. It fetches, for every followed Artist with an OfficialSite, the official top page and the links the concert search lists from it, and logs one line per page: the artist, the page URL, whether it is the top page or a linked one, the SHA-256 and length of the page's normalized visible text, and the fetch outcome. It never calls Gemini and writes nothing to the database.
- cloud-provisioning adds a temporary CronJob that runs that mode daily at 17:00 JST, one hour before the daily concert search, for 8 days.
- After the 8th run, the results are compared with the `concert.search.completed` events of the daily searches in the same period, and the findings are written into this change's design.md.
- Then the CronJob and the mode are removed.
- Out of scope: any change to when searches run. Running the search on Gemini's Flex tier in background attempts is change `move-concert-search-to-flex-tier`; the comparison in design D6 holds whether or not it is live during the measurement.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The measurement changes no product behavior: no fan, organizer or admin sees a difference, and the concert search runs exactly as before. The change sets `skip_specs: true`.

## Impact

- backend: a new mode of `cmd/job/concert-discovery` and a page-text hashing function next to the official top page fetch in `internal/infrastructure/gcp/gemini`; no new analytics topic. Both are removed at the end.
- cloud-provisioning: a new CronJob under `k8s/namespaces/backend` that reuses the concert-discovery image and its ConfigMap; removed at the end.
- Production: about 1,900 extra HTTP GETs to official sites per day (around 80 sites, a median of 22 listed links each), sequential per site. No Gemini or database cost; a few thousand operational log lines a day.
