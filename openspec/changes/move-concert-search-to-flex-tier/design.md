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
- **Workflows** (`internal/infrastructure/workflow`). These are DBOS workflows run only by the `workflow-worker` Deployment.
  - A step that fails with Unavailable or DeadlineExceeded is retried at 1 s doubling to at most 1 h (`stepOptions`).
  - `WithDeadline` stops a run and reports it for an admin.
  - `WithQueue` with `RegisterQueue(name, n)` caps concurrency across workers.
  - Starting an id that exists returns the existing run.
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

SearchNewConcerts keeps its skip rules and the pending upsert. It then starts the workflow `search-concerts` with:
- id `search-concerts:<artist>:<search time µs>`, the same business key as `create-from-discovered`;
- input: the Artist id, the search time and the trigger;
- queue `concert-search`;
- deadline: the search time plus 20 h.

The workflow is `ConcertUseCase.RunSearch` (registered in `internal/di/worker.go`). It holds the body of today's `executeSearch`.

Why a workflow:
- **Project rule.** The event-delivery spec ("Work for one receiver is started as a workflow") says a request for one receiver to do work is started as a workflow, not announced.
- **The platform already provides what the retry needs:**
  - the id makes a repeated start a no-op, which is exactly-once per search;
  - step retries with durable backoff up to 1 h;
  - a deadline;
  - a concurrency cap;
  - recovery after a worker restart.

A NATS subject with `NakWithDelay` would need a new stream subject, a Consumer CR, a delivery-count-based delay and an `ackWait` longer than a 15-minute call. It would also break that rule.

**Why the job and consumer start the workflow inline.** The durable-workflows spec allows API servers, consumers and jobs to start workflows. The pending upsert and the start are two writes, not one transaction. If the start fails after the upsert, SearchNewConcerts fails and the ConcertSearch stays pending until the 20-hour timeout. Either the first-follow consumer's redelivery or the next daily run starts it again; the redelivery is skipped as in progress, so the daily run recovers it. That gap is accepted rather than adding a transactional start.

### D2. Steps of the workflow

1. `search`: get the Artist and its OfficialSite, list upcoming Concerts and pending ConcertCandidate keys, then call Concert.Search and filter. It returns the new series.
   - Retried by the step policy on Unavailable and DeadlineExceeded.
   - Each run of the step re-reads the catalog, so the filter sees the catalog at the time the result arrives.
2. `hand-on`: when series remain, start `create-from-discovered` with today's id, then MarkFound.
3. `record-end`: UpdateStatus to completed or failed, and send `concert.search.completed` with the trigger from the input.

A permanent error in step 1 or 2 makes the run end with that error after `record-end` sets failed. The durable-workflows spec then reports it for an admin. Today such a failure is only a log line of the job.

### D3. Flex in the searcher, configurable, default on

- **Config.** `gemini.Config` gets `ServiceTier`, set on `GenerateContentConfig.ServiceTier` of every concert search call. `pkg/config` reads `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER`; the code default is `flex`, and `standard` sends no tier.
- **Call timeout.** `geminiCallTimeout` becomes 15 minutes when the tier is flex and stays 120 s otherwise.
- **Busy answers.** A 503 or 429 maps to Unavailable as today, so the existing 3 in-process attempts run, and then the step retry takes over.
- **Ticket sale searcher.** Unchanged: it never succeeded at Flex in the trial.

**Worst case for one step.** 3 attempts × 15 min plus the backoffs, about 45 minutes. A worker redeploy in the middle reruns the step after the new worker starts. The rerun repeats at most one interrupted call.

### D4. Queue `concert-search` with concurrency 8

- Registered in the worker next to the payment and checkout queues.
- 8 keeps the daily batch (about 80 Artists) moving when calls take minutes, and stays far below the project's Gemini request-rate limits.
- Gemini calls hold no database connection. The steps' short reads share the worker's pool, as `create-from-discovered` already does.

### D5. Pending timeout 20 hours, deadline 20 hours

