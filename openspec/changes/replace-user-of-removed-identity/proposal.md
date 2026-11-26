## Why

Account deletion removes the sign-in identity first and the User second. When the second step fails, the User stays. The fan cannot retry, because they can no longer sign in, and signing up again with the same email fails with AlreadyExists on every attempt: the app shows them as signed in, no account is ever created and nothing tells them why.

## What Changes

- When Create finds that the email belongs to a User whose sign-in identity no longer exists, it removes that User through UserUseCase.Delete and then creates the new account. A fan already stuck is repaired the next time the app resolves their account.
- The new account is empty. Orders and tickets stay linked to the removed User and are not moved.
- A User whose identity still exists is never touched: Create fails with AlreadyExists as today.
- A User that still has a deletion blocker is not removed: Create fails with AlreadyExists, and an admin resolves it.
- The identity service gains one read, whether an identity exists, which only the fan API may call.

## Capabilities

### New Capabilities

- `components/entity/user/has-identity`: reports whether the identity a User is linked to still exists.

### Modified Capabilities

- `components/usecase/user/create`: replaces a User whose identity is gone.
- `components/infrastructure/backend/process/identity-provider-credentials`: the fan API may ask whether an identity exists.
- `stories/sign-up-or-sign-in`: a failed Create no longer promises an account when the email belongs to another identity.
- `stories/delete-my-account`: signing up again works after a deletion that stopped halfway.

`entity/user/get-by-email`, `entity/user/delete`, `entity/user/delete-identity` and `usecase/user/delete` are used as they are.

## Impact

- specification: a new RPC on `liverty_music.rpc.backend.user.v1.UserService` and a release.
- backend: the identity service, its fan API listener, the entity operation and `UserUseCase.Create`.
- No database migration, no screen change and no new credential.
