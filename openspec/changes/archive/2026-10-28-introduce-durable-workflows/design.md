## Context

See proposal.md - Why. The facts this design rests on:

- **Today's recovery** is a set of goroutine sweepers in the fan workload (`backend/internal/di/provider.go:521-548`, started when `RunsPaymentSweepers()`, `backend/pkg/config/config.go:1096-1105`), plus CronJobs (`cloud-provisioning/k8s/namespaces/backend/base/cronjob/`). A purchase that needs an admin is logged with `LogKeyNeedsOperator` (`backend/internal/usecase/order_issue_uc.go:37-42`) and paged by a log-based alert (`cloud-provisioning/src/gcp/components/monitoring.ts:247-296`), which assumes a sweeper re-logs every minute (`autoClose: 3600s`).
- **Events** get a fresh UUIDv7 per publish today (`backend/internal/infrastructure/messaging/cloudevents.go:26-39`), and the publisher sets it as the JetStream `Nats-Msg-Id` (`messaging/publisher.go:53-55`, 2-minute duplicate window). A fact announced twice is two events (`usecase/event_publisher.go:8-15`).
- **Database**: one Cloud SQL Postgres (`db-f1-micro`, `max_connections=25`, shared with Zitadel). The app schema `app` is migrated by the Atlas Operator as `postgres` (`backend/k8s/atlas/base/atlas-migration.yaml`). Workload IAM users get DML through a loop over every `%@%.iam` role (`migrations/20260817010000_grant_fan_api_app_schema.sql`).
- **Single-pod guarantee precedent**: event-consumer runs with `maxSurge: 0, maxUnavailable: 1`, so the old Pod stops before the new one starts (`cloud-provisioning/k8s/namespaces/backend/base/event-consumer/deployment.yaml:18-27`).
- **Prod access for people** is the `db-proxy` runbook (`cloud-provisioning/docs/runbooks/cloud-sql-access.md`), which is read-only.
- **DBOS Transact Go v1.7.0**, read in its source at `98cea9b`. That commit is two commits after the v1.7.0 tag (`3397057`) and unreleased; the one difference that matters is that v1.7.0 still requires `EnablePatching` for `Patch` and `DeprecatePatch` (`dbos/workflow.go:4530`). Line numbers below are of `98cea9b`:
  - `Launch` recovers the PENDING workflows of its executor id and application version (`dbos.go:939`, `recovery.go:9`).
  - Starting an existing workflow id returns the existing handle (`WorkflowIDReusePolicyReturnExisting`, `workflow.go:899`).
  - Step retries run in memory with `WithStepRetryPredicate`, `WithStepBaseInterval`, `WithStepBackoffFactor`, `WithStepMaxInterval` and `WithStepMaxRetries` (`workflow.go:2460-2530`, `:2681`).
  - A workflow deadline is stored (`workflow_deadline_epoch_ms`) and enforced by a timeouts monitor (`dbos.go:977`).
  - Failed states: `ERROR`, `MAX_RECOVERY_ATTEMPTS_EXCEEDED` (default 100, `workflow.go:575-587`), `CANCELLED`.
  - `NewClient` enqueues, retrieves, lists, resumes, forks and deletes workflows without running them (`dbos.go:806-839`).
  - `ApplySchedules` installs cron schedules.
  - `SkipMigrations` and `DatabaseSchema` configure the system tables; `dbos migrate --print-migrations` and `--print-user-role` print their SQL.
  - Step outputs are JSON. There is no OpenTelemetry integration, no metrics endpoint and no automatic deletion of old workflows; retention, metrics and cross-executor recovery are DBOS Conductor features.
  - `NewContext` connects, verifies or migrates the schema and pings, bounded by `SystemDBStartupTimeout` (default 2 minutes); a failed context is terminal and a fresh one must be created (`docs/golang/reference/configuration.md` "System database startup").
  - Cancelling the context a workflow was started under durably cancels the workflow; a shutdown does not (`workflow.go:1684-1696`, `docs/golang/tutorials/workflow-management.md`).
  - `GetWorkflowID` and `GetStepID` are available inside a workflow; the step id is the step's position, the same on every run (`dbos.go:299-300`, `workflow.go:45`).
