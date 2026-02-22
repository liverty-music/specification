## Context

The `auto-concert-discovery` CronJob runs daily at 18:00 JST, iterating over all followed artists and calling `SearchNewConcerts()` for each. This method already returns only newly discovered concerts (deduplicated against existing records). The missing piece is delivering these results to users who follow the artist.

The frontend is an Aurelia 2 PWA served via Caddy. There is no existing Service Worker, PWA manifest, or push notification infrastructure. The backend uses Connect-RPC over HTTP/2 with JWT authentication.

## Goals / Non-Goals

**Goals:**
- Deliver Web Push notifications to users when new concerts are discovered for artists they follow
- Manage browser push subscriptions via RPC endpoints
- Integrate notification dispatch into the existing concert discovery job without adding a separate job
- Follow 2026 Web Platform Baseline standards (Push API, Service Worker, Permissions API)

**Non-Goals:**
- In-app notification inbox or notification history
- Email notifications
- Per-artist notification preferences (mute, quiet hours)
- Offline caching or precache strategy (Service Worker is push-only for MVP)
- Notification retry or guaranteed delivery

## Decisions

### 1. VAPID Direct over FCM

**Decision:** Use W3C Web Push Protocol with VAPID authentication directly from the Go backend via `webpush-go`.

**Alternatives considered:**
- **Firebase Cloud Messaging (FCM):** Adds Firebase SDK dependency, requires `fcm.googleapis.com` API enablement, and Firebase project setup. Chrome internally uses FCM for its push service, but developers don't need the Firebase SDK — the Push API endpoint URL is all that's needed.

**Rationale:** VAPID direct requires only a key pair and a Go library. No external service dependency, no additional GCP API enablement. Sufficient for the expected user scale.

### 2. Notification step in concert-discovery job (not a separate job)

**Decision:** Add `NotifyNewConcerts()` call inside the existing `concert-discovery` CronJob loop, immediately after `SearchNewConcerts()` returns new concerts.

**Alternatives considered:**
- **Separate notification-dispatch CronJob:** Would require a `notifications` table to track pending notifications, a second CronJob manifest, and coordination between jobs.

**Rationale:** `SearchNewConcerts()` already returns only new concerts. The discovery job has the exact context needed (which artist, which concerts are new). A separate job adds complexity without benefit at MVP scale. Notification dispatch failures are non-fatal and do not affect the job's exit code.

### 3. One notification per artist (batched concerts)

**Decision:** When multiple concerts are discovered for one artist, send a single push notification: "{Artist Name}: {N} new concerts found". The notification links to the artist's concert list page.

**Rationale:** Avoids notification spam. Users tap through to the concert list for details.

### 4. No notification history table (MVP)

**Decision:** Push notifications are fire-and-forget. No `notifications` table. Success/failure is logged via structured logging.

**Alternatives considered:**
- **Notification log table:** Enables delivery tracking, retry, and in-app inbox. Required for post-MVP features.

**Rationale:** MVP scope explicitly excludes in-app inbox. Structured logs provide sufficient observability. The existing `notification.go` entity will be replaced with a minimal `PushSubscription` entity.

### 5. Frontend service separation: NotificationManager + PushService

**Decision:** Split into two Aurelia DI services:
- `NotificationManager`: Monitors browser permission state via `permissions.query()`, exposes reactive `permission` property
- `PushService`: Handles `PushManager.subscribe()` and RPC calls to backend

**Rationale:** Separation of concerns. Permission state is needed by UI components independently of subscription lifecycle. `NotificationManager` can be injected into any component that needs to show permission-aware UI.

### 6. Soft Ask permission pattern

**Decision:** Never request notification permission on page load. Show an inline prompt in the dashboard UI when concerts are displayed, inviting the user to enable notifications. Only call `Notification.requestPermission()` after user interaction (button tap).

**Rationale:** 2026 Web Platform best practice. Unsolicited permission prompts lead to denials, which are permanent and cannot be re-prompted.

### 7. Service Worker: manual registration (no vite-plugin-pwa)

**Decision:** Hand-write `public/sw.js` and register it manually in `main.ts`.

**Alternatives considered:**
- **vite-plugin-pwa:** Automates SW generation, precaching, and manifest. Adds complexity and opinionated defaults.

**Rationale:** The Service Worker handles only push events (no precaching, no offline). A ~30-line file doesn't justify a build plugin dependency.

### 8. Service Worker notificationclick: reuse existing tabs

**Decision:** On notification click, use `clients.matchAll()` to check for an existing app tab. Focus it if found; otherwise open a new window.

**Rationale:** Prevents duplicate tabs. Standard UX pattern for PWA notifications.

### 9. Notification tag for deduplication

**Decision:** Use `tag: 'concert-{artistID}'` in `showNotification()` options.

**Rationale:** If the same artist's notification is sent again (edge case), the browser replaces the existing notification instead of stacking duplicates.

## Risks / Trade-offs

- **[Push endpoint expiry]** → Browser push subscriptions can expire or be revoked silently. Mitigation: Delete subscriptions on 410 Gone response. Users can re-subscribe from the dashboard.

- **[Notification delivery not guaranteed]** → Web Push has no delivery guarantee (device offline, browser closed, push service issues). Mitigation: Acceptable for MVP. Users still see concerts when they open the app. Post-MVP: add notification inbox.

- **[VAPID key rotation]** → Changing VAPID keys invalidates all existing subscriptions. Mitigation: Treat VAPID keys as long-lived secrets. Document rotation procedure (requires all users to re-subscribe).

- **[Job duration increase]** → Adding push dispatch to the discovery job increases its runtime. Mitigation: Push sends are fast (~100ms per subscription). At scale, consider batching or moving to a separate job.

- **[Permission denial is permanent]** → If a user clicks "Block" on the browser prompt, they cannot be re-prompted. Mitigation: Soft ask pattern reduces accidental denials. UI shows guidance to re-enable via browser settings if denied.
