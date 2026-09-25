## Context

See proposal.md - Why. Two backend use cases (`SalesPhaseAnnouncementUseCase`, `SalesReminderUseCase`) both build a `/series/<id>` deep link that the fan app cannot route. Both already resolve their audience through the series id alone (`TicketJourney.ListUserIDsTrackingSeries`), so neither currently has an Event handy to link to.

## Goals / Non-Goals

- Goal: both call sites link to a screen the fan app can actually render, without adding a new frontend route.
- Non-Goal: deciding which Event "best" represents a multi-event series' sales phase when the phase covers a subset of events - the issue's own resolution (earliest upcoming, else earliest) is accepted as-is; the mismatch this can produce for a festival-style series with many events is a pre-existing ambiguity in the notification model, not something this change resolves.

## Decisions

- **New `Concert.ListEventsBySeries` entity operation** on `ConcertRepository`, returning only the fields link resolution needs (id, local date, start time), following the existing `FindEventsByVenueAndDate` / `FindEventsByArtistAndDate` pattern (physical-identity projection, not the full `Concert` DTO). Implemented as a straight `SELECT ... WHERE series_id = $1 ORDER BY local_event_date, start_at NULLS LAST` in `rdb/concert_repo.go`.

  Alternative considered: reuse `SeriesRepository.GetAuthored`. Rejected - it is scoped to first-party organizer-authored series (branches on `DRAFT` publish state, also loads performers), which is the wrong semantic fit for a link resolved for any series (including scraped/discovered ones), and would pull in data the notification does not use.

- **Shared helper in `internal/usecase`** (e.g. `ResolveSeriesLinkURL(ctx, seriesID, concertRepo, logger) string`) used by both `SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase` and `SalesReminderUseCase`'s per-phase reminder-content fallback, mirroring how `ResolveSalesPhaseAudience` is already shared between the two so the two call sites cannot drift. It never returns an error: a repository failure is logged and falls back to `/dashboard`, so a link-resolution problem never blocks sending the notification itself.
- Picking "earliest upcoming, else earliest" is done in Go over the ordered list `ListEventsBySeries` returns (first element with local date >= today, else the first element), not in SQL, so the two-tier fallback stays readable and unit-testable against a mocked repository.
- Both use cases gain a `ConcertRepository` dependency, wired in `internal/di/consumer.go` (already constructs one for `concertCreationUC`) and newly constructed in `internal/di/sales_reminders_job.go`.

## Risks / Trade-offs

- [A series with several concurrent events (e.g. a two-city tour) links every recipient to one arbitrarily "earliest" event, not necessarily the one the phase is actually for] -> Accepted per the issue's own decision; a future change can thread the specific Event through `SalesPhaseDiscoveredData` / `SalesPhase` if this proves confusing in practice.
- [Extra query per phase/announcement] -> One `ListEventsBySeries` call per `AnnounceDiscoveredPhase` invocation and once per `processPhase` scan (not per user/stage), consistent with the existing per-phase audience and sent-log queries.

## Migration Plan

None - no data migration, no new route, no proto change. Deploys as a normal backend release.
