# Analytics Event Catalogue

This document is the single source of truth for every product-analytics event emitted by Liverty Music. It is referenced by the OpenSpec capability `product-analytics` and is the authority that frontend and backend event-name constants are reviewed against.

- **Frontend constants**: [`frontend/src/services/analytics-events.ts`](https://github.com/liverty-music/frontend/blob/main/src/services/analytics-events.ts)
- **Backend constants**: [`backend/internal/usecase/analytics_events.go`](https://github.com/liverty-music/backend/blob/main/internal/usecase/analytics_events.go)

Every pull request that adds, removes, or renames an event MUST update this catalogue in the same change. CI fails any code-side event constant that does not appear here.

## Naming conventions

- **Event name**: `<domain>.<action>[.<qualifier>][.<outcome>]`, lowercase, dot-separated, snake_case segments. Matches `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,3}$`. The optional qualifier supports four-segment names like `ticket.lottery.entry.submitted`.
- **Property keys**: snake_case, lowercase. Matches `^[a-z][a-z0-9_]*$`.
- **Outcomes**: `requested`, `submitted`, `initiated` (frontend intent); `completed`, `accepted`, `rejected`, `failed`, `verified`, `served`, `assigned`, `delivered`, `dismissed`, `opened` (state-confirming).

## PII handling

Properties are classified into three layers per the `product-analytics` capability:

- **Block**: email, phone, real name, address, exact birth date, payment details, raw IP, ZK proof / commitment values. Never sent.
- **Bucketize**: birth year (decade bucket), signup month, region (prefecture only), ticket price (bucket like `3000-4999`).
- **OK**: opaque domain IDs (`artist_id`, `event_id`, `ticket_id`, `notification_id`, `user_id`), categorical enums (`source`, `action_type`), counts, durations.

## User identity

The `distinct_id` on every event is the platform-internal `UserId` (UUID), never the Zitadel `sub` claim. Anonymous pre-consent events have no `distinct_id` and never include any property that maps to a real account.

## OpenTelemetry bridge

Conversion-critical events MAY include a `trace_id` property carrying the active OTel trace ID at emission time. This is the single permitted bridge between the analytics and observability tools.

## Event catalogue

The `Collection status` column records whether an event is currently collected:

- **active** — has a verified emission call site and fires in production today.
- **dormant** — has a wired (or catalogue-ready) emitter that is inactive only because its feature is deferred or externally blocked; it will begin firing when that feature ships. Dormant rows are NOT collected today but are kept as an honest forward inventory.

Events that were removed (never fired, duplicated another event, or double-counted a signal) are not listed here; they are recorded in the [Removed events](#removed-events) section with the reason for removal.

| Event name | Source | Domain | Collection status | Properties | Consumers |
| --- | --- | --- | --- | --- | --- |
| `account.signin` | BE | account | active | `trace_id?` | Active user trends, returning/active-user retention cohorts |
| `user.created` | BE | user | active | `signup_month`, `locale`, `home_region?`, `trace_id?` | Acquisition by month, signup funnel, D7/D30 retention cohort |
| `artist.search` | FE | artist | active | `query_length`, `result_count`, `trace_id?` | Search quality |
| `artist.follow.completed` | BE | artist | active | `artist_id`, `source?`, `trace_id?` | Follow funnel, retention cohort |
| `artist.unfollow.completed` | BE | artist | active | `artist_id`, `trace_id?` | Engagement loss |
| `concert.detail.viewed` | FE | concert | active | `event_id`, `artist_id`, `source`, `trace_id?` | Concert detail funnel |
| `ticket.journey.status.changed` | BE | ticket | active | `event_id`, `from_status`, `to_status`, `trace_id?` | Interest-tier progression (PENDING→TRACKING→ATTENDING), engagement depth |
| `ticket.lottery.entry.submitted` | FE | ticket | dormant | `event_id`, `lottery_round`, `trace_id?` | Lottery funnel — activates when ticket sales ship |
| `ticket.purchase.initiated` | FE | ticket | dormant | `ticket_id`, `event_id`, `price_bucket`, `trace_id?` | Purchase funnel — activates when ticket sales ship |
| `ticket.email.parsed` | BE | ticket | dormant | `email_type`, `parse_status`, `field_count`, `trace_id?` | Email-ingestion data quality — blocked by the OS-side email-import issue |
| `ticket.mint.completed` | BE | ticket | dormant | `event_id`, `trace_id?` | SBT issuance rate, ticket-activation funnel — activates when minting ships |
| `entry.checkin.attempted` | FE | entry | dormant | `event_id`, `trace_id?` | Entry funnel — activates when venue entry ships |
| `entry.zk_proof.verified` | BE | entry | dormant | `event_id`, `trace_id?` | **Operations KPI**, entry funnel — activates when venue entry ships |
| `entry.zk_proof.rejected` | BE | entry | dormant | `event_id`, `reason`, `trace_id?` | Entry rejection reasons — activates when venue entry ships |
| `notification.requested` | FE | notification | active | `source`, `trace_id?` | Notification opt-in funnel (paired) |
| `notification.subscribed` | BE | notification | active | `device_type`, `trace_id?` | Notification opt-in funnel (paired) |
| `notification.unsubscribed` | BE | notification | active | `device_type`, `trace_id?` | Push churn vs. browser cache-clear |
| `notification.delivered` | BE | notification | active | `notification_id`, `type`, `event_id?`, `artist_id?`, `trace_id?` | Notification reach (incl. `type = "sales_reminder"` for sales-reminder pushes) |
| `notification.opened` | FE | notification | active | `notification_id`, `event_id?`, `artist_id?`, `trace_id?` | Notification CTR |
| `notification.dismissed` | FE | notification | active | `notification_id`, `trace_id?` | Notification fatigue |

### Removed events

The following events were removed from the collected set. Each is recorded here with the reason so a future reviewer can see why the name is intentionally absent (and MUST NOT be silently re-added — see the anti-phantom requirement in the `product-analytics` capability).

| Event name | Source | Removal reason |
| --- | --- | --- |
| `page.viewed` | FE | **Firehose** — fired on every navigation; highest volume, lowest insight. The signup form it might have measured lives on the Zitadel hosted-login domain, out of the frontend's reach. |
| `account.signup.started` | FE | **Phantom** — no emission call site ever existed. |
| `account.preferred_language.updated` | BE | **Wrong altitude** — models durable user *state* as an *action* event. Replaced by a `preferred_language` person property (added in the follow-up person-property change, not here). |
| `user.deleted` | BE | **Phantom** — no emission call site ever existed. |
| `artist.discovery.viewed` | FE | **Redundant** — fired 1:1 with `artist.follow.requested` (same `artist_id`, `source`, instant) and measured no impressions. |
| `artist.follow.requested` | FE | **Redundant** — duplicated the backend `artist.follow.completed` for a single-tap action; the `source` attribution it carried is a one-off analysis, not a standing metric. |
| `sales_reminder.delivered` | BE | **Double-count** — a successful sales-reminder push already emits `notification.delivered` with `type = "sales_reminder"`, so reach is recoverable from `notification.delivered`. Delivery-failure visibility (`no_subscription` / `failed`) moves to an operational log-based metric, not product analytics. |
| `ticket.lottery.entry.accepted` | BE | **Phantom** — never-wired name constant; ticket sales are deferred indefinitely. |
| `ticket.lottery.entry.rejected` | BE | **Phantom** — never-wired name constant; ticket sales are deferred indefinitely. |
| `ticket.lottery.result.assigned` | BE | **Phantom** — never-wired name constant; ticket sales are deferred indefinitely. |
| `ticket.purchase.completed` | BE | **Phantom** — never-wired name constant; ticket sales are deferred indefinitely. |
| `ticket.purchase.failed` | BE | **Phantom** — never-wired name constant; ticket sales are deferred indefinitely. |

### Account-event source notes

- `account.signin` is sourced from a Zitadel Actions v2 **event execution** on `session.user.checked` (backend `/account-login-event` webhook → `ACCOUNT.login` NATS subject → `analytics-consumer`). The NATS transport subject remains `ACCOUNT.login`; the analytics-consumer maps it to the catalogue event name `account.signin`. `session.user.checked` is stored once per interactive login through the hosted Login UI; a silent `refresh_token` grant touches only the `oidc_session` aggregate and a machine `jwt_profile` grant never creates a Login-UI session, so the event is emitted **exactly once per interactive login and never on token refresh or machine grant** — the sign-in metric is never inflated. An event execution is fire-and-forget and cannot alter the auth request/response (unlike the reverted `response`-on-`CreateSession` approach, which broke sign-in). The event was renamed from `account.login` while it had zero production history; see the anti-phantom / naming notes in the `product-analytics` capability.
- **Signup is represented by `user.created`, not a separate `account.signup.completed` event.** Signup occurs at the same instant `user.created` is emitted, so a distinct completion event would double-count signups; `account.signup.completed` is therefore an alias of `user.created` and is not emitted. (The former FE pre-consent `account.signup.started` intent event was removed — it never fired; see the Removed events section.)

## Funnels and dashboards

Initial PostHog dashboards built on top of this catalogue:

1. **Live-music engagement funnel (primary)** — `artist.follow.completed` → `notification.delivered` → `notification.opened` → `concert.detail.viewed`. This is the one loop the current product can actually observe: register artists → deliver notifications → engagement. The funnel terminates at `concert.detail.viewed`, the last observable step; the former downstream steps (`ticket.lottery.entry.accepted`, `ticket.purchase.completed`, `entry.zk_proof.verified`) were removed or are dormant until ticket sales and venue entry ship.
2. **D7 / D30 retention by signup month** — cohorted on `user.created.signup_month`. Language segmentation uses the `preferred_language` **person property** (added in the follow-up person-property change), not an event.
3. **Per-domain event volume** — count of events by domain prefix, watched against the PostHog free-tier 1M events/month ceiling.

## Adding a new event

1. Decide the source (FE for UI/intent, BE for trust-critical state changes, both only for the paired-events set).
2. Add an entry to this catalogue with the domain, action, outcome, source, properties, and consuming dashboards.
3. Add the corresponding constant to [`frontend/src/services/analytics-events.ts`](https://github.com/liverty-music/frontend/blob/main/src/services/analytics-events.ts) or [`backend/internal/usecase/analytics_events.go`](https://github.com/liverty-music/backend/blob/main/internal/usecase/analytics_events.go).
4. If the event is emitted from the backend, configure the relevant subject in the `analytics-consumer` worker so that the corresponding NATS payload is decoded and forwarded.
5. In the same pull request, link the catalogue update so the CI check passes.
