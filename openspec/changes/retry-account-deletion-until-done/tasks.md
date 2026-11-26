## 1. specification: caller list

- [ ] 1.1 Update the service comment of `rpc/backend/user/v1/user_service.proto` to name the workflow worker as the caller of the code, link and `DeleteIdentity` procedures; verify `buf lint` and `buf breaking` pass, open the PR and merge it (comment only, no release)

## 2. backend: identity (components/entity/user/delete-identity, identity-provider-credentials)

- [ ] 2.1 Map an unreachable identity provider to Unavailable in the identity remover and keep that code through the identity client; verify one test per scenario of `entity/user/delete-identity`
- [ ] 2.2 Rename the port 9100 list to the workflow worker's, add `DeleteIdentity` to it and remove it from the fan and admin console API lists; verify listener tests for every scenario of `identity-provider-credentials`

## 3. backend: usecase and story (components/usecase/user/delete)

- [ ] 3.1 Add the `delete-user` workflow, make `Delete` start and await it, and wire the worker's `UserUseCase` with the identity remover and the blocker reads; verify one unit test per scenario of both requirements of `usecase/user/delete`
- [ ] 3.2 Add the story test for "A started deletion completes" with a failing record removal and verify it passes
- [ ] 3.3 Open the backend PR, merge, release; confirm read-only in prod that the release is rolled out, the worker registered `delete-user` and no `workflow.needs_admin` is raised for it

## 4. frontend: the withdrawal screen (components/infrastructure/fan/web/route/delete-account)

- [ ] 4.1 Treat NotFound from UserService.Delete as a completed deletion; verify one test per scenario of "After deletion the fan leaves signed out", and run the flow with Playwright on a local build with a mocked service returning Unavailable then NotFound
- [ ] 4.2 Open the frontend PR, merge, release; confirm read-only in prod that the release is rolled out
