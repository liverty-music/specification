## Why

A ground-truth audit of every emitted analytics event — verified at each call site, not from the catalogue — found that a large fraction of the collected events carry no analytical value: two are defined but never fire (phantoms), several duplicate other events, one double-counts the same push, one is a per-navigation firehose, and one is a niche settings action better modelled as a person property. At the same time the product's ticket-sales platform is deferred indefinitely and the ticket-email import is disabled by an OS-side issue, so their funnels cannot be built. Pruning now — while the renamed login event has zero production history — keeps the catalogue honest, cuts event volume against the PostHog free-tier ceiling, and lets the remaining events describe the one loop that is actually observable: register artists → deliver notifications → engagement → retention.

## What Changes

- **Delete phantom events that never fire** (no emission call site exists): `account.signup.started` (FE), `user.deleted` (BE), and the never-wired ticket-sales constants `ticket.lottery.entry.accepted`, `ticket.lottery.entry.rejected`, `ticket.lottery.result.assigned`, `ticket.purchase.completed`, `ticket.purchase.failed`.
- **Delete redundant / low-value events**: `page.viewed` (per-navigation firehose, highest volume, lowest insight), `artist.discovery.viewed` (fires 1:1 with `artist.follow.requested`; measures no impressions), `artist.follow.requested` FE half (redundant with backend `artist.follow.completed`).
- **Delete the double-counting event** `sales_reminder.delivered`: a successful sales-reminder push already emits `notification.delivered` with `type = "sales_reminder"`, so delivery reach is unified onto `notification.delivered`. Sales-reminder delivery-failure visibility moves to an operational (log-based) metric, not product analytics.
- **BREAKING — rename** `account.login` → `account.signin` for vocabulary consistency with the surviving `account.*` namespace. Safe now because the login event is mid-redesign and has no production history yet.
- **Delete** `account.preferred_language.updated`: language is durable user *state*, not an action worth an event. The replacement `preferred_language` person property is added in Change 2's identify enrichment, not here, so this change removes the event without adding the property.
- **Relabel the deferred set as dormant, not deleted** (wired implementations that will fire when their feature ships): `entry.zk_proof.verified`, `entry.zk_proof.rejected`, `ticket.mint.completed`, `ticket.email.parsed` (OS-blocked), and the FE intent events `ticket.purchase.initiated`, `entry.checkin.attempted`.
- **Add a collection-status column** to the event catalogue (`active` / `dormant` / `deleted`) and re-cut the primary conversion funnel to terminate at `concert.detail.viewed` (the last observable step) instead of `entry.zk_proof.verified`.

## Capabilities

### New Capabilities
<!-- none -->

### Modified Capabilities
- `product-analytics`: the collected event set is pruned to the observable notification-and-discovery loop; requirement examples that reference deleted events (`artist.discovery.viewed`, `page.viewed`, the lottery paired-event example) are updated; the login event is renamed to `account.signin`; the `preferred_language` event is removed (its replacement person property is added in Change 2, not here); a new requirement forbids catalogued active events without a verified emission call site (anti-phantom); the catalogue gains a per-event collection status and a re-cut primary funnel.
- `analytics-consent`: the anonymous pre-identification capture scenarios that name now-deleted events (`page.viewed`, `account.signup.started`, `artist.discovery.viewed`, `ticket.purchase.completed`) are re-illustrated with surviving catalogue events so the consent model examples stay valid.

## Impact

- **specification**: `docs/analytics/event-catalog.md` (source of truth) — remove deleted rows, add collection-status column, re-cut funnel #1; `openspec/specs/product-analytics/spec.md` delta.
- **frontend**: `src/services/analytics-events.ts` (remove `PageViewed`, `AccountSignupStarted`, `ArtistDiscoveryViewed`, `ArtistFollowRequested` from `Events`/`EventPropsMap`); delete their capture call sites in `app-shell.ts` and `discovery/discovery-route.ts`; keep `identify()` path (person property added by Change 2).
- **backend**: `internal/usecase/analytics_events.go` (remove phantom + deleted constants from `knownBackendEvents`); rename `EventAccountLogin`/`account.login` → `account.signin`; remove `HandleUserPreferredLanguageUpdated` analytics forwarding and `sales_reminder.delivered` emission (`sales_reminder_delivery_uc.go`, `analytics_consumer.go`, `event_data.go` subjects); confirm no non-analytics consumer depends on `USER.preferred_language_updated` before removing its publish.
- **ops follow-up**: add a log-based metric for sales-reminder delivery failures (`no_subscription` / `failed`) so the visibility lost by deleting `sales_reminder.delivered` is preserved operationally.
- **Non-goals**: person-property enrichment and Group Analytics (Change 2), dashboards (Change 3), and any ticket-sales re-enablement.
