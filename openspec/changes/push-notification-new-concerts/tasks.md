## 1. Proto & API Definition

- [x] 1.1 Define `PushNotificationService` proto with `Subscribe` and `Unsubscribe` RPCs
- [x] 1.2 Push to BSR and generate Go/TypeScript clients

## 2. Database

- [x] 2.1 Create migration for `push_subscriptions` table (id, user_id, endpoint, p256dh, auth)
- [x] 2.2 Apply migration and update schema.sql

## 3. Backend Entity & Repository

- [x] 3.1 Create `PushSubscription` entity and `PushSubscriptionRepository` interface (Create, DeleteByEndpoint, ListByUserIDs, DeleteByUserID)
- [x] 3.2 Remove old `notification.go` entity and its mock
- [x] 3.3 Implement `PushSubscriptionRepository` (PostgreSQL, UPSERT by endpoint)
- [x] 3.4 Add `ListFollowers(ctx, artistID) ([]*User, error)` to `ArtistRepository` interface and implementation

## 4. Backend Use Case

- [x] 4.1 Create `PushNotificationUseCase` interface (Subscribe, Unsubscribe, NotifyNewConcerts)
- [x] 4.2 Implement `PushNotificationUseCase` with `webpush-go` for VAPID-based delivery
- [x] 4.3 Write unit tests for `PushNotificationUseCase`

## 5. Backend RPC Handler

- [x] 5.1 Create `PushNotificationHandler` implementing Connect-RPC service
- [x] 5.2 Wire handler into DI provider and Connect server registration
- [x] 5.3 Write unit tests for handler

## 6. Concert Discovery Job Integration

- [x] 6.1 Add `PushNotificationUseCase` to `JobApp` struct and DI initialization
- [x] 6.2 Add `NotifyNewConcerts` call in job loop after `SearchNewConcerts` returns new concerts
- [x] 6.3 Add VAPID config fields to application config

## 7. Infrastructure

- [x] 7.1 Store VAPID key pair in GCP Secret Manager
- [x] 7.2 Add `VAPID_PRIVATE_KEY` to backend ExternalSecret
- [x] 7.3 Add `VAPID_PUBLIC_KEY` to job ConfigMap and server ConfigMap
- [x] 7.4 Add `VITE_VAPID_PUBLIC_KEY` to frontend build environment

## 8. Frontend: Service Worker & PWA

- [x] 8.1 Create `public/manifest.webmanifest` with PWA metadata
- [x] 8.2 Add manifest link to `index.html`
- [x] 8.3 Create `public/sw.js` with push event and notificationclick handlers
- [x] 8.4 Register Service Worker in `main.ts`
- [x] 8.5 Update Caddyfile with Service Worker cache headers

## 9. Frontend: Notification Services

- [x] 9.1 Create `NotificationManager` service (permission state monitoring via `permissions.query()`)
- [x] 9.2 Create `PushService` (PushManager.subscribe, RPC Subscribe/Unsubscribe calls)
- [x] 9.3 Register services in Aurelia DI container

## 10. Frontend: Permission Prompt UI

- [x] 10.1 Create notification opt-in prompt component for dashboard (soft ask pattern)
- [x] 10.2 Bind prompt visibility and button state to `NotificationManager.permission`
- [x] 10.3 Handle denied state with browser settings guidance