- **DBOS documentation** (dbos-inc/dbos-docs at `5c118aa`, 2026-10-16):
  - "We do not recommend setting [the system database pool] to less than 5" (`production/checklist.md`).
  - "have the [readiness] probe wait until DBOS is launched"; each replica needs a unique executor ID, assigned automatically only with Conductor (`production/hosting-with-kubernetes.md`).
  - Without Conductor, "each time you restart your application's process, DBOS recovers all workflows that were executing before the restart" on a single server, and each executor recovers only its own executor ID in a distributed setting (`production/workflow-recovery.md`).
  - A workflow, queue or schedule is run only by the application (`AppName`) that owns it (`explanations/sharing-a-system-database.md`).
  - Conductor: DBOS-hosted Pro is $99 a month; a self-hosted Conductor needs a paid license in production (`conductor/self-hosting/hosting-conductor.md:228`, dbos.dev/pricing).

## Goals / Non-Goals

**Goals:**
- One mechanism that later changes use instead of a sweeper per flow, with the order of steps written in the usecase.
- No business behavior changes in this change; it can be verified in prod with its own GC and report schedules.

**Non-Goals:**
- Moving any existing flow; the lottery and checkout changes do that.
- DBOS Conductor or the enterprise features (see "Conductor" below).
- A larger Cloud SQL tier; it waits until real users arrive.

## Decisions

### Engine: DBOS Transact Go

Chosen because it is a library over the database the platform already runs: no server, no second store, state readable with SQL.

| Rejected | Why |
|---|---|
| Temporal (self-hosted or Cloud) | Self-hosting is a multi-service cluster with its own persistence and visibility stores. Cloud puts an external service on the payment path. |
| Restate | A second durable store beside Cloud SQL; its server is BSL. |
| River | A job queue, not a workflow engine: the order of steps would be split across job handlers. |
| One sweeper per flow (today) | Each flow needs its own state column, ticker, retry rule and admin report (proposal - Why). |

### The workflow worker owns execution

- New entrypoint `cmd/worker`. It runs the fan workload's configuration and identity and calls `dbos.Launch`, which starts the queue runners, the schedules and the recovery of its own pending workflows.
- New Deployment `workflow-worker`: `replicas: 1`, `strategy.rollingUpdate` with `maxSurge: 0` and `maxUnavailable: 1`, as event-consumer does. It uses the `fan-api` service account and secrets, so it holds the same Stripe and database identity as the code it takes over, and no new IAM user is needed.
- `ExecutorID: "workflow-worker"` and `ApplicationVersion: "1"` are fixed. A new Pod therefore recovers exactly what the old one left, and no two Pods ever run at once. This is the documented single-server recovery.
- `AppName: "liverty-music-backend"` for the worker and for every client, because only the owning application dequeues, runs and recovers a workflow.
- A change to the steps of a registered workflow follows the documented lifecycle: wrap the new steps in `dbos.Patch(ctx, "<name>")`, later replace it with `dbos.DeprecatePatch`, and remove it once no workflow started before it is running. The version is never bumped for that. `EnablePatching: true` is set, because v1.7.0 refuses `Patch` without it; DBOS defaults the version only when it is empty, so the fixed `ApplicationVersion` stays. `Flow` therefore has `DeprecatePatch` beside `Patched`.
- API servers, consumers and jobs create a `dbos.Client` (`dbos.NewClient`) and never call `Launch`, so the fan API can go back to 2 replicas without either replica recovering the other's work. A client never starts a workflow in-process, so cancelling a request context can never cancel a workflow.
- **Readiness**: the worker's readiness probe succeeds only after `Launch` returned; its liveness probe checks only the process, as the API liveness rule of `health-probes` does.
- **Startup**: `SystemDBStartupTimeout` is 5 minutes, and a failed `NewContext` is retried with a fresh context until then, to meet `startup-dependencies` ("keep trying … for at least 5 minutes").
- **Logs**: `Config.Logger` is the project's slog logger, so DBOS's own lines follow `structured-logging`.
- **Queues**: `RegisterQueue` in code is the only source of a queue's settings; the settings are never changed at runtime, because the next start overwrites them (`docs/golang/tutorials/queue-tutorial.md` "Reconfiguring Queues").

### The usecase interface

`internal/usecase/workflow.go` declares the interface, defined where it is consumed (`backend/AGENTS.md`, "Interfaces are defined where consumed"):

