## Context

See proposal.md for why. The current code this design changes (backend `main`, 2026-11-27):

- **Callers.** `ConcertUseCase.SearchNewConcerts` (`internal/usecase/concert_uc.go`) has two:
  - the `concert-discovery` CronJob (18:00 JST), which walks followed Artists one at a time and stops after 3 consecutive failures (`cmd/job/concert-discovery/main.go`);
  - `SearchNewConcertsOnFirstFollow`, run by the `search-first-followed-artist` NATS consumer.
- **What SearchNewConcerts does inline.** It upserts the ConcertSearch as pending and then, in `executeSearch`:
  - calls Gemini;
  - filters the results;
  - starts the `create-from-discovered` workflow (id `create-from-discovered:<artist>:<search time µs>`);
  - marks the result found;
  - updates the status;
  - sends `concert.search.completed`.
- **Timeouts.**
  - `pendingTimeout` is 3 minutes.
  - The consumer's `ackWait` is 10 minutes.
- **The Gemini searcher** (`internal/infrastructure/gcp/gemini/searcher.go`).
  - Each call has a 120-second budget (`geminiCallTimeout`), detached from the caller's context.
  - A transient failure, an incomplete response included, is retried for 3 attempts at 1 s, 2 s and 4 s.
  - The tier is not set, so calls run at the standard tier.
- **Workflows** (`internal/infrastructure/workflow`). These are DBOS workflows (v1.8.0) run only by the `workflow-worker` Deployment.
  - A step that fails with Unavailable or DeadlineExceeded is retried at 1 s doubling to at most 1 h (`stepOptions`). The run stays PENDING while it waits between retries.
  - `WithQueue` with `RegisterQueue(name, n)` caps concurrency across workers. The cap counts every PENDING run of the queue (`system_database.go:5086-5157`), so a run waiting between step retries holds a slot.
  - `WithDeadline` is counted from the dequeue, not from the start (`client.go:77-85`; DBOS `system_database.go:5273`). A run that waits in the queue therefore gets more time than asked for.
  - `WithDelay` keeps a run DELAYED until its time. A DELAYED run is not PENDING, so it holds no slot.
  - Starting an id that exists returns the existing run. A stored run is resumed by its registered name, so an older worker that lacks the name cannot run it (`runtime.go:168`).
- **Flex** (Gemini API docs, "Flex inference", read 2026-11-26).
  - Requested with `service_tier: flex`; it costs 50% less on tokens.
  - Target latency is 1 to 15 minutes, and the docs' example sets a 900-second client timeout.
  - When busy, it answers 503 or 429.
  - It is Preview, and the docs describe no automatic fallback to the standard tier.
  - The Go SDK in use (`google.golang.org/genai` v1.79.1) has `ServiceTier` with `ServiceTierFlex`.
  - The 2026-11-26 trial billed Flex tokens at half price under SKUs named "... flex" and recorded `serviceTier: flex` on the response.

## Goals / Non-Goals

**Goals:**
- Every concert search, daily or first-follow, runs at the Flex tier and survives hours of 503 without losing the search or starting a duplicate.
- The daily job and the first-follow consumer stop holding a Gemini call.
- Searches for different Artists run in parallel within a fixed cap.
- The observation in tasks section 4 can tell success rate, attempts and delay per search.

**Non-Goals:**
- A fallback to the standard tier, a shorter freshness window, and the ticket sale search (proposal.md, Out of scope).
- Showing fans anything new while a search is running.

## Decisions

### D1. The background search is a DBOS workflow, not a NATS announcement

SearchNewConcerts keeps its skip rules, the pending upsert and the Artist data check.

The data check is `artist.CheckSearchable`. Today it runs at the top of `executeSearch`, after the upsert, so the ConcertSearch of such an Artist ends as failed. The living spec's sequence diagram puts the check before `Upsert "pending"`, and "Artist data required" says only "fail with Internal, before any external search". The check moves into SearchNewConcerts, after the skip rules and before the upsert, as the diagram shows. An Artist with no name or no MBID then fails SearchNewConcerts with Internal, its ConcertSearch is left as it was, and no attempt is started. The next daily run fails the same way until an admin fixes the Artist, as today.

SearchNewConcerts then starts the first attempt of the workflow `search-concerts` with:
- id `search-concerts:<artist>:<search time µs>:1`;
- input: the Artist id, the search time, the trigger and the attempt number;
- queue `concert-search`;
- no DBOS deadline (D5 explains why).

