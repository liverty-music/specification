## Why

Web Push notification copy is not consistently rendered in the recipient's preferred language. Sales reminders are already localized, but **concert-discovery notifications** ("N new concerts found") are hardcoded English, and the **sales-phase announcement** ("New Ticket Sales Phase") is also hardcoded English even though the `sales-reminders` Notification Content requirement already mandates that the discovery announcement be localized per recipient. Japanese-preferring fans receive English notification text, breaking the personalized experience.

## What Changes

- Concert-discovery follower notifications SHALL select title/body copy by the recipient's `preferred_language`, defaulting to `en` when unset. Body covers singular/plural ("1 new concert found" / "N new concerts found") with a Japanese equivalent.
- The sales-phase discovery announcement SHALL be built per recipient and localized (default `en`), aligning the implementation with the existing `sales-reminders` Notification Content requirement (it currently omits personalization).
- A cross-cutting rule is established: every user-facing Web Push notification selects copy by the recipient's `preferred_language` with an `en` fallback, reusing the existing `NotificationPayload` shape.
- No proto/schema change, no new RPC, no DB migration — localization happens in the backend delivery path using the existing `users.preferred_language` column.

## Capabilities

### New Capabilities
- `push-notification-localization`: Cross-cutting requirement that all user-facing Web Push notification copy is selected by the recipient's `preferred_language` (default `en`), plus the specific content contract for the concert-discovery follower notification (artist name + new-concert count) which is currently unspecified and English-only.

### Modified Capabilities
- `sales-phase-discovery`: The "Event-Driven Announcement on New Phase" requirement is strengthened to state that the announcement is built per recipient and localized to `preferred_language` (default `en`), preventing the implementation drift that left it English-only.

## Impact

- Backend only (`liverty-music/backend`):
  - `internal/entity/push_notification.go` — `NewConcertNotificationPayload` gains a `lang` parameter and localized body.
  - `internal/usecase/push_notification_uc.go` — `NotifyNewConcerts` maps each recipient to a language and marshals one payload per language.
  - `internal/usecase/sales_phase_announcement_uc.go` — gains a `userRepo` dependency to hydrate recipients and localize the announcement.
  - `internal/infrastructure/database/rdb/follow_repo.go` — `ListFollowers` query/scan surfaces `preferred_language`.
  - `internal/di/consumer.go` — wires `userRepo` into the announcement use case.
- No frontend, specification proto, or cloud-provisioning change.
- No breaking changes; behavior change is notification copy language only.
