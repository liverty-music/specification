## Why

The ticket-email-import feature depended on the Android Gmail app's "share" action targeting the PWA via the manifest `share_target` declaration. That share entry point no longer exists — modern Gmail/OS share sheets dropped the action that fed it — so the ingestion path can never fire. The feature is already dormant in production (the frontend route serves an "unavailable" state and the backend leaves the Gemini parser unwired, so the use case and RPC handler are never registered). Rather than carry dead code and a dormant analytics event indefinitely, we remove the capability entirely.

## What Changes

- **BREAKING** Remove the `TicketEmailService` RPC (`CreateTicketEmail`, `UpdateTicketEmail`) and the `TicketEmail` / `TicketEmailId` / `TicketEmailType` proto definitions by deleting their `.proto` files, and push through Buf breaking-change review with the `buf skip breaking` label.
- Remove the frontend import wizard route, its RPC client service, DI registration, route registration, build-template marker, and tests. Remove the disabled Service Worker share-target comment block.
- Remove the backend `TicketEmail` entity, parser interface, use case, RPC handler, mapper, repository, and the Gemini `EmailParser` infrastructure (ticket-email only).
- Remove the `ticket.email.parsed` analytics event: the NATS subject, published payload, catalogue entry, and the analytics consumer handler/registration.
- Drop the `ticket_emails` database table (Atlas migration + schema.sql).
- **Preserve** the independent `ticket-journey` capability. Only the one-directional write from ticket-email confirmation into ticket-journey status goes away; the journey use case, RPC, manual `SetStatus`, and its consumers (sales reminders, sales-phase announcements) are untouched.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `ticket-email-import`: All requirements are removed — the capability is retired in full (entity, IDs, Create/Update RPCs, database schema, PWA share target, and import wizard).
- `product-analytics`: The `ticket.email.parsed` event is removed from the live catalogue and recorded under Removed events; the dormant-event example scenarios that reference it are updated.
- `frontend-testing`: The "Import ticket email route has component integration tests" requirement is removed.

**Not a delta (main-spec hand edit):** `ticket-journey` keeps its behavior; only the orphaned "Status set via ticket email confirmation" scenario and the "or as a side effect of confirming a ticket email import" clause in `Set Ticket Journey Status` must be removed. OpenSpec deltas cannot drop a single scenario from a surviving requirement (MODIFIED refuses to omit scenarios, and same-name REMOVE+ADD is rejected), so this is handled as a direct edit to `openspec/specs/ticket-journey/spec.md` during implementation.

## Impact

- **Proto / BSR**: `entity/v1/ticket_email.proto`, `rpc/ticket_email/v1/ticket_email_service.proto` deleted. Breaking change → requires the `buf skip breaking` label. (No number reservation: the whole files are deleted, so there is no surviving `message`/`enum` in which to write `reserved`.) The `@buf` generated code the frontend client imports disappears in lockstep.
- **Backend**: `entity/ticket_email.go`, `entity/ticket_email_parser.go`, `usecase/ticket_email_uc.go`, `adapter/rpc/ticket_email_handler.go`, `adapter/rpc/mapper/ticket_email.go`, `infrastructure/database/rdb/ticket_email_repo.go`, `infrastructure/gcp/gemini/email_parser.go`, `entity/mocks/mock_TicketEmailRepository.go` deleted. Surgical edits to `di/provider.go`, `di/consumer.go`, `entity/event_data.go`, `usecase/analytics_events.go`, `adapter/event/analytics_consumer.go`.
- **Frontend (fan-web)**: `routes/import-ticket-email/`, `services/ticket-email-service.ts`, and route tests deleted. Edits to `app-shell.ts`, `main.ts`, `scripts/verify-build-templates.lib.ts`, `test/app-shell.spec.ts`, `sw.ts`.
- **Database**: `DROP TABLE ticket_emails` (no inbound FK references; applied via ArgoCD main-tracking as a follow-up release). `ticket_journeys` retained.
- **Analytics**: `ticket.email.parsed` removed from the PostHog catalogue.
