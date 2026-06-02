## Why

Fans who refuse to miss a live show currently get notified when a new concert is discovered, but the platform has no objective record of the **ticket sales timeline** — when applications open, when they close, when lottery results are announced, and when payment is due. Missing any of these is how a fan "misses" a show even after knowing it exists. We need to capture the sales schedule as first-class data and remind fans at each critical moment.

## What Changes

- Introduce a `SalesPhase` entity that models one ticket-sales opportunity for a tour/series (method, channel, sequence, application window, lottery-result time, payment deadline, application URL). It is **Series-scoped**, because sales phases are announced per tour, not per individual date. **This depends on `auto-discovery-series-grouping`**: only once a `Series` represents a whole tour does Series-scoping avoid per-date duplication — without it the current per-`(venue, date)` SINGLE fallback would fragment a tour and duplicate each phase per date.
- Add a dedicated Gemini-grounded **sales-phase searcher**, separate from the concert searcher, that takes an artist name + series title as input and extracts that series' sales phases. A new scheduled discovery job loops over known series and upserts `SalesPhase` rows idempotently.
- Add a **multi-stage reminder** job that scans upcoming sales phases and pushes notifications at: application open, 24h before close, 1h before close, and lottery-result day. Reminders target performers' followers, reusing the existing hype-filtered Web Push pipeline.
- **Disable the ticket-email-import entry point.** Android Gmail removed its share action, so the PWA Share Target ingestion path no longer works. The feature code/proto/DB is left in place (frozen) but its frontend entry is made unavailable and the dead `share_target` manifest entry is removed.

## Capabilities

### New Capabilities
- `sales-phase`: The `SalesPhase` entity model (method/channel/sequence/timeline fields), its Series-scoped persistence, and the idempotent upsert key that lets repeated discovery runs converge without duplicates.
- `sales-phase-discovery`: The dedicated Gemini searcher (series-scoped input, verbatim-extract + JSON-coerce discipline to suppress hallucinated dates) and the scheduled discovery job that refreshes sales phases for followed artists' upcoming series.
- `sales-reminders`: The scheduled scan that fires multi-stage push reminders for approaching sales-phase milestones, with a sent-log for idempotent once-only delivery, reusing the existing follower hype-filter and Web Push sender.

### Modified Capabilities
- `ticket-email-import`: The import entry point is disabled — the frontend route/navigation is made unavailable and the `share_target` manifest entry is removed. Backend RPCs, parsing, and storage remain but are no longer reachable by users. **Archive ordering**: this delta MODIFIES `ticket-email-import`, so this change MUST be archived after the in-flight `ticket-email-import` change, otherwise the MODIFIED baseline requirements do not yet exist in `openspec/specs/`.

## Impact

- **specification**: New `entity/v1/sales_phase.proto` (`SalesPhase`, `SalesPhaseId`, `SalesMethod`, `SalesChannel`). Optional reference RPC if `SalesPhase` is surfaced on concert detail. `ticket_email.proto` is unchanged.
- **backend**: New sales-phase searcher in `internal/infrastructure/gcp/gemini`, new use case + pgx repository, Atlas migration for `sales_phases` and `sales_phase_reminders` (no change to `ticket_emails`), two new job entrypoints (`cmd/job/sales-phase-discovery`, `cmd/job/sales-reminders`) and a reminder consumer. Reuses `webpush.Sender`, `PushSubscriptionRepository.ListByUserIDs`, the event publisher, and the hype-filter from `NotifyNewConcerts`.
- **frontend**: Disable the `/import/ticket-email` entry, remove `share_target` from `manifest.webmanifest`, and disable the Service Worker share interception. Component/client code is retained.
- **cloud-provisioning**: Two new CronJob manifests (`sales-phase-discovery` daily, `sales-reminders` ~15-minute) and confirmation of Vertex AI / DB IAM for the new jobs.
- **Depends on**: `auto-discovery-series-grouping` (a `Series` must represent a whole tour for the Series-scoped model to hold); and on the `ticket-email-import` change being archived first (this change MODIFIES its spec).
- **Out of scope (later phases)**: email→`SalesPhase` integration on revival, lottery win/loss (result) import (funnel stage ③), `TicketJourney`↔`SalesPhase` linkage, per-user first-come payment deadlines, the F dashboard, and C merch.
