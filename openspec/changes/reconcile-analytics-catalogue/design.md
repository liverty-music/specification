# Design — Reconcile the analytics catalogue

## Context

The archived `introduce-analytics-tool` change established PostHog Cloud EU as the sole product-analytics platform and codified `docs/analytics/event-catalog.md` as the single source of truth (the `product-analytics` capability). Two follow-up catalogue cleanups were drafted independently:

1. Remove the recommendation events, which appeared to describe a recommendation engine that does not exist.
2. Move `concert.search.completed` out of PostHog because it is user-less pipeline telemetry.

A devil's-advocate review of (1) inspected the actual frontend code. It first considered renaming `concert.recommendation.clicked` (the name implies an engine that does not exist), but found a stronger reason to **delete** it: the event is redundant. A dashboard card tap fires both the click event and `concert.detail.viewed` (the tap dispatches `event-selected`, the dashboard opens the detail sheet, which captures `concert.detail.viewed`). The only datum unique to the click event is `position`, and its CTR denominator is the phantom impression event being deleted — so no real click-through rate is computable. The review also found that both cleanups edit the same four files, so shipping them as separate changes would create a catalogue/spec merge collision. Hence one combined reconciliation.

Grounding facts from the code:

- `event-card.ts` `onClick` fires `concert.recommendation.clicked` then dispatches `event-selected`; `dashboard-route.ts` handles that by calling `detailSheet.open(event, 'recommendation')`, and `event-detail-sheet.ts` `open` captures `concert.detail.viewed` with that `source`. So one tap produces two events, and `concert.detail.viewed` already carries `concert_id`, `artist_id`, and the originating surface.
- The `EventSource` member `'recommendation'` is the surface label for the dashboard concert list; it is ungrounded (no engine) and is renamed to `'dashboard'` to match the route `frontend/src/routes/dashboard/`.
- `analytics_events.go` — `EventConcertRecommendationServed` constant and its `knownBackendEvents` allowlist entry exist with no publisher.
- `business_metrics.go` — `concert.search.count` OTel counter, `RecordConcertSearch(ctx, status)` records `status` only; `concert_uc.go` `executeSearch` calls it with `"success"`/`"error"` in a deferred handler.

## Goals

- Make the catalogue honest: every listed event is real, non-redundant, and named for what it actually measures.
- Delete the redundant click event; its signal is preserved by `concert.detail.viewed`.
- Ground the dashboard surface label (`EventSource`) in the real route name rather than an imaginary engine.
- Remove the genuine phantom (`concert.recommendation.served`) so the BE allowlist matches reality.
- Keep user-less pipeline health entirely in OTel, and complete that signal with a `zero_results` outcome.
- Ship both cleanups together so the shared files are edited once, coherently.

## Non-Goals

- Building a recommendation engine or any server-side impression event.
- Adding a replacement click event under a different name; the conversion is already observable via `concert.detail.viewed`.
- Changing the OTel export pipeline, sampling, or any other counter.
- Touching proto schema or triggering BSR regeneration.

## Decisions

### Delete the redundant click event, keep `concert.detail.viewed`

The click event is not worth keeping. It fires on the same user action as `concert.detail.viewed` (a dashboard card tap opens the detail sheet), so it duplicates `concert_id`/`artist_id`/surface, adding only `position`. With the impression event deleted as a phantom, `position` cannot yield a click-through rate, so it carries little analytic value on its own. Deleting the event — its constant, props type, props-map entry, call site, and the `position` plumbing that fed only it — removes the duplication. The "which concert from the dashboard list did the user open" question is answered by `concert.detail.viewed` filtered on `source = 'dashboard'`.

### Ground the dashboard surface label in the route

`concert.detail.viewed` still needs to record where a view originated. Its `EventSource` value for the dashboard list was `'recommendation'` — ungrounded, since no recommendation engine exists. It is renamed to `'dashboard'`, matching the actual route (`frontend/src/routes/dashboard/`), so the surface label names a real thing and reads clearly for analysts. (`EventSource` is intentionally a presentation-layer enumeration of UI surfaces — `page`, `search_result`, `discovery_orb`, `dashboard`, `notification` — not a domain-entity vocabulary.)

