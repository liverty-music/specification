## Context

See proposal.md. `userUseCase.Create` (backend `internal/usecase/user_uc.go`) turns an email conflict into AlreadyExists. The fan app calls Create on every start while it remembers no account, so a stuck fan retries by itself. The fan API reaches the identity service's fan listener, which allows `VerifyEmail` and `DeleteIdentity` (`di.FanAPIProcedures`). The identity service calls Zitadel with the `backend-app` machine key, whose `ORG_USER_MANAGER` membership on the product organization already removes users.

## Goals / Non-Goals

**Goals:** repair a left-behind User at the moment its email is used again, without a job or an admin action.

**Non-Goals:** moving orders or tickets to the new account; repairing a User that still has deletion blockers; a screen message for the AlreadyExists that remains.

## Decisions

- **Repair inside Create.** Alternatives: a periodic job over all Users (needs an identity lookup per User and still leaves the fan stuck until it runs); an admin action (needs a screen, and nobody learns that the fan is stuck).
- **Ask the identity provider, do not infer.** The product organization keeps sign-in names unique, so a second identity with the email suggests the first is gone, but a sign-in name changed at the provider would break that inference and remove a live fan's account. `User.HasIdentity` reports false only on the provider's NotFound.
- **`HasIdentity` is a new RPC `rpc.backend.user.v1.UserService.HasIdentity(provider_user_id) returns (bool exists)`**, added to `FanAPIProcedures` only. The identity service realizes it with the Zitadel user service `GetUserByID` and the `backend-app` key; `ORG_USER_MANAGER` includes `user.read`, so no role changes. The task confirms this in production.
- **Reuse `UserUseCase.Delete`.** It checks the deletion blockers, treats an identity already gone as removed and deletes the User, so no second removal path exists.
- **Concurrency.** The condition "the identity is gone" cannot become false again: the provider never reissues a user ID. Blockers are checked by Delete as for any deletion. Two repairs of the same User meet at User.Delete (the loser gets NotFound and continues) and at User.Create (the loser reads the winner's User by provider user ID). No row lock is added.
- **Who may trigger it.** Only a signed-in identity whose token carries the email reaches Create. The new account receives nothing of the old one, so registering someone's former address exposes none of their data.

## Risks / Trade-offs

- [A sign-up with an address the person does not control removes a left-behind User] → that User can no longer be signed in to by anyone, and its orders and tickets remain.
- [A left-behind User with blockers stays stuck] → it needs an admin; the failure is logged with the User id.

## Migration Plan

specification release (RPC), then backend. The identity service and the fan API deploy from the same release; while the identity service is still old, HasIdentity fails and Create returns that error, which the app retries. Rollback: revert the backend release.
