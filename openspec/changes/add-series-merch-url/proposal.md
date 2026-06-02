## Why

Fans who never want to miss a live also do not want to miss official merchandise — but today the platform offers no path from a concert to its goods page, forcing fans to search externally. The lowest-cost, highest-value step is a single tap from the event detail sheet to the tour's official merch page. We intentionally store only the link (not sale timing, channels, or item catalogs): the linked page already carries those details, and keeping the model to one URL mirrors the proven `Series.source_url` pattern.

Merch information, however, surfaces on a different cadence and from different sources than concert schedules: it is published close to the event (weeks before, not the 6–12 months ahead that concert discovery runs), and it is frequently richest on an artist's official **social media** post rather than the official website. A merch URL is therefore resolved by a dedicated, time-windowed discovery job rather than piggybacking on the concert-discovery crawl.

## What Changes

- Add an optional `merch_url` field (type `Url`) to the `Series` entity, mirroring the existing optional `source_url` (next field number, `5`). Non-breaking, additive.
- Persist `merch_url` on the series row (new nullable column) and resolve it onto the embedded `Series` in every `Concert` response, exactly as `source_url` is handled.
- Add a dedicated, scheduled **merch-url discovery job** (mirroring the existing concert-discovery job) that:
  - selects series whose **earliest event** is within the next 60 days and whose `merch_url` is empty **or** a dead link (HTTP non-2xx/3xx) — clearing dead links before re-searching;
  - asks Gemini Flash-Lite (with search grounding) for the single URL carrying the richest merch sales information, restricted to the **official site or official social media**, returning empty when no confident official source exists (no hallucinated URL);
  - persists the resolved URL fill-once (never overwriting a live URL), with `Url` validation.
- Render a "グッズ情報" (merch info) link in the event detail sheet when `concert.series.merch_url` is present, as a sibling to the existing official-info link, with parallel JA/EN i18n copy.

## Capabilities

### New Capabilities

- `merch-discovery`: A scheduled job that discovers and maintains official merch information for series with an upcoming event — currently the merch page URL (`Series.merch_url`) — using a time-windowed candidate scan, dead-link revalidation, and a Gemini Flash-Lite search restricted to official site / official social media.

### Modified Capabilities

- `event-management`: The `Series` entity gains an optional `merch_url` (`Url`) field; series persistence and the embedded `Series` in the `Concert` DTO carry it through to clients.
- `concert-detail`: The event detail sheet renders a merch info link when the embedded series carries a `merch_url`, with a dedicated `eventDetail.*` i18n key.

## Impact

- **specification**: `series.proto` gains `Url merch_url = 5`; regenerated Go/TS types via BSR. Additive — no breaking change.
- **backend**: New nullable `merch_url` column on the series table (migration); repository read/write and Concert hydration. New job under `cmd/job/merch-discovery` (mirroring `cmd/job/concert-discovery`): series-listing query (earliest-event within 60 days, `merch_url` empty/dead), HTTP liveness checker, Gemini Flash-Lite searcher, fill-once persistence, and `auto-concert-discovery`-style resilience.
- **frontend**: `event-detail-sheet` template + view model render the link; new `eventDetail.viewMerch` i18n key in JA/EN `translation.json`.
- **cloud-provisioning**: New CronJob manifest scheduling the merch-url discovery job (daily in prod, weekly in dev), reusing the Vertex AI workload-identity service account already used by concert discovery.
- **dependencies**: None new. Reuses the existing `Url` value object, the Gemini client, and the established job/scheduling and `source_url` rendering flows.
