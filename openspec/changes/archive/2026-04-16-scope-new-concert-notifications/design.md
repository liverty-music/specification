## Context

The push-notification delivery path today is triggered by a `CONCERT.created` NATS event whose payload is `{artist_id, artist_name, concert_count}`. The handler then **re-fetches** `upcoming` concerts via `ConcertRepository.ListByArtist(artistID, true)` and passes the full list to the notification use case. Two problems result:

1. **Semantic bug**: the new-concert trigger fans out over the artist's entire upcoming catalog. Hype filters (`home`, `nearby`) incorrectly match on stale venues, and the payload count reflects total upcoming, not new.
2. **Layering bug**: the consumer handler owns business logic (artist hydration + concert list shaping). Per clean architecture rules in `backend/CLAUDE.md`, handlers in `adapter/` should delegate to `usecase/`; they should not reach into repositories.

Additionally, the only way to exercise the delivery path end-to-end today is `ConcertService.SearchNewConcerts`, which depends on a live Gemini call discovering new data. This makes integration testing non-deterministic and slow.

This change fixes both bugs and introduces a debug RPC so the delivery path can be invoked deterministically.

Stakeholders: backend engineers (code owners), QA / operators (integration testing), specification maintainers (proto contract).

## Goals / Non-Goals

**Goals:**
- Delivery decisions (hype filter + payload) are computed strictly from the newly created concert set.
- The consumer handler is reduced to CloudEvent decode + single use-case call.
- The `ConcertCreatedData` struct lives in the use case layer (not the entity layer) since it is a use-case input, not a domain entity.
- A `NotifyNewConcerts` Connect RPC exists on `PushNotificationService` for deterministic invocation of the delivery path.
- The debug RPC is only usable in non-production environments.

**Non-Goals:**
- Changing the hype-level semantics themselves (`watch` / `home` / `nearby` / `away` rules stay as-is).
- Changing the Web Push transport layer, VAPID key management, or 410-Gone cleanup logic.
- Changing the client (frontend) push subscription surface (`Create` / `Get` / `Delete` / self-heal) — those requirements remain untouched.
- Keeping backward compatibility with old `CONCERT.created` event schemas. The NATS `CONCERT` stream will be purged.
- Making the debug RPC available to end users or shipping it to production.

## Decisions

### D1. Event payload becomes `{artist_id, concert_ids[]}`

**Chosen**: Replace the payload entirely with an identifier-only shape.

**Rationale**: The publisher already has the concrete concert list when it decides to emit the event. Passing the identifiers downstream eliminates the re-fetch race, makes the consumer work with an authoritative "this is what just happened" set, and keeps the payload tiny. Names and counts are derivable from identifiers.

**Alternatives considered**:
- *Inline concert objects*: duplicates entity data in the event; payload bloats with venue/date fields; serialization semantics drift from the DB. Rejected.
- *Keep `concert_count` as a sibling of `concert_ids`*: redundant (count is `len(concert_ids)`) and encourages consumers to trust derivable data. Rejected.
- *Add versioned schema field (`v2`) with dual-consume shim*: only worthwhile if we need to tolerate historical events. Since we can purge dev/staging streams, the shim is pure cost. Rejected.

### D2. NATS `CONCERT` stream is purged on deploy

**Chosen**: Single-shot purge of the stream in dev/staging when the backend with the new schema rolls out.

**Rationale**: Pre-existing events with the old shape will fail to unmarshal into the new struct. With 7-day retention and no production usage of this feature yet, purging is simpler and safer than dual-consume logic. Purge is executed via `nats stream purge CONCERT` inside the consumer pod (or out-of-band by the operator) during the deploy window.

**Risks**:
- *Events in flight at deploy time are dropped*: accepted. The source of truth for "new concerts" is the DB; a dropped event only means a skipped notification for one batch, which is recoverable via the new debug RPC.
- *Prod migration requires care if feature lands in prod later*: by that time the schema stabilizes and no migration of persisted events will be needed.

### D3. `ConcertCreatedData` moves from `internal/entity/` to `internal/usecase/`

**Chosen**: Define the struct in `internal/usecase/push_notification_uc.go` (or a sibling `notification_events.go` in the same package) and export it as `usecase.ConcertCreatedData`.

**Rationale**: The struct is the input shape of a use case, not a domain entity. Placing it in `entity/` blurs layer ownership and creates a circular-feeling dependency where adapter packages import entity types only to hand them to use cases.

**Alternatives considered**:
- *Leave it in `entity/`*: status quo; violates layer responsibilities.
- *Introduce a new `internal/event/` package*: over-engineered for a single struct. Can revisit if multiple event payloads warrant consolidation.

### D4. `NotifyNewConcerts` use case hydrates artist and concerts itself

**Chosen**: The use case method accepts `ConcertCreatedData` and internally calls `artistRepo.Get(artistID)` and `concertRepo.ListByIDs(concertIDs)`.

**Rationale**: The consumer handler must be free of repo calls (layering). Moving hydration inside the use case means the same method can be invoked from the consumer **and** the debug RPC without duplicating fetches.

**Alternatives considered**:
- *Caller passes in hydrated `artist` and `[]concert`*: forces every caller (consumer, debug RPC) to replicate the same fetch logic. Rejected.
- *Caller passes only `artistID` and the use case fetches concerts by `artistID` + "upcoming"*: reintroduces the original bug.

