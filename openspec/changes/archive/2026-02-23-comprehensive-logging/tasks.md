## 1. Backend: Blockchain Client Logging

- [x] 1.1 Add logger injection to `ticketsbt/client.go` constructor and log RPC connection initialization at INFO
- [x] 1.2 Add logging to `Mint()`: DEBUG for each retry attempt with `attempt`, `maxAttempts`, `tokenID`, `error`; INFO on success with `txHash`; ERROR on final failure with response body
- [x] 1.3 Add logging to `OwnerOf()`: DEBUG for query and retry attempts; ERROR on failure with response body
- [x] 1.4 Add logging to `IsTokenMinted()`: WARN for unexpected errors (non-ERC721NonexistentToken) with `tokenID`, `error`

## 2. Backend: External API Client Logging

- [x] 2.1 Add logger injection and logging to `lastfm/client.go`: INFO for each API method call with `method`, `artistID`/`query`; ERROR with `statusCode` on failure; DEBUG for rate limiter backoff
- [x] 2.2 Add logger injection and logging to `musicbrainz/client.go`: INFO for requests with `mbid`/`venueName`; WARN for URL resolution fallback; ERROR on failure; DEBUG for rate limiter backoff
- [x] 2.3 Add logger injection and logging to `google/client.go`: INFO for search with `venueName`; ERROR with `statusCode` on failure
- [x] 2.4 Add logger injection and logging to `gemini/searcher.go`: INFO for search with `artistID`, `query`; WARN for invalid dates; ERROR on model failure

## 3. Backend: Database Mutation Logging

- [x] 3.1 Add INFO logging to `ticket_repo.go` Create method with `entityType=ticket`, `ticketID`, `userID`, `eventID`; WARN for duplicate key
- [x] 3.2 Add INFO logging to `user_repo.go` Create and UpdateSafeAddress methods with `entityType=user`, `userID`; WARN for duplicate email
- [x] 3.3 Add INFO logging to `concert_repo.go` Create method with `entityType=concert`, bulk count
- [x] 3.4 Add INFO logging to venue and artist repository write operations

## 4. Backend: Entry Verification Logging

- [x] 4.1 Add INFO logging to `entry_uc.go` for event ID verification step with `step=eventID`, `eventID`, `match`
- [x] 4.2 Add INFO logging for Merkle root comparison step with `step=merkleRoot`, `eventID`, `match`
- [x] 4.3 Add INFO/WARN logging for nullifier duplicate check with `step=nullifier`, `eventID`, `userID`, `isDuplicate`

## 5. Frontend: Connect-RPC Logging Interceptor

- [x] 5.1 Create logging interceptor in `grpc-transport.ts` that logs DEBUG on request start and response with method name and duration; ERROR on failure with Connect error code
- [x] 5.2 Register the logging interceptor in the transport interceptor chain (order: OTEL, logging, auth)

## 6. Frontend: Replace console.* with ILogger

- [x] 6.1 Replace `console.error` in `grpc-transport.ts` auth interceptor with `ILogger.error()` by passing logger to `createTransport()`
- [x] 6.2 Replace `console.warn` in `main.ts` Service Worker registration with `ILogger.warn()`

## 7. Frontend: Fire-and-forget Retry + Toast

- [x] 7.1 Add 1-retry with toast notification to unfollow artist in `my-artists-page.ts`: retry once on failure, toast + revert optimistic UI on retry failure
- [x] 7.2 Add 1-retry with toast notification to passion level update in `my-artists-page.ts`
- [x] 7.3 Add 1-retry with toast notification to follow artist rollback in `artist-discovery-service.ts`

## 8. Frontend: ZK Proof Timing Metrics

- [x] 8.1 Add timing metrics to `proof-service.ts`: log at INFO with `durationMs` on completion; ERROR with `durationMs` on failure

## 9. Backend: Replace stdlib log with structured logger

- [x] 9.1 Add `Logger` field to `App` struct in `di/app.go` and replace `log.Println` with `a.Logger.Info()` in `Shutdown()`
- [x] 9.2 Replace `log.Println` in `di/job.go` `Shutdown()` with `a.Logger.Info()`
- [x] 9.3 Replace all `log.Printf`/`log.Println` in `cmd/api/main.go` with structured `logging.Logger` (bootstrap logger pre-init, `app.Logger` post-init)
- [x] 9.4 Replace all `log.Printf`/`log.Println` in `cmd/job/concert-discovery/main.go` with structured `logging.Logger`

## 10. Verification Fixes

- [x] 10.1 Refactor `artist-service-client.ts` to use shared `createTransport()` with logging + OTEL interceptors
- [x] 10.2 Add optimistic UI rollback (re-insert artist) to `commitPendingUnfollow()` on retry failure
- [x] 10.3 Add DEBUG rate limiter backoff logging before `throttler.Do()` in `lastfm/client.go` and `musicbrainz/client.go`
- [x] 10.4 Add ERROR log at Gemini model failure site in `gemini/searcher.go`
- [x] 10.5 Add `artistID` attribute to Gemini INFO search log
- [x] 10.6 Add `statusCode` attribute to lastfm and google HTTP error logs
