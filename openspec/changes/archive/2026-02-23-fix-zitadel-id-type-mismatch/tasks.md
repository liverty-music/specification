## 1. Database Migration

- [x] 1.1 Create Atlas migration to alter `users.external_id` from UUID to TEXT
- [x] 1.2 Update `schema.sql` to reflect `external_id TEXT` type

## 2. Protobuf

- [x] 2.1 Update `User.external_id` field validation from `string.uuid` to non-empty string in proto definition
- [x] 2.2 Run `buf lint` and `buf build` to verify proto changes

## 3. Backend: Use Case Layer

- [x] 3.1 Add `UserRepository` dependency to `ArtistUseCase` constructor
- [x] 3.2 Update `ArtistUseCase.Follow` to resolve external ID to internal user UUID via `UserRepository.GetByExternalID` before calling `ArtistRepository.Follow`
- [x] 3.3 Update `ArtistUseCase.Unfollow` to resolve external ID to internal user UUID before calling `ArtistRepository.Unfollow`
- [x] 3.4 Update `ArtistUseCase.ListFollowed` to resolve external ID to internal user UUID before calling `ArtistRepository.ListFollowed`

## 4. Backend: Wiring

- [x] 4.1 Update dependency injection to pass `UserRepository` to `ArtistUseCase` constructor

## 5. Verification

- [x] 5.1 Run existing unit tests and fix any failures caused by the new `UserRepository` dependency
- [x] 5.2 Run `golangci-lint run` and `go vet ./...`