The workflow is `ConcertUseCase.RunSearch` (registered in `internal/di/worker.go`). One run is one attempt: it calls Concert.Search once. A busy service does not make it wait. Instead it starts the next attempt with a delay and ends (D2).

Why a workflow:
- **Project rule.** The event-delivery spec ("Work for one receiver is started as a workflow") says a request for one receiver to do work is started as a workflow, not announced.
- **The platform already provides what the retry needs:**
  - an id per attempt makes a repeated start a no-op, so each attempt runs once;
  - a delayed start that holds no queue slot while it waits;
  - a concurrency cap;
  - recovery after a worker restart.

A NATS subject with `NakWithDelay` would need a new stream subject, a Consumer CR, a delivery-count-based delay and an `ackWait` longer than a 15-minute call. It would also break that rule.

**Why not retry inside one run.** Two facts rule out the step retry policy (Context, Workflows):
- A run waiting between step retries stays PENDING, so 8 busy searches would hold all 8 slots for hours. The other searches would make no call at all.
- `WithDeadline` counts from the dequeue, so a search queued for hours would outlive the 20-hour window and could be duplicated by the next daily run.

The attempt chain avoids both. A slot is held only during a call, and the 20-hour limit is checked against the search time itself.

**Why the job and consumer start the workflow inline.** The durable-workflows spec allows API servers, consumers and jobs to start workflows. The pending upsert and the start are two writes, not one transaction. If the start fails after the upsert:
- SearchNewConcerts fails, and the ConcertSearch stays pending until the 20-hour timeout;
- a redelivery to the first-follow consumer is skipped, because the search counts as in progress;
- so the next daily run is what searches the Artist again.

That gap is accepted rather than adding a transactional start.

### D2. One attempt, step by step

1. `check`: read the Artist and its ConcertSearch. The attempt ends without searching in two cases:
   - **The search was replaced.** The ConcertSearch is no longer pending with this search time. The attempt changes nothing and sends no signal, also when an earlier attempt called Concert.Search. A missing ConcertSearch counts as replaced.
   - **The Artist may no longer be searched.** Its activity has ended, or an active Organizer represents it. The attempt goes to `record-end` as nothing new. The signal is sent only when an earlier attempt called Concert.Search, that is, when the attempt number is above 1.

   A read of the ConcertSearch or the Artist that fails with Unavailable or DeadlineExceeded is retried by the platform. Any other failure of it fails the run itself: `record-end` does not run, so the ConcertSearch stays pending (the pending timeout frees the Artist), no signal is sent, and the run is reported for an admin.

   Both checks ran only before the pending upsert before this change. They are repeated because an attempt can start hours after the request.
2. `search`: if the search time is 20 h or more in the past, skip the call and treat the attempt as busy. Otherwise:
   - read the OfficialSite, the upcoming Concerts and the pending ConcertCandidate keys;
   - call Concert.Search once;
   - filter the result.

   The step returns one of three results:
   - **the new series**;
   - **busy**: Concert.Search failed with Unavailable or DeadlineExceeded;
   - **failed**: the error kind of a permanent error.

   Busy and failed are values, not errors, so the step retry policy never runs for them. A read before the call that fails with Unavailable or DeadlineExceeded is returned as the step's error, so the platform retries it before anything is called; any other read failure is **failed**. The 20 h limit is checked after the reads, immediately before the call.
3. **busy, and the next attempt would start less than 20 h after the search time:** start the next attempt and end. (When it would start at or past 20 h, go to `record-end` as failed instead.) The next attempt has:
   - the id `...:<attempt+1>`;
   - a delay of 1 minute doubling to at most 1 hour;
   - the same queue.

   The start is checkpointed in the run, so a resumed run does not start it twice.
4. `hand-on`: when series remain, start `create-from-discovered` with today's id (`create-from-discovered:<artist>:<search time µs>`), then MarkFound.
5. `record-end`: UpdateStatus and send `concert.search.completed` with the trigger from the input:
   - **completed** after a hand-on or nothing new;
   - **failed** with the error kind after a permanent error;
   - **failed** with the kind of the last error when the attempt was busy and the next one would start at or past 20 h.

   No attempt starts at or past 20 h after the search time. An attempt that gets its slot only after 20 h skips the call (step 2) and ends here as failed, with the kind of the previous attempt's error, which the input carries.

   **When the signal is sent.** Only when some attempt of the search called Concert.Search, that is, when this attempt called it or the attempt number is above 1. Attempt 1 that gets its slot after 20 h records failed without a signal, as the spec's "Each search reports its outcome" requires.

