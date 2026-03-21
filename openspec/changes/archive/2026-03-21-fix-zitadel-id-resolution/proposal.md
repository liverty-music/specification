## Why

Multiple RPC handlers pass the Zitadel JWT `sub` claim (a numeric string like `"365016846690184714"`) directly as `user_id` to PostgreSQL, where the column type is `UUID`. This causes `SQLSTATE 22P02: invalid input syntax for type uuid` at runtime. The same bug was fixed in `PushNotificationHandler` (#239) and `TicketHandler`, but three handlers were missed: `FollowHandler`, `TicketJourneyHandler`, and `TicketEmailHandler`.

## What Changes

- `FollowHandler`: inject `UserRepository`, resolve `claims.Sub` → `user.ID` before calling use case (affects `Follow`, `Unfollow`, `ListFollowed`, `SetHype`)
- `TicketJourneyHandler`: inject `UserRepository`, resolve `claims.Sub` → `user.ID` before calling use case (affects `SetStatus`, `Delete`, `ListByUser`)
- `TicketEmailHandler`: inject `UserRepository`, resolve `claims.Sub` → `user.ID` before calling use case (affects `CreateTicketEmail`, `UpdateTicketEmail`)
- `di/provider.go`: wire `UserRepository` into the three handlers above

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

_None._ This is a pure bug fix — no requirements change, only the implementation corrects a missing ID-resolution step.

## Impact

- **Backend handlers**: `follow_handler.go`, `ticket_journey_handler.go`, `ticket_email_handler.go`
- **DI wiring**: `di/provider.go`
- **Tests**: handler unit tests for the three affected files must be updated/added
- **No API changes**: request/response shapes are unchanged
- **No DB migration**: schema is unchanged
