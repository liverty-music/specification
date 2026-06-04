## Why

Users who follow multiple artists must manually track ticket lottery deadlines and payment due dates across dozens of emails from e+, pia, Lawson Ticket, etc. Missing a payment deadline means losing a won lottery ticket. PWA Share Target lets users import ticket-related emails directly from the Gmail Android app into Liverty Music with minimal effort (tap Share → select app → confirm), centralizing deadline management and enabling push notification reminders.

## What Changes

- Add PWA Share Target to `manifest.webmanifest` so the app appears in Android's share sheet
- Add a multi-step email import wizard in the frontend: validation → artist matching → concert selection → body confirmation → submit
- Add `TicketEmail` entity and two new RPCs (`CreateTicketEmail`, `UpdateTicketEmail`) for persisting and confirming parsed email data
- Integrate Vertex AI Gemini Flash on the backend to parse unstructured email text into structured ticket data (lottery dates, payment deadlines, win/loss status)
- Auto-update `TicketJourney` status based on parsed email content (TRACKING for lottery info, UNPAID/PAID/LOST for lottery results)
- Add `ticket_emails` table to store imported email metadata and parsed results

## Capabilities

### New Capabilities

- `ticket-email-import`: PWA Share Target integration, email validation, Gemini-based parsing, and structured data extraction from ticket-related emails

### Modified Capabilities

- `ticket-journey`: TicketJourney status is now also updated as a side effect of email import confirmation (TRACKING, UNPAID, PAID, LOST), in addition to manual user updates

## Impact

- **specification**: New `TicketEmail` entity proto, new `TicketEmailService` RPC definitions, `TicketEmailType` enum
- **backend**: New service handler, Gemini Flash client integration, new DB table + repository, new migration
- **frontend**: Share Target in manifest, Service Worker POST interception, new import wizard route/components, artist search + concert selection UI
- **cloud-provisioning**: Vertex AI API enablement (if not already enabled), IAM service account permissions for Gemini
