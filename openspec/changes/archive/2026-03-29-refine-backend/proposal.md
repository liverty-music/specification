## Why

The backend codebase has grown to ~21,000 LOC across 120+ files with strong Clean Architecture adherence, but a comprehensive analysis revealed structural gaps in test coverage (56% of files tested), performance bottlenecks in ZKP operations (Merkle path N+1 queries), no global rate limiting, and documentation drift. Addressing these issues now prevents technical debt accumulation and hardens the system before scaling.

## What Changes

- **Test coverage expansion**: Add tests for untested adapter mappers (5 files), messaging layer (6 files), user event consumer, and pkg utilities
- **Merkle path query optimization**: Replace per-depth QueryRow loop with single batch query in `GetPath()`
- **Merkle node batch insert optimization**: Replace per-node `tx.Exec()` loop with `pgx.SendBatch()` pipelining in `StoreBatch()`
- **Application-level rate limiting**: Add Connect-RPC interceptor for per-user and per-IP rate limiting using `x/time/rate`
- **CLAUDE.md documentation fix**: Update DI description from "Google Wire" to manual DI (Wire is not in go.mod)
- **Handler infrastructure coupling fix**: Extract `SafePredictor` interface to entity layer, removing direct infrastructure import from adapter
- **Error handling consistency**: Fix `err.Error()` string extraction in logging, add request context to error returns in handlers
- **Business metrics instrumentation**: Add OpenTelemetry counters for key business operations (concert searches, ticket mints, push notifications)

## Capabilities

### New Capabilities

- `api-rate-limiting`: Application-level rate limiting via Connect-RPC interceptor with per-user (JWT sub) and per-IP token bucket strategies

### Modified Capabilities

- `usecase-test-coverage`: Extend test requirements to cover adapter mapper layer, messaging infrastructure, and event consumers
- `entity-test-coverage`: Extend test requirements to cover error documentation completeness for entity interfaces

## Impact

- **Backend repo only** (no proto changes, no frontend changes)
- **internal/infrastructure/database/rdb/merkle_repo.go**: Query rewrite for GetPath() and StoreBatch()
- **internal/infrastructure/server/connect.go**: New rate limiting interceptor in chain
- **internal/adapter/rpc/**: Error handling fixes, SafePredictor interface extraction
- **internal/entity/**: New SafePredictor interface, new Cache-related interfaces
- **pkg/**: New rate limiter package or interceptor
- **CLAUDE.md / AGENTS.md**: Documentation corrections
- **Test files**: ~15-20 new test files across adapter, infrastructure, and pkg layers
