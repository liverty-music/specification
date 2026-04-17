## 1. Pre-work — audit the frontend userID boot flow

- [x] 1.1 Read `frontend/src/services/user-service.ts` and the auth-callback route to document where the authenticated userID is first learned and how it is cached across reloads
- [x] 1.2 Confirm or falsify the assumption that the userID is reliably available to `UserService.Get`'s first invocation (either from a `Create` response for sign-up, or from cached session data for returning users) — **FALSIFIED**: three boot paths (`UserHydrationTask`, `auth-callback` returning user, new device) hit `Get` before any userID is known
- [x] 1.3 Design a minimal cache layer and document it in design.md — **Resolved**: D4 adds a `localStorage` cache keyed by `external_id`; D5 makes `UserService.Create` idempotent to provide a uniform cache-miss recovery path

## 2. Specification (proto)

- [x] 2.1 Update `proto/liverty_music/rpc/user/v1/user_service.proto`: add required `entity.v1.UserId user_id = 1` to `GetRequest`
- [x] 2.2 Add required `entity.v1.UserId user_id` (field 1) to `UpdateHomeRequest`; shift existing `home` to field 2
- [x] 2.3 Add required `entity.v1.UserId user_id = 1` to `ResendEmailVerificationRequest`
- [x] 2.4 Update all doc comments to reflect the new `user_id` field and the JWT-match behavior, including `PERMISSION_DENIED` in the Possible Errors list for `Get`, `UpdateHome`, and `ResendEmailVerification`
- [x] 2.5 Do NOT add `user_id` to `CreateRequest`; update `CreateRequest`'s doc to explicitly state that creation RPCs are exempt per the `rpc-auth-scoping` capability, AND that the RPC is idempotent on duplicate `external_id` (returns the existing user rather than `ALREADY_EXISTS`) per `user-account-sync`
- [x] 2.6 Run `buf lint` and `buf format -w` until clean
- [x] 2.7 Run `buf breaking --against '.git#branch=main'` and expect breaking changes; add the `buf skip breaking` PR label
- [ ] 2.8 Commit and open specification PR; merge; create GitHub Release so `buf-release.yml` publishes to BSR

## 3. Backend — shared helper

- [ ] 3.1 Add a package-private helper `requireMatchingUserID(ctx context.Context, reqUserID string) error` to `backend/internal/adapter/rpc/` (new file, e.g., `auth.go`) returning `apperr.InvalidArgument` for empty input and `apperr.PermissionDenied` for mismatch
- [ ] 3.2 Add unit tests covering the three outcomes (match, mismatch, empty)
- [ ] 3.3 Refactor `PushNotificationService.Get` and `Delete` handlers (introduced by `fix-push-notification-toggle-sync`) in the same `rpc` package to call the shared `requireMatchingUserID` helper

## 4. Backend — UserService handlers

- [ ] 4.1 Update the `UserService.Get` handler in `backend/internal/adapter/rpc/user_handler.go`: extract `req.UserId.Value`, call `requireMatchingUserID(ctx, reqUserID)`; on success, proceed with existing logic
- [ ] 4.2 Update `UpdateHome` handler the same way
- [ ] 4.3 Update `ResendEmailVerification` handler the same way
- [ ] 4.4 Change `Create` handler to be idempotent on duplicate `external_id`: when the user already exists, return the existing `User` in `CreateResponse.user` with an OK response instead of `apperr.AlreadyExists`. `email`/`name` fields on the existing row SHALL NOT be overwritten
- [ ] 4.5 Add/update unit tests for `Create`: (a) fresh user creation path (existing behavior); (b) duplicate `external_id` returns existing user via OK; (c) any remaining failure modes still map to their original errors
- [ ] 4.6 Add handler-level unit tests for `Get` / `UpdateHome` / `ResendEmailVerification` covering: JWT-match success, mismatch (→ `PermissionDenied`), empty `user_id` (→ `InvalidArgument`)
- [ ] 4.7 Run `make check`
- [ ] 4.8 Open backend PR (default: hold until BSR gen completes to avoid CI noise); merge once CI passes post-BSR

## 5. Frontend — userID cache + call site migration

- [ ] 5.1 Add a `userId` localStorage key constant to `src/constants/storage-keys.ts` using the pattern `liverty:userId:<external_id>`, plus small read/write/clear helpers keyed by `external_id`
- [ ] 5.2 Update `UserServiceClient` so that `get()`, `updateHome()`, and `resendEmailVerification()` read the cached `user_id` from localStorage (via `IAuthService.user.profile.sub`) and inject it into the request. Business-code call sites MUST remain unchanged (still call `userService.get()` etc. with the same signatures)
- [ ] 5.3 Update `UserServiceClient` so that every successful `get`/`create`/`updateHome` response writes the userID to the cache keyed by the current `external_id`
- [ ] 5.4 Simplify `auth-callback-route.ensureUserProvisioned` and `user-hydration-task` to the new flow: (a) if cache has `user_id` → call `Get`; (b) otherwise → call `Create` (now idempotent), hydrate cache, done. Remove the old `Get`-then-`Create`-on-NotFound-then-`Get`-on-AlreadyExists dance
- [ ] 5.5 Update `UserServiceClient.clear()` and any sign-out path to remove the cached `user_id` for the signed-out `external_id`
- [ ] 5.6 Update unit tests: (a) `UserServiceClient` reads/writes the cache correctly; (b) `auth-callback-route` cache-hit path calls `Get` only; cache-miss path calls `Create` only; (c) duplicate-external_id response is consumed without an `ALREADY_EXISTS` catch
- [ ] 5.7 Run `make check` in `frontend/`; resolve lint / type errors
- [ ] 5.8 Open frontend PR (default: hold until BSR gen completes); merge once CI passes post-BSR

## 6. Verification

- [ ] 6.1 Deploy backend + frontend to dev; confirm existing flows (Settings page load, home area change, email resend) still work end-to-end
- [ ] 6.2 Exercise the cache-miss boot path in dev: clear localStorage, sign in as an existing user, confirm the frontend calls `Create` and receives the existing user (OK, not `ALREADY_EXISTS`), and that subsequent calls succeed
- [ ] 6.3 Manually simulate a mismatched `user_id` via `curl` or `grpcurl` against the dev backend; confirm `PERMISSION_DENIED` is returned
- [ ] 6.4 Manually simulate an empty `user_id`; confirm `INVALID_ARGUMENT`
- [ ] 6.5 Confirm the ArgoCD deployment succeeded and the new backend pod is serving requests
- [ ] 6.6 Run `openspec validate standardize-user-scoped-rpc-auth --strict` and resolve findings
