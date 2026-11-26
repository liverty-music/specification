## Context

See proposal.md. Facts (backend `origin/main`, 2026-11-26):

- `userUseCase.Delete` runs `User.SerializeDeletion` around the blocker check, `DeleteIdentity` and `User.Delete`, in the fan API or the admin console API process.
- Durable workflows (DBOS, change `introduce-durable-workflows`): `Workflows.Start` and `Await` for callers; the workflow worker runs them, resumes them after a restart, retries a step that fails with Unavailable or DeadlineExceeded, and reports workflows that end in a failed state to an admin (`workflow.needs_admin`). The fan API and the admin console API already have the `dbos` grants.
- The identity service's listener on port 9100 (`di.EventConsumerProcedures`) is reached only by the workflow worker (NetworkPolicy `identity-ingress`, `IDENTITY_SERVICE_URL`), which runs as the fan API's service account.
- The worker's `UserUseCase` is built without the identity remover and the blocker reads.

## Goals / Non-Goals

**Goals:** a deletion that was accepted always ends in removal or in an admin being told.

**Non-Goals:** repairing Users already left behind (there are none to repair: an admin can delete one on the Users screen); a new screen message for the Unavailable case.

## Decisions

- **A workflow `delete-user`, awaited by Delete.** Delete does its two checks, starts the workflow and awaits it for 10 seconds, below the API handler timeout. Alternatives: repair at the next sign-up (leaves personal data until then and lets a sign-up delete another User); a sweeper over Users without an identity (a second mechanism the workflow change replaced).
- **One step: the existing `SerializeDeletion` block.** The check, the identity removal and the row removal stay under the same advisory lock the blocker creators take. Splitting into steps would release the lock between the check and the removal. Every part is safe to repeat: an identity already gone counts as removed, and NotFound from `User.Delete` is success.
- **Rows locked.** As today: `pg_advisory_xact_lock('user:' || id)` exclusive in the deletion, shared in every path that creates a blocker (`delete-fan-accounts` design D2).
- **Outcomes are values.** The step returns "removed" or "blocked"; a blocker is not a workflow failure. Delete maps "blocked" to FailedPrecondition.
- **Workflow id `delete-user:<user id>:<new uuid>`.** A fixed id per User would return an earlier run that ended "blocked" and never try again. Concurrent runs serialize on the lock.
- **Deadline 24 hours**, as the other workflows that retry an external call.
- **Retry classification.** `IdentityRemover.DeleteIdentity` maps an unreachable provider to Unavailable instead of Internal, so the step retries it.
- **Permission moves to the worker.** `DeleteIdentity` joins the port 9100 list and leaves the fan and admin console API lists. The worker also processes external data (concert discovery), which the identity spec wanted kept away from identity deletion; this is accepted so that the removal can be retried. The two internet-facing APIs lose the permission. Alternative: retry only the record removal in the worker; rejected because a DeleteIdentity that succeeded with a lost answer would still be left behind. Rename `EventConsumerProcedures` to `WorkflowWorkerProcedures`.

## Risks / Trade-offs

- [Unavailable although the deletion completes later] → the screen offers a retry, and NotFound then counts as done.
- [During the rollout an old API pod calls DeleteIdentity and is refused, or a new API starts a workflow the old worker does not know] → the first fails that one request, which the person retries; the second waits in the queue until the new worker runs.

## Migration Plan

One backend release for identity, worker and APIs; then the frontend release. Rollback: revert the backend release; runs left pending are reported to an admin by the existing schedule.
