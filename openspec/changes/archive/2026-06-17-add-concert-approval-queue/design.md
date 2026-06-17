# Design: Concert Approval Queue

## Context

Discovery pipeline today (all async via Watermill):

```
SearchNewConcerts ──publish CONCERT.discovered──▶ ConcertConsumer.Handle
                                                        │
                                                        ▼
                                              CreateFromDiscovered
                                                ├─ resolve venue (Google Places)
                                                ├─ insert series / events / performers (UPSERT)
                                                └─ publish CONCERT.created ──▶ push "new concert!"
```

`CONCERT.discovered` carries raw `ScrapedConcert` (pre-venue-resolution). Read RPCs (`List`,
`ListByFollower`, `ListWithProximity`) read straight from `events`, so a concert is visible to
fans the instant `CreateFromDiscovered` finishes. The deterministic series id
(`SHA1(venue_id|date)`) plus the `(date, listed_venue_name)` dedup mean a deleted bad event is
re-created identically on the next daily run.

## Goals

- A human checkpoint between discovery and fan-visible publication.
- Re-discovery never silently re-publishes a known-bad event **without** re-review.
- Reject is **not** a permanent blocklist — a later run with corrected data can re-surface the item.
- Keep a durable record of rejections for searcher-quality analysis.
- No re-architecture needed to later relax the gate (auto-approve).

## Decision 1 — Gate by staging, not by post-hoc delete

Insert an approval state between discovery and the `events` write. Discovered items become
`staged_concert(pending)`; only **approve** runs the existing series/event/performer insert.

```
SearchNewConcerts ──CONCERT.discovered──▶ consumer
                                             ├─ resolve venue (Places)
                                             └─ upsert staged_concert(pending)   ← NO events write

admin console ── ApproveConcert ──▶ insert series/events/performers + publish CONCERT.created
             └─ RejectConcert  ──▶ delete staged row + append rejected_concerts_log
```

Why staging over "auto-insert + delete": delete is reactive (bad data is live until a human
notices) and fights the re-discovery loop. Staging is opt-in publication — nothing bad is ever
fan-visible, and the loop is handled by the dedup rule (Decision 4).

## Decision 2 — Resolve the venue **before** staging (review fidelity)

Venue mis-resolution (Places matching the wrong place, or a venue string that should not resolve
at all) is itself a common error class. Resolving up front lets the reviewer see the canonical
venue name + `admin_area` next to the raw `listed_venue_name` and catch those errors.

Sub-decision **B2 (recommended): resolve but do not persist a `venues` row until approval.**
At staging time, call Places and **denormalize** the resolved fields (place_id, canonical name,
admin_area, lat/lng) onto the `staged_concert` row. Create/lookup the real `venues` row only at
approval. This keeps the `venues` table free of orphans from rejected items — important because
the upcoming `add-admin-venue-list` (duplicate detection) reads that table and orphan venues
would pollute it.

Alternative B1 (reuse `resolveVenue` as-is, which creates the `venues` row at staging) is less
code but leaves orphan venues for every rejected/never-approved item. Rejected.

Cost: Places is called for items that may be rejected. Volume is (followed artists × daily), so
this is negligible.

## Decision 3 — `CONCERT.created` fires at approval, not discovery

Downstream consumers of `CONCERT.created` (notably push "new concert!") must only run for
verified data. Move the publish from `CreateFromDiscovered` into the approve use case. This is
strictly more correct: fans are never notified about unverified concerts.

## Decision 4 — Dedup consults published + pending, never rejected

`FilterNew` currently excludes concerts already in `events`. Extend it to also exclude items
already `pending` in `staged_concerts`, so the same item is not queued twice. **Rejected items
are deliberately not consulted** — per the product decision, a later run may bring corrected data
and should re-surface the item for re-review.

Natural key for staging dedup: `(artist_id, local_date, google_place_id)` using the resolved
place id (more robust than the raw listed name). When the venue does not resolve, fall back to
`(artist_id, local_date, listed_venue_name)`.

Resulting staging model is effectively **pending-only**:

```
discover:
  ├ natural key in events            → skip (already published)
  ├ natural key in staged(pending)   → refresh payload, stay pending (latest data wins)
  └ otherwise                        → insert pending

approve → insert into events + delete staged row + publish CONCERT.created
reject  → delete staged row + append rejected_concerts_log
          (next run may re-insert it as pending → re-review)
```

Known, accepted cost: if Gemini returns the *exact same* wrong data the next day, a rejected item
re-appears as pending and must be rejected again (review-level churn, never fan-visible).

## Decision 5 — `rejected_concerts_log` is append-only, analysis-only

A rejection writes one row: raw scraped payload, resolved-venue preview, reason, reviewer
identity, timestamp. It is **never** read by the dedup path (it does not suppress). It exists to
answer "which errors does the searcher repeat?" and feed searcher tuning. Keeping it separate
from `staged_concerts` preserves the pending-only simplicity of the staging table.

## Decision 6 — Admin-scoped moderation service

New `ConcertModerationService` in `rpc/admin/v1`, authorized only for the admin org (per
`rpc-auth-scoping`), consistent with the admin console's auth boundary. A dedicated `admin`
package leaves room for the future venue-admin service without crowding the consumer-facing
`ConcertService`.

- `ListPendingConcerts` → `PendingConcert[]` (staged id, artist, title, local_date, start_time,
  listed_venue_name, resolved venue {name, admin_area, place_id}, source_url, discovered_time).
- `ApproveConcert(staged_id)` → publishes the concert; idempotent if already approved/gone.
- `RejectConcert(staged_id, reason)` → drops + logs; idempotent if already gone.

The published entity shape (`entity.v1.Concert`) is unchanged; `PendingConcert` is a distinct
review DTO because a staged item has no `EventId` yet.

## Onboarding tradeoff (accepted)

Onboarding reads `listConcerts()` straight from `events` right after follow. Gated, a
brand-new artist (never followed by anyone) shows zero concerts until approval. Popular artists
are pre-approved by the daily cron, so the common path is mostly unaffected. Accepted as a
temporary cost; the relaxation path (auto-approve allowlist) is out of scope here.

## Open questions

- **Approve edits?** MVP approves the staged item as-is. Inline correction at review time
  (fix a wrong date/venue then approve) is deferred — for now a wrong-detail item is rejected and
  expected to come back corrected, or handled by the future event-edit change.
- **Reviewer identity source** — Zitadel subject from the admin session; confirm it is available
  to the RPC for `rejected_concerts_log.reviewed_by`.
- **Retention** of `rejected_concerts_log` — unbounded for now; revisit if volume grows.
