## 1. Proto Definitions (specification)

- [x] 1.1 Define `TicketEmailId` wrapper message in `entity/v1/ticket_email.proto`
- [x] 1.2 Define `TicketEmailType` enum (`LOTTERY_INFO`, `LOTTERY_RESULT`) in `entity/v1/ticket_email.proto`
- [x] 1.3 Define `TicketEmail` message with all fields (id, user_id, event_id, email_type, raw_body, parsed_data, payment_deadline, lottery_start, lottery_end, application_url) in `entity/v1/ticket_email.proto`
- [x] 1.4 Define `TicketEmailService` with `CreateTicketEmail` and `UpdateTicketEmail` RPCs in `rpc/ticket_email/v1/ticket_email_service.proto`
- [x] 1.5 Define request/response messages for both RPCs (CreateTicketEmailRequest accepts raw_body, email_type, repeated event_ids; UpdateTicketEmailRequest accepts ticket_email_id and correctable fields)
- [x] 1.6 Run `buf lint` and `buf format -w`, verify no breaking changes

## 2. Database Migration (backend)

- [x] 2.1 Create Atlas migration for `ticket_emails` table (id UUID PK, user_id FK, event_id FK, email_type SMALLINT, raw_body TEXT, parsed_data JSONB, payment_deadline TIMESTAMPTZ, lottery_start TIMESTAMPTZ, lottery_end TIMESTAMPTZ, application_url TEXT)
- [x] 2.2 Add index on `(user_id, event_id)` for efficient lookups
- [x] 2.3 Apply migration locally and verify with `atlas migrate apply --env local`

## 3. Backend Entity & Repository (backend)

- [x] 3.1 Define `TicketEmail` entity struct and `TicketEmailType` constants in `internal/entity/ticket_email.go`
- [x] 3.2 Define `TicketEmailRepository` interface (Create, Update, GetByID, ListByUserAndEvent)
- [x] 3.3 Implement pgx-based `TicketEmailRepository`
- [x] 3.4 Write repository integration tests

## 4. Gemini Client (backend)

- [x] 4.1 Create `internal/gemini/parser.go` with `TicketEmailParser` interface
- [x] 4.2 Implement Vertex AI Gemini Flash client with structured output (response schema defining lottery dates, payment deadline, win/loss status, payment status, application URL)
- [x] 4.3 Define the Gemini prompt for Japanese ticket email parsing
- [x] 4.4 Write unit tests with mock Gemini responses

## 5. Backend Service Handler (backend)

- [x] 5.1 Implement `CreateTicketEmail` handler: validate input → call Gemini parser → persist TicketEmail records (one per event_id) → return parsed results
- [x] 5.2 Implement `UpdateTicketEmail` handler: validate ownership → update TicketEmail record → upsert TicketJourney status based on email_type and parsed content
- [x] 5.3 Wire `TicketEmailService` into DI graph (Google Wire)
- [x] 5.4 Write handler unit tests (mock repository + mock Gemini parser)

## 6. Cloud Provisioning

- [x] 6.1 Verify Vertex AI API is enabled in GCP project
- [x] 6.2 Add Vertex AI permissions to backend service account IAM (if not already present)

## 7. Frontend: PWA Share Target (frontend)

- [x] 7.1 Add `share_target` entry to `manifest.webmanifest` (POST, multipart/form-data, title + text params)
- [x] 7.2 Add Service Worker handler to intercept share target POST and redirect to import wizard route with shared data
- [ ] 7.3 Verify share target works on Android via Chrome DevTools or physical device

## 8. Frontend: Import Wizard Route (frontend)

- [x] 8.1 Create `/import/ticket-email` route and view model
- [x] 8.2 Implement Step 1: regex validation for ticket-related keywords
- [x] 8.3 Implement Step 2-3: artist matching (search followed artists in email body) + artist dropdown selection
- [x] 8.4 Implement Step 4: concert selection (filter dashboard by selected artist, multi-select)
- [x] 8.5 Implement Step 5: email body display with edit capability
- [x] 8.6 Implement Step 6: call `CreateTicketEmail` API and display parse results
- [x] 8.7 Implement Step 7: parsed result review/correction + call `UpdateTicketEmail` API

## 9. Frontend: RPC Client (frontend)

- [x] 9.1 Create `ticket-email-service.ts` Connect-RPC client for `TicketEmailService`
- [x] 9.2 Wire into DI container
