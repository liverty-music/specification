## 1. Proto Schema

- [x] 1.1 Add `ListByFollower` RPC to `ConcertService` in `concert_service.proto`
- [x] 1.2 Define `ListByFollowerRequest` (empty message) and `ListByFollowerResponse` (repeated Concert)
- [x] 1.3 Run `buf lint` and `buf format -w` to verify proto changes

## 2. Backend Repository

- [x] 2.1 Add `listConcertsByFollowerQuery` SQL constant in `concert_repo.go` joining concerts, events, venues, and followed_artists
- [x] 2.2 Add `ListByFollower(ctx, userID string) ([]*entity.Concert, error)` method to `ConcertRepository`
- [x] 2.3 Add `ListByFollower` to the concert repository interface

## 3. Backend UseCase

- [x] 3.1 Add `userRepo` dependency to `concertUseCase` struct and constructor
- [x] 3.2 Add `resolveUserID` helper method (external ID → internal UUID)
- [x] 3.3 Add `ListByFollower(ctx, externalUserID string) ([]*entity.Concert, error)` method to concert usecase
- [x] 3.4 Add `ListByFollower` to the concert usecase interface

## 4. Backend Handler

- [x] 4.1 Add `ListByFollower` handler method to `ConcertHandler` extracting user ID from auth context
- [x] 4.2 Register the new handler in Connect-RPC route setup

## 5. Backend Tests

- [x] 5.1 Add repository test for `ListByFollower` with followed artists returning concerts
- [x] 5.2 Add repository test for `ListByFollower` with no followed artists returning empty list
- [x] 5.3 Add handler test for unauthenticated `ListByFollower` returning UNAUTHENTICATED error

## 6. Frontend

- [x] 6.1 Add `listByFollower()` method to `ConcertService` calling the new RPC
- [x] 6.2 Replace `fetchConcertsForArtists()` N-call loop in `DashboardService` with single `listByFollower()` call
- [x] 6.3 Update `DashboardService` to map `Concert` responses with artist name resolution
