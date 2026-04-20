## Why

The `fix-push-notification-toggle-sync` change introduces a pattern where user-scoped RPC requests carry an explicit `user_id` that is compared to the userID extracted from the JWT context; mismatches are rejected with `PERMISSION_DENIED`. This provides defense-in-depth against client bugs that would otherwise silently operate on the wrong user's data. `UserService` today uses a different pattern — it reads the userID solely from the JWT and exposes no client-supplied identifier — which means the two services now follow inconsistent authentication shapes. This change aligns `UserService` with the new pattern so the entire authenticated RPC surface behaves uniformly.

## What Changes

- **BREAKING**: `UserService.Get` gains a required `user_id` field in `GetRequest`. The backend verifies it matches the JWT-derived userID; mismatches return `PERMISSION_DENIED`.
- **BREAKING**: `UserService.UpdateHome` gains a required `user_id` field in `UpdateHomeRequest`, verified the same way.
- **BREAKING**: `UserService.ResendEmailVerification` gains a required `user_id` field in `ResendEmailVerificationRequest`, verified the same way.
- `UserService.Create` remains exempt from the `user_id` convention (no `user_id` on the request), but its behavior on duplicate `external_id` changes: instead of returning `ALREADY_EXISTS`, the RPC SHALL return the existing user as a successful response. This makes `Create` idempotent and gives the frontend a single uniform way to resolve its internal `user_id` from `external_id` on any device, which is required for the boot-time cache-miss recovery path (see `design.md` D4/D5).
- Introduce a shared backend helper (interceptor or function) `requireMatchingUserID(ctx, reqUserID)` that compares the JWT userID to the request-supplied value, returning `PERMISSION_DENIED` on mismatch. Reuse it across `UserService` and `PushNotificationService`.
- Frontend: update every `UserService.Get`/`UpdateHome`/`ResendEmailVerification` call site to include the cached `user_id`.

## Capabilities

### New Capabilities
- `rpc-auth-scoping`: Defines the cross-service convention that every authenticated per-user RPC (except creation RPCs where the caller's internal ID does not yet exist) SHALL carry an explicit `user_id` in the request body, verified against the JWT-derived userID in the handler.

### Modified Capabilities
- `user-home`: The `UpdateHome` RPC requirement changes to include the explicit `user_id` field and the JWT-match check.
- `email-verification`: The "Resend verification email via RPC" requirement changes to include the explicit `user_id` field and the JWT-match check.
- `user-account-sync`: The `Create` RPC becomes idempotent on duplicate `external_id` — returns the existing user as a success instead of `ALREADY_EXISTS`. The frontend boot flow drops the `ALREADY_EXISTS` branch and the follow-up `Get` call that relied on it.

## Impact

- **Proto (specification repo)**: Breaking changes to three `UserService` request messages. `buf skip breaking` label required on the PR.
- **Backend**: `UserService` handlers gain the `requireMatchingUserID` check. The shared helper is implemented as a package-private function inside the existing `backend/internal/adapter/rpc/` package (next to the handlers that consume it). Handler-level tests expand to cover `PERMISSION_DENIED` paths for the three RPCs.
- **Frontend**: A small `localStorage` cache keyed by `external_id` (Zitadel `sub`) is introduced to hold the internal `user_id` across page reloads. `UserServiceClient` writes this cache on every successful Get / Create / UpdateHome response and reads it on-demand so that business-code call sites continue to call `userService.get()` etc. without passing `user_id` explicitly. Boot flow simplifies to: read cached `user_id` by `sub`; if present, call `Get`; if absent, call the now-idempotent `Create` to obtain/create the user and hydrate the cache.
- **Database**: No schema change.
- **Migration**: No data migration. Clients using the old proto will receive `INVALID_ARGUMENT` on missing `user_id` after the backend deploys; this is acceptable because frontend deploys in the same release sequence.
- **Dependency**: This change SHOULD land after `fix-push-notification-toggle-sync`. That ordering lets this change reuse the shared `requireMatchingUserID` helper introduced there, and keeps the bug fix on its faster path.
