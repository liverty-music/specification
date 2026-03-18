## Context

Users receive ticket-related emails (lottery announcements, win/loss notifications) from Japanese ticketing platforms (e+, pia, Lawson Ticket). These emails contain critical deadlines (payment due dates, lottery periods) that are easy to lose track of across multiple concerts. The existing `TicketJourney` system only tracks status (TRACKING → APPLIED → UNPAID/PAID/LOST) without any associated deadline or metadata.

Push notifications are already implemented. The `TicketJourney` entity and RPC service exist. The frontend is an Aurelia 2 PWA with Workbox-based Service Worker running on Android.

## Goals / Non-Goals

**Goals:**
- Enable users to import ticket emails from Gmail Android app via PWA Share Target with minimal friction
- Parse unstructured Japanese email text into structured data using Vertex AI Gemini Flash
- Persist parsed email data in a `ticket_emails` table linked to `TicketJourney`
- Auto-update `TicketJourney` status based on parsed results
- Provide a two-step flow: create (parse + persist) → update (user confirms/corrects)

**Non-Goals:**
- iOS support (PWA Share Target is not stable on iOS Safari)
- Email forwarding / auto-ingestion (Phase 2)
- Push notification scheduling for deadlines (separate change — infrastructure exists)
- Supporting non-ticket emails or generic email import
- Manual form entry for ticket data

## Decisions

### Decision 1: PWA Share Target as the input mechanism

**Choice**: Web Share Target API (POST with `multipart/form-data`)

**Rationale**: On Android, Gmail's share button passes email subject as `title` and plain-text body as `text`. This requires only a manifest entry and Service Worker handler — no native app, no Gmail Add-on, no email forwarding infrastructure.

**Alternative considered**: Email forwarding with per-user ingest address. Rejected for Phase 1 because it requires email server infrastructure (MX records, SMTP ingest), per-user token management, and has higher PII risk (full email including headers stored server-side). PWA Share Target gives the user explicit control over what is shared.

### Decision 2: Two-step API (CreateTicketEmail → UpdateTicketEmail)

**Choice**: `CreateTicketEmail` persists the raw email + Gemini parse result immediately. `UpdateTicketEmail` applies user corrections and triggers `TicketJourney` status update.

**Rationale**: Persisting on first call is more robust than a pure preview-then-confirm pattern. If the user's session drops after parsing, the data is not lost. The user can return and correct/confirm later. This also creates an audit trail of what was imported.

**Alternative considered**: Parse-only preview (no DB write) then single create. Rejected because a session drop after an expensive Gemini call loses all work.

### Decision 3: Vertex AI Gemini Flash for email parsing

**Choice**: `gemini-3.0-flash` via Vertex AI Go SDK with structured output (response schema).

**Rationale**: The system already runs on GCP (GKE + Cloud SQL). Gemini 3.0 Flash is cost-effective, fast (sub-second for short emails), and handles diverse Japanese email formats without per-vendor regex maintenance. Structured output via response schema ensures the model returns a defined JSON shape.

**Alternative considered**: Per-vendor regex patterns. Rejected due to high maintenance cost — each ticketing platform has different email formats that change without notice.

### Decision 4: TicketEmail as a separate table (not extending TicketJourney)

**Choice**: New `ticket_emails` table with FK to `(user_id, event_id)` matching `ticket_journeys` composite key.

**Rationale**: Multiple emails can be imported per concert per user (lottery announcement + result notification). The `ticket_journeys` table remains a simple status record. Parsed metadata (deadlines, URLs) lives in `ticket_emails`, and the most recent relevant values can be queried via a join or denormalized on write.

### Decision 5: Frontend validation before API call

**Choice**: Client-side regex validation to filter obviously non-ticket emails before sending to backend.

**Rationale**: Avoids unnecessary Gemini API calls (cost + latency) for irrelevant emails. The regex checks for keywords common across Japanese ticketing platforms (e.g., "抽選", "当選", "落選", "チケット", "入金期限"). False negatives are acceptable — users can also manually enter data via existing `SetStatus`.

### Decision 6: Artist matching on the client side

**Choice**: The frontend searches the user's followed artists list against the email body text locally, then presents a dropdown for confirmation/override.

**Rationale**: The followed artists list is already available on the client (loaded for dashboard). No additional API call needed. Fuzzy matching is not required — exact substring match of artist names suffices for Phase 1.

## Risks / Trade-offs

**[Risk] Gemini hallucination on dates/amounts** → Mitigation: Two-step flow ensures user reviews parsed data before it affects `TicketJourney` status. `UpdateTicketEmail` is the only path that triggers status changes.

**[Risk] Gmail share data fidelity varies** → Mitigation: Gmail Android typically passes subject + plain-text body. HTML structure is lost but Gemini handles unstructured text well. If `text` is empty/truncated, the frontend validation step catches it early.

**[Risk] Email body contains PII (name, address, phone)** → Mitigation: Step 5 of the import wizard shows the email body and allows editing before submission. Users can redact sensitive information. The `raw_body` field stores the user-edited version, not the original.

**[Trade-off] Client-side artist matching is naive** → Acceptable for Phase 1 with a small followed-artists list. If users follow hundreds of artists, consider server-side search later.

**[Trade-off] No offline support for import** → Share Target POST requires network connectivity to call Gemini. Acceptable because the import flow is inherently online (needs parsing). Offline queuing could be added later via Service Worker background sync.
