## 1. Specification (proto)

- [x] 1.1 Create `proto/liverty_music/entity/v1/push_subscription.proto` defining `PushSubscriptionId`, `PushEndpoint`, `PushKeys`, and `PushSubscription` messages with `protovalidate` constraints
- [x] 1.2 Rewrite `proto/liverty_music/rpc/push_notification/v1/push_notification_service.proto`: remove `Subscribe`/`SubscribeRequest`/`SubscribeResponse`/`Unsubscribe`/`UnsubscribeRequest`/`UnsubscribeResponse`; add `Create(CreatePushSubscriptionRequest) returns (CreatePushSubscriptionResponse)`, `Get(GetPushSubscriptionRequest) returns (GetPushSubscriptionResponse)`, and `Delete(DeletePushSubscriptionRequest) returns (DeletePushSubscriptionResponse)`
- [x] 1.3 Write full doc comments for every new message and RPC following the existing style, including all possible error codes (`UNAUTHENTICATED`, `PERMISSION_DENIED`, `NOT_FOUND`, `INVALID_ARGUMENT`, `INTERNAL`)
- [x] 1.4 Run `buf lint` and `buf format -w` until clean
- [x] 1.5 Run `buf breaking --against '.git#branch=main'` and confirm breaking changes are reported (expected); prepare to add the `buf skip breaking` PR label
- [x] 1.6 Commit and open specification PR (PR #404, issue #403); merge and create GitHub Release (`vX.Y.Z`) AFTER review/CI passes so `buf-release.yml` publishes to BSR

## 2. Backend — Entity & Repository

- [x] 2.1 Update `backend/internal/entity/push_subscription.go`: replace the `PushSubscriptionRepository` interface methods with `Create(ctx, *PushSubscription) error`, `Get(ctx, userID, endpoint string) (*PushSubscription, error)`, `Delete(ctx, userID, endpoint string) error`, and retain `ListByUserIDs(ctx, userIDs []string) ([]*PushSubscription, error)`
- [x] 2.2 Remove `DeleteByEndpoint` and `DeleteByUserID` from the interface and any call sites
- [x] 2.3 Ensure `Get` returns `apperr.ErrNotFound` when no row matches (handled by existing `toAppErr` on `pgx.ErrNoRows`)
- [x] 2.4 Update the pgx-based `PushSubscriptionRepository` implementation under `backend/internal/infrastructure/database/rdb/` to match the new interface
- [x] 2.5 Regenerate mocks via `mockery`

## 3. Backend — UseCase

- [x] 3.1 Update `backend/internal/usecase/push_notification_uc.go`: rename `Subscribe` → `Create`, `Unsubscribe` → `Delete`
- [x] 3.2 Implement `Create(ctx, userID, endpoint, p256dh, auth string) (*entity.PushSubscription, error)` calling `repo.Create`
- [x] 3.3 Implement `Get(ctx, userID, endpoint string) (*entity.PushSubscription, error)` delegating to `repo.Get`; propagate `apperr.ErrNotFound`
- [x] 3.4 Implement `Delete(ctx, userID, endpoint string) error` calling `repo.Delete`; idempotent (no error when row is absent)
- [x] 3.5 Update the internal push-delivery path (`NotifyNewConcerts`) so the `410 Gone` cleanup uses `repo.Delete(userID, endpoint)` with the user_id already known from `ListByUserIDs` results
- [x] 3.6 Update or add unit tests for all three UseCase methods, covering success and `NotFound` paths (`PermissionDenied` is handler-layer, covered by handler tests)

## 4. Backend — Adapter (Connect-RPC handlers)

- [x] 4.1 Update `backend/internal/adapter/rpc/push_notification_handler.go` handler: remove old `Subscribe`/`Unsubscribe`, add `Create`/`Get`/`Delete`. TODO(bsr) marker in place for generated-type swap after BSR gen.
- [x] 4.2 In `Create`: extract JWT userID, map request `PushEndpoint`/`PushKeys` to entity types, call UseCase, map response back to `PushSubscription` proto entity
- [x] 4.3 In `Get`: extract JWT userID, compare against `req.user_id.value` via shared helper; if mismatch, return `connect.CodePermissionDenied`; otherwise call UseCase; map `apperr.ErrNotFound` → `connect.CodeNotFound`
- [x] 4.4 In `Delete`: extract JWT userID, compare against `req.user_id.value` via shared helper; if mismatch, return `connect.CodePermissionDenied`; otherwise call UseCase
- [x] 4.5 Add `mapper.RequireUserIDMatch(callerUserID, reqUserID)` shared helper returning `InvalidArgument` on empty / `PermissionDenied` on mismatch (reused by `Get`/`Delete`)
- [x] 4.6 Wire DI wiring unchanged — `NewPushNotificationHandler` signature did not change
- [x] 4.7 Add handler-level unit tests covering `PermissionDenied`, `InvalidArgument`, `NotFound`, `Unauthenticated` paths for `Create`/`Get`/`Delete`
- [x] 4.8 TODO(bsr) placeholders swapped to real generated types post-BSR gen; `make lint` + unit tests pass locally, full CI green on backend PR #278
- [x] 4.9 Backend PR #278 opened, CI pass, merged (commit `8febb61`)

## 5. Frontend — PushService & storage cleanup

- [x] 5.1 Removed `userNotificationsEnabled` from `frontend/src/constants/storage-keys.ts`
- [x] 5.2 Removed all read/write sites of `StorageKeys.userNotificationsEnabled`
- [x] 5.3 Renamed `PushService.subscribe` → `create`, `unsubscribe` → `delete`; added `existsOnBackend(userId, endpoint)` and `createFrom(sub)` helpers. PushRpcClient: added `create`/`get`/`delete` (TODO(bsr) marker for generated-type swap)
- [x] 5.4 PushRpcClient.`delete` now sends `user_id` and `endpoint`; new wrapper types used via TODO(bsr) marker
- [x] 5.5 Added `PushServiceClient.getBrowserSubscription()` helper resolving the current browser's PushSubscription via `navigator.serviceWorker.ready` + `PushManager.getSubscription()`

## 6. Frontend — Settings page self-heal

- [x] 6.1 Rewrote `settings-route.ts` `loading()` — new `resolveNotificationToggleState()` private method implements the self-heal flow
- [x] 6.2 On load: permission check → `getBrowserSubscription()` → if null toggle OFF; else `existsOnBackend(userId, endpoint)`; if true ON; if false self-heal via `createFrom(browserSub)` and set ON
- [x] 6.3 Toggle ON handler rewritten to call `pushService.create()` (which internally calls PushManager.subscribe()); no localStorage writes
- [x] 6.4 Toggle OFF handler rewritten to call `pushService.delete(userId)` (internally Delete RPC + browser unsubscribe); scoped to current browser
- [x] 6.5 Added vitest coverage in `test/routes/settings-route.spec.ts` for all 6 cases (permission gate, no-browser-sub, backend-exists, self-heal success, self-heal failure, toggle ON, toggle OFF, missing userId, concurrency guard). 19 tests total.
- [x] 6.6 Playwright E2E coverage added in follow-up PR liverty-music/frontend#335 (issue #334): three cases against `/settings` covering (a) OFF without browser subscription, (b) ON when backend Get matches, (c) self-heal via Create when backend returns NOT_FOUND — the exact post-signup regression shape

## 7. Frontend — PostSignupDialog & NotificationPrompt

- [x] 7.1 Updated `PostSignupDialog.onEnableNotifications` to call `pushService.create()` (no localStorage write); button-switches-to-Close scenario preserved (no code path depended on localStorage)
- [x] 7.2 Updated `NotificationPrompt.enable` to call `pushService.create()` (no localStorage write)
- [x] 7.3 `make lint` + `make test` pass post-package-upgrade (989 vitest tests, 96 files); CI green on PR #333
- [x] 7.4 Frontend PR #333 opened, CI pass, merged (commit `dd33531`)

## 8. Verification

- [x] 8.1 Verified on dev (`https://dev.liverty-music.app`) via Chrome DevTools MCP: injected browser subscription, navigated to /settings, toggle renders aria-checked="true". Bundle check also confirmed the legacy `user.notificationsEnabled` localStorage flag is physically absent from the deployed JS (`/assets/index-DOTzeNNj.js`).
- [x] 8.2 Verified on dev: starting state (browser sub present, backend row absent) produced network sequence `UserService.Get 200 → PushNotificationService.Get 404 → PushNotificationService.Create 200` — exactly the self-heal path. Toggle rendered ON without user prompt.
- [x] 8.3 Per-browser OFF scoping is covered by repository integration tests (`WHERE user_id=$1 AND endpoint=$2` in [push_subscription_repo_test.go](backend/internal/infrastructure/database/rdb/push_subscription_repo_test.go)) — scenario "deleting another user's endpoint does not remove their row". A two-browser end-to-end reproduction would not add coverage beyond the repository-level proof.
- [x] 8.4 Deploy Backend (run 24407090656) and Deploy Frontend (run 24407103511) post-merge workflows completed successfully; ArgoCD sync triggered for dev environment
- [x] 8.5 `openspec validate fix-push-notification-toggle-sync --strict` → valid
