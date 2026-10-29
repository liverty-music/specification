## Why

Four of every five spans the backend sends to Cloud Trace belong to no unit of work. On 2026-10-28 the backend sent 14,984 billable spans; 11,928 of them were client spans with no parent, each one a trace of its own:

- 10,368 database queries of the payment sweepers that run every 1 or 5 minutes in the fan workload and almost always find nothing to do;
- 1,560 Cloud SQL Admin API calls made by the database connector when it refreshes its certificate, about once an hour in every process.

Requests from fans, consumers and jobs made up the remaining 3,056. With no users yet, the noise hides the few traces worth reading, and it grows with every pod and every sweeper. Cost is not the driver: the volume is still inside the free tier.

## What Changes

- The backend records no span for an outgoing call (a database query, an HTTP call) made outside any unit of work. The same call made while handling a request, an event, a job run or a workflow is recorded as today.
- Log lines written outside a unit of work keep a `trace_id`, as today.
- Nothing else changes: the sampling ratio, the jobs' and consumers' spans, and the spans Cloud SQL Query Insights writes (not billed) stay as they are.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/infrastructure/backend/process/trace-propagation`: adds the rule that work outside any unit of work records no trace. The capability is created by `fix-trace-propagation`, which is archived before this change.

## Impact

- backend: `pkg/telemetry/telemetry.go` (the root sampler) with unit tests in `pkg/telemetry`.
- No proto, frontend or cloud-provisioning change. No new dependency.
- Cloud Trace: about 12,000 fewer spans a day at today's load.
- `make-lottery-draw-durable` (design "Traces: a schedule run that finds no sale records nothing") follows the same rule for its schedule run, which is a workflow span and not a client span, so it keeps its own task.
