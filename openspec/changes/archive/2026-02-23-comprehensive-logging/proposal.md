## Why

The backend blockchain client, all external API clients (Last.fm, MusicBrainz, Google Maps, Gemini), and RPC handler business logic have little to no structured logging. On the frontend, fire-and-forget RPC mutations silently fail without user notification or retry, and several critical paths use `console.*` instead of the structured Aurelia ILogger. This makes production troubleshooting extremely difficult and leaves users unaware of failed operations.

## What Changes

- Add structured logging (info/debug/warn/error) to the Go backend blockchain client, covering mint retries, on-chain queries, and RPC connection lifecycle
- Add structured logging with context attributes (userID, artistID, venueID) to all external API clients (Last.fm, MusicBrainz, Google Maps, Gemini)
- Add info-level logging to database mutation operations (INSERT/UPDATE) with warn for constraint violations
- Add logging to entry verification steps (Merkle root comparison, nullifier duplicate check, event ID verification)
- Add a frontend Connect-RPC logging interceptor that logs all RPC calls with timing at debug level and errors at error level
- Replace `console.error` / `console.warn` calls with structured `ILogger` in `grpc-transport.ts` and `main.ts`
- Add 1-retry with toast notification for fire-and-forget RPC operations (unfollow, passion level update) using existing `IToastService`
- Add timing metrics logging for ZK proof generation in the proof worker

## Capabilities

### New Capabilities
- `backend-structured-logging`: Comprehensive structured logging for Go backend covering blockchain, external APIs, database mutations, and RPC handler business logic
- `frontend-rpc-logging`: Connect-RPC logging interceptor and structured logging improvements for the Aurelia 2 frontend

### Modified Capabilities
- `frontend-observability`: Add Connect-RPC request/response logging interceptor to existing OTEL instrumentation
- `frontend-error-handling`: Add 1-retry mechanism and toast notification for fire-and-forget RPC mutations

## Impact

- **Backend**: `internal/infrastructure/blockchain/ticketsbt/client.go`, `internal/infrastructure/music/{lastfm,musicbrainz}/client.go`, `internal/infrastructure/maps/google/client.go`, `internal/infrastructure/gcp/gemini/searcher.go`, `internal/infrastructure/database/rdb/*_repo.go`, `internal/adapter/rpc/*_handler.go`, `internal/usecase/entry_uc.go`, `internal/usecase/ticket_uc.go`
- **Frontend**: `src/services/grpc-transport.ts`, `src/main.ts`, `src/routes/my-artists/my-artists-page.ts`, `src/services/artist-discovery-service.ts`, `src/services/proof-service.ts`
- **Dependencies**: No new dependencies; uses existing `slog` (backend) and Aurelia `ILogger` + `IToastService` (frontend)
