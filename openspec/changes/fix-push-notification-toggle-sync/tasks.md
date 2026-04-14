## 1. Specification (proto)

- [x] 1.1 Create `proto/liverty_music/entity/v1/push_subscription.proto` defining `PushSubscriptionId`, `PushEndpoint`, `PushKeys`, and `PushSubscription` messages with `protovalidate` constraints
- [x] 1.2 Rewrite `proto/liverty_music/rpc/push_notification/v1/push_notification_service.proto`: remove `Subscribe`/`SubscribeRequest`/`SubscribeResponse`/`Unsubscribe`/`UnsubscribeRequest`/`UnsubscribeResponse`; add `Create(CreatePushSubscriptionRequest) returns (CreatePushSubscriptionResponse)`, `Get(GetPushSubscriptionRequest) returns (GetPushSubscriptionResponse)`, and `Delete(DeletePushSubscriptionRequest) returns (DeletePushSubscriptionResponse)`
- [x] 1.3 Write full doc comments for every new message and RPC following the existing style, including all possible error codes (`UNAUTHENTICATED`, `PERMISSION_DENIED`, `NOT_FOUND`, `INVALID_ARGUMENT`, `INTERNAL`)
- [x] 1.4 Run `buf lint` and `buf format -w` until clean
- [x] 1.5 Run `buf breaking --against '.git#branch=main'` and confirm breaking changes are reported (expected); prepare to add the `buf skip breaking` PR label
- [ ] 1.6 Commit and open specification PR; merge; create GitHub Release (`vX.Y.Z`) so `buf-release.yml` publishes to BSR

## 2. Backend — Entity & Repository

- [ ] 2.1 Update `backend/internal/entity/push_subscription.go`: replace the `PushSubscriptionRepository` interface methods with `Create(ctx, *PushSubscription) error`, `Get(ctx, userID, endpoint string) (*PushSubscription, error)`, `Delete(ctx, userID, endpoint string) error`, and retain `ListByUserIDs(ctx, userIDs []string) ([]*PushSubscription, error)`
- [ ] 2.2 Remove `DeleteByEndpoint` and `DeleteByUserID` from the interface and any call sites
- [ ] 2.3 Ensure `Get` returns `apperr.ErrNotFound` when no row matches
- [ ] 2.4 Update the pgx-based `PushSubscriptionRepository` implementation under `backend/internal/infrastructure/database/rdb/` to match the new interface
- [ ] 2.5 Regenerate mocks via `mockery`

## 3. Backend — UseCase

- [ ] 3.1 Update `backend/internal/usecase/push_notification_uc.go`: rename `Subscribe` → `Create`, `Unsubscribe` → `Delete`
- [ ] 3.2 Implement `Create(ctx, userID, endpoint, p256dh, auth string) (*entity.PushSubscription, error)` calling `repo.Create`
- [ ] 3.3 Implement `Get(ctx, userID, endpoint string) (*entity.PushSubscription, error)` delegating to `repo.Get`; propagate `apperr.ErrNotFound`
- [ ] 3.4 Implement `Delete(ctx, userID, endpoint string) error` calling `repo.Delete`; idempotent (no error when row is absent)
- [ ] 3.5 Update the internal push-delivery path (`NotifyNewConcerts`) so the `410 Gone` cleanup uses `repo.Delete(userID, endpoint)` with the user_id already known from `ListByUserIDs` results
- [ ] 3.6 Update or add unit tests for all three UseCase methods, covering success, `NotFound`, and `PermissionDenied` paths (the last is handler-layer but covered by integration)

## 4. Backend — Adapter (Connect-RPC handlers)