`record-end` writes the status first. A transient failure of that write is the step's error, so the platform tries it again until it succeeds; the metric and the signal follow only then. A ConcertSearch left pending would keep the Artist from being searched for 20 h. A failed Search call or read of a run that is itself being cancelled is returned as the step's error, never recorded as an outcome.

A failure to start `create-from-discovered` is a permanent error and ends as failed, as today. Apart from the failed check read of step 1, the run itself ends successfully in every case above, so no outcome is reported for an admin. A run that fails outside these paths (a bug) still is, per durable-workflows.

Attempt numbers count from 1, and every attempt reports its call (Concert.Search "Each external call reports its usage"). The observation therefore sees each attempt.

### D3. Flex in the searcher, configurable, default on

- **Config.** `gemini.Config` gets `ServiceTier`, set on `GenerateContentConfig.ServiceTier` of every concert search call. `pkg/config` reads `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER`; the code default is `flex`, and `standard` sends no tier.
- **Call timeout.** `geminiCallTimeout` becomes 15 minutes when the tier is flex and stays 120 s otherwise.
- **One request per attempt.** The searcher does not retry a failed request; the attempt chain (D2) is the only retry. The former 3 in-process tries at 1, 2 and 4 seconds cannot outlast a busy service, which the trial saw refuse for minutes, and at a 15-minute budget they would hold a queue slot for about 45 minutes. The one re-send of a request rejected as invalid stays: it is a different request (without the tool report).
- **Which failures are tried again.** Only those that time fixes and that cost little to repeat. The Gemini API bills no tokens for 4xx and 5xx answers, and its docs retry 429, 408 and 5xx with exponential backoff and not 400, 402 or 403 (billing and troubleshooting pages, read 2026-11-27).

  | Failure | Search fails with | The attempt |
  |---|---|---|
  | 503, 429, 500, 502, 504, 408, 401, lost connection, no answer in 15 minutes | Unavailable | busy |
  | 402 depleted credits, 403 refusal, 400 rejected twice | FailedPrecondition, PermissionDenied, InvalidArgument | failed |
  | no candidate, not completed normally (too many tool calls, MAX_TOKENS, RECITATION, ...), broken or empty text | Internal | failed |

  No candidate is not a result with no concerts: the API returns none "only if there was something wrong with the prompt" (API reference, GenerateContentResponse), and an empty result is a candidate with an empty series list. Before this decision these cases and an incomplete response failed with Unavailable, which the attempt chain would have repeated for 20 hours.
- **Fewer chances.** Under a refusal that lasts the whole window, a search now sends 25 requests instead of 75. The observation decides whether the 1-hour cap of the wait must come down.
- **No jitter.** The docs advise it; the queue's cap of 8 already spreads the attempts.
- **A request not answered in time is transient** at both tiers, as is a lost connection. Before this change both failed as permanent.
- **Ticket sale searcher.** Unchanged: it never succeeded at Flex in the trial.

**Worst case for one attempt.** 15 minutes (30 when a request rejected as invalid is sent again), during which the attempt holds a queue slot. A worker redeploy in the middle reruns the `search` step after the new worker starts. The rerun repeats at most one interrupted call.

### D4. Queue `concert-search` with concurrency 8

- Registered in the worker next to the payment and checkout queues.
- 8 keeps the daily batch (about 80 Artists) moving when calls take minutes, and stays far below the project's Gemini request-rate limits.
- Gemini calls hold no database connection. The steps' short reads share the worker's pool, as `create-from-discovered` already does.
- **A search can wait behind a batch.** A first-follow search started during the daily batch may wait for free slots. The worst case is about 80 × 15 min / 8, about 2.5 h; when Flex answers quickly, it is minutes. Nobody waits for it (stories/follow-an-artist). The order in which waiting attempts get a slot is the queue's own; this change does not set priorities.

### D5. One 20-hour window, checked against the search time

