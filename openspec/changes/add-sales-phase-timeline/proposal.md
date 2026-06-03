## Why

Fans who refuse to miss a live show currently get notified when a new concert is discovered, but the platform has no objective record of the **ticket sales timeline** — when applications open, when they close, when lottery results are announced, and when payment is due. Missing any of these is how a fan "misses" a show even after knowing it exists. We need to capture the sales schedule as first-class data and remind fans at each critical moment.

## What Changes

- Introduce a `SalesPhase` entity that models one ticket-sales opportunity (method, channel, sequence, application window, lottery-result time, payment deadline, application URL). It **belongs to a `Series` (tour)** and **covers a subset of that tour's events** via an `event_sales_phases` join, so a tour can have distinct phases per leg (e.g. first-half vs. second-half dates) rather than one phase applying to every date. **This depends on `auto-discovery-series-grouping`**: only once a `Series` represents a whole tour (multiple events) does the per-leg subset model hold — without it the current per-`(venue, date)` SINGLE fallback gives each Series a single event and the subset degenerates.
- Add a dedicated Gemini-grounded **sales-phase searcher**, separate from the concert searcher, that takes an artist name + series title as input and extracts that series' sales phases **and the dates each phase covers**. A new scheduled discovery job loops over known series and upserts `SalesPhase` rows idempotently.
- **Two notification paths**: (1) an **event-driven announcement** when the discovery job finds a new phase (reusing the existing discovery→event→push pipeline), and (2) **time-based reminders** scanned at: application open, 24h before close, 1h before close, and lottery-result day. Both target the followers of the performers of each phase's **covered events**, reusing the existing hype-filtered Web Push pipeline, and respect **quiet hours** (22:00–08:00 in the user's `time_zone`, fallback JST) so reminders never wake users at night.
- **Disable the ticket-email-import entry point.** Android Gmail removed its share action, so the PWA Share Target ingestion path no longer works. The feature code/proto/DB is left in place (frozen) but its frontend entry is made unavailable and the dead `share_target` manifest entry is removed.

## Capabilities

### New Capabilities
- `sales-phase`: The `SalesPhase` entity model (method/channel/sequence/timeline fields), its Series ownership plus the covered-events M:N relationship (`event_sales_phases`), and the collision-free stable identity that lets repeated discovery runs converge without duplicates or overwrites.
- `sales-phase-discovery`: The dedicated Gemini searcher (series-scoped input, verbatim-extract + JSON-coerce discipline, covered-event resolution) and the scheduled discovery job that refreshes sales phases for followed artists' upcoming series, including an event-driven announcement push when a new phase is found.
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
