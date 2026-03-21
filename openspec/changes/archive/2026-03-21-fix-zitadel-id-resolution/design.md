## Context

The backend uses Zitadel as the identity provider. Each Zitadel user has an `external_id` (the JWT `sub` claim, a numeric string such as `"365016846690184714"`). Internally, every row in `users` has a `id UUID` primary key that is distinct from the Zitadel ID.

All tables that store per-user data (`followed_artists`, `ticket_journeys`, `ticket_emails`, `push_subscriptions`, `tickets`) define `user_id UUID NOT NULL REFERENCES users(id)`. The correct flow is:

```
JWT sub claim (external_id)
  → userRepo.GetByExternalID(ctx, claims.Sub)
  → user.ID  (internal UUID)
  → passed to use case / repository
```

The fix was applied to `TicketHandler` (originally correct) and later to `PushNotificationHandler` (#239). `FollowHandler`, `TicketJourneyHandler`, and `TicketEmailHandler` still use `auth.GetUserID()` — which returns `claims.Sub` — and pass it directly to use cases that ultimately write or query against a UUID column.

## Goals / Non-Goals

**Goals:**
- Fix the `SQLSTATE 22P02` error in `FollowHandler`, `TicketJourneyHandler`, and `TicketEmailHandler`
- Apply the same pattern established by `TicketHandler` and `PushNotificationHandler`
- Add/update unit tests for all three handlers

**Non-Goals:**
- Changing the ID resolution strategy (e.g., caching, middleware-based resolution)
- Modifying use case or repository interfaces
- Any database schema or API changes

## Decisions

### Inject `UserRepository` into each handler (not the use case)

The resolution of `external_id` → `internal UUID` is an **adapter-layer concern**: it bridges the identity-provider world (JWT) and the domain world (UUID). The use case should only receive domain identifiers. Injecting `UserRepository` at the handler level keeps this mapping at the correct layer boundary, consistent with the existing pattern in `TicketHandler`.

Alternative considered: resolve in a shared middleware interceptor. Rejected because not all RPCs require user resolution (e.g., unauthenticated endpoints), and the current per-handler pattern avoids over-fetching for those cases.

### Reuse `mapper.GetClaimsFromContext` + `userRepo.GetByExternalID`

Both helpers already exist and are used in `TicketHandler`. No new abstractions are needed.

### Return `CodeNotFound` when user is not found

After signup the user record is created via `UserService/Create`. If `GetByExternalID` returns `nil` (user not yet created), the correct response is `CodeNotFound`, consistent with `TicketHandler` and `PushNotificationHandler`.

## Risks / Trade-offs

- **Extra DB lookup per request**: Each of the 9 affected handler methods now issues one additional `SELECT` to resolve the user. This is the same trade-off accepted for `TicketHandler` and `PushNotificationHandler`. Acceptable at current scale.
- **DI wiring changes**: `di/provider.go` must be updated for all three handlers. Wire re-generation is needed.
