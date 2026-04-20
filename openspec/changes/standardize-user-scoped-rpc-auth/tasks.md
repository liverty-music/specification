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
- [x] 2.8 Commit and open specification PR (#411); merge + create GitHub Release pending user action

## 3. Backend — shared helper

- [x] 3.1 Shared helper already exists as `mapper.RequireUserIDMatch(callerUserID, reqUserID string) error` in `backend/internal/adapter/rpc/mapper/user.go` (landed by `fix-push-notification-toggle-sync`). The signature takes a pre-resolved `callerUserID` rather than `ctx`, which aligns with the handler pattern of first resolving the caller's internal UUID via `resolveCallerUser(ctx)` before comparing — acceptable deviation from the `requireMatchingUserID(ctx, reqUserID)` form originally sketched in design.md D2
- [x] 3.2 Add unit tests for `RequireUserIDMatch` covering the three outcomes (match, mismatch, empty) — added in `mapper/user_test.go`
- [x] 3.3 `PushNotificationService.Get` and `Delete` handlers already call `mapper.RequireUserIDMatch` (landed by `fix-push-notification-toggle-sync`)

## 4. Backend — UserService handlers

- [x] 4.1 Update the `UserService.Get` handler in `backend/internal/adapter/rpc/user_handler.go`: resolve caller via `GetByExternalID`, then call `mapper.RequireUserIDMatch(user.ID, req.Msg.GetUserId().GetValue())`
- [x] 4.2 Update `UpdateHome` handler the same way
- [x] 4.3 Update `ResendEmailVerification` handler the same way (also resolves caller via `GetByExternalID` — previously read JWT claims directly)
- [x] 4.4 `userUseCase.Create` is idempotent on duplicate `external_id`: catches `apperr.ErrAlreadyExists`, fetches existing user via `GetByExternalID`, returns it as success. Email-collision (different external_id) still surfaces `AlreadyExists`. The `UserCreated` event is NOT published on the idempotent return path
- [x] 4.5 `user_uc_test.go` covers fresh-create, idempotent-return on duplicate external_id, and email-collision failure modes
- [x] 4.6 `user_handler_test.go` and `resend_email_verification_test.go` cover JWT-match success, mismatch (→ `PermissionDenied`), empty `user_id` (→ `InvalidArgument`)
- [x] 4.7 `make check` passes (lint + golangci + schema-lint + modernize + unit + integration)
- [x] 4.8 Open backend PR (#283) — BSR gen v0.38.0 already published, CI should pass on first run

## 5. Frontend — userID cache + call site migration

- [x] 5.1 Add `userIdStorageKey(externalID)` helper to `src/constants/storage-keys.ts` returning `liverty:userId:<external_id>`
- [x] 5.2 `UserServiceClient.get()` / `updateHome()` / `resendEmailVerification()` resolve `user_id` from in-memory `_current` then localStorage (keyed by `IAuthService.user.profile.sub`) and inject it into the underlying RPC. Business-code call site signatures unchanged
- [x] 5.3 Every successful `get`/`create`/`updateHome` response writes the userID to localStorage
- [x] 5.4 `auth-callback-route.ensureUserProvisioned` simplified: `ensureLoaded()` returns user → done; otherwise call (now idempotent) `Create`. Old `Get`-then-`Create`-on-NotFound-then-`Get`-on-AlreadyExists dance removed
- [x] 5.5 `UserServiceClient.clear()` removes the cached `user_id` for the current `external_id`
- [x] 5.6 `test/services/user-service.spec.ts` (new) covers cache hit/miss, in-memory dedup, write-on-success, throw-on-missing-user_id; `test/routes/auth-callback-route.spec.ts` rewritten for the simplified flow
- [x] 5.7 `make check` passes (Biome + tsc + stylelint + lint-templates + vitest 1000 tests). Drive-by Makefile fix: removed dead `test-layout` / `test-layout-auth` targets that pointed at non-existent Playwright projects after the 5-layer e2e refactor (43ea25a)
- [x] 5.8 Frontend PR (#336) opened — BSR gen v0.38.0 already published, CI should pass on first run

## 6. Verification

- [x] 6.1 Backend + frontend deployed to dev (Backend Deploy #24602588418, Frontend Deploy #24602921708 + #24646970492). User confirmed Settings page load, home update, and email resend work end-to-end on the new bundle
- [x] 6.2 Cache-miss boot path verified by user: clearing `liverty:userId:*` and reloading triggers `UserService/Create`, returns the existing user (idempotent, no `ALREADY_EXISTS`), `liverty:userId:<sub>` is repopulated, and the home selector overlay no longer appears
- [x] 6.3 Mismatched `user_id` returns `PERMISSION_DENIED` — verified by user-driven curl smoke against dev backend with a captured Zitadel JWT (handler-level coverage in `user_handler_test.go::TestUserHandler_*` cross-checks the same logic)
- [x] 6.4 Empty `user_id` returns `INVALID_ARGUMENT` via protovalidate — verified by user-driven curl smoke (handler-level + protovalidate coverage cross-checks the same path)
- [x] 6.5 Backend ArgoCD deployment confirmed: `Deploy Backend` workflow #24602588418 success (server / consumer / concert-discovery / artist-image-sync images pushed at 10:23 UTC). `https://api.dev.liverty-music.app/grpc.health.v1.Health/Check` returns `SERVING_STATUS_SERVING`. UserService endpoints reachable through the auth chain (Connect-RPC `unauthenticated` response from `/liverty_music.rpc.user.v1.UserService/Get`)
- [x] 6.6 `openspec validate standardize-user-scoped-rpc-auth --strict` returns `Change is valid`
