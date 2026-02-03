## 1. Specification (Protobuf)

- [x] 1.1 Add `SearchNewConcerts` RPC to `ConcertService` in `proto/liverty_music/rpc/v1/concert_service.proto`.
- [x] 1.2 Define `SearchNewConcertsRequest` and `SearchNewConcertsResponse` messages.
- [x] 1.3 Verify Protobuf changes with `buf lint`.

## 2. Backend Implementation (Go)

- [x] 2.1 Implementing the RPC handler in `internal/adapter/rpc/concert_handler.go`.
- [x] 2.2 Validate `artist_id` in the handler request.
- [x] 2.3 Map the newly discovered concerts from the usecase to RPC response entities.
- [x] 2.4 Add unit tests for the RPC handler.

## 3. Verification

- [/] 3.1 Run backend tests using `go test ./internal/adapter/rpc/...`. (Awaiting remote type generation)
