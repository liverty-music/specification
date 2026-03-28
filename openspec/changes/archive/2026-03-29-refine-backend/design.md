## Context

The backend repo (~21,000 LOC, 120+ files) follows Clean Architecture well, but a comprehensive analysis revealed 8 improvement areas: test coverage gaps, DB query performance bottlenecks, missing rate limiting, documentation drift, minor architecture violations, error handling inconsistencies, and missing business metrics. All changes are backend-only with no proto or frontend impact.

## Goals / Non-Goals

**Goals:**

- Raise test coverage from 56% to ~80% of production files, prioritizing untested adapter mappers and messaging layer
- Eliminate N+1 query pattern in Merkle path retrieval (10-20ms latency improvement)
- Optimize Merkle node batch inserts via pgx pipelining (30-50% faster)
- Add application-level rate limiting as a Connect-RPC interceptor
- Fix documentation, architecture coupling, and error handling inconsistencies
- Add OpenTelemetry business metrics for key operations

**Non-Goals:**

- Redis or distributed rate limiting (YAGNI at current scale, single-digit Pod count)
- Cloudflare WAF or Cloud Armor rate limiting (Phase 2, separate change)
- sqlc adoption (valuable but large scope, separate change)
- Migrating to Google Wire (manual DI works well, document it instead)
- Adding integration tests for messaging or job systems (separate change)

## Decisions

### D1: Rate Limiting — Connect-RPC Unary Interceptor with `x/time/rate`

**Choice:** In-process token bucket interceptor using Go's `x/time/rate`, inserted between tracing and access log interceptors.

**Alternatives considered:**
- **Redis-backed (distributed):** Adds infrastructure dependency (Memorystore), operational cost, latency per request. Not justified at current Pod count (1-3 replicas).
- **Cloudflare Rate Limiting:** Cannot key on JWT `sub` claim (only IP/URL). Good for DDoS but not for per-user abuse prevention.
- **HTTP middleware (pre-auth):** Cannot distinguish authenticated users. Rate limiting per-IP only.

**Design:**

```
Interceptor chain (updated):

  [1] tracingInterceptor
  [2] rateLimitInterceptor  ← NEW: after tracing (needs span), before access log
  [3] accessLogInterceptor
  [4] errorHandlingInterceptor
  [5] recoverHandler
  [6] claimsBridgeInterceptor
  [7] validationInterceptor
```

Rate limit interceptor logic:
- **Authenticated requests:** Key = JWT `sub` claim (extracted from `authn.GetInfo(ctx)`)
- **Unauthenticated requests (public endpoints):** Key = client IP from `X-Forwarded-For` or `RemoteAddr`
- **Algorithm:** Token bucket via `rate.NewLimiter(rate.Every(interval), burst)`
- **Defaults:** 100 req/sec burst 200 (authenticated), 30 req/sec burst 60 (unauthenticated)
- **Response:** `connect.CodeResourceExhausted` with `Retry-After` header
- **Cleanup:** Background goroutine evicts idle limiters (no access for 10 minutes)
- **Configuration:** Environment variables (`RATE_LIMIT_AUTH_RPS`, `RATE_LIMIT_ANON_RPS`, etc.)

**Migration for existing UserHandler.resendLog:** The in-memory resendLog in UserHandler is retained. The 3-per-10min email resend limit is a business rule (not infrastructure rate limiting) and sits correctly at the use-case level. The general rate limiter provides separate, orthogonal abuse prevention at the infrastructure level.

### D2: Merkle Path Query — Single Batch Query

**Choice:** Replace per-depth `QueryRow` loop with a single query using `unnest` + JOIN.

**Current:** `GetPath()` issues `treeDepth` individual queries (up to 16 round trips).

**New query:**

```sql
SELECT mt.hash
FROM unnest($2::int[], $3::int[]) AS params(depth, node_index)
JOIN merkle_tree mt
  ON mt.event_id = $1 AND mt.depth = params.depth AND mt.node_index = params.node_index
ORDER BY params.depth
```

