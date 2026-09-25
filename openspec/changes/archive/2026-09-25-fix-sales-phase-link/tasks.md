## 1. Entity operation

- [x] 1.1 Add `ListEventsBySeries` to `entity.ConcertRepository` in `internal/entity/concert.go`
- [x] 1.2 Implement it in `internal/infrastructure/database/rdb/concert_repo.go` (query ordered by `local_event_date`, `start_at` NULLS LAST)
- [x] 1.3 Regenerate mocks with `mockery`

## 2. Shared link resolution

- [x] 2.1 Add a shared link-resolution helper in `internal/usecase` (earliest upcoming Event's `/concerts/<id>`, else earliest Event's, else `/dashboard`)
- [x] 2.2 Update `SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase` to use it instead of `/series/<id>`
- [x] 2.3 Update `sales_reminder_uc.go`'s `buildReminderPayload` fallback (phase has no url) to use it instead of `/series/<id>`
- [x] 2.4 Wire `entity.ConcertRepository` into both use case constructors and their DI wiring (`internal/di/consumer.go`, `internal/di/sales_reminders_job.go`)

## 3. Tests

- [x] 3.1 Integration test for `ListEventsBySeries` against local Postgres
- [x] 3.2 Unit tests for the link-resolution helper: earliest upcoming, fallback to earliest, fallback to dashboard (no events), fallback to dashboard (repository error)
- [x] 3.3 Update `SalesPhaseAnnouncementUseCase` and `SalesReminderUseCase` unit tests for the new URL behavior

## 4. Spec coverage exemptions

@spec-manual components/usecase/sales-phase/announce-discovered-phase "Phase with an application url" -- AnnounceDiscoveredPhase's input, entity.SalesPhaseDiscoveredData, carries only PhaseID and SeriesID; it has no application-url field at all, so the announcement can never read one regardless of what the underlying SalesPhase row holds. There is no way to construct a test input that represents "the phase has an application url" from this use case's perspective — every test of AnnounceDiscoveredPhase already exercises the code path this scenario describes, since the phase's own url is structurally unreachable. Verified by inspection of `entity.SalesPhaseDiscoveredData` (internal/entity/event_data.go) and `salesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase` (internal/usecase/sales_phase_announcement_uc.go), which never reference a phase url.
