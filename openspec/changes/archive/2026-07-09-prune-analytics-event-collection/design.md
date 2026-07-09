## Context

The analytics event set was built ahead of the product across three prior changes (`introduce-analytics-tool`, `reconcile-analytics-catalogue`, `emit-notification-analytics-events`) plus the ticket-system MVP work. A per-call-site audit of the live code (not the catalogue) revealed that the collected set has drifted from what actually fires and from what the current product can observe:

- **Phantoms** — `account.signup.started` (FE) and `user.deleted` (BE) have no emission call site; the never-wired ticket-sales constants (`ticket.lottery.entry.accepted/.rejected`, `ticket.lottery.result.assigned`, `ticket.purchase.completed/.failed`) exist only as name constants.
- **Redundancy** — `artist.discovery.viewed` fires 1:1 with `artist.follow.requested` (same `artist_id`, `source`, instant) and measures no impressions; the FE `artist.follow.requested` duplicates backend `artist.follow.completed` for a single-tap action.
- **Double-count** — a successful sales-reminder push emits `notification.delivered` (`type = "sales_reminder"`) via `NotificationUseCase` **and** `sales_reminder.delivered` via `salesReminderDeliveryUseCase`, counting one delivery twice.
- **Firehose** — `page.viewed` fires on every `au:router:navigation-end`; highest volume, lowest insight, and the signup form it might have measured lives on the Zitadel hosted-login domain where FE page views cannot reach.
- **Wrong altitude** — `account.preferred_language.updated` models user *state* as an *action* event.

Constraints: the ticket-sales platform is deferred indefinitely; `ticket.email.parsed` (and the email-driven `ticket.journey` promotion path) is disabled by an OS-side issue; the login event is mid-redesign (`redesign-account-login-event-handler`) and reverted from production, so it has **zero** production history. `trace_id` correlation across the NATS boundary is intact (watermill-opentelemetry propagation), so no correlation work is required here.

## Goals / Non-Goals

**Goals:**
- Delete events that never fire, duplicate another event, or double-count the same signal.
- Rename `account.login` → `account.signin` while it has no production history.
- Demote `preferred_language` from an event to a person property without losing its segmentation value.
- Distinguish `dormant` (wired, will fire when a feature ships) from `deleted` (removed) in the catalogue, and prevent future phantoms with a verified-call-site requirement.
- Preserve sales-reminder delivery-failure visibility operationally after removing its analytics event.

**Non-Goals:**
- Person-property enrichment (including `preferred_language`'s `$set` wiring), and Group Analytics — deferred to Change 2.
- Dashboard/funnel construction and event-volume governance tooling — Change 3.
- Any re-enablement of ticket sales, ZK entry, minting, or email import.

## Decisions

**D1 — Delete vs. dormant is decided by "does a call site exist?"** An event with no emitter is deleted (phantom); an event with a real emitter that is inactive only because its feature is deferred or externally blocked is kept as `dormant`. This keeps the catalogue an honest inventory: `entry.zk_proof.*`, `ticket.mint.completed`, `ticket.email.parsed`, and the FE intent events `ticket.purchase.initiated` / `entry.checkin.attempted` stay as `dormant`; the never-wired lottery/purchase BE constants are deleted. *Alternative considered:* keep all deferred constants for "future-proofing" — rejected because indistinguishable dead constants are exactly how the phantoms accumulated.

**D2 — Unify delivery reach on `notification.delivered`; delete `sales_reminder.delivered`.** `notification.delivered.type` already carries `sales_reminder`, so reach is fully recoverable by filtering on `type`. The only unique signal in `sales_reminder.delivered` was the non-success outcomes (`no_subscription`, `failed`) per `phase_stage`, which is a *delivery-reliability* concern that belongs in operational telemetry, not product analytics. *Alternative considered:* rescope `sales_reminder.delivered` to failures only — rejected as it keeps a bespoke product-analytics event for an ops metric and still risks double-reading against `notification.delivered`.

**D3 — Rename now, accept the discontinuity as zero.** Renaming `account.login` → `account.signin` is normally a breaking, history-splitting change (PostHog best practice: keep names static). It is free here precisely because the event is mid-redesign and has no production data. Doing it now avoids a permanent `login`/`signup` vocabulary mismatch. *Alternative considered:* keep `account.login` — rejected for lasting inconsistency at no offsetting benefit.

**D4 — Delete the `preferred_language` event here; defer the person property to Change 2.** Language is durable user state, better modelled as a person property that powers segmentation (e.g., retention by locale) than as a per-change event. This change removes only the *event* (`HandleUserPreferredLanguageUpdated` forwarding) and, after confirming no non-analytics consumer subscribes to `USER.preferred_language_updated`, its publish. The replacement `preferred_language` person property is wired in Change 2's identify enrichment, not here, so the language signal is intentionally uncaptured in the interval between the two changes. *Alternative considered:* wire the person property in this same change — rejected to keep Change 1 a pure deletion and all person-property work in one place (Change 2).

**D5 — Prevent recurrence with a verified-call-site requirement.** The audit only found the phantoms because it read call sites. Encode that as a `product-analytics` requirement so future reviews check the emitter, not just the catalogue row.

## Risks / Trade-offs

- **Loss of sales-reminder delivery-failure breakdown in PostHog** → Mitigation: add a log-based metric (`no_subscription` / `failed` per stage) in the ops follow-up task before or with the deletion; delivery failures are already logged.
- **Renaming `account.login` after some data exists** (if a release shipped it between audit and merge) → Mitigation: verify zero production events for `account.login` at implementation time; if any exist, add a PostHog alias rather than a hard rename.
- **Removing `USER.preferred_language_updated` publish could break an unknown consumer** → Mitigation: grep all consumers before removing the publish; if any non-analytics consumer exists, remove only the analytics forwarding and keep the publish.
- **Deleting FE `artist.follow.requested` drops follow `source` attribution** → Accepted: `source` (orb vs. search) is a one-off analysis, not a standing metric; backend `artist.follow.completed` intentionally does not carry `source`.
- **CI catalogue check** may fail transiently while code constants and the catalogue are edited in separate repos → Mitigation: land the specification catalogue update first, then the FE/BE constant removals reference it.

## Migration Plan

1. Land the specification change: catalogue rows removed, collection-status column added, funnel #1 re-cut, `account.signin` documented.
2. Backend: remove deleted/phantom constants from `knownBackendEvents`; rename the login constant and subject; drop `sales_reminder.delivered` emission and `HandleUserPreferredLanguageUpdated`; add the ops log-based metric for reminder delivery failures.
3. Frontend: remove `PageViewed`, `AccountSignupStarted`, `ArtistDiscoveryViewed`, `ArtistFollowRequested` from `Events`/`EventPropsMap` and delete their capture call sites.
4. Rollback: the change is additive-safe to revert — restoring the deleted constants and catalogue rows re-enables the prior (noisier) set; no data migration is required because deleted events simply stop being sent.

## Open Questions

- Confirm at implementation time that `USER.preferred_language_updated` has no non-analytics subscriber (determines whether the publish is removed or only its analytics forwarding).
- Confirm `account.login` has zero production events at merge time (hard rename vs. alias).