### Search-pipeline health is OTel, not PostHog

Per Decisions 10 and 13 of `introduce-analytics-tool`, product analytics (PostHog) carries user-attributed product events, and system/pipeline observability (OTel) carries traces, metrics, and logs; the only bridge is `trace_id`. `concert.search.completed` is user-less — a Gemini discovery cron outcome with no `distinct_id` — so it never belonged in the catalogue. It already has an OTel home (`concert.search.count`) and never had a PostHog publisher. Removing the catalogue row aligns the catalogue with the existing implementation rather than introducing a new publisher.

### Add `zero_results` to the OTel counter (real work, not a confirmation)

Today `RecordConcertSearch` is called with only `"success"`/`"error"`. A search that completes but finds no new concerts is currently indistinguishable from a fruitful one, yet it is the most interesting pipeline-health case (quota burned, nothing discovered). Adding a `zero_results` outcome — recorded in `executeSearch` when a successful run yields an empty concert set — makes the OTel view complete and is the search-health home that justifies dropping the PostHog row.

### Standardise the underlying-event identifier on `event_id`

`Concert` is a user-facing DTO whose `id` field is an `EventId`; `Event` is the canonical entity that tickets and entry records link to. The catalogue therefore refers to one identifier under two names — `concert_id` (ten events) and `event_id` (five). Because PostHog joins funnels on property equality, a name that changes between `concert.detail.viewed`, `ticket.purchase.completed`, and `entry.zk_proof.verified` silently breaks the cross-event funnel. The fix is to name the identifier after the canonical entity — `event_id` — everywhere. `concert_id` is removed from the catalogue (including the PII-safety example list) and from the implemented frontend types/call site. The user-facing event *names* (`concert.detail.viewed` etc.) are unchanged: the `concert` segment is the product-action vocabulary, while `event_id` is the entity reference — the two layers are intentionally distinct.

### Delete `account.signup.completed` as a phantom duplicate

`account.signup.completed` is defined and allow-listed but never emitted, while `user.created` is emitted with identical properties and covers both self-signup and admin provisioning. Keeping a never-emitted constant violates the same "catalogue matches reality" rule that removes `concert.recommendation.served`, and the duplicate properties would double-count the signup terminus if it were ever wired up. It is deleted; `account.signup.started` (FE) now pairs with `user.created` for the signup funnel.

### Combine the cleanups into one change

All of these cleanups edit `docs/analytics/event-catalog.md`, the `product-analytics` spec, and the FE/BE event constants. Separate changes would collide on these files and on the same requirements. One change edits each file once and reproduces each modified requirement coherently. The `event_id` standardisation and the `account.signup.completed` deletion were surfaced by a catalogue-wide naming audit during this change and are the same class of defect (ungrounded or duplicated vocabulary), so they belong here rather than in a separate change that would re-touch the same catalogue table.

## Risks / Trade-offs

- **PostHog series discontinuity.** Deleting `concert.recommendation.clicked` means PostHog stops receiving it; its historical series is retained but no longer extended, and any saved insight/funnel referencing it must be repointed to `concert.detail.viewed` (filtered on `source = 'dashboard'`). This is accepted: the event was redundant and misleadingly named, the volume to date is small, and the same conversion remains observable. Note the cutover date when the deletion ships so analysts can stitch any historical analysis manually if needed.
- **Allowlist drift in reverse.** Deleting `EventConcertRecommendationServed` is safe only because nothing publishes it; the BE allowlist guard would reject it anyway. Verified by grep — no publisher references the constant.
- **OTel label cardinality.** Adding one bounded outcome value (`zero_results`) to an existing low-cardinality `status` attribute is negligible; the attribute already carries `success`/`error`.
- **Property-name discontinuity on `concert.detail.viewed`.** Renaming the emitted property `concert_id` → `event_id` means historical `concert.detail.viewed` events carry `concert_id` while new ones carry `event_id`; saved insights filtering on `concert_id` must be repointed. Accepted for the same reasons as the event rename — only `concert.detail.viewed` actually emits today, its volume is small, and the other renamed events are not yet wired up, so they ship correct from day one.