- **20 h < 24 h.** A search that gives up frees the Artist before the next daily run at the same hour, so the next run requests a fresh search with new ids.
- **The window is checked by the attempt itself** (D2 step 2), against the search time, so time in the queue counts. No DBOS deadline is set, because it would count from the dequeue.
- **The last call can end after the window.** An attempt started just before 20 h can finish its call after it. A search that a first follow started in the evening can then still be running when the next daily run, finding it older than 20 h, requests a new search. ConcertSearch.UpdateStatus therefore takes the search time and changes only that search, in one conditional UPDATE, so `record-end` of a late search cannot end its successor. MarkFound is unchanged: the discovery it records happened.
- **Alerting.** A permanent failure of the call (a refused account, an unusable answer) is logged at ERROR by the worker, which alerts as the job's per-artist ERROR did before. A transient one is information (a busy flex tier answers 503 for minutes and the attempt chain tries again), and so is a search that gives up at 20 h, which includes a spend cap answered as 429.
- **Giving up sends the failed signal with the error kind unavailable** (D2 step 5). During the Flex-only observation, the count of these signals shows how often Flex failed for a whole day. No admin report is raised for it.

### D6. The daily job and first-follow consumer

- **Daily job.** It keeps its loop and its 3-consecutive-failures stop. A failure now means the ConcertSearch could not be recorded or the workflow could not be started, which points to the database, so stopping still makes sense. The job ends in seconds.
- **First-follow consumer.** `ackWait` 10 minutes stays and is now far above the handler's time. `SearchNewConcertsOnFirstFollow` is unchanged.
- **No searcher outside the worker.** The job, the consumer and the API server no longer build the Gemini searcher, and the consumer and API server no longer require `GCP_GEMINI_SEARCH_API_KEY`; the worker requires it outside local.
- **Previews.** `SearchNewConcerts` returns only an error (the previews and `previewConcerts` are deleted), and the `ConcertUseCase` interface and mocks follow.

### D7. Reporting

- **Service tier on each generation.** `posthog.LLMGeneration` gets `ServiceTier`, reported as `service_tier`. Cost from PostHog's own price table reads as standard pricing; the billing export stays the source of truth for money. Sending our own cost figures was rejected: it would put a price table in code that goes stale on each repricing.
- **Every search that reached the external search ends with one signal.** `concert.search.completed` is sent once per search, from the `record-end` of its last attempt, including a search that gave up at 20 h (outcome failed, error kind unavailable). A search that never called Concert.Search sends none, as a skipped search does today: one ended by the `check` step on attempt 1, or one whose attempt 1 got its slot only after 20 h (D2 step 5).

### D8. Model and tier pins follow the process that calls Gemini

- **Before.** The prod model and thinking pins live in the `concert-discovery` job ConfigMap. The workflow worker reads `fan-api-config` and runs the code defaults (the same values).
- **After.** The job no longer calls Gemini, so the pins move to the prod `fan-api` ConfigMap, which the worker reads, with `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER=flex` beside them. They are removed from the job ConfigMap so no stale pin is left.
- **What stays in the job ConfigMap.** `GCP_GEMINI_SEARCH_CACHE_TTL=96h`: the skip rules run in the job.

## Risks / Trade-offs

- [Flex stays busy for most of a day, as in the trial] → each search keeps trying, up to hourly, until 20 h after its search time. Waiting attempts hold no slot, so every search gets its turn. Searches still busy at 20 h end as failed with error kind unavailable. The observation decides on the fallback.
- [The spend cap refuses calls in prod] → nothing is stored, as the paid-api-spend-cap spec requires. Prod shows both forms (checked in task 1.2, Cloud Logging):
  - 403 "Spend cap breached": PermissionDenied, not retried; the search ends as failed and the next daily run searches again;
  - 429 "temporarily rate-limited to prevent exceeding its monthly spending cap": cannot be told from a busy refusal by status, so the search keeps trying for 20 h. The refusals are not billed, and raising the cap within the window recovers the search.

  Depleted prepaid credits answer 402: FailedPrecondition, not retried.
- [An Organizer starts to represent the Artist, or its activity ends, while a search waits] → every attempt checks both before calling (D2 step 1).
- [Filtering runs hours after the search started, while CreateFromDiscovered of an earlier search is still running] → dedup at the database natural key (`UNIQUE (series_id, local_event_date, venue_id)`) is the source of truth, as today.
- [The worker now builds the Gemini searcher] → the worker gets the Gemini key from `fan-api-backend-secrets`, which already holds `GCP_GEMINI_SEARCH_API_KEY`. Its startup fails loudly if the key is missing, as the API server does.

