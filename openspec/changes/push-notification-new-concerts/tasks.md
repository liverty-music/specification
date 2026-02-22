## 1. Proto & API Definition

- [ ] 1.1 Define `PushNotificationService` proto with `Subscribe` and `Unsubscribe` RPCs
- [ ] 1.2 Push to BSR and generate Go/TypeScript clients

## 2. Database

- [ ] 2.1 Create migration for `push_subscriptions` table (id, user_id, endpoint, p256dh, auth)
- [ ] 2.2 Apply migration and update schema.sql

## 3. Backend Entity & Repository

- [ ] 3.1 Create `PushSubscription` entity and `PushSubscriptionRepository` interface (Create, DeleteByEndpoint, ListByUserIDs, DeleteByUserID)
- [ ] 3.2 Remove old `notification.go` entity and its mock
- [ ] 3.3 Implement `PushSubscriptionRepository` (PostgreSQL, UPSERT by endpoint)
- [ ] 3.4 Add `ListFollowers(ctx, artistID) ([]*User, error)` to `ArtistRepository` interface and implementation

## 4. Backend Use Case

- [ ] 4.1 Create `PushNotificationUseCase` interface (Subscribe, Unsubscribe, NotifyNewConcerts)
- [ ] 4.2 Implement `PushNotificationUseCase` with `webpush-go` for VAPID-based delivery
- [ ] 4.3 Write unit tests for `PushNotificationUseCase`

## 5. Backend RPC Handler

- [ ] 5.1 Create `PushNotificationHandler` implementing Connect-RPC service
- [ ] 5.2 Wire handler into DI provider and Connect server registration
- [ ] 5.3 Write unit tests for handler

## 6. Concert Discovery Job Integration

- [ ] 6.1 Add `PushNotificationUseCase` to `JobApp` struct and DI initialization
- [ ] 6.2 Add `NotifyNewConcerts` call in job loop after `SearchNewConcerts` returns new concerts
- [ ] 6.3 Add VAPID config fields to application config

## 7. Infrastructure

- [ ] 7.1 Store VAPID key pair in GCP Secret Manager
- [ ] 7.2 Add `VAPID_PRIVATE_KEY` to backend ExternalSecret
- [ ] 7.3 Add `VAPID_PUBLIC_KEY` to job ConfigMap and server ConfigMap
- [ ] 7.4 Add `VITE_VAPID_PUBLIC_KEY` to frontend build environment

## 8. Frontend: Service Worker & PWA

- [ ] 8.1 Create `public/manifest.webmanifest` with PWA metadata
- [ ] 8.2 Add manifest link to `index.html`
- [ ] 8.3 Create `public/sw.js` with push event and notificationclick handlers
- [ ] 8.4 Register Service Worker in `main.ts`
- [ ] 8.5 Update Caddyfile with Service Worker cache headers

## 9. Frontend: Notification Services

- [ ] 9.1 Create `NotificationManager` service (permission state monitoring via `permissions.query()`)
- [ ] 9.2 Create `PushService` (PushManager.subscribe, RPC Subscribe/Unsubscribe calls)
- [ ] 9.3 Register services in Aurelia DI container

## 10. Frontend: Permission Prompt UI

- [ ] 10.1 Create notification opt-in prompt component for dashboard (soft ask pattern)
- [ ] 10.2 Bind prompt visibility and button state to `NotificationManager.permission`
- [ ] 10.3 Handle denied state with browser settings guidance
