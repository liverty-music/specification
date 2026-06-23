## Context

The approval-queue screen (`admin/approval-queue/`) renders a flat `<table>` over a
`QueueRow[]` array derived from `PendingConcert[]`. The approved-concerts screen
(`admin/approved-concerts/`) already groups a flat `Concert[]` list into
`ArtistGroup → SeriesGroup → ConcertRow[]` using `groupByArtistAndSeries()` and
renders it with `<details>` elements.

`PendingConcert` exposes `performer.name` (artist) and `title` (tour/show name), which
serve as natural grouping keys equivalent to `performers[0].name` and `series.title`
used in the approved-concerts page. No `series.id` is present on `PendingConcert`
because series entities are created during approval; the title is the only series
identity available at staging time.

## Goals / Non-Goals

**Goals:**
- Group pending concerts by artist then by title in the approval-queue UI.
- Show unresolved-venue count per series in the collapsed summary so reviewers can
  triage without expanding every group.
- Preserve per-row Approve / Reject (with reason inline form) unchanged.
- Reuse the `<details>` / `<summary>` pattern already established on approved-concerts.

**Non-Goals:**
- Bulk approve-all / reject-all per series (deferred; adds rubber-stamp risk).
- Proto or backend changes (no new fields needed).
- Grouping by series ID (unavailable on `PendingConcert`; title is sufficient).

## Decisions

### Decision: Group by `title` as series proxy (no proto change)

**Choice:** Use `PendingConcert.title.value` as the series grouping key within each
artist bucket, mirroring how `Concert.series.title` is used on approved-concerts.

**Rationale:** `title` is described in the proto comment as "the tour or show name"
and is set from the AI-extracted series title at staging time. Introducing a
`series_id` on `PendingConcert` would require a proto change, BSR generation, and a
backend join — disproportionate cost for a display-only feature. Title-based grouping
is consistent with how approved-concerts falls back when `series.id` is absent.

**Risk:** AI extraction may produce slightly different title strings for the same tour
across separate discovery runs (e.g., casing or punctuation variation). In practice,
concerts from a single discovery batch share a normalised title; cross-batch variation
is rare and the grouping degrades gracefully (two groups instead of one).

### Decision: `unresolvedCount` surfaced in series summary

**Choice:** Compute the count of rows without a resolved venue (`hasResolvedVenue === false`)
at group-build time and display it in the `<summary>` (e.g., "⚠ 2 unresolved venues").

**Rationale:** Unresolved venues are the primary reason a reviewer needs to inspect
individual rows. Surfacing the count at the collapsed level lets a reviewer skip
fully-resolved series quickly.

### Decision: No `<details open>` by default

**Choice:** All series groups are collapsed on load.

**Rationale:** The queue may contain many series. Expanding all by default re-creates
the cognitive load problem the grouping is meant to solve. A reviewer opens only the
series they need to inspect.

### Decision: Reuse `groupByArtistAndSeries` pattern, not the function itself

**Choice:** Implement a parallel `groupQueueByArtistAndSeries` function in
`approval-queue-route.ts` rather than extracting a shared utility.

**Rationale:** The two pages have different row types (`QueueRow` vs `ConcertRow`) and
different source types (`PendingConcert` vs `Concert`). A shared generic would require
type parameters or duck-typing that adds complexity without proportional benefit.
The algorithm is short (~30 lines); duplication is intentional here.

## Risks / Trade-offs

- **Title variation across discovery batches** → Degrades to extra groups rather than
  breaking; acceptable given the queue lifecycle (batches are reviewed promptly).
- **Large queue size** → Collapse-by-default mitigates; no virtual-scroll needed at
  expected queue sizes.

## Migration Plan

Frontend-only change; no database migration or proto release required. Deployed as a
standard frontend release.