- [ ] 4.1 Update `backend/internal/adapter/ipc/push_notification/` handlers: remove old `Subscribe`/`Unsubscribe`, add `Create`/`Get`/`Delete`
- [ ] 4.2 In `Create`: extract JWT userID, map request `PushEndpoint`/`PushKeys` to entity types, call UseCase, map response back to `PushSubscription` proto entity
- [ ] 4.3 In `Get`: extract JWT userID, compare against `req.user_id.value`; if mismatch, return `connect.CodePermissionDenied`; otherwise call UseCase; map `apperr.ErrNotFound` → `connect.CodeNotFound`
- [ ] 4.4 In `Delete`: extract JWT userID, compare against `req.user_id.value`; if mismatch, return `connect.CodePermissionDenied`; otherwise call UseCase
- [ ] 4.5 Add a shared helper or interceptor to compare JWT userID against a request-supplied `UserId` and return `PermissionDenied` on mismatch (reused by `Get`/`Delete`)
- [ ] 4.6 Update Wire DI wiring to register the new handler signatures
- [ ] 4.7 Add handler-level unit tests covering the `PermissionDenied` path for `Get` and `Delete`
- [ ] 4.8 Run `make check` to confirm lint + tests pass
- [ ] 4.9 Open backend PR (as draft until BSR gen completes); merge once CI passes post-BSR

## 5. Frontend — PushService & storage cleanup

- [ ] 5.1 Remove `userNotificationsEnabled` from `frontend/src/services/storage-keys.ts` (or equivalent `StorageKeys` module)
- [ ] 5.2 Remove all read and write sites of `StorageKeys.userNotificationsEnabled` across the codebase
- [ ] 5.3 Rename `PushService.subscribe` → `create`, `unsubscribe` → `delete`; add `get(userId, endpoint)` method; update all imports
- [ ] 5.4 Update `PushService` method signatures to accept/return the new proto types; `delete` now sends `user_id` and `endpoint`
- [ ] 5.5 Add a helper on `PushService` to resolve the current browser's `PushSubscription` endpoint via `navigator.serviceWorker.ready` + `PushManager.getSubscription()`

## 6. Frontend — Settings page self-heal

- [ ] 6.1 Rewrite `frontend/src/routes/settings/settings-route.ts` `loading()` (or equivalent lifecycle) to implement the self-heal flow per `specs/settings/spec.md`
- [ ] 6.2 On page load: (a) get browser subscription; if null → toggle OFF; (b) else call `pushService.get(userId, endpoint)`; if success → ON; if `NotFound` → call `pushService.create(...)` and set ON on success
- [ ] 6.3 Rewrite the toggle ON handler to call `PushManager.subscribe()` + `pushService.create()` without writing any `localStorage` flag
- [ ] 6.4 Rewrite the toggle OFF handler to call `pushService.delete(userId, endpoint)` + `browserSubscription.unsubscribe()` (this browser only)
- [ ] 6.5 Add/update unit tests (vitest) covering: subscribed state, unsubscribed state, self-heal path, self-heal failure, ON action, OFF action
- [ ] 6.6 Add/update Playwright E2E coverage for the scenario "enable from PostSignupDialog → navigate to settings → toggle shows ON"

## 7. Frontend — PostSignupDialog & NotificationPrompt

- [ ] 7.1 Update `PostSignupDialog.onEnableNotifications` to call `pushService.create(...)` (no `localStorage` write); confirm no regression in the "button switches to Close" scenario
- [ ] 7.2 Update `NotificationPrompt.enable` to call `pushService.create(...)` (no `localStorage` write)
- [ ] 7.3 Run `make check` in `frontend/`; resolve any lint or type errors
- [ ] 7.4 Open frontend PR (as draft until BSR gen completes); merge once CI passes post-BSR

## 8. Verification

- [ ] 8.1 Deploy backend and frontend to dev; verify the original bug (enable from PostSignupDialog → settings shows OFF) is resolved
- [ ] 8.2 Manually verify self-heal: delete the user's `push_subscriptions` row while the browser retains its subscription; reload settings; confirm the toggle restores to ON via a `Create` call
- [ ] 8.3 Manually verify OFF scoping: sign in on two browsers, enable on both, toggle OFF in browser A; confirm browser B still receives notifications and its DB row remains
- [ ] 8.4 Confirm the ArgoCD deployment ran successfully via `gh run list --repo liverty-music/backend --branch main` and the new pod is serving the updated RPC
- [ ] 8.5 Run `openspec validate fix-push-notification-toggle-sync --strict` and resolve any findings
