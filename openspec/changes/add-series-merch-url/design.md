## Context

The `Series` entity (defined in `event-management`) already carries an optional `source_url` for official source/announcement pages, rendered by the event detail sheet (`concert-detail`) as an official-info link. Fans have no in-app path to a tour's official merchandise page. This change adds a single optional merch URL plus the mechanism that keeps it populated.

The first design piggybacked merch-url extraction on the concert-discovery Gemini crawl (`gemini-grounded-extract-and-coerce`). That was rejected: concert discovery runs 6–12 months ahead of events (before merch pages exist), targets the official website (merch is often richest on official social media), and loops per-artist (merch URL is per-series). Instead, a dedicated time-windowed job resolves the URL when the information actually exists. This aligns with feature A (sales timeline), which already adopted a dedicated per-series Gemini searcher rather than extending concert search.

This is the "C. グッズ・物販" feature of the never-miss-a-live roadmap, scoped down (after explicit product review) from a richer merch-timeline model to a single link.

## Goals / Non-Goals

**Goals:**
- One-tap access from the event detail sheet to a tour's/single-live's official merch page (official site or official social media).
- Resolve the URL at the right time (close to the event) and keep it healthy (revalidate dead links).
- Minimal, additive, non-breaking schema change that mirrors `Series.source_url`.

**Non-Goals:**
- Storing sale timing (start/deadline), sales channels, limited-goods detail, prices, inventory, or item catalogs — these live on the linked page and are the user's to read.
- Feeding the Next Action dashboard (F): because no timing is stored, merch contributes no deadlines. F's deadline sources remain ticket sales (A) and ticket-email-import.
- Per-event or per-venue merch links — the link is series-level only.
- Verifying merch availability or page content beyond a URL liveness (HTTP status) check.

## Decisions

**1. A field on `Series`, not a new `MerchSale` entity.**
The requirement reduced to "one official merch link per tour." A dedicated entity (channel/timing/items) was rejected as over-modeling: nothing beyond the URL is stored, and one-URL-per-series is exactly the `source_url` precedent. Field number `5`, optional `Url`, additive — no breaking change.

**2. Store only the URL.**
Alternative considered: a merch-timeline model carrying sale start/deadline so reminders could fire and F could surface "受注締切まであと2日." Rejected per product direction — the linked page already holds those details. Accepted consequence: C is purely a navigational link and does not participate in deadline aggregation.

**3. A dedicated scheduled job, not a concert-search piggyback.**
Resolving `merch_url` inside the concert-discovery crawl fails on three axes:

| Axis | Concert-search piggyback | Dedicated merch-url job |
|------|--------------------------|--------------------------|
| Timing | Runs 6–12 months ahead; merch page does not exist yet → field stays empty with no reliable re-visit | Runs against series whose earliest event is ≤ 60 days away — when merch info actually exists; retries each run until found |
| Source | Tuned for the official-site schedule; merch is often richest on official social media | Prompt restricted to official site **or** official social media |
| Granularity | Per-artist loop | Per-series scan (matches `Series.merch_url`) |
| Prompt/cost | Bolts merch onto a complex multi-event extraction prompt; cost on every crawl | Single-purpose Flash-Lite prompt; cost bounded to the within-60-day empty/dead set |

The job mirrors `cmd/job/concert-discovery` and adopts `auto-concert-discovery`'s resilience (consecutive-failure circuit breaker, per-series non-fatal failures, job always exits success). Feature A's per-series searcher shares this shape; a future "series enrichment scanner" could host both extractors, but the two features ship independently for now.

**4. Candidate selection and dead-link revalidation.**
A series is a candidate when its **earliest event's** `local_date` falls in `[today, today+60d]` **and** its `merch_url` is empty or dead. For a non-empty `merch_url` in that window, the job performs an HTTP liveness check: a definitive non-2xx/3xx response (or hard failure) means dead → clear the field → re-search. Transient/ambiguous results (timeouts, network blips, bot-blocked HEAD) are treated as alive to avoid churn. The earliest-event baseline means lookup starts ~60 days before the first show, when tour merch is typically announced, and the series naturally drops out once that date passes.

**5. Gemini resolution: official-only, single best URL, or empty.**
The job calls Gemini Flash-Lite with search grounding, passing the artist name and series title, and asks for the one URL with the richest merch sales information, sourced only from the official site or official social media accounts. When no confident official source exists (common in the 60-day window before merch drops), it returns empty rather than a plausible-but-wrong URL. The resolved value MAY be a social-media post (e.g. an X status), since those frequently carry the fullest merch lineup. Persistence is fill-once: set only when the field is empty (or just cleared as dead), never overwriting a live URL, and always `Url`-validated.

## Risks / Trade-offs

- **Social-media post is deleted but still returns HTTP 200** → Status-based liveness catches hard-dead links (404/410/5xx) but not all social deletions, which can render as a 200 "post unavailable" page. Accepted limitation; the link is optional and low-harm if stale.
- **Officialness is soft** → Restricting to "official site or official social media" relies on the prompt + grounding, with no hard ownership proof. Same trust model as feature A's searcher. Mitigated by the empty-if-uncertain rule.
- **Liveness false-positive (bot-blocked HEAD)** → Only a definitive non-2xx/3xx triggers deletion; transient/ambiguous keeps the URL, avoiding needless re-search churn and re-billing Gemini.
- **Gemini cost / quota** → Bounded by the within-60-day empty/dead candidate set and Flash-Lite pricing; the circuit breaker stops the job on repeated failures.

## Migration Plan

- Add a nullable `merch_url` column to the series table via an additive migration. No backfill; existing rows are NULL until the job populates them.
- Standard cross-repo order: specification proto change → BSR generation → backend (column + repository + job) → frontend (link + i18n) → cloud-provisioning (CronJob manifest). All steps are additive; rollback is removing the CronJob, dropping the unused column, and reverting the optional field.
