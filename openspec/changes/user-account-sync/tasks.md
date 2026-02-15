## 1. Database Schema

- [x] 1.1 Create migration to add `external_id UUID UNIQUE NOT NULL` column to `users` table
- [x] 1.2 Update `schema.sql` to reflect the new column

## 2. Protobuf Definitions

- [x] 2.1 Add `external_id` field (UUID-validated) to `User` entity in `liverty_music/entity/v1/user.proto`
- [x] 2.2 Add protovalidate UUID constraint for `external_id` field
- [x] 2.3 Run `buf lint` and `buf format` to verify protobuf changes
- [x] 2.4 Add `name` field to `User` entity for display name from identity provider

## 3. Backend Implementation

- [x] 3.1 Update `User` entity struct in `internal/entity/user.go` to include `ExternalID` and `Name` fields
- [x] 3.2 Implement `GetByExternalID` method in `UserRepository` interface and `user_repo.go`
- [x] 3.3 Update `Create` method in `user_repo.go` to persist `external_id` and `name`
- [ ] 3.4 Update `Create` RPC handler in `user_handler.go` to require JWT authentication and map `external_id`
- [ ] 3.5 Write unit tests for repository and handler changes

## 4. Frontend Implementation

- [ ] 4.1 Update `AuthService.register()` to pass `state: { isRegistration: true }` in `signinRedirect`
- [ ] 4.2 Update `AuthCallback.loading()` to detect `state.isRegistration` after callback
- [ ] 4.3 Call backend `Create` RPC in callback when `isRegistration` is true, passing `email` only (backend extracts `external_id` from JWT `sub` claim and `name` from JWT `name` claim)
- [ ] 4.4 Handle `ALREADY_EXISTS` response gracefully (treat as success)
- [ ] 4.5 Handle other `Create` failures gracefully — log error but complete auth flow

## 5. Integration Testing

- [ ] 5.1 Verify end-to-end signup flow: Zitadel registration → callback → `Create` → user in DB
- [ ] 5.2 Verify idempotency: calling `Create` twice with same `external_id` returns `ALREADY_EXISTS`
- [ ] 5.3 Verify login flow: existing user login does NOT trigger `Create`
