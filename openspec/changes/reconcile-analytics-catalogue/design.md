# Design — Reconcile the analytics catalogue

## Context

The archived `introduce-analytics-tool` change established PostHog Cloud EU as the sole product-analytics platform and codified `docs/analytics/event-catalog.md` as the single source of truth (the `product-analytics` capability). Two follow-up catalogue cleanups were drafted independently:

1. Remove the recommendation events, which appeared to describe a recommendation engine that does not exist.
2. Move `concert.search.completed` out of PostHog because it is user-less pipeline telemetry.

A devil's-advocate review of (1) inspected the actual frontend code and found `concert.recommendation.clicked` is a live, position-keyed click-through signal on the dashboard feed — only its name lies. The review also found that both cleanups edit the same four files, so shipping them as separate changes would create a catalogue/spec merge collision. Hence one combined reconciliation.

Grounding facts from the code:

- `dashboard-route.ts:369` — the dashboard concert list is the recommendation feed; the detail sheet is opened with `source: 'recommendation'` so FE clicks can be joined to a (then-planned) impression signal.
- `event-card.ts:57-67` — fires the click event position-keyed, guarded by `if (this.position !== null)` so a null position never emits `0` and skews CTR.
- `analytics_events.go:59,165` — `EventConcertRecommendationServed` constant and its `knownBackendEvents` allowlist entry exist with no publisher.
- `business_metrics.go:28-46` — `concert.search.count` OTel counter, `RecordConcertSearch(ctx, status)` records `status` only; `concert_uc.go` `executeSearch` calls it with `"success"`/`"error"` in a deferred handler.

## Goals

- Make the catalogue honest: every listed event is real and named for what it actually measures.
- Preserve the live feed-CTR signal through a rename, not a deletion.
- Remove the genuine phantom (`concert.recommendation.served`) so the BE allowlist matches reality.
- Keep user-less pipeline health entirely in OTel, and complete that signal with a `zero_results` outcome.
- Ship both cleanups together so the shared files are edited once, coherently.

## Non-Goals

- Building a recommendation engine or any server-side impression event.
- Migrating or back-filling the old `concert.recommendation.clicked` PostHog series into the new name.
- Changing the OTel export pipeline, sampling, or any other counter.
- Touching proto schema or triggering BSR regeneration.

## Decisions

### Rename, do not delete, the feed click-through event

The signal is real and valuable (feed CTR), so deleting it would lose a metric. The only defect is the name: `recommendation` implies an engine that does not exist. Renaming to `concert.feed.card.tapped` keeps the behaviour (position-keyed capture, null-position guard, `position` property) while telling the truth — the user tapped a card in the concert feed. The `EventSource` union member `'recommendation'` is renamed to `'feed'` to match.

### Search-pipeline health is OTel, not PostHog

Per Decisions 10 and 13 of `introduce-analytics-tool`, product analytics (PostHog) carries user-attributed product events, and system/pipeline observability (OTel) carries traces, metrics, and logs; the only bridge is `trace_id`. `concert.search.completed` is user-less — a Gemini discovery cron outcome with no `distinct_id` — so it never belonged in the catalogue. It already has an OTel home (`concert.search.count`) and never had a PostHog publisher. Removing the catalogue row aligns the catalogue with the existing implementation rather than introducing a new publisher.

### Add `zero_results` to the OTel counter (real work, not a confirmation)

Today `RecordConcertSearch` is called with only `"success"`/`"error"`. A search that completes but finds no new concerts is currently indistinguishable from a fruitful one, yet it is the most interesting pipeline-health case (quota burned, nothing discovered). Adding a `zero_results` outcome — recorded in `executeSearch` when a successful run yields an empty concert set — makes the OTel view complete and is the search-health home that justifies dropping the PostHog row.

### Combine the two cleanups into one change

Both edit `docs/analytics/event-catalog.md`, the `product-analytics` spec, and the FE/BE event constants. Separate changes would collide on these files and on the same two requirements. One change edits each file once and reproduces each modified requirement coherently.

## Risks / Trade-offs

- **PostHog series discontinuity.** Renaming `concert.recommendation.clicked` to `concert.feed.card.tapped` means PostHog treats it as a brand-new event name; the historical series under the old name does not carry forward, and any saved insight/funnel referencing the old name must be repointed. This is accepted: the old name was actively misleading, the volume to date is small, and honest vocabulary is worth the break. Note the cutover date when the rename ships so analysts can stitch the two series manually if needed.
- **Allowlist drift in reverse.** Deleting `EventConcertRecommendationServed` is safe only because nothing publishes it; the BE allowlist guard would reject it anyway. Verified by grep — no publisher references the constant.
- **OTel label cardinality.** Adding one bounded outcome value (`zero_results`) to an existing low-cardinality `status` attribute is negligible; the attribute already carries `success`/`error`.
