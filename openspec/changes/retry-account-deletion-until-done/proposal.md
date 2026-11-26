## Why

Account deletion removes the sign-in identity and then the User, inside the request. When the second step fails, nothing runs it again: the fan can no longer sign in to retry, the User and its personal data stay, signing up again with the same email fails every time, and no admin is told.

## What Changes

- Once Delete has accepted a deletion, the platform carries it to the end on its own: it continues after the request ends and after a restart, and tries a failed step again for up to 24 hours.
- An admin is told about a deletion that ends without removing the account.
- Delete waits up to 10 seconds. A deletion still running then is answered with success, because it was accepted and completes on its own. The fan sees the account deleted and is signed out, as today.
- A removal that cannot go on, including one that finds a new blocker, is reported to an admin.
- The removal runs in the workflow worker. Only the worker may delete a fan identity: the fan API and the admin console API lose that permission.
- The identity-provider spec names the workflow worker where it still says event consumer.
- Replaces the plan `replace-user-of-removed-identity`, which repaired a left-behind User at the next sign-up; it is removed.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `components/usecase/user/delete`: the deletion completes on its own.
- `components/entity/user/delete-identity`: fails with Unavailable when the identity provider cannot be reached.
- `components/entity/user/delete`: fails with Unavailable when the store cannot be reached.
- `components/infrastructure/backend/process/identity-provider-credentials` (Purpose): who may delete a fan identity; the workflow worker as the caller.
- `stories/delete-my-account`: a started deletion completes.
- `stories/sign-up-or-sign-in`: a failed Create no longer promises an account regardless of the cause.

`entity/user/get` and `usecase/user/list-deletion-blockers` are used as they are.

## Impact

- backend: `UserUseCase.Delete`, a workflow, the worker's wiring, the identity service's listeners, the identity remover's error code.
- specification: the caller list in the identity service's proto comment. No schema, database or cluster change, and no release needed.
