## 1. FollowHandler

- [x] 1.1 Add `userRepo entity.UserRepository` field to `FollowHandler` struct and update `NewFollowHandler` constructor
- [x] 1.2 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `Follow`
- [x] 1.3 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `Unfollow`
- [x] 1.4 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `ListFollowed`
- [x] 1.5 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `SetHype`
- [x] 1.6 Update `follow_handler_test.go` to inject a mock `UserRepository` and cover the ID-resolution path for all four methods

## 2. TicketJourneyHandler

- [x] 2.1 Add `userRepo entity.UserRepository` field to `TicketJourneyHandler` struct and update `NewTicketJourneyHandler` constructor
- [x] 2.2 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `SetStatus`
- [x] 2.3 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `Delete`
- [x] 2.4 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `ListByUser`
- [x] 2.5 Update `ticket_journey_handler_test.go` to inject a mock `UserRepository` and cover the ID-resolution path for all three methods

## 3. TicketEmailHandler

- [x] 3.1 Add `userRepo entity.UserRepository` field to `TicketEmailHandler` struct and update `NewTicketEmailHandler` constructor
- [x] 3.2 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `CreateTicketEmail`
- [x] 3.3 Replace `auth.GetUserID` with `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID` in `UpdateTicketEmail`
- [x] 3.4 Update `ticket_email_handler_test.go` to inject a mock `UserRepository` and cover the ID-resolution path for both methods

## 4. DI Wiring

- [x] 4.1 Update `di/provider.go` to pass `UserRepository` to `NewFollowHandler`, `NewTicketJourneyHandler`, and `NewTicketEmailHandler`
- [x] 4.2 Run `wire` (or verify Wire auto-generation) to confirm the dependency graph compiles

## 5. Verification

- [x] 5.1 Run `make check` (lint + unit tests) and confirm all tests pass
- [ ] 5.2 Manually verify `TicketJourneyService/ListByUser` no longer returns 400 after signup in the dev environment
