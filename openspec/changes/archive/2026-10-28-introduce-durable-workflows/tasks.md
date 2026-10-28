## 1. Connection budget (cloud-provisioning)

- [x] 1.1 Set `DATABASE_MAX_OPEN_CONNS` / `DATABASE_MAX_IDLE_CONNS` of every backend workload in the prod and dev overlays to the "New" column of design "Connections: the whole instance stays within 25" (fan-api 3, event-consumer 2, series-image-consumer 1, organizer-console-api 1, admin-console-api 1, reception-api 1, each CronJob 1); verify `kustomize build` of both overlays shows the values and their sum with Zitadel's 6 and the worker's 5 is 22
- [x] 1.2 Merge the PR and run the prod `pulumi up` by hand; confirm in prod (read-only) that every workload rolled out and `SELECT count(*) FROM pg_stat_activity` stays below 22 over an hour

## 2. Schema (backend)

- [x] 2.1 Pin `github.com/dbos-inc/dbos-transact-golang` v1.7.0; generate the `dbos` schema with `dbos migrate --print-migrations all`, wrap the `--print-user-role` grants in the loop over `%@%.iam` roles, commit both as one Atlas migration, and limit `scripts/lint-schema.sh` to the `app` schema; verify `make lint-schema` passes and the migration applies to a local database
- [x] 2.2 Add a CI test that compares `dbos migrate --print-migrations all` of the pinned module with the committed migration; verify it fails when the module version is bumped without a new migration

## 3. Workflow runtime (components/infrastructure/backend/process/durable-workflows)

- [x] 3.1 Declare `Flow`, `Workflows`, `StartOption` and the typed helpers in `internal/usecase/workflow.go` and generate their mocks. Implement them in `internal/infrastructure/workflow/` with the settings of design "The workflow worker owns execution", "Failure classification" and "Connections": `AppName`, fixed `ExecutorID` and `ApplicationVersion`, `SkipMigrations`, `DatabaseSchema: "dbos"`, the shared pool, `SystemDBStartupTimeout` of 5 minutes with a fresh context per attempt, the slog logger and the step defaults. Verify integration tests against local Postgres for "Worker stops between two steps", "Same workflow started twice", "Payment provider unavailable for 10 minutes" and "Deadline passed"
- [x] 3.2 Add `cmd/worker`: it launches the runtime with the fan workload's DI graph, serves a readiness endpoint that succeeds only after `Launch` and a liveness endpoint that checks only the process, and has the subcommands `workflow list|steps|resume|fork|delete`. Verify the integration test "Database unreachable at start" (not ready for 3 minutes, never restarted, ready after), and that `workflow list` prints the schedule runs locally
- [x] 3.3 Add the `report-workflows-needing-admin` schedule, the `workflow.needs_admin` gauge and `LogKeyWorkflowNeedsAdmin`; verify the integration test "Unexpected error" sees the gauge at 1 with the workflow's name within 5 minutes and one log line with its id, and the gauge back at 0 after `workflow delete`
- [x] 3.4 Make every CloudEvent id in `messaging.NewEvent` a UUIDv5 under one fixed namespace: named `<workflow id>/<step id>` when the step context carries them, and a fresh random value otherwise (design "One id per announcement"); verify unit tests that the id is the same for one step, different for two passes of a loop and different for two publishes outside a workflow, that every id is version 5, and an integration test of "Step runs again after a stop" that publishes twice with one id and sees JetStream keep one message
- [x] 3.5 Carry the trace context through the workflow attributes (design "Trace context"); verify a step span carries the starting span's trace id in the integration test
- [x] 3.6 Add the `delete-old-workflows` schedule; verify the integration tests "Old finished workflow", "Old failed workflow" and "Workflow still waiting" with the clock moved forward
- [x] 3.7 Write into `backend/AGENTS.md` the workflow rules of design "The usecase interface" (values read in steps, stable step names, the patch lifecycle, outcomes as results, conflict and cancellation errors never ignored, `WithoutCancel` for detached children), the module upgrade procedure and the queue rule; verify the section is in the PR

## 4. Deployment (cloud-provisioning)

- [x] 4.1 Add the `workflow-worker` Deployment to `k8s/namespaces/backend/base`: `replicas: 1`, `maxSurge: 0`, `maxUnavailable: 1`, the `fan-api` service account and secrets, the readiness and liveness probes of task 3.2, and pool size 5. Add dev and prod overlays (image pin, config map). Verify `kustomize build` for both overlays renders one replica and the probes
- [x] 4.2 Add the metric alert "Workflow Needs Admin" in `src/gcp/components/monitoring.ts` on `workflow.needs_admin > 0` (labels `workflow_name`, `status`), and the runbook `docs/runbooks/workflow-needs-admin.md` (what each status means, `workflow steps`, then `resume`, `fork --step` or `delete`). Verify `pulumi preview` for prod shows only the new alert

## 5. Release and production check

- [x] 5.1 Merge the backend PR and cut the release; merge the cloud-provisioning PR and run the prod `pulumi up` by hand. Confirm:
  - the AtlasMigration applied the `dbos` schema;
  - one `workflow-worker` Pod is Ready;
  - `report-workflows-needing-admin` has a run for each 5 minutes since the rollout;
  - the gauge reads 0 in Cloud Monitoring;
  - `kubectl exec deploy/workflow-worker -n backend -- /worker workflow list` works.
- [x] 5.2 The next day, confirm `delete-old-workflows` ran at 03:00 Asia/Tokyo
