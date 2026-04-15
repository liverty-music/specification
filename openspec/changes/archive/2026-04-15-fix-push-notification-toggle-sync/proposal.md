## Why

After signup, a user enables push notifications from the PostSignupDialog, but when they later navigate to the settings page the toggle is shown as OFF. The cause is a three-way divergence between the browser `PushManager` subscription, the backend `push_subscriptions` DB row, and a client-side `localStorage` flag — every enable path must remember to write all three, and the PostSignupDialog forgets to write the `localStorage` flag. The deeper problem is that the backend already persists the authoritative subscription state but exposes no read RPC, forcing the frontend to maintain its own cache that drifts from reality. This change replaces the cache-based design with the backend DB as the single source of truth, plus browser-side self-healing for stale rows.

## What Changes

- Introduce a `PushSubscription` entity and its wrapper types (`PushSubscriptionId`, `PushEndpoint`, `PushKeys`) in `entity/v1/`, replacing the ad-hoc `endpoint`/`p256dh`/`auth` string fields currently defined inside `SubscribeRequest`.
- **BREAKING**: Rename `PushNotificationService` RPCs to match AIP Standard Methods and the repository naming: `Subscribe` → `Create`, `Unsubscribe` → `Delete`. Add new `Get` RPC.
- **BREAKING**: `Delete` now takes `(user_id, endpoint)` instead of deleting all of the user's subscriptions. This matches the schema design where `push_subscriptions` is keyed by browser endpoint.
- `Get` returns the subscription keyed by `(user_id, endpoint)` and returns `NOT_FOUND` when no matching row exists (AIP-131 compliant).
- Remove the client-side `localStorage` flag `userNotificationsEnabled`. The settings toggle derives its state from `PushManager.getSubscription()` combined with the `Get` RPC result.
- Add a self-healing flow on settings page load: if the browser has a subscription but the backend does not, silently re-register it via `Create` so the UI reflects the browser's intent.
- Backend repository: drop `DeleteByEndpoint(endpoint)` and `DeleteByUserID(userID)`; replace with `Get(userID, endpoint)` and `Delete(userID, endpoint)` to keep all authenticated operations scoped to the caller.

## Capabilities

### New Capabilities
- `push-notification-service`: Defines the RPC surface and entity model for browser push subscription management — `PushSubscription` entity, `Create`/`Get`/`Delete` RPC methods, per-browser scoping rules, and self-heal semantics.

### Modified Capabilities
- `settings`: The "Push Notification Toggle" requirement changes — the toggle's enabled state is derived from the backend via `Get` and the browser's `PushManager` state, not from `localStorage`. The OFF-toggle behavior changes from "delete all subscriptions" to "delete only this browser's subscription".
- `post-signup-dialog`: The "Notification opt-in from dialog" scenario changes — the dialog calls `PushNotificationService.Create` (was `Subscribe`) and no longer needs to write `localStorage`.

## Impact

- **Proto (specification repo)**: New `entity/v1/push_subscription.proto`. `rpc/push_notification/v1/push_notification_service.proto` rewritten with the new RPC set. Breaking change → requires `buf skip breaking` label.
- **Backend**: `PushSubscriptionRepository` interface, `PushNotificationUC`, and Connect-RPC handlers all change. Generated proto types shift (Base64 `string` fields become nested messages).
- **Frontend**: `PushService` API renamed to `create`/`get`/`delete`. `StorageKeys.userNotificationsEnabled` removed. `settings-route.ts` `loading()` rewritten with self-heal flow. `PostSignupDialog.onEnableNotifications` and `NotificationPrompt.enable` simplified (no `localStorage` write needed).
- **Database**: No schema change. Existing `push_subscriptions` table already keyed by endpoint.
- **Migration**: No data migration needed. Stale orphan rows (browser data cleared but DB row remains) are self-healed over time via the existing `410 Gone` cleanup in `PushNotificationUC.NotifyNewConcerts`.
- **Cross-repo order**: specification PR → merge → Release → BSR gen → backend PR → frontend PR (standard workspace dependency chain).
