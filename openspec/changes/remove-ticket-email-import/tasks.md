## 1. Proto / BSR

- [x] 1.1 Delete `specification/proto/liverty_music/entity/v1/ticket_email.proto`
- [x] 1.2 Delete `specification/proto/liverty_music/rpc/ticket_email/v1/ticket_email_service.proto`
- [x] 1.3 Run `buf lint` / `buf breaking` locally and confirm the only breaking findings are the two removed files
- [ ] 1.4 Open the proto PR with the `buf skip breaking` label; merge and cut a BSR release

## 2. Backend — delete ticket-email-only files

- [x] 2.1 Delete `backend/internal/entity/ticket_email.go` and `backend/internal/entity/ticket_email_parser.go`
- [x] 2.2 Delete `backend/internal/usecase/ticket_email_uc.go`
- [x] 2.3 Delete `backend/internal/adapter/rpc/ticket_email_handler.go` and `backend/internal/adapter/rpc/mapper/ticket_email.go`
- [x] 2.4 Delete `backend/internal/infrastructure/database/rdb/ticket_email_repo.go`
- [x] 2.5 Delete `backend/internal/infrastructure/gcp/gemini/email_parser.go`
- [x] 2.6 Delete `backend/internal/entity/mocks/mock_TicketEmailRepository.go` (by hand — do not rely on mockery regen, which can fail with `image without types`)
- [x] 2.7 Delete `backend/internal/adapter/rpc/ticket_email_handler_test.go` and any other `*ticket_email*_test.go` files

## 3. Backend — surgical edits to shared files

- [x] 3.1 `di/provider.go`: remove the `emailParser` declaration/comment block, the `ticketEmailRepo`, `ticketEmailUC` and its nil-guard, and the guarded `TicketEmailService` handler registration
- [x] 3.2 `di/consumer.go`: remove the `track-ticket-email` consumer registration (line ~231)
- [x] 3.3 `entity/event_data.go`: remove `SubjectTicketEmailParsed`, `TicketEmailParsedData`, and the subject-list entry
- [x] 3.4 `usecase/analytics_events.go`: remove `EventTicketEmailParsed` and its catalogue map entry
- [x] 3.5 `adapter/event/analytics_consumer.go`: remove `HandleTicketEmailParsed`
- [x] 3.6 Grep the backend for residual `TicketEmail` references (excluding `TicketJourney`) and confirm none remain
- [x] 3.7 Run `make check` (build + lint + test) and fix fallout

## 4. Database

- [x] 4.1 Add a new Atlas migration `DROP TABLE ticket_emails` (and its index) as a file that sorts after all applied migrations (do NOT edit historical migrations; the migration-rebase-guard enforces this)
- [x] 4.2 Register the new migration file in `k8s/atlas/base/kustomization.yaml` and run `atlas migrate hash` to regenerate `atlas.sum`
- [x] 4.3 Remove the `ticket_emails` table, comments, and `idx_ticket_emails_user_event` from `schema/schema.sql`
- [x] 4.4 Run the local migrate check (`make check`; if it fails on a stale DB, `docker compose down -v` first)

## 5. Frontend (fan-web)

- [x] 5.1 Delete `frontend/src/routes/import-ticket-email/` (route.ts + route.html)
- [x] 5.2 Delete `frontend/src/services/ticket-email-service.ts`
- [x] 5.3 `app-shell.ts`: remove the import-ticket-email route registration
- [x] 5.4 `main.ts`: remove the `ITicketEmailService` import and `au.register(ITicketEmailService)`
- [x] 5.5 `scripts/verify-build-templates.lib.ts`: remove the `import-ticket-email` marker entry
- [x] 5.6 `sw.ts`: remove the disabled share-target handler comment block
- [x] 5.7 Delete `frontend/test/routes/import-ticket-email-route.spec.ts` and remove the `ImportTicketEmailRoute` mock from `test/app-shell.spec.ts`
- [x] 5.8 Run the frontend build + tests and confirm green

## 6. Analytics catalogue

- [x] 6.1 Move `ticket.email.parsed` from the dormant/live catalogue to the Removed events section with reason "ticket-email import capability removed"

## 7. ticket-journey main-spec cleanup (direct edit, not a delta)

- [x] 7.1 In `openspec/specs/ticket-journey/spec.md`, remove the "or as a side effect of confirming a ticket email import" clause from the `Set Ticket Journey Status` requirement description
- [x] 7.2 In the same file, remove the orphaned `#### Scenario: Status set via ticket email confirmation` block

## 8. Spec sync & release

- [x] 8.1 Run `openspec validate remove-ticket-email-import --strict` and resolve any findings
- [ ] 8.2 Land backend + frontend PRs (proto/BSR merged first); cut releases
- [ ] 8.3 Deploy the DB `DROP TABLE` migration as a follow-up release after the code that read/wrote the table is gone
- [ ] 8.4 Sync delta specs to main specs, then archive the change
