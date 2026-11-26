## Context

See proposal.md. Facts (backend `origin/main`, 2026-11-26):

- `userUseCase.Delete` runs `User.SerializeDeletion` around the blocker check, `DeleteIdentity` and `User.Delete`, in the fan API or the admin console API process.
- Durable workflows (DBOS, change `introduce-durable-workflows`): `Workflows.Start` and `Await` for callers; the workflow worker runs them, resumes them after a restart, retries a step that fails with Unavailable or DeadlineExceeded, and reports workflows that end in a failed state to an admin (`workflow.needs_admin`). The fan API and the admin console API already have the `dbos` grants.
- The identity service's listener on port 9100 (`di.EventConsumerProcedures`) is reached only by the workflow worker (NetworkPolicy `identity-ingress`, `IDENTITY_SERVICE_URL`), which runs as the fan API's service account.
- The worker's `UserUseCase` is built without the identity remover and the blocker reads.

## Goals / Non-Goals

**Goals:** a deletion that was accepted always ends in removal or in an admin being told.

**Non-Goals:** repairing Users already left behind (there are none to repair: an admin can delete one on the Users screen); any screen change.

## Decisions

- **A workflow `delete-user`, awaited by Delete.** Delete does its two checks, starts the workflow and awaits it for 5 seconds. The fan and admin apps give up on a call after 10 seconds (`rpcTimeoutMs`, its default, which prod does not override), counted from before the request is sent, so the wait leaves room for the network and the checks before it; it is also below the API handler timeout. A timeout of the await is success: the run is durable. Alternatives: answer Unavailable on a timeout, rejected because a fan whose identity is gone cannot sign in again to retry, and the withdrawal screen would report a failure for a deletion that completes; repair at the next sign-up, which leaves personal data until then and lets a sign-up delete another User; a sweeper over Users without an identity, a second mechanism the workflow change replaced.
- **Two steps, each under `SerializeDeletion`.** `remove-identity`: User gone → done; blockers → FailedPrecondition; `DeleteIdentity`. `remove-user`: User gone → done; blockers → FailedPrecondition; `User.Delete`. Reading the User first matters: the blocker read fails with NotFound for a removed User, which would report a successful deletion. The lock is released between tries, so the second step checks the blockers again; a token issued before the identity was removed stays valid and can create one.
- **Rows locked.** As today: `pg_advisory_xact_lock('user:' || id)` exclusive in each step, shared in every path that creates a blocker (`delete-fan-accounts` design D2).
- **Every failure ends the run in ERROR**, a blocker included, so the existing report tells an admin. The awaiting Delete returns that error's code. An admin finishes it by deleting the User on the Users screen once the cause is gone.
- **Workflow id `delete-user:<user id>:<new uuid>`.** A fixed id per User would return an earlier failed run and never try again. Concurrent runs serialize on the lock.
- **A failed run keeps its error code.** DBOS v1.9.0 stores a workflow's error with gob and, when the type cannot be encoded, as its message only. An `apperr` error cannot be encoded (`type not registered for interface: apperr.AppErr`), so a caller in another process would read every failure as Internal. `internal/infrastructure/workflow` records the failure of a run in a form that carries the apperr code and message, and `Await` returns an error with that code. This holds for every workflow, so `Await` also marks an error as the run's own failure, which keeps it apart from the caller's wait timing out. The passkey removal's wait for the addition's run branches on Unavailable, DeadlineExceeded and Aborted as outcomes of the wait; it checks the mark first and keeps treating every failed run as one that stores nothing. `OrderUseCase.Place` returns a failed Issue run's code where it returned Internal. Alternative: end the run successfully with the code in its result; rejected because the admin report only sees failed states.
- **Deadline 24 hours**, as the other workflows that retry an external call.
- **Retry classification.** `IdentityRemover.DeleteIdentity` maps an unreachable provider to Unavailable instead of Internal. `rdb.toAppErr` today classifies only PostgreSQL error codes and leaves a failed connection (`pgconn.ConnectError`, a network error) unclassified; it maps those to Unavailable too, which covers `User.Delete`, the lock and the blocker reads. Without this the step would not retry a database outage.
- **Permission moves to the worker.** `DeleteIdentity` joins the port 9100 list and leaves the fan and admin console API lists. The worker also processes external data (concert discovery), which the identity spec wanted kept away from identity deletion; this is accepted so that the removal can be retried. The two internet-facing APIs lose the permission. Alternative: retry only the record removal in the worker; rejected because a DeleteIdentity that succeeded with a lost answer would still be left behind. Rename `EventConsumerProcedures` to `WorkflowWorkerProcedures`.

## Risks / Trade-offs

- [Success is answered while the identity provider is down] → the fan is signed out and could sign in again until the removal runs; anything created then makes it a reported blocker, not a silent loss.
- [`DeleteIdentity` succeeds, its answer is lost and a blocker appears before the retry] → the first step ends with the blocker and an admin is told.
- [During the rollout an old API pod calls DeleteIdentity and is refused, or a new API starts a workflow the old worker does not know] → the first fails that one request, which the person retries; the second waits in the queue until the new worker runs.

## Migration Plan

One backend release for identity, worker and APIs. Rollback: revert the backend release. A `delete-user` run left pending or enqueued is not in the admin report (only failed states are), so before reverting, check that none is open (`dbos` system tables, read-only), or delete those Users on the Users screen afterwards.