```go
type Flow interface {
	// Step runs fn once to completion; a resumed run returns the recorded result.
	Step(ctx context.Context, name string, fn func(context.Context) ([]byte, error)) ([]byte, error)
	// Start starts the named workflow with input, once per id; opts set the deadline, delay and queue.
	Start(ctx context.Context, workflow, id string, input any, opts ...StartOption) error
	// Recv waits for a signal sent to this workflow, up to timeout.
	Recv(ctx context.Context, topic string, timeout time.Duration) ([]byte, bool, error)
	// Patched reports whether this run takes the steps added under name.
	Patched(ctx context.Context, name string) (bool, error)
	// DeprecatePatch replaces Patched(name) once no run started before the patch is left.
	DeprecatePatch(ctx context.Context, name string) error
}

type Workflows interface { // for callers outside a workflow (API handlers, consumers)
	Start(ctx context.Context, workflow, id string, input any, opts ...StartOption) error
	Send(ctx context.Context, id, topic string, message any) error
	Await(ctx context.Context, id string, timeout time.Duration, out any) error
	// Cancel stops a workflow that has not started yet and reports whether it did;
	// false means it already started or ended.
	Cancel(ctx context.Context, id string) (bool, error)
}
```

- Typed helpers (`Step[R]`, `Await[R]`) do the JSON round trip.
- A workflow is a usecase method `func(ctx context.Context, f Flow, in In) (Out, error)`, registered by stable name in `internal/infrastructure/workflow`.
- Usecase tests mock `Flow` and `Workflows` with mockery, as every other port is (`backend/AGENTS.md:79`); `RunAndReturn` calls `fn` directly.
- Rules that types cannot carry go into `backend/AGENTS.md`:
  - read every value that changes between runs (clock, ids, random numbers) inside a step;
  - keep step names stable;
  - change steps only under `Patched`, then deprecate and remove the patch;
  - return a business outcome as a result, not as an error;
  - never ignore `ErrConflictingWorkflowID` (another execution owns the workflow) or `ErrWorkflowCancelled`; return them;
  - detach a child workflow that must outlive its parent with `WithoutCancel`.

### Failure classification

- **Step defaults** (applied by the implementation to every `Step`): retry when the error is Unavailable or DeadlineExceeded; base 1 s, factor 2, at most 1 h between tries, `WithStepMaxRetries(10000)`. The limit on a retry is the workflow's deadline, not the count, because the in-memory count restarts when the worker does.
- **Deadline**: each `Start` that needs a bound passes `WithDeadline`. The deadline is stored, so it holds across restarts.
- **Business outcomes** are returned values. A workflow returns an error only for a failure nobody planned for.
- **Report**: a schedule `report-workflows-needing-admin` (`0 */5 * * * *`; DBOS cron has a seconds field) lists the workflows in those statuses (`ListWorkflows`, which also gives the ids to log) and counts them by status and name. It records the count of workflows in `ERROR`, `MAX_RECOVERY_ATTEMPTS_EXCEEDED` or `CANCELLED` as an OpenTelemetry gauge `workflow.needs_admin` (labels `workflow_name`, `status`), and logs `LogKeyWorkflowNeedsAdmin` ("workflow needs an admin") with `workflow_id` once for each workflow it sees for the first time.
  - The alert fires on the gauge being above 0 and closes when it returns to 0, so it stays open exactly while a workflow needs an admin.
  - The log line gives the ids to act on.
  - Rejected: a log line every 5 minutes per workflow, which the log-based alert would need to stay open.
- An admin resolves a report by resuming or forking the workflow, or by deleting it after handling it by hand (runbook below).

### One id per announcement