### D5. New repo method `ConcertRepository.ListByIDs`

**Chosen**: Add `ListByIDs(ctx, ids []string) ([]*Concert, error)` to the `ConcertRepository` interface, backed by `WHERE event_id = ANY($1)` in the pgx implementation. Return order need not match input order; the use case treats the result as a set. Missing IDs are silently dropped but logged at `WARN`.

**Rationale**: Precise hydration of the "just created" set. Reuses existing pgx bulk patterns.

**Open alternatives**:
- *Return error on any missing ID*: strict but noisy under race conditions (e.g., concert deleted between publish and consume). A WARN log is a pragmatic middle ground.

### D6. Debug RPC is environment-gated at the server via existing `ENVIRONMENT`

**Chosen**: Add `NotifyNewConcerts` to `PushNotificationService`. The handler is always registered, but when the server's existing `config.ServerConfig.IsProduction()` returns `true`, the method returns `PERMISSION_DENIED` before doing any work. No new env var is introduced.

**Rationale**:
- The project already has an `ENVIRONMENT` config (`local` / `development` / `staging` / `production`) with `Is{Local,Development,Staging,Production}()` helpers in `pkg/config/config.go`. Debug-feature gating is a natural extension of this existing knob.
- A dedicated `ENABLE_DEBUG_RPCS` flag would be a second source of truth, requires cloud-provisioning overlay changes in every environment, and creates a risk of combinatorial misconfiguration (e.g., `ENVIRONMENT=production` with `ENABLE_DEBUG_RPCS=true`). Reusing `ENVIRONMENT` keeps one canonical signal.
- Keeping the RPC on the existing service avoids a new proto service surface, simplifies auth interceptor wiring, and reuses the `RequireUser` interceptor so unauthenticated calls still return `UNAUTHENTICATED`.
- Server-side gating (not route-level omission) ensures a well-known error code surfaces in prod if someone probes the endpoint, instead of 404. This is easier to observe and alert on than a missing route.

**Alternatives considered**:
- *Dedicated `ENABLE_DEBUG_RPCS` env var*: explicit about intent, but redundant with `ENVIRONMENT` and adds per-overlay configuration burden. Rejected as over-engineered.
- *Separate `PushNotificationDebugService` with its own interceptor chain*: cleaner ACL model but requires a second service registration and more proto surface. Rejected for complexity.
- *Require an admin role claim in JWT*: no admin role currently exists in Zitadel for this app; adding one is out of scope.

### D7. Debug RPC rejects unknown concert IDs

**Chosen**: The debug RPC fetches concerts by the provided IDs filtered by `artist_id`. If any provided ID fails to resolve under that artist, return `INVALID_ARGUMENT` and do no delivery.

**Rationale**: The debug RPC is for deliberate invocations; silently dropping mismatched IDs would mask operator mistakes. The consumer path (D5) is stricter-by-nature because the publisher constructed the IDs in the same transaction — mismatches there are rare race conditions, not operator errors.

## Risks / Trade-offs

- **[Risk]** Consumer pods deployed ahead of publisher pods will fail to parse new payloads. → **Mitigation**: deploy publisher (`server-app`) before consumer (`consumer-app`), OR purge the stream before either comes up. Both pods live in the same backend image, so rolling update ordering in the Deployment surface is sufficient.
- **[Risk]** `ListByIDs` with a very large slice could hit Postgres parameter limits. → **Mitigation**: typical batches are `≤ 100`; document an upper bound (`max_items = 1000`) on the debug RPC request via protovalidate.
- **[Trade-off]** The use case now makes one extra DB round-trip (`ListByIDs`) compared to the previous single `ListByArtist`. → **Acceptable**: payload correctness outweighs a ~few-millisecond overhead. A future optimization could pass concerts inline in the event if profiling shows this matters.
- **[Risk]** Operator accidentally invokes the debug RPC against production. → **Mitigation**: server-side `PERMISSION_DENIED` when `cfg.IsProduction()`. `ENVIRONMENT=production` is already set in the prod overlay as part of standard deployment configuration; no new knob to maintain.
- **[Trade-off]** No dual-compat for the event schema means any operator who missed the NATS purge will see consumer pods CrashLoop on bad messages. → **Acceptable**: runbook note in the task list; dev/staging only.

## Migration Plan

1. Land the specification PR (proto adds `NotifyNewConcerts` + request/response; backward compatible at proto level).
2. Tag `vX.Y.Z` GitHub Release on specification → BSR generates client/server stubs.
3. Backend PR updates BSR dep; lands the refactor (event schema, use case, consumer, repo, handler, DI, tests).
4. Deploy to dev: as part of the rollout, purge the `CONCERT` stream (one-line operator command; document in task 7).
5. Validate in dev with the debug RPC against the existing test user `pepperoni9+pixel@gmail.com`.
6. Promote to staging with the same purge step.
7. Rollback: revert backend PR; NATS stream can be re-purged; no DB migration to reverse.

## Open Questions

- **Debug RPC auth beyond env-gating**: for defense-in-depth, should we also require a signed header / bearer from a short-list of operator identities? Current answer: no (env-gating + JWT is enough for dev/staging), but revisit if the RPC survives beyond testing purposes.
- **Partial delivery on consumer side**: if `ListByIDs` returns fewer concerts than requested (some race-deleted), should the use case abort or proceed with what it has? Current answer: proceed and log at WARN; revisit if telemetry shows this is common.
