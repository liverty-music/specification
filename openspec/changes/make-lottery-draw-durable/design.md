## Context

See proposal.md - Why. Facts this design depends on:

- **The draw today** (`backend/internal/usecase/lottery_entry_uc.go:427-520`): `RunLotteryDraw(…, uc.newRand())` with a crypto-seeded random source per call (`:474`, `:539-550`), then `Capture` / `release` per entry (`:475-496`), then `PersistDrawOutcome` (`:499`). `release` only logs a failure (`:526-533`), and `Release` of a captured authorization returns FailedPrecondition (`infrastructure/payment/stripe_card_authorization.go:222-223`).
- **Sweepers** run as goroutines in the fan workload only (`internal/di/provider.go:521-548`, `pkg/config/config.go:1096-1105`): the 1-minute lottery draw and issuance sweepers are the two this change replaces.
- **Database**: one Cloud SQL Postgres (`db-f1-micro`, `max_connections=25`, shared with Zitadel; `cloud-provisioning/src/gcp/components/postgres.ts:209-216`, `zitadel-monitoring.ts:318-321`). The app schema is `app`; Atlas applies migrations as `postgres` with `search_path: app` (`backend/k8s/atlas/base/atlas-migration.yaml`), and each workload's IAM user has only DML on `app` (`migrations/20250726000000_bootstrap_app_schema.sql`). The fan workload's pool is a `pgxpool` behind the Cloud SQL connector with IAM auth, 5 connections in prod (`internal/infrastructure/database/rdb/postgres.go:25-63`, `cloud-provisioning … overlays/prod/fan-api/configmap.env`).
- **Trace context**: `fix-trace-propagation` injects W3C `traceparent` / `tracestate` into message metadata with the global propagator and extracts it before each consumer span.
- **Admin alert**: `LogKeyNeedsOperator` (`usecase/order_issue_uc.go:42`) drives a log-based alert (`cloud-provisioning/src/gcp/components/monitoring.ts:269`).
- **DBOS Transact Go v1.7.0** (2026-10-15), read in its source at `98cea9b`: `Config.SystemDBPool *pgxpool.Pool`, `DatabaseSchema` (default `dbos`), `SkipMigrations`, `ApplicationVersion`, `ExecutorID` (default `local`); `dbos migrate --print-migrations all` and `--print-user-role --app-role <role>` print the SQL instead of running it; `RegisterQueue` with `WithPartitionQueue`, `WithPartitionConcurrency`, `WithRateLimiter`; `ApplySchedules`; step options `WithStepMaxRetries`, `WithStepBaseInterval`, `WithStepBackoffFactor`, `WithStepMaxInterval`, `WithStepRetryPredicate`; `Patch`; `WithWorkflowAttributes` / `WithEnqueueAttributes`. `Launch` recovers the PENDING workflows of its executor ID and application version. Step outputs are JSON-encoded. The Go module has no OpenTelemetry dependency.

## Goals / Non-Goals

**Goals:**
- One durable mechanism for "do the next step until it is done" on the lottery path, with the order of steps written in the usecase.
- No change to how a usecase is tested: its dependencies stay interfaces with mockery mocks.

**Non-Goals:**
- The first-come checkout and `FulfillPayment` for checkouts (`unify-order-issuance`).
- The other sweepers and the notification fan-out.
- DBOS Conductor or the enterprise features.

## Decisions

### A workflow interface in the usecase layer; DBOS stays in infrastructure

`internal/usecase/workflow.go` declares the interface the usecases call, the way `EventPublisher` is declared (`backend/AGENTS.md:74`):

```go
// Flow runs the steps of one durable workflow.
type Flow interface {
	// Step runs fn once to completion for this workflow and name; on a resumed
	// run it returns the recorded result without calling fn.
	Step(ctx context.Context, name string, fn func(context.Context) ([]byte, error), opts ...StepOption) ([]byte, error)
	// Enqueue starts the named workflow with input once per id.
	Enqueue(ctx context.Context, workflow, id string, input any, partition string) error
}

func Step[R any](ctx context.Context, f Flow, name string, fn func(context.Context) (R, error), opts ...StepOption) (R, error)
```

