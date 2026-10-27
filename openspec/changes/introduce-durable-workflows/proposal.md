## Why

Every multi-step process in the backend that must survive a stopped process is recovered by a sweeper written for it: a goroutine on a 1- or 5-minute ticker in the fan workload (`backend/internal/di/provider.go:521-548`) that re-reads a state column and runs the next step again. The checkout, the lottery draw and issuance, resale refunds, settlement payouts and the organizer reconciler each carry their own state column, ticker, retry rule and "needs an admin" report, and each new flow (lottery result notifications, dispute representment with deadlines, scheduled publishing, periodic identity re-checks) would add another. Some failures are not recovered at all: a lost CONCERT.created after an organizer publish is never re-sent, and an event announced twice gets two ids, so consumers and product analytics count it twice.

This change adds one durable workflow mechanism to the backend, in the platform's own database, so that a process written as ordered steps resumes after a stop from its last completed step, retries transient failures, waits durably, and reports what cannot finish. It changes no business flow by itself; the lottery and checkout changes that follow (`remove-lottery-entry-withdrawal`, `make-lottery-draw-durable`, `unify-order-issuance`) are its first users.

## What Changes

- A durable workflow engine (DBOS Transact Go, a library that keeps its state in Postgres) is added to the backend. Its tables live in a separate schema of the same database and are created by the Atlas migrations.
- A new backend workload, the workflow worker, is the only process that runs workflows, their queues and their schedules. API servers, event consumers and jobs only start workflows and wait for their results.
- The usecase layer gets a workflow interface (steps, starting a workflow, waiting for a signal or a result, durable delays). The engine stays in the infrastructure layer.
- Failures are classified once for every workflow: transient failures are retried inside the step; business outcomes are results, not errors; a workflow that ends with an error, is interrupted again and again, or passes its deadline is reported to an admin.
- An event that a workflow step publishes carries an id derived from the workflow and the step, so it has the same id every time the step runs. Every other event keeps a fresh id per publish, and all event ids share one format.
- Workflows that ended successfully more than 30 days ago are deleted once a day; failed ones stay until an admin resolves them.
- The workflow worker reports ready only once it runs workflows.

## Capabilities

### New Capabilities

- `components/infrastructure/backend/process/durable-workflows`: how a backend workflow survives a stopped process, which process runs it, how its failures are retried and reported, how its announcements keep one id, and how long its records are kept.

### Modified Capabilities

None. No entity, usecase or story changes in this change.

## Impact

- **backend**: new dependency `github.com/dbos-inc/dbos-transact-golang`; `cmd/worker`; `internal/usecase/workflow.go` (the interface); `internal/infrastructure/workflow/` (the DBOS implementation and the client the other workloads use); `EventPublisher` gains a stable id for a publish from a workflow step; an Atlas migration for the `dbos` schema and its grants; `backend/AGENTS.md` gains the workflow rules.
- **cloud-provisioning**: a `workflow-worker` Deployment in `k8s/namespaces/backend` (dev and prod overlays); a metric alert for workflows that need an admin, with its runbook; lower database pool limits for every backend workload, so that all of them with Zitadel and the worker stay within the instance's 25 connections. A larger Cloud SQL tier is left until real users arrive.
- **Operations**: stopped or failed workflows are listed and resumed with the DBOS CLI through the prod database access runbook, which gains a write step for this purpose.
