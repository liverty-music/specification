## Context

The ticket-email-import capability spans four layers — proto/BSR, backend (entity → usecase → rpc → infra + DI + analytics consumer), frontend (route + service + SW), and the database. See proposal.md — Why. It is already dormant in production: `di/provider.go` leaves `emailParser` nil, which the `emailParser != nil` guards use to skip registering both `TicketEmailUseCase` and the `TicketEmailService` handler; the frontend route serves an `unavailable` state and the manifest `share_target` was already removed. The only cross-capability coupling is a one-directional write from `UpdateTicketEmail` into `ticket_journeys`; `ticket-journey` has independent writers (manual `SetStatus`) and readers (sales reminders, sales-phase announcements via `ListUserIDsTrackingSeries`).

## Goals / Non-Goals

**Goals:**
- Delete all ticket-email-only code across every layer with no dangling references.
- Keep the proto removal reviewable as a controlled breaking change (whole-file deletion under the `buf skip breaking` gate).
- Preserve `ticket-journey` and the shared analytics infrastructure intact.

**Non-Goals:**
- Any change to `ticket-journey` behavior beyond dropping the email side-effect writer.
- Migrating or preserving existing `ticket_emails` rows (feature was dormant; no meaningful data).
- Reworking the Gemini concert searcher (separate from the ticket-email parser).

## Decisions

- **Remove the proto service outright.** Delete `entity/v1/ticket_email.proto` and `rpc/ticket_email/v1/ticket_email_service.proto`. Because these are separate top-level files (no other proto imports them — verified), removal is clean; the Buf breaking check still flags the deletion, so the PR carries the `buf skip breaking` label, matching the `remove-merch-search` precedent. Note: `reserved` cannot apply here — it only lives inside a surviving `message`/`enum` body, and whole-file deletion leaves nowhere to write it (unlike `remove-merch-search`, which reserved a field number inside the surviving `series` message). The `buf skip breaking` label is what gates this breaking change; there is no field/enum number to reserve.
- **Frontend deletion follows the generated-client dependency.** `services/ticket-email-service.ts` imports `@buf/...ticket_email_service_connect`, which vanishes when the proto is removed. Deleting the service, its `main.ts` registration, the route, the `app-shell.ts` registration, the `verify-build-templates.lib.ts` marker, and both tests removes every consumer before the generated import disappears, so the build stays green.
- **Surgical edits to shared backend files, not deletion.** `entity/event_data.go`, `usecase/analytics_events.go`, `adapter/event/analytics_consumer.go`, `di/provider.go`, and `di/consumer.go` host many other features. Remove only the `TicketEmail*` symbols (`SubjectTicketEmailParsed`, `TicketEmailParsedData`, `EventTicketEmailParsed`, `HandleTicketEmailParsed`, the `track-ticket-email` consumer registration, and the parser/UC/handler wiring). The nil-guard blocks in `provider.go` collapse to plain removal.
- **Drop the table in a follow-up migration.** Add an Atlas migration `DROP TABLE ticket_emails` and update `schema/schema.sql`. No inbound FK exists (verified), so the drop is order-independent w.r.t. other tables. Author it as a new file that sorts after all applied migrations to avoid rewriting history (which the repo's migration-rebase-guard enforces); then regenerate the directory checksum with `atlas migrate hash` and register the file in `k8s/atlas/base/kustomization.yaml`, per the `remove-merch-search` / `remove-blockchain-ticket-system` precedent.
- **Analytics event → Removed events.** Move `ticket.email.parsed` out of the live catalogue into the Removed events section, mirroring the blockchain-event precedent, rather than deleting it silently.

## Risks / Trade-offs

- **Mockery regeneration bug** → `mockery` can die with `image without types` on regen after deleting the `TicketEmailRepository` interface. Mitigation: delete `mock_TicketEmailRepository.go` by hand rather than relying solely on regen, per the `remove-merch-search` experience.
- **Breaking proto consumed by frontend** → the `@buf` client import breaks the frontend build if the service file is removed before its consumers. Mitigation: land frontend consumer deletions and the proto removal together; verify `make lint`/build locally.
- **DB drop timing under ArgoCD main-tracking** → the migration auto-applies on merge. Mitigation: sequence the table drop as its own release step after code that reads/writes the table is gone (it already is — repo/UC removed in the same change), so there is no window where live code queries a dropped table.
- **The "deferred ticketing events are dormant" analytics scenario loses its concrete example** → that scenario's only example (`ticket.email.parsed`) is being removed and no other dormant ticketing event remains. Mitigation: the scenario is retained but generalized — its `such as ticket.email.parsed` clause is replaced with generic wording ("an event whose feature is deferred or externally blocked"), so the principle survives without a stale example. (OpenSpec MODIFIED cannot drop a scenario, so generalizing in place is also the only tool-valid option.)

## Migration Plan

1. Proto: delete the two `.proto` files; PR with `buf skip breaking`; BSR release.
2. Backend: delete ticket-email-only files, apply surgical edits to shared files, regen/hand-edit mocks; `make check`.
3. Frontend: delete route/service/tests, remove registrations and marker; build.
4. DB: add `DROP TABLE ticket_emails` Atlas migration + schema.sql update, run `atlas migrate hash`, register in `k8s/atlas/base/kustomization.yaml`; apply as a follow-up release.
5. Analytics: move `ticket.email.parsed` to Removed events in the catalogue.

Rollback: revert the PRs; the proto messages and the table can be recreated from the prior definitions/migration if the feature is ever revived (full re-implementation, not a flip).
