## Why

Since the release of 2026-11-21 the concert search makes almost no Google Search queries (0 to 28 a day, inside the 5,000 free queries a month), so its cost from December is almost all tokens. Gemini's Flex tier halves the token price (confirmed in the billing export on 2026-11-26: input 237 to 119 yen and output 1,187 to 593 yen per million tokens). In exchange it may answer up to 15 minutes later, and it refuses with 503 when it is busy: in a 10-minute trial on 2026-11-26, 11 of 13 calls were refused.

Nobody waits for a search. The daily run is a background job, and the first-follow search already runs in the background (stories/follow-an-artist). So a late answer costs nothing, as long as a refused search is tried again for hours instead of being given up after a few seconds. Today it cannot be: the search runs inline in the daily job and the event consumer, with 3 attempts a few seconds apart, a 120-second call timeout, a 3-minute pending timeout, one Artist at a time, and a job that stops after 3 failures in a row.

This change moves the search into background attempts that retry a busy refusal for up to 20 hours. It then runs the search on Flex only, to observe its success rate and delay for several days before deciding on a fallback to the standard tier or a shorter search interval.

## What Changes

- **SearchNewConcerts runs the search in the background.** It still applies every skip rule and records the ConcertSearch as pending. It then starts a background search, named after the Artist and the search time, and returns at once without previews.
  - The daily run therefore only records and starts searches.
  - The first-follow search starts one the same way.
- **The background search survives a busy service.** It runs the steps that were inline before: Concert.Search, the filtering, handing on to CreateFromDiscovered, the status update and the completed signal.
  - It calls Concert.Search in attempts. At most 8 attempts call it at once across the platform, and attempts waiting to retry hold no place.
  - A busy or timed-out attempt is followed by another, first after 1 minute and then at doubling intervals of at most 1 hour, as long as the next attempt would start less than 20 hours after the search time. Otherwise the search ends as failed, with one completed signal of outcome failed.
  - Every attempt first checks again that the search is still current and the Artist may still be searched (not ended, not represented by an active Organizer), because an attempt can run hours after the request.
- **The pending timeout becomes 20 hours (from 3 minutes).** While a background search may still be running, no second search for the same Artist starts.
- **Concert.Search asks for the lower-priced service level (Flex).** It waits up to 15 minutes for each answer.
- **Concert.Search sends one request and classifies its failure.** The 3 tries inside it are removed: the background attempts are the only retry. A busy, rate-limited or failing service, a lost connection and a late answer are transient. A response that holds no usable result (no candidate, not completed, broken or empty) is not, so it is not repeated for 20 hours.
- **The usage report of each Gemini call carries the service level.** Without it, cost in product analytics reads at twice the billed price.
- **Removed: the previews SearchNewConcerts returned.** No caller reads them: the daily job and the first-follow search both discard them.
- **Out of scope:**
  - a fallback to the standard tier after some hours;
  - a shorter search interval than the prod 96 hours;
  - the ticket sale search, which never succeeded on Flex in the trial;
  - change detection of official pages (change measure-official-page-change-detection, planned on its own; its comparison holds whether or not this change is live).

  The first two are decided from this change's observation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/usecase/concert/search-new-concerts`:
  - the search runs in the background, in attempts until 20 hours after the search time, at most 8 calling at once;
  - every attempt checks the search and the Artist again before calling;
  - the pending timeout becomes 20 hours;
  - the status and the completed signal are set by the background search, once per search, including a search that gives up at 20 hours;
  - the previews are removed.
  - (Purpose) The sequence diagram changes: SearchNewConcerts ends by starting the background search, and the steps after Upsert move into it. The diagram is fixed at archive.
- `components/entity/concert-search/update-status`:
  - UpdateStatus changes only the search with the given search time, so a search that ends late cannot end a later one.
- `components/entity/concert/search`:
  - Search asks for the lower-priced service level and waits up to 15 minutes for an answer;
  - each call's usage report carries the service level;
  - Search no longer retries a failed request, and an incomplete response is no longer a transient failure.

Unchanged, and why:
- **ConcertSearch and its operations Upsert, MarkFound and GetByArtistID.** They are called as before, only from the background search (UpdateStatus changes, above); the pending timeout is a value SearchNewConcerts passes, and "Search still in progress" keeps its rule.
- **`components/usecase/concert/search-new-concerts-on-first-follow`.** It still calls SearchNewConcerts and fails when SearchNewConcerts fails, which now means only that the search could not be recorded or started.
- **`stories/follow-an-artist`.** It already describes the first search as a background one whose concerts arrive "once the search completes".

## Impact

- **backend:**
  - a new background search run by the workflow worker on its own queue;
  - SearchNewConcerts starts it instead of searching inline;
  - the Gemini concert searcher sets the Flex service tier and a 15-minute call timeout;
  - the generation report carries the service tier;
  - the daily job and the first-follow consumer finish in seconds.
- **cloud-provisioning:**
  - the search model, thinking level and service tier are pinned in the prod ConfigMap the workflow worker reads, and removed from the job's;
  - the backend release reaches prod through the CI-written prod pins, with no hand-edited pin.
- **Production:**
  - concert-search token cost roughly halves;
  - new concerts may reach fans up to some hours later on a busy day;
  - a search still refused 20 hours after it started ends as failed, and the next daily run searches the Artist again;
  - leaving Flex is a setting (no release). Reverting the release is not a rollback: the previous worker cannot run the stored attempts.
