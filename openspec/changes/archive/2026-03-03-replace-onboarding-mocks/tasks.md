## 1. Backend: Make SearchNewConcerts Public

- [x] 1.1 Add `ConcertService/SearchNewConcerts` to `publicProcedures` map in `backend/internal/di/provider.go`
- [x] 1.2 Add test case in `backend/internal/infrastructure/auth/authn_test.go` verifying unauthenticated `SearchNewConcerts` requests pass through (covered by existing generic public procedure tests)

## 2. Frontend: Fire-and-forget SearchNewConcerts on Follow

- [x] 2.1 Inject `IConcertService` into `ArtistDiscoveryService` and call `searchNewConcerts(artistId)` fire-and-forget inside `markFollowed()` after localStorage write
- [x] 2.2 Update `artist-discovery-service` tests to verify `searchNewConcerts` is called on follow (no await, error does not reject)

## 3. Frontend: Replace checkLiveEvents Mock

- [x] 3.1 Change `checkLiveEvents(artistName: string)` signature to `checkLiveEvents(artistId: string)` and replace hash mock with `ConcertServiceClient.listConcerts(artistId)` call returning `concerts.length > 0`
- [x] 3.2 Update callers in `discover-page.ts` and `artist-discovery-page.ts` to pass `artist.id` instead of `artist.name`
- [x] 3.3 Update test mocks in `mock-rpc-clients.ts`, `discover-page.spec.ts`, and `artist-discovery-page.spec.ts`

## 4. Verification

- [x] 4.1 Run backend tests (`go test ./...`)
- [x] 4.2 Run frontend tests (`npm test`)
- [x] 4.3 Run linters and verify clean build