A workflow is a usecase method of the form `func(ctx context.Context, f Flow, in Input) (Out, error)`. `internal/infrastructure/workflow/dbos.go` registers each one with `dbos.RegisterWorkflow` under a stable name and passes a `dbosFlow` that maps `Step` to `dbos.RunAsStep` and `Enqueue` to `dbos.Enqueue`, which DBOS checkpoints as a step when it is called inside a workflow (`WithEnqueueWorkflowID` gives the id). A unit test passes a fake `Flow` that calls `fn` directly and records the enqueues.

- **Why not call DBOS from the usecase**: the usecase would import the engine and take `dbos.Context`, so its tests would need a DBOS runtime and Postgres.
- **What the interface cannot hide**: a workflow must run the same steps in the same order on a resumed run. Values that change between runs (the clock, ids, the random order of the draw) are read inside a step. A change to the steps of a registered workflow uses `dbos.Patch` (below). These rules go into `backend/AGENTS.md` with this change.

### The draw records first, then fans out

```
DBOS schedule "draw-due-sales" (* * * * *)
  -> LotteryEntryUseCase.DrawDueSales: step ListDueForDraw; Enqueue Draw(sale) id=draw:<sale>
LotteryEntryUseCase.Draw(sale)                                  workflow
  for each TicketType:
    step ListUndrawnForTicketType(tt)
    step RunLotteryDraw(entered, quantity, rng)                  random order recorded once
    step RecordDrawOutcome(tt, outcome)                          the only multi-row write
    Enqueue OrderUseCase.Issue(entry)        id=issue:<entry>    per Won entry, partition <sale>
    Enqueue CardAuthorizationUseCase.Release id=release:<ca>     per Lost entry and Draft
  step TicketSale.RecordDraw(sale, now)
  step PublishEvent(ORDER.lottery_entry_drawn) per entry
OrderUseCase.Issue(entry)                                       workflow
  step GetByLotteryEntryID / Get(entry) -> Won
  step Capture(ca)                     retried on Unavailable for 24 h
    FailedPrecondition -> step RevertWin, step Release, step signal Lost
  step Get(ca), TicketType.Get, Organizer -> step Order.Issue
  step PublishEvent(ORDER.paid)
CardAuthorizationUseCase.Release(ca)                            workflow
  step Release(ca)                     retried on Unavailable for 24 h
```

- **`RecordDrawOutcome` is per TicketType** because the invariant "the Won tickets of a TicketType never exceed its quantity" is per TicketType; reading and computing need no transaction, because after the window closes no entry can be confirmed and none can be withdrawn (`remove-lottery-entry-withdrawal`). It updates `WHERE state = 1` rows in one transaction and compares the stored outcome when no row is Entered (spec "Recorded again" / "Another outcome").
- **`RunLotteryDraw` keeps its name** for this change. The spec layer forbids a rename inside a behavior change ("renaming the method … is a change of its own"); dropping `Run` from it is a follow-up.
- **The analytics Won signal is sent at the draw and a Lost signal again from `Issue` on a failed capture**, so the mart reads the last result per entry.

### 24-hour retries

`Capture` and `Release` steps use `WithStepRetryPredicate(apperr.IsUnavailable)`, `WithStepBaseInterval(1*time.Minute)`, `WithStepBackoffFactor(2)`, `WithStepMaxInterval(1*time.Hour)` and `WithStepMaxRetries(30)`: 1, 2, 4 … 32 minutes, then hourly, about 24 hours in all. A JPY authorization lasts 30 days (`docs/payments-design.md`), so the retries end well before it lapses. When retries run out the workflow ends in ERROR and logs `LogKeyNeedsOperator`; an admin resumes it with `dbos workflow resume` once the cause is fixed.

### Queues and the schedule

- One queue `payment`: `WithPartitionQueue()` keyed by the TicketSale id, `WithPartitionConcurrency(5)` and `WithRateLimiter(&dbos.RateLimiter{Limit: 20, Period: time.Second})`, so one large sale cannot use every connection or exceed the payment provider's rate. The numbers are provisional and set from the load test in tasks.
- `dbos.ApplySchedules` installs `draw-due-sales` with `Schedule: "* * * * *"` and `AutomaticBackfill: true`. A backfilled tick only enqueues `Draw` with the same id, which DBOS deduplicates.
- Rejected: a Kubernetes CronJob for the schedule. It starts a Pod for every run, and it would need its own DBOS client to enqueue.

### Database placement and migrations