An event id has one use here: telling a repeated publish from a new one (the JetStream `Nats-Msg-Id` window, PostHog's `uuid`); other consumers stay idempotent by business ids. So the id must be the same when the same publish is repeated and different otherwise. A repeated publish can be recognised safely only inside a workflow step, whose position is recorded. Anywhere else, the inputs can differ between the two tries: a key built from business values was removed before (`expand-product-analytics`, "an entity id is not an event id"), and a key built from the incoming event and a counter shifts when a re-read list changes, so another fan's notification would be dropped as a duplicate.

- Every event id is a UUIDv5 under one fixed namespace, made in `messaging.NewEvent` alone; no publisher changes.
- Inside a step, the name is `<workflow id>/<step id>`. `Flow.Step` puts the workflow id and the DBOS step id (`GetStepID`, the step's position, the same on every run and distinct for each pass of a loop) into the step's context. The same publish gets the same id on every run. Each publish in one step run also gets its position in that run (`<workflow id>/<step id>/<n>`), so a step that publishes twice (one event per fan) does not lose the second event to the JetStream duplicate window; a run of the step again publishes in the same order.
- Anywhere else, the name is a fresh random value, so each publish gets its own id, as today. A publisher moved into a workflow later gets the repeated-publish id with no change of its own.
- Rejected: minting a UUIDv7 in an earlier step and recording it, which adds one checkpoint write per publish for the same result; deriving ids outside a step from business values or from the incoming event, for the false duplicates above.
- This derivation is for events only. An external call's idempotency key names the business operation (a Checkout id, `refund:<order>`), or is left to the client library when the provider's own state prevents a second effect, as for a Stripe capture. A key from the workflow id and the step names the run: it changes under `fork` and when a patch adds a step, and it would keep returning a 500 the provider saved under it (`make-lottery-draw-durable` design "Stripe keys: the operation, not the run").
- The id is also the JetStream `Nats-Msg-Id`, and consumers already keep idempotency by the event id or by business ids.
- The usecase calls `PublishEvent` as today; nothing in the usecase layer changes.

### Placement, migrations and connections

- **Schema**: the system tables live in schema `dbos` of the same database, so point-in-time recovery restores them with the business data.
- **Migration**: one Atlas migration holds the output of `dbos migrate --print-migrations all`, plus the grant SQL of `--print-user-role` applied to the `fan-api` IAM role by name, the identity of the worker and of the fan API. Not the loop over every `%@%.iam` role: the grant convention of `20261008020000_restrict_organizer_console_api_and_zitadel_app_grants.sql` keeps narrow roles (Zitadel, organizer, reception) out of generic loops, and workflow inputs carry business data. A workload that starts workflows later grants its own role by name. The file starts with `-- atlas:txmode none`, because the DBOS SQL builds indexes `CONCURRENTLY`. The workloads start DBOS with `SkipMigrations: true` and `DatabaseSchema: "dbos"`.
- **Upgrading the module**: commit the output of `--print-migrations <first new number>` as a new Atlas migration first. This is written in `backend/AGENTS.md`.
- **Schema lint and `schema.sql`**: the engine's tables are not entities, so they stay out of `schema.sql`, the desired state Atlas diffs against; `scripts/lint-schema.sh` reads only `schema.sql` and needs no change. Without more, the next `atlas migrate diff` would end with `DROP SCHEMA "dbos" CASCADE` (verified with Atlas v1.3.0); `atlas.hcl` sets `diff { skip { drop_schema = true } }` (an env `exclude` does not reach `migrate diff`), and `scripts/check-migration-drift.sh` does not ask a DBOS migration for a `schema.sql` change.
- **Migration check**: a CI test compares `dbos migrate --print-migrations all` of the pinned module with the committed migration, so a module bump without its migration fails CI. At start, `SkipMigrations` makes the worker verify the schema version and fail if it is behind; the Atlas sync wave runs before the backend's.
- **Retention**: a schedule `delete-old-workflows` (`0 0 3 * * *`, Asia/Tokyo) lists `SUCCESS` workflows created more than 30 days ago (`WithFilterStatus`, `WithFilterCreatedBefore`) and deletes them with `DeleteWorkflows`. Workflows in a failed state stay until an admin resolves them, so a failure nobody handled is never deleted silently (Conductor's retention would delete them too, `docs/conductor/retention.md`).

### Connections: the whole instance stays within 25

`max_connections` is 25 on `db-f1-micro` and is shared with Zitadel. The pools' upper limits today add up to 61. Pools open lazily, so this has not failed yet, but nothing bounds it. Each workload's limit is set so the total is 22, which leaves 3 for the Atlas Operator during a deploy and for a person's `db-proxy` session. A larger tier waits until real users arrive.

| Workload | Today (prod) | New |
|---|---|---|
| Zitadel | 6 (`zitadel/base/values.yaml:145`) | 6, unchanged (its projection workers need it, values.yaml:136-153) |
| workflow-worker | – | 5: one pool shared by the app and DBOS (DBOS's minimum is 5) |
| fan-api | 5 | 3, shared with its DBOS client |
| event-consumer | 5 | 2 |
| series-image-consumer | 5 | 1 |
| organizer-console-api | 5 (reads `fan-api-config`) | 1, set in its own container `env`, which takes precedence over `fan-api-config` |
| admin-console-api | 5 (reads `fan-api-config`) | 1, set in its own container `env`, which takes precedence over `fan-api-config` |
| reception-api | 5 (reads `fan-api-config`) | 1, set in its own container `env`, which takes precedence over `fan-api-config` |
| CronJobs (5) | 5 each | 1 each; at most 2 run at once (sales-reminders every 15 minutes plus one daily job), so 2 |
| **Total** | **61** | **22** |

- `DATABASE_MAX_IDLE_CONNS` is set to at most the new limit (the default is 2, `backend/pkg/config/config.go:346`).
- With a pool of 1, a console API serves one database call at a time; with no users this is accepted, and the limits are revisited with the tier at launch.
- A shared pool is passed to DBOS as `Config.SystemDBPool` / `ClientConfig.SystemDBPool`. The docs warn that a pool exhausted by the application delays DBOS's startup; the 5-minute startup timeout covers it.

### Conductor

Not used now.
- What it adds: recovery of a dead executor's workflows by another executor, dashboards, retention, metrics and alerting.
- Cost: DBOS-hosted Pro is $99 a month; self-hosting needs an Enterprise license.
- What this design builds instead, which covers one worker: the fixed executor ID, the report schedule, the gauge and the retention schedule.
- When more than one worker is needed, either run the worker as a StatefulSet whose Pod name is the executor ID (`workflow-worker-0`, `workflow-worker-1`, each restarting with its own ID), or connect Conductor.

### Trace context

`Start` writes the caller's `traceparent` / `tracestate` into the workflow attributes. `Send` does not: DBOS messages carry no metadata, and replacing the attributes would lose the starter's context. A run starts a span whose parent is that context, and each step is a child span. A run resumed after a restart starts a new root span linked to the stored context, the job-item pattern of `fix-trace-propagation`.

### Operating a workflow

`cmd/worker` gains the subcommands `workflow list|steps|resume|fork|delete`, which wrap the DBOS client. An admin runs them with `kubectl exec deploy/workflow-worker -n backend -- /worker workflow …`, so the write goes through the worker's own database identity and the read-only people access stays read-only. The runbook `cloud-provisioning/docs/runbooks/workflow-needs-admin.md` describes each report status and the action for it.

### Implementation notes

Decided while implementing, against DBOS Transact Go v1.7.0:

- **Registration**: DBOS names a workflow function after its symbol, so the adapters of one generic `Register` would collide. A usecase workflow is registered as a configured instance named after the workflow (`dbos.WithInstance`), and `Start` enqueues it with that name as its config name. The two schedule workflows are plain functions, because DBOS schedules address a workflow by its plain name.
- **Start** enqueues on the default queue `workflows` (or the named one) from a client and from a running workflow alike; inside a workflow DBOS checkpoints the enqueue as a step. A deadline passed from a client is stored as a timeout that DBOS counts from the dequeue, so `Start` subtracts the delay; the queue picks a workflow up within a second.
- **Cancel** deletes the workflow in one statement when it is still `ENQUEUED` or `DELAYED`. DBOS's `CancelWorkflow` also stops running workflows and leaves them `CANCELLED`, which the report would page about.
- **Shared pool**: DBOS closes the pool it is given when the runtime or client shuts down, even one it did not create. The worker stops the runtime in the drain shutdown phase, before the database closes; a client goes in a phase before the database's.
- **Worker graph**: the worker builds only configuration, logging, telemetry, the database and the runtime. Building the fan API graph would also start its payment sweepers a second time; the first usecase workflow brings the usecases it needs.
- **Tests** create the `dbos` tables with `dbos.Migrate` rather than the Atlas apply: the grant migrations would give the grants test's cluster-wide fake roles privileges in the scratch databases while that test drops them. `TestDBOSMigrationsMatchModule` keeps the two SQL texts equal, and the grants test applies every migration.

@spec-manual components/infrastructure/backend/process/durable-workflows "Worker redeployed" -- the old Pod stops before the new one starts by the Deployment strategy (`maxSurge: 0`, `maxUnavailable: 1`, task 4.1, checked in the rendered prod overlay); the new worker continuing the workflow is "Worker stops between two steps" (`TestRuntime_WorkerStopsBetweenTwoSteps`).

## Risks / Trade-offs

- [DBOS Go is 3 months past 1.0 and its vendor is seed-funded] → It is a library with its state in the platform's database; the usecases depend only on `Flow` and `Workflows`.
- [A single worker is a single point of execution] → A stopped worker delays workflows but loses none; the queues and schedules resume when it is back. The deployment restarts it.
- [Workflow code changed without `Patched` breaks resumed runs] → The AGENTS.md rule, and an integration test that resumes a run recorded by the previous code.
- [Pools of 1 or 2 make requests wait under load] → Accepted while there are no users; the limits and the tier are revisited at launch.

## Migration Plan

1. backend: dependency, migration, `cmd/worker`, `Flow` / `Workflows`, `NewEvent` ids, the two schedules, AGENTS.md.
2. cloud-provisioning: the pool limits of every workload (applied first, before the worker exists), the `workflow-worker` Deployment (dev and prod overlays), the gauge alert and the runbook.
3. Deploy; confirm the AtlasMigration status, one worker Pod, and that `delete-old-workflows` and `report-workflows-needing-admin` run on time.

Rollback: scale `workflow-worker` to 0 and revert the release. The `dbos` schema stays and no business table changes.
