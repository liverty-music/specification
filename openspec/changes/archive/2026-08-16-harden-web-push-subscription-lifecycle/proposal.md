## Why

New-concert push notifications silently stopped reaching every follower in production. The pipeline (approve → `CONCERT.created` → consumer → follower/hype match → notification record) is healthy; delivery fails only at the final Web Push send because **no push subscription exists** for the recipients. Forensics on one follower show deliveries succeeded through 2026-07-29, then the first send after that (2026-08-13 09:55:18) returned `410 Gone`, the backend auto-deleted the row, and every later send recorded `no active push subscription`. The trigger was a legitimate client event (a PWA uninstall→reinstall), but two latent product defects turned a routine subscription loss into a permanent, invisible outage:

1. The Service Worker does not handle `pushsubscriptionchange`, so browser-initiated subscription rotation/expiry is never renewed.
2. After a subscription is lost (410, uninstall, data clear), nothing re-subscribes the user or prompts them — push is lost until they happen to toggle it back on manually.

And it stayed invisible for ~2 weeks because delivery failures are recorded only in the database, never surfaced as logs, metrics, or alerts.

## What Changes

- **Service Worker renews subscriptions automatically**: add a `pushsubscriptionchange` handler that re-subscribes with the configured VAPID key and re-registers the new subscription with the backend `Create` RPC — without any user interaction.
- **Client recovers from a lost/absent subscription instead of no-op**: when browser notification permission is already granted but the browser has no active subscription (or the backend reports the endpoint gone), the client re-subscribes automatically; if permission is not granted, the user is re-prompted rather than left silently off. This extends today's self-heal, which explicitly does nothing when the browser subscription is missing — the exact gap that caused this outage.
- **Subscribe/registration failures are surfaced**: `pushManager.subscribe()` / `Create` errors are no longer swallowed; they are logged and reflected in the UI toggle state.
- **Delivery failures become observable**: the backend emits WARNING logs and a metric for every failed push delivery (including `no active push subscription`), and the notify use case logs its zero-recipient early-returns instead of returning silently.
- **Alerting on systemic push loss**: a new alert fires when the push delivery failure ratio (or active-subscription starvation) crosses a threshold, so a repeat of this outage is caught in minutes, not weeks.
- Out of scope (not the cause here): the hype/proximity venue-coordinate filtering. It is left unchanged; the new observability will make any future proximity-driven drops visible.

## Capabilities

### New Capabilities
- `web-push-delivery-alerting`: detection and alerting when Web Push delivery is systemically failing (high failure ratio, or zero active subscriptions while notifications are being generated), so silent push outages surface operationally.

### Modified Capabilities
- `push-notification-service`: client subscription lifecycle gains automatic renewal on `pushsubscriptionchange` and automatic recovery when the browser subscription is lost/absent (the current self-heal is a no-op in that case); subscribe/register failures are surfaced rather than swallowed.
- `notification-lifecycle`: per-notification delivery failures SHALL be surfaced as observable signals (WARNING log + delivery-outcome metric), and the notification-fan-out SHALL log when it skips delivery because there are zero followers or zero eligible recipients, instead of returning silently.

## Impact

- **frontend** (Aurelia 2 PWA): `src/sw.ts` (new `pushsubscriptionchange` handler), `src/services/push-service.ts` (recovery + error surfacing), `src/routes/settings/settings-route.ts` and the notification-prompt flow (recovery/re-prompt). No proto/schema change — reuses the existing `PushNotificationService.Create`/`Get` RPCs and the unchanged VAPID public key.
- **backend** (Go): `internal/usecase/notification_uc.go` and `internal/usecase/push_notification_uc.go` (WARNING logs + metric on failed delivery and zero-recipient early-returns); a delivery-outcome metric via the existing OTel instrumentation.
- **cloud-provisioning**: a Cloud Monitoring alert policy for the push delivery failure metric (mirrors existing `app-error-log-alerting` / `argocd-deployment-alerts` patterns).
- **Recovery**: existing users whose subscriptions already lapsed are re-subscribed automatically on next app open (permission granted) or re-prompted (permission not granted); no manual per-user action required.
