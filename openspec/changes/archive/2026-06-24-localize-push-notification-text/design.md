## Context

The backend sends three kinds of Web Push notifications:

| Notification | Pipeline | Current copy |
|---|---|---|
| Sales reminders | time-based scan → event → push | Already localized (en/ja) — reference pattern |
| Concert discovery | concert search → follower fan-out push | Hardcoded English |
| Sales-phase announcement | phase discovery → event → push | Hardcoded English |

The `sales-reminders` Notification Content requirement already mandates that the discovery announcement and every reminder stage be localized per recipient using `users.preferred_language` (default `en`). The reminder path complies; the announcement path drifted (a code comment states personalization is "intentionally omitted"). The concert-discovery notification has never been specified and is English-only.

The reference implementation is `internal/usecase/sales_reminder_uc.go`: `buildReminderPayload` reads `lang := user.PreferredLanguage` (normalizing empty → `en`) and uses unexported `map[lang]string` helpers (`stageTitle`, `stageBody`, `channelDisplayName`, `formatLocalTime`). `users.preferred_language` is an ISO-639-1 string, empty when unset; no schema change is needed.

## Goals / Non-Goals

**Goals:**
- Concert-discovery and sales-phase-announcement notification copy rendered in the recipient's `preferred_language`, defaulting to `en`.
- Reuse the existing `NotificationPayload` and Web Push delivery path — no proto, RPC, or DB change.
- Avoid per-subscription marshalling cost when fanning out to many recipients.

**Non-Goals:**
- No new supported languages beyond the existing `en`/`ja` set.
- No frontend, proto schema, or migration work.
- No extraction of a shared i18n package — copy stays local to each notification builder.

## Decisions

### Resolve recipient language at the delivery use case, not the transport

The language is resolved where the recipient is known (the use case), and the resolved copy is baked into the `NotificationPayload` before marshalling. The Web Push sender stays language-agnostic. This mirrors the reminder path and keeps the transport layer unchanged.

### Concert discovery: surface `preferred_language` via the follower query

`NotifyNewConcerts` already loads followers via `followRepo.ListFollowers(artistID)`, whose query JOINs `users`. We extend that query to also select `COALESCE(u.preferred_language, '')` and populate `Follower.User.PreferredLanguage`.

- **Alternative considered:** per-recipient `userRepo.Get` (N+1). Rejected — the follower JOIN already exists, so adding one column is free and avoids N point reads for popular artists.
- `ListFollowers` has a single caller, so the additive column is low-risk.

### Sales-phase announcement: hydrate recipients via `userRepo`

The announcement use case currently resolves only user IDs and lists subscriptions; it has no `userRepo`. We add a `userRepo entity.UserRepository` dependency and hydrate each recipient with the same warn-and-skip loop the reminder path uses (`userRepo.Get` per ID; a failed read skips that recipient without aborting the batch). DI in `internal/di/consumer.go` constructs `rdb.NewUserRepository(db)` and passes it in.

- **Alternative considered:** add `preferred_language` to the audience-resolution query (`ResolveSalesPhaseAudience` / ticket-journey join). Rejected for now — it would change a shared query's shape for one consumer; the hydrate loop matches the established reminder pattern and keeps blast radius small. Batched `ListByIDs` is a known future perf improvement shared with the reminder path.

### Build at most one payload per distinct language

Both fan-out paths iterate subscriptions (`sub.UserID`), not recipients. To avoid re-marshalling per subscription, each path builds a `map[userID]lang` during recipient resolution and a `map[lang][]byte` payload cache, lazily marshalling a payload the first time each language is needed (≤2 marshals for en+ja). The send loop picks bytes by the subscription's resolved language, defaulting to `en` if a subscription's user is unexpectedly absent from the map.

### Localization copy stays local to each builder

The three notification types have non-overlapping copy. The concert body table lives inside `NewConcertNotificationPayload(artist, count, lang)` in `internal/entity/push_notification.go`; the announcement uses two small unexported helpers (`announcementTitle(lang)` / `announcementBody(lang)`) in its use-case file, matching the reminder helpers' `map[lang]string` + `en`-fallback shape. A shared i18n package is deferred until a fourth notification type appears.

## Risks / Trade-offs

- **Per-subscription marshalling cost** → mitigated by the `map[lang][]byte` cache (≤2 marshals regardless of subscription count).
- **`ListFollowers` query change blast radius** → single caller confirmed; the added column is `COALESCE`'d so no NULL-scan panic.
- **Announcement now performs N user reads** (previously zero) → same pattern and cost profile as the reminder path; warn-and-skip prevents one bad recipient from dropping the whole batch.
- **Empty/unsupported language fallback** → normalized to `en` in exactly one place per builder (entity constructor for concerts, helper for announcement) to prevent a missed empty string producing blank copy.

## Migration Plan

Pure code change, no data migration. Deploy via the normal backend release; rollback is reverting the backend image. Notification copy language is the only observable behavior change.
