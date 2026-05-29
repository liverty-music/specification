# Analytics Event Catalogue

This document is the single source of truth for every product-analytics event emitted by Liverty Music. It is referenced by the OpenSpec capability `product-analytics` and is the authority that frontend and backend event-name constants are reviewed against.

- **Frontend constants**: [`frontend/src/services/analytics-events.ts`](https://github.com/liverty-music/frontend/blob/main/src/services/analytics-events.ts)
- **Backend constants**: [`backend/internal/usecase/analytics_events.go`](https://github.com/liverty-music/backend/blob/main/internal/usecase/analytics_events.go)

Every pull request that adds, removes, or renames an event MUST update this catalogue in the same change. CI fails any code-side event constant that does not appear here.

## Naming conventions

- **Event name**: `<domain>.<action>[.<qualifier>][.<outcome>]`, lowercase, dot-separated, snake_case segments. Matches `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){1,3}$`. The optional qualifier supports four-segment names like `ticket.lottery.entry.{submitted,accepted,rejected}` and `ticket.lottery.result.assigned`.
- **Property keys**: snake_case, lowercase. Matches `^[a-z][a-z0-9_]*$`.
- **Outcomes**: `requested`, `submitted`, `initiated` (frontend intent); `completed`, `accepted`, `rejected`, `failed`, `verified`, `served`, `assigned`, `delivered`, `dismissed`, `opened` (state-confirming).

## PII handling

Properties are classified into three layers per the `product-analytics` capability:

- **Block**: email, phone, real name, address, exact birth date, payment details, raw IP, ZK proof / commitment values. Never sent.
- **Bucketize**: birth year (decade bucket), signup month, region (prefecture only), ticket price (bucket like `3000-4999`).
- **OK**: opaque domain IDs (`artist_id`, `concert_id`, `ticket_id`, `event_id`, `notification_id`, `user_id`), categorical enums (`source`, `action_type`), counts, durations.

## User identity

The `distinct_id` on every event is the platform-internal `UserId` (UUID), never the Zitadel `sub` claim. Anonymous pre-consent events have no `distinct_id` and never include any property that maps to a real account.

## OpenTelemetry bridge

Conversion-critical events MAY include a `trace_id` property carrying the active OTel trace ID at emission time. This is the single permitted bridge between the analytics and observability tools.

## Event catalogue

| Event name | Source | Domain | Properties | Consumers |
| --- | --- | --- | --- | --- |
| `page.viewed` | FE | page | `path`, `title`, `referrer?`, `trace_id?` | Acquisition funnel, top-of-funnel dashboard |
| `account.signup.started` | FE | account | `source` (pre-consent: no `trace_id` per `analytics-consent` spec) | Signup funnel |
| `account.signup.completed` | BE | account | `signup_month`, `locale`, `home_region?`, `trace_id?` | Signup funnel, D7/D30 retention cohort |
| `account.login` | BE | account | `trace_id?` | Active user trends |
| `account.preferred_language.updated` | BE | account | `from_locale`, `to_locale`, `trace_id?` | Locale change rate |
| `user.created` | BE | user | `signup_month`, `locale`, `home_region?`, `trace_id?` | Acquisition by month |
| `user.deleted` | BE | user | `account_age_days_bucket`, `trace_id?` | Account-deletion analysis |
| `artist.discovery.viewed` | FE | artist | `artist_id`, `source`, `trace_id?` | Artist discovery funnel |
| `artist.search` | FE | artist | `query_length`, `result_count`, `trace_id?` | Search quality |
| `artist.follow.requested` | FE | artist | `artist_id`, `source`, `trace_id?` | Follow funnel (paired) |
| `artist.follow.completed` | BE | artist | `artist_id`, `source?`, `trace_id?` | Follow funnel (paired), retention cohort |
| `artist.unfollow.completed` | BE | artist | `artist_id`, `trace_id?` | Engagement loss |
| `concert.detail.viewed` | FE | concert | `concert_id`, `artist_id`, `source`, `trace_id?` | Concert detail funnel |
| `concert.recommendation.served` | BE | concert | `concert_id`, `artist_id`, `algorithm_version`, `position`, `trace_id?` | Recommendation impression |
| `concert.recommendation.clicked` | FE | concert | `concert_id`, `artist_id`, `position`, `trace_id?` | Recommendation CTR |
| `ticket.lottery.entry.submitted` | FE | ticket | `concert_id`, `lottery_round`, `trace_id?` | Lottery funnel (paired) |
| `ticket.lottery.entry.accepted` | BE | ticket | `concert_id`, `lottery_round`, `trace_id?` | Lottery funnel (paired) |
| `ticket.lottery.entry.rejected` | BE | ticket | `concert_id`, `lottery_round`, `reason`, `trace_id?` | Lottery rejection reasons |
| `ticket.lottery.result.assigned` | BE | ticket | `concert_id`, `lottery_round`, `result` (`WON`/`LOST`), `trace_id?` | Lottery success rate |
| `ticket.purchase.initiated` | FE | ticket | `ticket_id`, `concert_id`, `price_bucket`, `trace_id?` | Purchase funnel (paired) |
| `ticket.purchase.completed` | BE | ticket | `ticket_id`, `concert_id`, `price_bucket`, `trace_id?` | **Revenue KPI**, purchase funnel (paired) |
| `ticket.purchase.failed` | BE | ticket | `ticket_id`, `concert_id`, `reason`, `trace_id?` | Payment failure analysis |
| `entry.checkin.attempted` | FE | entry | `event_id`, `trace_id?` | Entry funnel |
| `entry.zk_proof.verified` | BE | entry | `event_id`, `trace_id?` | **Operations KPI**, entry funnel |
| `entry.zk_proof.rejected` | BE | entry | `event_id`, `reason`, `trace_id?` | Entry rejection reasons |
| `push.subscription.requested` | FE | push | `source`, `trace_id?` | Notification opt-in funnel (paired) |
| `push.subscription.completed` | BE | push | `device_type`, `trace_id?` | Notification opt-in funnel (paired) |
| `push.notification.delivered` | BE | push | `notification_id`, `concert_id?`, `artist_id?`, `trace_id?` | Notification reach |
| `push.notification.opened` | FE | push | `notification_id`, `concert_id?`, `artist_id?`, `trace_id?` | Notification CTR |
| `push.notification.dismissed` | FE | push | `notification_id`, `trace_id?` | Notification fatigue |

## Funnels and dashboards

Initial PostHog dashboards built on top of this catalogue:

1. **Live-music conversion funnel** — `artist.discovery.viewed` → `artist.follow.completed` → `ticket.lottery.entry.accepted` → `ticket.purchase.completed` → `entry.zk_proof.verified`.
2. **Recommendation effectiveness** — `concert.recommendation.served` → `concert.recommendation.clicked` → `concert.detail.viewed`.
3. **D7 / D30 retention by signup month** — cohorted on `user.created.signup_month`.
4. **Per-domain event volume** — count of events by domain prefix, watched against the PostHog free-tier 1M events/month ceiling.

## Adding a new event

1. Decide the source (FE for UI/intent, BE for trust-critical state changes, both only for the paired-events set).
2. Add an entry to this catalogue with the domain, action, outcome, source, properties, and consuming dashboards.
3. Add the corresponding constant to [`frontend/src/services/analytics-events.ts`](https://github.com/liverty-music/frontend/blob/main/src/services/analytics-events.ts) or [`backend/internal/usecase/analytics_events.go`](https://github.com/liverty-music/backend/blob/main/internal/usecase/analytics_events.go).
4. If the event is emitted from the backend, configure the relevant subject in the `analytics-consumer` worker so that the corresponding NATS payload is decoded and forwarded.
5. In the same pull request, link the catalogue update so the CI check passes.