- The DBOS system tables live in schema `dbos` of the same database, so the workflow state is backed up and restored with the business data (point-in-time recovery is on for the instance).
- The Atlas migration is generated, not hand-written: `dbos migrate --print-migrations all` for the tables and functions, and `dbos migrate --print-user-role --app-role <fan IAM role>` for the grants, both committed as one migration under `backend/k8s/atlas/base/migrations/`. The fan workload starts DBOS with `SkipMigrations: true` and `DatabaseSchema: "dbos"`, so the app role keeps DML only.
- Upgrading the module: run `dbos migrate --print-migrations <first new number>` and commit the output as a new Atlas migration before the version bump. This procedure goes into `backend/AGENTS.md`.
- `backend/scripts/lint-schema.sh` enforces the entity schema policies (no SERIAL, TIMESTAMPTZ, comments on every table and column) on `schema.sql`. The `dbos` tables belong to the engine, not to an entity, and do not follow them, so the script is limited to the `app` schema.

### Connections

DBOS gets its own `pgxpool` (`MaxConns: 3`) built from the same Cloud SQL connector dialer and IAM user as the app pool, passed as `Config.SystemDBPool`. Rejected: sharing the 5-connection app pool, because the engine's notification listener holds one connection and its queue polling would compete with request handling. The fan workload then uses at most 8 connections.

### Where workflows run

Only the fan workload calls `dbos.Launch`, as only it runs the payment sweepers today. `ApplicationVersion` is pinned to a constant (`"1"`) and `ExecutorID` stays `local`, so the Pod that starts after a deploy recovers every PENDING workflow of the one before it. A change to a registered workflow's steps wraps the new steps in `dbos.Patch(ctx, "<name>")` instead of bumping the version.

### Trace context

`Enqueue` writes the caller's `traceparent` / `tracestate` into the workflow attributes (`WithEnqueueAttributes`). The DBOS implementation starts a span per workflow run whose parent is the extracted context, and a child span per step. A run resumed after a restart starts a new root span with a link to the stored context, as `fix-trace-propagation` does for job items.

### FulfillPayment for lottery charges

The `payment_intent.succeeded` notice of a lottery capture arrives after `Issue` captured. `FulfillPayment` finds the LotteryEntry and returns without effect, so the Order is announced once, by `Issue`. Rejected: issuing from the notice and ending `Issue` after the capture. The capture result is the synchronous response of the call the platform made; waiting for the notice adds a dependency on the provider's delivery (retried for up to 3 days) and a second path to the same Order.

## Risks / Trade-offs

- [DBOS Go is 3 months past 1.0 and its vendor is seed-funded] → The engine is a library and its state is in the platform's own Postgres, readable with SQL; the workflow interface keeps it out of the usecases.
- [Two Pods overlap during a rolling deploy, and the new one recovers workflows the old one is still running] → Every step is idempotent (Capture and Release by idempotency key and status, Order.Issue by AlreadyExists, RecordDrawOutcome by comparison), so a step run twice has no second effect. The DBOS fencing tokens of v1.6 are checked in the integration test.
- [The connection budget of the instance is already close to 25] → Tasks list every workload's pool size from the prod config maps before the rollout; the DBOS pool is 3.
- [Workflow code changed without `Patch` breaks resumed runs] → The AGENTS.md rule above, and the integration test resumes a run recorded by the previous code.
- [A Won entry has no Order for a few seconds] → Readers that need a paid purchase read the Order, not the state (`Order.GetByLotteryEntryID`); the organizer's stats count Won as allocated.

## Migration Plan

1. backend: generated `dbos` migration; the workflow interface and the DBOS implementation; `Draw`, `Issue`, `Release`; removal of `RunDraw`, `IssueFromCapturedWin`, `IssueDueWins` and the two goroutines.
2. Before the deploy, read-only in prod: list sales due for a draw and Won entries without an Order. The product has no users, so both are expected to be empty. A due sale is drawn by the new `DrawDueSales` after the deploy. A Won entry without an Order has no trigger in the new code (the DBOS CLI cannot enqueue): if one is found, stop and issue it with the old code before deploying.
3. Deploy, then confirm the AtlasMigration status, the rollout, and that `dbos.workflow_status` receives the `draw-due-sales` runs.

Rollback: revert the backend release. The `dbos` schema stays and is unused; no business table changes shape.
