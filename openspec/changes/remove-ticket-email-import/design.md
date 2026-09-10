## Context

The ticket-email-import capability spans four layers — proto/BSR, backend (entity → usecase → rpc → infra + DI + analytics consumer), frontend (route + service + SW), and the database. See proposal.md — Why. It is already dormant in production: `di/provider.go` leaves `emailParser` nil, which the `emailParser != nil` guards use to skip registering both `TicketEmailUseCase` and the `TicketEmailService` handler; the frontend route serves an `unavailable` state and the manifest `share_target` was already removed. The only cross-capability coupling is a one-directional write from `UpdateTicketEmail` into `ticket_journeys`; `ticket-journey` has independent writers (manual `SetStatus`) and readers (sales reminders, sales-phase announcements via `ListUserIDsTrackingSeries`).

## Goals / Non-Goals

**Goals:**
- Delete all ticket-email-only code across every layer with no dangling references.
- Keep the proto removal reviewable as a controlled breaking change (reserve numbers, Buf breaking gate).
- Preserve `ticket-journey` and the shared analytics infrastructure intact.

**Non-Goals:**
- Any change to `ticket-journey` behavior beyond dropping the email side-effect writer.
- Migrating or preserving existing `ticket_emails` rows (feature was dormant; no meaningful data).
- Reworking the Gemini concert searcher (separate from the ticket-email parser).

## Decisions

- **Remove the proto service outright, reserve the numbers.** Delete `entity/v1/ticket_email.proto` and `rpc/ticket_email/v1/ticket_email_service.proto`. Because these are separate top-level files (no other proto imports them — verified), removal is clean; the Buf breaking check still flags the deletion, so the PR carries the `buf skip breaking` label, matching the `remove-merch-search` precedent. Alternative (keeping the messages as `reserved` stubs) was rejected: nothing depends on them and empty stubs add noise.
- **Frontend deletion follows the generated-client dependency.** `services/ticket-email-service.ts` imports `@buf/...ticket_email_service_connect`, which vanishes when the proto is removed. Deleting the service, its `main.ts` registration, the route, the `app-shell.ts` registration, the `verify-build-templates.lib.ts` marker, and both tests removes every consumer before the generated import disappears, so the build stays green.
- **Surgical edits to shared backend files, not deletion.** `entity/event_data.go`, `usecase/analytics_events.go`, `adapter/event/analytics_consumer.go`, `di/provider.go`, and `di/consumer.go` host many other features. Remove only the `TicketEmail*` symbols (`SubjectTicketEmailParsed`, `TicketEmailParsedData`, `EventTicketEmailParsed`, `HandleTicketEmailParsed`, the `track-ticket-email` consumer registration, and the parser/UC/handler wiring). The nil-guard blocks in `provider.go` collapse to plain removal.
- **Drop the table in a follow-up migration.** Add an Atlas migration `DROP TABLE ticket_emails` and update `schema/schema.sql`. No inbound FK exists (verified), so the drop is order-independent w.r.t. other tables. It sorts after all applied migrations so `atlas.sum` stays consistent.
- **Analytics event → Removed events.** Move `ticket.email.parsed` out of the live catalogue into the Removed events section, mirroring the blockchain-event precedent, rather than deleting it silently.

## Risks / Trade-offs

- **Mockery regeneration bug** → `mockery` can die with `image without types` on regen after deleting the `TicketEmailRepository` interface. Mitigation: delete `mock_TicketEmailRepository.go` by hand rather than relying solely on regen, per the `remove-merch-search` experience.
- **Breaking proto consumed by frontend** → the `@buf` client import breaks the frontend build if the service file is removed before its consumers. Mitigation: land frontend consumer deletions and the proto removal together; verify `make lint`/build locally.
- **DB drop timing under ArgoCD main-tracking** → the migration auto-applies on merge. Mitigation: sequence the table drop as its own release step after code that reads/writes the table is gone (it already is — repo/UC removed in the same change), so there is no window where live code queries a dropped table.
- **Losing the general "deferred ticketing events are dormant" analytics scenario** → that scenario's only example (`ticket.email.parsed`) is being removed and no other dormant ticketing event remains. Mitigation: the principle is retained via the `active`/`dormant`/Removed status requirement text; the example-specific scenario is dropped.

## Migration Plan

1. Proto: delete the two `.proto` files, reserve numbers; PR with `buf skip breaking`; BSR release.
2. Backend: delete ticket-email-only files, apply surgical edits to shared files, regen/hand-edit mocks; `make check`.
3. Frontend: delete route/service/tests, remove registrations and marker; build.
4. DB: add `DROP TABLE ticket_emails` Atlas migration + schema.sql update; apply as a follow-up release.
5. Analytics: move `ticket.email.parsed` to Removed events in the catalogue.

Rollback: revert the PRs; the proto messages/numbers can be un-reserved and the table recreated from the prior migration if the feature is ever revived (full re-implementation, not a flip).
