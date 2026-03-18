## 1. Proto — Entity and RPC Definitions

> Proto files in `specification/proto/liverty_music/`. BSR publishes generated code after release.

- [x] 1.1 Define `entity/v1/ticket_journey.proto`: `TicketJourney` message (user_id, event_id, status) and `TicketJourneyStatus` enum (UNSPECIFIED, TRACKING, APPLIED, LOST, UNPAID, PAID)
- [x] 1.2 Define `rpc/ticket_journey/v1/ticket_journey_service.proto`: `TicketJourneyService` with `SetStatus`, `Delete`, `ListByUser` RPCs
- [x] 1.3 Add protovalidate constraints: required fields, defined_only on status enum, UUID validation on event_id
- [x] 1.4 Run `buf lint` and `buf breaking` to verify proto changes

## 2. Backend — Database Migration

- [x] 2.1 Write Atlas migration: CREATE TABLE `ticket_journeys` (user_id UUID FK → users, event_id UUID FK → events, status SMALLINT, PRIMARY KEY (user_id, event_id))
- [x] 2.2 Verify migration applies cleanly on local PostgreSQL and is backward-compatible

## 3. Backend — Entity and Repository

- [x] 3.1 Define `TicketJourney` entity in `internal/entity/ticket_journey.go`
- [x] 3.2 Define `TicketJourneyRepository` port interface in `internal/usecase/port/`
- [x] 3.3 Implement `TicketJourneyRepository` with pgx in `internal/infrastructure/database/rdb/`: Upsert, Delete, ListByUser queries

## 4. Backend — Use Case

- [x] 4.1 Implement `TicketJourneyUseCase` in `internal/usecase/ticket_journey_uc.go`: SetStatus (upsert), Delete, ListByUser
- [x] 4.2 Write unit tests for use case methods

## 5. Backend — RPC Handler and DI

- [x] 5.1 Implement `TicketJourneyServiceHandler` in `internal/adapter/rpc/ticket_journey/`: proto ↔ entity mapping, auth context extraction
- [x] 5.2 Register handler in Google Wire DI configuration (`internal/di/`)
- [x] 5.3 Register route in server mux setup

## 6. Frontend — API Client and Data Integration

- [x] 6.1 Add `TicketJourneyService` Connect client to frontend service layer
- [x] 6.2 Extend `DashboardService.loadDashboardEvents()` to fetch `ListByUser` in parallel with `ListByFollower`
- [x] 6.3 Extend `Concert` entity with optional `journeyStatus` field
- [x] 6.4 Build `Map<eventId, TicketJourneyStatus>` from ListByUser response and merge into Concert objects

## 7. Frontend — Concert Card Badge

- [x] 7.1 Add ticket journey status badge element to `event-card.html` template (visible only when `journeyStatus` is set)
- [x] 7.2 Style the badge per status value using CUBE CSS methodology with `data-journey-status` attribute

## 8. Frontend — Detail Sheet Status Controls

- [x] 8.1 Add ticket journey status display and change controls to `event-detail-sheet.html`
- [x] 8.2 Implement status change handler: call `TicketJourneyService.SetStatus`, update local state
- [x] 8.3 Implement "start tracking" control for events with no journey (initial status selection)
- [x] 8.4 Implement "remove tracking" control: call `TicketJourneyService.Delete`, clear local state
- [x] 8.5 Ensure status changes on the detail sheet reflect immediately on the dashboard card badge
