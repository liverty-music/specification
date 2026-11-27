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
  - A call is retried for 3 attempts at 1 s, 2 s and 4 s.
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

The data check is `artist.CheckSearchable`, which today runs at the top of `executeSearch`, after the upsert. It stays in SearchNewConcerts, after the upsert and before the start: an Artist with no name or no MBID fails SearchNewConcerts with Internal and the ConcertSearch becomes failed, as today (spec "Artist data required"). No attempt is started for it.

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
   - **The search was replaced.** The ConcertSearch is no longer pending with this search time. The attempt changes nothing.
   - **The Artist may no longer be searched.** Its activity has ended, or an active Organizer represents it. The attempt goes to `record-end` as nothing new. The signal is sent only when an earlier attempt called Concert.Search, that is, when the attempt number is above 1.

   Both checks ran only before the pending upsert before this change. They are repeated because an attempt can start hours after the request.
2. `search`: if the search time is 20 h or more in the past, skip the call and treat the attempt as busy. Otherwise:
   - read the OfficialSite, the upcoming Concerts and the pending ConcertCandidate keys;
   - call Concert.Search once;
   - filter the result.

   The step returns one of three results:
   - **the new series**;
   - **busy**: Concert.Search failed with Unavailable or DeadlineExceeded;
   - **failed**: the error kind of a permanent error.

   Busy and failed are values, not errors, so the step retry policy never runs.
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

A failure to start `create-from-discovered` is a permanent error and ends as failed, as today. The run itself ends successfully in every case above, so no outcome is reported for an admin. A run that fails outside these paths (a bug) still is, per durable-workflows.

Attempt numbers count from 1, and every attempt reports its call (Concert.Search "Each external call reports its usage"). The observation therefore sees each attempt.

### D3. Flex in the searcher, configurable, default on

- **Config.** `gemini.Config` gets `ServiceTier`, set on `GenerateContentConfig.ServiceTier` of every concert search call. `pkg/config` reads `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER`; the code default is `flex`, and `standard` sends no tier.
- **Call timeout.** `geminiCallTimeout` becomes 15 minutes when the tier is flex and stays 120 s otherwise.
- **Busy answers.** A 503 or 429 maps to Unavailable as today. The existing 3 in-process tries run within one attempt; then the attempt is busy (D2).
- **Ticket sale searcher.** Unchanged: it never succeeded at Flex in the trial.

**Worst case for one attempt.** 3 tries × 15 min plus the backoffs, about 45 minutes, during which the attempt holds a queue slot. A worker redeploy in the middle reruns the `search` step after the new worker starts. The rerun repeats at most one interrupted call.

### D4. Queue `concert-search` with concurrency 8

- Registered in the worker next to the payment and checkout queues.
- 8 keeps the daily batch (about 80 Artists) moving when calls take minutes, and stays far below the project's Gemini request-rate limits.
- Gemini calls hold no database connection. The steps' short reads share the worker's pool, as `create-from-discovered` already does.
- **A search can wait behind a batch.** A first-follow search started during the daily batch may wait for free slots. The worst case is about 80 × 45 min / 8, about 7.5 h; when Flex answers quickly, it is minutes. Nobody waits for it (stories/follow-an-artist). The order in which waiting attempts get a slot is the queue's own; this change does not set priorities.

### D5. One 20-hour window, checked against the search time

- **20 h < 24 h.** A search that gives up frees the Artist before the next daily run at the same hour, so the next run requests a fresh search with new ids.
- **The window is checked by the attempt itself** (D2 step 2), against the search time, so time in the queue counts. No DBOS deadline is set, because it would count from the dequeue.
- **The last call can end after the window.** An attempt started just before 20 h can finish its call up to about 45 min later, still well before the next daily run at 24 h. Only the daily run and a first follow of a never-searched Artist start searches, so no newer search can begin in that gap.
- **Giving up sends the failed signal with the error kind unavailable** (D2 step 5). During the Flex-only observation, the count of these signals shows how often Flex failed for a whole day. No admin report is raised for it.

### D6. The daily job and first-follow consumer

- **Daily job.** It keeps its loop and its 3-consecutive-failures stop. A failure now means the ConcertSearch could not be recorded or the workflow could not be started, which points to the database, so stopping still makes sense. The job ends in seconds.
- **First-follow consumer.** `ackWait` 10 minutes stays and is now far above the handler's time. `SearchNewConcertsOnFirstFollow` is unchanged.
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
- [The spend cap refuses calls (403) in prod] → nothing is stored, as the paid-api-spend-cap spec requires. Task 1.2 checks whether the searcher maps this refusal to a transient error:
  - if it does, the search keeps trying until 20 h and ends as failed with error kind unavailable;
  - if not, it ends at once as failed with its error kind.
- [An Organizer starts to represent the Artist, or its activity ends, while a search waits] → every attempt checks both before calling (D2 step 1).
- [Filtering runs hours after the search started, while CreateFromDiscovered of an earlier search is still running] → dedup at the database natural key (`UNIQUE (series_id, local_event_date, venue_id)`) is the source of truth, as today.
- [The worker now builds the Gemini searcher] → the worker gets the Gemini key from `fan-api-backend-secrets`, which already holds `GCP_GEMINI_SEARCH_API_KEY`. Its startup fails loudly if the key is missing, as the API server does.

## Migration Plan

1. backend PR: the workflow, queue, searcher tier, reporting and preview removal. Merge and release.
2. cloud-provisioning PR: the pins (D8) and the prod release pin for the job, consumer, API server and worker images. It goes live on merge through ArgoCD.
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

To be written after the observation (task 4.2).