## Migration Plan

1. cloud-provisioning PR: the ConfigMap pins (D8). Merged first, it changes nothing that runs: the current code ignores the tier variable, and the moved model and thinking pins equal the code defaults.
2. backend PR: the workflow, queue, searcher tier, reporting and preview removal. Merge and release. The release retags the images into prod, and `bump-prod-pin.yml` in cloud-provisioning rewrites every backend prod pin and pushes to main; ArgoCD then syncs the job, consumer, API server and worker together. The prod pins are CI-written, never edited by hand (`k8s/namespaces/backend/overlays/prod/kustomization.yaml`, "Bumping on release").
   - In-flight inline searches at the moment of the rollout finish in their old Pods.
   - The first daily run after the rollout starts workflows.
3. Rollback: set `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER=standard` (no release) to leave Flex. A waiting attempt reads the setting when it runs, so it calls the standard tier.
   - **Do not revert the release pin.** The previous worker does not register `search-concerts` and could not run the attempts already stored (Context, Workflows). Their ConcertSearch rows would stay pending for 20 h.
   - **A defect in the new code is fixed by a new release.** If the code itself must go, first cancel every `search-concerts` run that has not ended, then revert the pin. The Artists are searched again 20 h later by the daily run.

## Observation (Flex only, no fallback)

For 3 days after the rollout, read in prod (read-only):
- PostHog `$ai_generation` with `service_tier = flex`: successes, 503/429 counts, latency percentiles;
- `concert.search.completed` by outcome;
- the DBOS workflow records of `search-concerts` (through the cloud-provisioning read-only db-proxy runbook): attempts per search, and time from the search time to the last attempt's end.

Results go into the Results section below. The decision on a standard-tier fallback and on a shorter freshness window is made from them, in a separate change.

## Results

Interim, as of 2026-11-28. Task 4.2 completes it after the scheduled run of 2026-12-02 09:00 UTC, the first one that searches again (`GCP_GEMINI_SEARCH_CACHE_TTL=96h` after the manual run).

**Rollout runs**

| Run (UTC) | Job duration | Searches started |
|---|---|---|
| 2026-11-27 15:57, manual | 12 s | searched below |
| 2026-11-28 09:00, scheduled | 8 s | none, every artist inside the 96 h cache TTL |

**Searches of the manual run** (PostHog `$ai_generation` with `service_tier = flex`, and `concert.search.completed`)

- 98 searches of 98 artists ended: 85 `nothing_new`, 13 `found`, none failed and none gave up at 20 hours.
- 260 calls: 98 succeeded and 162 failed (2.65 calls per search). A failed call reported no tokens.
- Success rate per call by hour: 37% (15:00, 84 calls), 36% (16:00, 159 calls), then 3 of 9, 4 of 6 and 2 of 2. The later hours are too small to show a time-of-day effect.
- Time from the start of the run to the end of a search: median 4 minutes; 95th percentile 68 minutes (`nothing_new`) and 152 minutes (`found`); the last search ended after 3 h 9 min.
- Latency of a successful call by hour: median 13 to 26 s in the two large hours, longest 639 s.

**Tokens and cost** (successful calls, same model; billing export, JPY)

| Day | Tier | Successful calls | Avg input | Avg output (with thinking) |
|---|---|---|---|---|
| 2026-11-23 | standard | 16 | 9,540 | 2,959 |
| 2026-11-27 | standard | 13 | 10,802 | 2,052 |
| 2026-11-28 | flex | 98 | 7,119 | 1,379 |

- Token cost per search: 5.6 on the standard tier (11-23), 1.6 on flex. The unit prices on the bill are the flex half prices; why a flex call used fewer tokens is not established, and the standard samples are small.
- Google Search queries cost about 2.2 each on the November bill (171 queries, 378.7, on the flex run), because November's free queries were used up around 11-21. If the 5,000 free queries a month return on 12-01, about 1,900 queries a month fit in them and the cost is tokens alone, about 1,800 a month. The December bill has not confirmed this.

**Not yet observed:** a scheduled run that searches, the time-of-day pattern over several days, and the INFO log level of a busy attempt in prod (covered by a unit test).

**Recommendation:** none yet; the standard-tier fallback and the freshness window are decided from the completed observation.
