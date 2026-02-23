## 1. Backend: Blockchain Client Logging

- [ ] 1.1 Add logger injection to `ticketsbt/client.go` constructor and log RPC connection initialization at INFO
- [ ] 1.2 Add logging to `Mint()`: DEBUG for each retry attempt with `attempt`, `maxAttempts`, `tokenID`, `error`; INFO on success with `txHash`; ERROR on final failure with response body
- [ ] 1.3 Add logging to `OwnerOf()`: DEBUG for query and retry attempts; ERROR on failure with response body
- [ ] 1.4 Add logging to `IsTokenMinted()`: WARN for unexpected errors (non-ERC721NonexistentToken) with `tokenID`, `error`

## 2. Backend: External API Client Logging

- [ ] 2.1 Add logger injection and logging to `lastfm/client.go`: INFO for each API method call with `method`, `artistID`/`query`; ERROR with `statusCode` on failure; DEBUG for rate limiter backoff
- [ ] 2.2 Add logger injection and logging to `musicbrainz/client.go`: INFO for requests with `mbid`/`venueName`; WARN for URL resolution fallback; ERROR on failure; DEBUG for rate limiter backoff
- [ ] 2.3 Add logger injection and logging to `google/client.go`: INFO for search with `venueName`; ERROR with `statusCode` on failure
- [ ] 2.4 Add logger injection and logging to `gemini/searcher.go`: INFO for search with `artistID`, `query`; WARN for invalid dates; ERROR on model failure

## 3. Backend: Database Mutation Logging

- [ ] 3.1 Add INFO logging to `ticket_repo.go` Create method with `entityType=ticket`, `ticketID`, `userID`, `eventID`; WARN for duplicate key
- [ ] 3.2 Add INFO logging to `user_repo.go` Create and UpdateSafeAddress methods with `entityType=user`, `userID`; WARN for duplicate email
- [ ] 3.3 Add INFO logging to `concert_repo.go` Create method with `entityType=concert`, bulk count
- [ ] 3.4 Add INFO logging to venue and artist repository write operations

## 4. Backend: Entry Verification Logging

- [ ] 4.1 Add INFO logging to `entry_uc.go` for event ID verification step with `step=eventID`, `eventID`, `match`
- [ ] 4.2 Add INFO logging for Merkle root comparison step with `step=merkleRoot`, `eventID`, `match`
- [ ] 4.3 Add INFO/WARN logging for nullifier duplicate check with `step=nullifier`, `eventID`, `userID`, `isDuplicate`

## 5. Frontend: Connect-RPC Logging Interceptor

- [ ] 5.1 Create logging interceptor in `grpc-transport.ts` that logs DEBUG on request start and response with method name and duration; ERROR on failure with Connect error code
- [ ] 5.2 Register the logging interceptor in the transport interceptor chain (order: OTEL, logging, auth)

## 6. Frontend: Replace console.* with ILogger

- [ ] 6.1 Replace `console.error` in `grpc-transport.ts` auth interceptor with `ILogger.error()` by passing logger to `createTransport()`
- [ ] 6.2 Replace `console.warn` in `main.ts` Service Worker registration with `ILogger.warn()`

## 7. Frontend: Fire-and-forget Retry + Toast

- [ ] 7.1 Add 1-retry with toast notification to unfollow artist in `my-artists-page.ts`: retry once on failure, toast + revert optimistic UI on retry failure
- [ ] 7.2 Add 1-retry with toast notification to passion level update in `my-artists-page.ts`
- [ ] 7.3 Add 1-retry with toast notification to follow artist rollback in `artist-discovery-service.ts`

## 8. Frontend: ZK Proof Timing Metrics

- [ ] 8.1 Add timing metrics to `proof-service.ts`: log at INFO with `durationMs` on completion; ERROR with `durationMs` on failure
