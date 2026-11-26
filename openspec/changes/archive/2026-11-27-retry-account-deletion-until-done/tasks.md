## 1. specification: caller list

- [x] 1.1 Update the service comment of `rpc/backend/user/v1/user_service.proto` to name the workflow worker as the caller of the code, link and `DeleteIdentity` procedures; verify `buf lint` and `buf breaking` pass, open the PR and merge it (comment only, no release)
- [x] 1.2 Add FAILED_PRECONDITION (the identity of a removed User) to the errors of `rpc/user/v1/user_service.proto` `UserService.Create`; verify `buf lint` and `buf breaking` pass, open the PR and merge it (comment only, no release)

## 2. backend: identity (components/entity/user/delete-identity, identity-provider-credentials)

- [x] 2.1 Map an unreachable identity provider to Unavailable in the identity remover and keep that code through the identity client; verify one test per scenario of `entity/user/delete-identity`
- [x] 2.2 Rename the port 9100 list to the workflow worker's, add `DeleteIdentity` to it and remove it from the fan and admin console API lists; verify listener tests for every scenario of `identity-provider-credentials`

- [x] 2.3 Map a failed database connection to Unavailable in `rdb.toAppErr`; verify a test for every scenario of `entity/user/delete`, with the database stopped for "Store unreachable"

- [x] 2.4 Add the `deleted_user_identities` migration, make `User.Delete` record the provider user id and `User.Create` refuse a recorded one; verify one test per added or modified scenario of `entity/user/delete` and `entity/user/create`, including a Create that runs while the removal commits, `scripts/check-migration-drift.sh` and `make lint-schema`

## 3. backend: usecase and story (components/usecase/user/delete)

- [x] 3.1 Keep the apperr code of a failed run through `Workflows.Await` in `internal/infrastructure/workflow`; verify an integration test where a client other than the worker awaits a run that failed with FailedPrecondition and reads that code, and that the run is still reported for an admin, and a passkey test where an addition's run that failed with Aborted still lets the removal continue
- [x] 3.2 Add the `delete-user` workflow (User first, then the identity), make `Delete` start and await it, wire the worker's `UserUseCase` with the identity remover and the blocker reads, and cover `usecase/user/create`; verify one unit test per scenario of both requirements of `usecase/user/delete` and of the modified requirement of `usecase/user/create`
- [x] 3.3 Add the story tests for "A started deletion completes" with a failing identity removal and verify they pass
- [x] 3.4 Open the backend PR, merge, release; confirm read-only in prod that the migration is applied, the release is rolled out, the worker registered `delete-user` and no `workflow.needs_admin` is raised for it

## 4. specification: Purpose

- [x] 4.1 At archive, reword the Purpose of `identity-provider-credentials`: a compromise of an API server cannot take over fan accounts or Organizers' Organizations; the workflow worker, which also processes external data, may delete a fan identity so that an account removal can be completed. Verify `openspec validate --specs` passes
