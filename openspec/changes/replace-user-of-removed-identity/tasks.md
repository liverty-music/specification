## 1. specification: proto (components/entity/user/has-identity)

- [ ] 1.1 Add `HasIdentity` to `rpc/backend/user/v1/user_service.proto` with a required `provider_user_id`, `bool exists`, doc comments and the service comment naming the fan API as its caller; verify `buf lint` and `buf breaking` pass
- [ ] 1.2 Open the specification PR, merge it, cut the release and verify `buf-release.yml` succeeds

## 2. backend: identity service (components/entity/user/has-identity, identity-provider-credentials)

- [ ] 2.1 Declare `HasIdentity`, implement it over Zitadel and in the identity client, and verify one test per scenario of `entity/user/has-identity`
- [ ] 2.2 Add the handler and allow the procedure to the fan API listener only; verify tests that the fan listener serves it and the other listeners refuse it

## 3. backend: usecase and story (components/usecase/user/create)

- [ ] 3.1 Replace a User whose identity is gone in `UserUseCase.Create`; verify one unit test per scenario of both requirements in `usecase/user/create`
- [ ] 3.2 Add the story test for "A deletion that stopped halfway does not block a new account" and verify it passes
- [ ] 3.3 Open the backend PR, merge, release; confirm read-only in prod that the release is rolled out and the identity service logs no permission error for HasIdentity