- **20 h < 24 h.** A search abandoned at its deadline frees the Artist before the next daily run at the same hour, so the next run requests a fresh search with a new id.
- **The workflow deadline** uses the same 20 h counted from the search time. The background search can never outlive the window in which no second search starts.
- **A run stopped at the deadline is reported for an admin** (durable-workflows). During the Flex-only observation this is the signal that Flex failed for a whole day. If it happens on more than a few Artists, the next change adds the standard-tier fallback.

### D6. The daily job and first-follow consumer

- **Daily job.** It keeps its loop and its 3-consecutive-failures stop. A failure now means the ConcertSearch could not be recorded or the workflow could not be started, which points to the database, so stopping still makes sense. The job ends in seconds.
- **First-follow consumer.** `ackWait` 10 minutes stays and is now far above the handler's time. `SearchNewConcertsOnFirstFollow` is unchanged.
- **Previews.** `SearchNewConcerts` returns only an error (the previews and `previewConcerts` are deleted), and the `ConcertUseCase` interface and mocks follow.

### D7. Reporting

- **Service tier on each generation.** `posthog.LLMGeneration` gets `ServiceTier`, reported as `service_tier`. Cost from PostHog's own price table reads as standard pricing; the billing export stays the source of truth for money. Sending our own cost figures was rejected: it would put a price table in code that goes stale on each repricing.
- **Searches that end.** `concert.search.completed` is still sent once per search that called Gemini, from `record-end`.
- **Searches stopped at the deadline.** They send no signal; they are counted from the workflow records in the observation.

### D8. Model and tier pins follow the process that calls Gemini

- **Before.** The prod model and thinking pins live in the `concert-discovery` job ConfigMap. The workflow worker reads `fan-api-config` and runs the code defaults (the same values).
- **After.** The job no longer calls Gemini, so the pins move to the prod `fan-api` ConfigMap, which the worker reads, with `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER=flex` beside them. They are removed from the job ConfigMap so no stale pin is left.
- **What stays in the job ConfigMap.** `GCP_GEMINI_SEARCH_CACHE_TTL=96h`: the skip rules run in the job.

## Risks / Trade-offs

- [Flex stays busy for most of a day, as in the trial] → each search keeps retrying, up to hourly, until its 20-hour deadline. No duplicate starts, and the run is reported. The observation decides on the fallback.
- [A deadline report per Artist on a bad day floods the admin view] → accepted for the observation period. The fallback change removes the cause.
- [The spend cap refuses calls (403) in prod] → nothing is stored, as the paid-api-spend-cap spec requires. Whether the searcher maps this refusal to a transient error is checked in task 1.2. If it does, the step retries until the deadline; if not, the run ends at once. Either way, the run is reported for an admin.
- [Filtering runs hours after the search started, while CreateFromDiscovered of an earlier search is still running] → dedup at the database natural key (`UNIQUE (series_id, local_event_date, venue_id)`) is the source of truth, as today.
- [The worker now builds the Gemini searcher] → the worker gets the Gemini key from `fan-api-backend-secrets`, which already holds `GCP_GEMINI_SEARCH_API_KEY`. Its startup fails loudly if the key is missing, as the API server does.

## Migration Plan

1. backend PR: the workflow, queue, searcher tier, reporting and preview removal. Merge and release.
2. cloud-provisioning PR: the pins (D8) and the prod release pin for the job, consumer, API server and worker images. It goes live on merge through ArgoCD.
   - In-flight inline searches at the moment of the rollout finish in their old Pods.
   - The first daily run after the rollout starts workflows.
3. Rollback:
   - set `GCP_GEMINI_CONCERT_SEARCH_SERVICE_TIER=standard` (no release) to leave Flex;
   - or revert the release pin to go back to inline searches. Workflows already started finish under the old searcher's rules.

## Observation (Flex only, no fallback)

For 3 days after the rollout, read in prod (read-only):
- PostHog `$ai_generation` with `service_tier = flex`: successes, 503/429 counts, latency percentiles;
- `concert.search.completed` by outcome;
- the DBOS workflow records of `search-concerts` (through the cloud-provisioning read-only db-proxy runbook): run time from start to end, step attempts, runs stopped at the deadline.

Results go into the Results section below. The decision on a standard-tier fallback and on a shorter freshness window is made from them, in a separate change.

## Results

To be written after the observation (task 4.2).
