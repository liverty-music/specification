## Why

The concert discovery job (`auto-concert-discovery`) finds new concerts automatically, but there is no mechanism to notify users. Users must manually open the app to see new events. The core value proposition — "never miss a live show" — requires proactive delivery of discovery results via push notifications.

## What Changes

- Add Web Push notification delivery when the concert discovery job finds new concerts for followed artists
- Add a `push_subscriptions` table for storing browser Push API subscription data per user
- Add RPC endpoints for subscribing/unsubscribing push notification credentials
- Add Service Worker push event handling in the frontend PWA
- Add notification permission prompt UI in the dashboard
- Add VAPID key management to infrastructure (Secret Manager, K8s secrets)
- Extend the concert discovery job with a notification dispatch step
- Add `ListFollowers` method to `ArtistRepository` for querying users who follow a given artist

## Capabilities

### New Capabilities
- `push-notification`: Web Push subscription management, VAPID-based notification delivery, and Service Worker push event handling

### Modified Capabilities
- `auto-concert-discovery`: Add notification dispatch step after discovering new concerts for an artist
- `artist-following`: Add `ListFollowers` query to retrieve users following a specific artist

## Impact

- **Backend**: New entity (`PushSubscription`), repository, use case, and RPC handler. Modified concert discovery job and artist repository.
- **Frontend**: New Service Worker (`sw.js`), PWA manifest, `NotificationManager` service, `PushService` service, and permission prompt UI component.
- **Infrastructure**: VAPID keys in GCP Secret Manager, ExternalSecret updates, ConfigMap updates, Caddyfile headers for Service Worker.
- **Proto**: New `PushNotificationService` with `Subscribe`/`Unsubscribe` RPCs.
- **Dependencies**: `github.com/SherClockHolmes/webpush-go` (Go backend).
