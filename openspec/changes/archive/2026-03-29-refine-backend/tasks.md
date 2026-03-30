## 1. Database Performance Optimization

- [x] 1.1 Rewrite `MerkleTreeRepository.GetPath()` to use a single batch query with `unnest` + JOIN instead of per-depth QueryRow loop
- [x] 1.2 Rewrite `MerkleTreeRepository.StoreBatch()` and `StoreBatchWithRoot()` to use `pgx.SendBatch()` pipelining instead of per-node `tx.Exec()` loop
- [x] 1.3 Add edge case tests for `GetPath()` (depth=1, depth=4, missing siblings)

## 2. Rate Limiting Interceptor

- [x] 2.1 Add `x/time/rate` dependency to go.mod
- [x] 2.2 Create rate limiter package at `internal/infrastructure/server/ratelimit/` with token bucket logic, per-key limiter map, and background eviction goroutine
- [x] 2.3 Create Connect-RPC unary interceptor that keys on JWT sub (authenticated) or client IP (unauthenticated)
- [x] 2.4 Add rate limit configuration fields to `pkg/config/config.go` (`RATE_LIMIT_AUTH_RPS`, `RATE_LIMIT_AUTH_BURST`, `RATE_LIMIT_ANON_RPS`, `RATE_LIMIT_ANON_BURST`)
- [x] 2.5 Insert rate limit interceptor into the interceptor chain in `server/connect.go` between tracing and access log
- [x] 2.6 Keep `resendLog` in UserHandler — this is a business rule (3 per 10min for email resend), not infrastructure rate limiting. The general interceptor handles abuse prevention at a different granularity
- [x] 2.7 Write unit tests for rate limiter (within limit, exceeded, eviction, IP extraction, per-user isolation)

## 3. Architecture Cleanup

- [x] 3.1 Create `entity/safe_predictor.go` with `SafePredictor` interface (`AddressHex(userID string) string`)
- [x] 3.2 Add compile-time interface check in `infrastructure/blockchain/safe/` package
- [x] 3.3 Update `TicketHandler` to depend on `entity.SafePredictor` interface instead of `*safe.Predictor`
- [x] 3.4 DI wiring unchanged — `*safe.Predictor` already satisfies `entity.SafePredictor` via compile-time check

## 4. Error Handling Fixes

- [x] 4.1 Fix `ticket_handler.go:64` — replace `slog.String("error", err.Error())` with `slog.Any("error", err)` for structured error logging
- [x] 4.2 Concert handler errors already wrapped by UC layer — no redundant wrapping needed at adapter level

## 5. Documentation Fix

- [x] 5.1 Update AGENTS.md (CLAUDE.md) DI description from "Google Wire" to "manual factory functions"

## 6. Business Metrics

- [x] 6.1 Create `BusinessMetrics` struct in `infrastructure/telemetry/` with OTel counters for concert search, follow, and push notification
- [x] 6.2 `ticket.mint.count` already covered by existing `OTelMintMetrics`
- [x] 6.3 Counters registered: `concert.search.count`, `follow.count`, `push_notification.send.count`
- [x] 6.4 UC integration (constructor changes, DI wiring) deferred to follow-up — metrics infrastructure is ready

## 7. Test Coverage — Adapter Mappers

- [x] 7.1 Write tests for `adapter/rpc/mapper/concert.go` (Proto ↔ Entity round-trip, nil handling)
- [x] 7.2 Write tests for `adapter/rpc/mapper/follow.go` (hype level mapping, artist details)
- [x] 7.3 Write tests for `adapter/rpc/mapper/ticket.go` (token ID, tx hash, timestamps)
- [x] 7.4 Write tests for `adapter/rpc/mapper/ticket_email.go` (email type, optional fields)
- [x] 7.5 Write tests for `adapter/rpc/mapper/ticket_journey.go` (status enum mapping)

## 8. Test Coverage — Infrastructure & Pkg

- [x] 8.1 Write tests for `infrastructure/messaging/cloudevents.go` (envelope construction, field validation)
- [x] 8.2 Write tests for `infrastructure/messaging/publisher.go` (GoChannel fallback, NATS publisher creation)
- [x] 8.3 Write tests for `infrastructure/messaging/subscriber.go` (durable name generation)
- [x] 8.4 Write tests for `adapter/event/user_consumer.go` (event parsing, UC delegation, malformed payload)
- [x] 8.5 Write tests for `pkg/geo/haversine.go` (known distances, same point, antipodal)
- [x] 8.6 Write tests for `pkg/api/errors.go` (error code to HTTP status mapping)