Where `$2` and `$3` are precomputed Go slices of depth levels and sibling node indices respectively. The sibling index computation (`currentIndex ^ 1`, then `currentIndex /= 2`) moves to Go code before the query. Using `unnest` with parallel arrays is cleaner than `generate_series` + array subscripting for this lookup pattern.

**Alternative:** `generate_series` + LEFT JOIN with array subscripting. Rejected — same performance, but parallel `unnest` is more readable for this access pattern.

### D3: Merkle Batch Insert — pgx.SendBatch

**Choice:** Replace per-node `tx.Exec()` loop with `pgx.Batch` pipelining within the same transaction.

**Current:** N individual `tx.Exec` calls in a loop.
**New:** Build `pgx.Batch`, call `tx.SendBatch(ctx, batch)`, read results.

This reduces round trips from N to 1 while maintaining transaction atomicity.

### D4: SafePredictor Interface Extraction

**Choice:** Define `SafePredictor` interface in entity layer, removing adapter's direct import of `infrastructure/blockchain/safe`.

```go
// entity/safe_predictor.go
type SafePredictor interface {
    AddressHex(userID string) string
}
```

`TicketHandler` receives the interface via DI. `safe.Predictor` implements it.

**Alternative:** Leave as-is (acceptable pragmatism). Rejected because the fix is trivial and improves testability of TicketHandler.

### D5: Business Metrics via OpenTelemetry

**Choice:** Add counters/histograms using the existing OTel meter provider. No new dependencies.

Metrics to add:
- `concert.search.count` (counter, labels: `status=success|error`)
- `ticket.mint.count` (counter, labels: `status=success|error`)
- `push_notification.send.count` (counter, labels: `status=success|error|gone`)
- `follow.count` (counter, labels: `action=follow|unfollow`)

Location: Each use case records its own metrics. The meter is injected via DI (same pattern as existing `telemetry/mint_metrics.go`).

### D6: Test Coverage Strategy

**Priority order for new test files:**

1. **Adapter mappers** (5 files) — concert, follow, ticket, ticket_email, ticket_journey. Proto ↔ Entity conversion bugs are silent and hard to detect.
2. **Messaging layer** (6 files) — publisher, subscriber, router, cloudevents, streams. Event-driven flows are currently untestable.
3. **user_consumer.go** — The only untested event consumer.
4. **Error handling fixes** — Fix `err.Error()` extraction, add request context to error returns.
5. **pkg utilities** — `geo/haversine`, `api/errors`.

Testing approach: Unit tests with mocks (consistent with existing patterns). No new integration tests in this change.

### D7: Error Handling Fixes

Specific fixes:
- `ticket_handler.go:64` — Replace `slog.String("error", err.Error())` with structured error logging
- `concert_handler.go` — Wrap returned errors with artist/concert context where missing
- Standardize: handlers that call single UC methods return errors directly (no wrap needed — UC already wraps). Handlers that do pre-processing (e.g., user lookup + UC call) wrap the pre-processing errors only.

## Risks / Trade-offs

- **[In-memory rate limiting is per-Pod]** → Acceptable at current scale (1-3 replicas). Effective per-user rate = N × configured rate where N = Pod count. Document this limitation. Mitigation: migrate to Redis-backed when Pod count exceeds 5.

- **[Merkle query rewrite changes tested behavior]** → Existing `merkle_repo_test.go` integration tests cover `GetPath()`. Run tests after rewrite to verify identical results. Add edge case tests (depth=0, max depth).

- **[Rate limiter memory growth]** → Token bucket limiters accumulate per unique user/IP. Mitigation: background eviction of idle limiters (10-min TTL). Memory bounded by active user count.

- **[Large PR scope]** → 8 items in one change. Mitigation: tasks are independent and can be split across multiple PRs if needed. Group by theme: (1) DB perf, (2) rate limiting, (3) tests, (4) cleanup.
