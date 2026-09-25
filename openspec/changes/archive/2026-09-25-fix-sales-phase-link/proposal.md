## Why

Sales-phase announcements and reminders link to `/series/<id>`, but the fan app has no series route (liverty-music/frontend#630), so tapping the notification lands on a missing page. Per the issue's own resolution, the backend should link to an existing screen instead of the frontend adding a new one.

## What Changes

- `SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase` and `SalesReminderUseCase`'s reminder-content fallback (used when a phase has no application url) now link to the concert-detail route (`/concerts/<event_id>`) of the series' earliest upcoming Event, falling back to the series' earliest Event when none is upcoming, and to `/dashboard` when the series has no Event.
- New `Concert.ListEventsBySeries` entity operation returns a series' Events (id, local date, start time) in date order, for resolving which Event to link to.

## Capabilities

### New Capabilities

- `components/entity/concert/list-events-by-series`: lists a series' Events in date order for link resolution

### Modified Capabilities

- `components/usecase/sales-phase/announce-discovered-phase`: the announcement links to the resolved Event's concert page (or the dashboard) instead of the non-existent series page. Relies on `Concert.ListEventsBySeries` (new, above); the audience resolution (`TicketJourney.ListUserIDsTrackingSeries`) is unchanged.
- `components/usecase/sales-phase/scan-due-reminders`: the reminder-content fallback link (used when the phase has no url) is the resolved Event's concert page (or the dashboard) instead of the series page. Relies on `Concert.ListEventsBySeries` (new, above); all other requirements (scheduling, quiet hours, audience) are unchanged.

## Impact

- **Backend**: `internal/entity/concert.go` (new repository method), `internal/infrastructure/database/rdb/concert_repo.go` (implementation + query), `internal/usecase/sales_phase_announcement_uc.go`, `internal/usecase/sales_reminder_uc.go`, a new shared link-resolution helper in `internal/usecase/`, and DI wiring in `internal/di/consumer.go` / `internal/di/sales_reminders_job.go` to supply `ConcertRepository` to both use cases.
- **No proto/frontend changes**: `/concerts/:id` and `/dashboard` already exist in `frontend/src/app-shell.ts`.
