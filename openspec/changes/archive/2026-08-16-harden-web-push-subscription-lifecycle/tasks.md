# Tasks

No proto/schema change — this change reuses the existing `PushNotificationService.Create`/`Get` RPCs and the unchanged VAPID keypair, so no BSR/specification-release coordination is required.

## 1. Backend — delivery observability

- [x] 1.1 Emit a WARNING log on every `failed` notification delivery in `notification_uc.go`, including the failure reason and user/notification identifiers
- [x] 1.2 Emit a delivery-outcome metric (counter) labelled by outcome and failure reason via the existing OTel instrumentation, keeping labels to the bounded failure-reason set (no high cardinality)
- [x] 1.3 Log zero-recipient early-returns in `push_notification_uc.go` (`NotifyNewConcerts`) with the reason (no followers / no eligible recipients / no deliverable concerts) and the artist id, instead of returning silently
- [x] 1.4 Unit tests: failed delivery produces the WARNING log + metric; each zero-recipient path produces its log; success path stays quiet
- [x] 1.5 `make check` passes

## 2. cloud-provisioning — alerting

- [x] 2.1 Add a log-based metric derived from the backend delivery-failure WARNING log (label by failure reason)
- [x] 2.2 Add a Cloud Monitoring alert policy for sustained delivery-failure ratio, paired with a minimum-volume guard (mirror the existing `app-error-log-alerting` pattern)
- [x] 2.3 Add an alert for active-subscription starvation (failures dominated by `no active push subscription` while notifications are being generated)
- [x] 2.4 Validate the policy applies cleanly in prod (avoid the known missing-metric 400-on-apply failure mode; use the log-based metric, not a raw OTLP metric)

## 3. Frontend — Service Worker renewal

- [x] 3.1 Add a `pushsubscriptionchange` handler in `src/sw.ts` that re-subscribes with the VAPID key and re-registers via `PushNotificationService.Create`, without requiring an open client
- [x] 3.2 Make the VAPID public key available to the SW by fetching same-origin `/config.json` (cache-first) at renewal time, preserving the env-agnostic bundle
- [x] 3.3 Ensure the handler never crashes the event when a new subscription cannot be obtained (permission revoked / offline); best-effort with retry on next event
- [x] 3.4 Tests for the renewal handler (success re-registers; failure is non-fatal)

## 4. Frontend — client recovery and error surfacing

- [x] 4.1 In `push-service.ts`, add an auto re-subscribe path: when permission is `granted` and `PushManager.getSubscription()` is `null`, subscribe with the VAPID key and call `Create`; gate it on a state check so it runs once per actual loss
- [x] 4.2 Update the settings/notification-prompt flow so that permission-granted-but-no-subscription resolves to auto re-subscribe, and permission-not-granted surfaces a re-enable affordance (no silent OFF)
- [x] 4.3 Surface `subscribe()` / `Create` failures: log on the client and reflect OFF in the toggle; never show a success state on failure
- [x] 4.4 Component/unit tests for the recovery matrix (granted+null → re-subscribe; not-granted+null → affordance; subscribe/Create error → OFF + surfaced)
- [x] 4.5 `make check` passes (including visual/baseline updates if the affordance changes UI)

## 5. Verification and prod rollout

- [x] 5.1 Ship backend release to prod; confirm the WARNING log + metric appear on a forced/failed delivery
- [x] 5.2 Merge cloud-provisioning; confirm ArgoCD syncs the alert policy and it is active
- [x] 5.3 Ship frontend release to prod; confirm the SW update rolls out
- [x] 5.4 On a real device: let a lapsed (permission-granted) client auto re-subscribe on app open; confirm a new `push_subscriptions` row is created
- [x] 5.5 Approve a concert for a followed artist and confirm real-device push receipt and a `delivered` notification record (closes the original report)
- [x] 5.6 Confirm `push_subscriptions` count recovers as clients re-subscribe, and that a forced failure raises the alert
