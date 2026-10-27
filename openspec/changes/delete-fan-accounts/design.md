## Context

See proposal.md - Why. The state this design builds on:

- `UserUseCase.Delete` (backend `internal/usecase/user_uc.go`) checks Tickets and Orders, then calls `identityRemover.DeleteIdentity` (Zitadel User v2 delete) and `userRepo.Delete`. Only the admin `UserService.Delete` exposes it.
- `users` has no `created_at` column. Follows, journeys, push subscriptions, notifications, reminders, identity verifications, passkeys and wallet keys reference `users(id) ON DELETE CASCADE`. `orders`, `tickets`, `checkouts`, `lottery_entries` and `resale_listings` keep `user_id` without a foreign key, so they survive a deletion with no migration.
- The fan app's access token is a Zitadel JWT with no `auth_time` and no `amr` claim. The ID token has both. This was checked on the prod fan and organizer tokens stored by the E2E sessions (claim names only).
- Passkey management already runs a second OIDC request (`src/services/passkey-auth-service.ts`, change `fan-passkey-recovery-and-management` D3): `max_age=300`, an in-memory `UserManager` and the callback `/auth/passkeys-callback`, which is registered as a redirect URI of the fan app in Zitadel.
- Only the identity service holds identity-provider credentials. Each calling workload reaches it on its own listener, which serves only that workload's procedures: the admin console API's listener serves `DeleteIdentity`, the fan API's only `VerifyEmail` (backend `internal/di/identity.go`). A NetworkPolicy admits each listener from its one workload, and no route exposes the identity service outside the cluster (cloud-provisioning `k8s/namespaces/backend/base/identity-networkpolicy.yaml`). The fan API has no setting for the fan app's client id.
- Several flows check a condition and then act on it. Those flows serialize with a transaction-scoped advisory lock held while the work runs on other connections (`CheckoutRepository.Serialize`, `pg_advisory_xact_lock`), or with row locks (`event_removal.go`).

## Goals / Non-Goals

**Goals:**
- A purchase, lottery entry or resale listing must never be left behind half-done by a deletion that raced it.
- Fan and admin deletion run one usecase and one blocker rule.
- The backend proves the fresh sign-in itself. Hiding the button on the screen is not the check.

**Non-Goals:**
- Anonymizing kept records. Orders and tickets keep the deleted `user_id`, which no longer resolves to a person.
- Deleting PostHog persons or events.
- A soft-delete or grace period. Deletion is immediate.

## Decisions

### D1. One blocker rule, read by the screens and enforced by Delete

`UserUseCase.ListDeletionBlockers` returns `[]DeletionBlocker{Kind, Count}`. `Delete` calls it under the lock (D2) and fails with FailedPrecondition when it is not empty. The four kinds and their reads:

| kind | read | blocks when |
|---|---|---|
| Upcoming ticket | `Ticket.ListByUser` + `Event.Get` per distinct event | Issued and the event's `local_date` ≥ today in `Asia/Tokyo` |
| Listed resale | `ResaleListing.ListByUser` + `Event.Get` | open: status Listed and before its deadline (an expired listing keeps the stored status Listed forever) |
| Pending lottery entry | `LotteryEntry.ListByUser` (new) | state Entered |
| Payment in progress | `Checkout.ListByUser` (new); `LotteryEntry.ListByUser` + `Order.GetByLotteryEntryID` | a Checkout Committed, or Held with `hold_expiry` > now; a lottery entry Won with no Order yet |

A Won entry with no Order is a win whose card is not charged yet: the issuance sweeper (and, after `make-lottery-draw-durable`, `OrderUseCase.Issue`, which retries for up to 24 hours) still has to charge it and read the User for the confirmation. It counts as Payment in progress, the same thing to the fan as a Committed Checkout, so no new kind is added. A Lost entry never charges and does not block.

The ticket rule uses the event's date, not its start time. Many events have no start time, and a start-time rule would block those tickets forever. The rule counts the whole event day as in progress. A fan can withdraw from the next day on.

Alternative considered: one SQL query that counts all four kinds. It would be faster, but it would restate the entity rules in SQL. A fan has few of these rows, so composing the existing operations is cheap enough.

Proto: `liverty_music.entity.v1.DeletionBlocker { Kind kind = 1; int32 count = 2; }` with `enum Kind { KIND_UNSPECIFIED, KIND_UPCOMING_TICKET, KIND_LISTED_RESALE, KIND_PENDING_LOTTERY_ENTRY, KIND_PAYMENT_IN_PROGRESS }`. The names follow the `rpc-design` skill:
- fan `UserService.ListDeletionBlockers` and `UserService.Delete`;
- admin `UserService.GetByEmail`, which returns `User` and `repeated DeletionBlocker`.

### D2. Delete serializes with every path that creates a blocker

This decision covers the race between checking the blockers and deleting the User.

- **The new operation.** It is `User.SerializeDeletion(ctx, id, fn)`. It follows the same pattern as `Checkout.Serialize`: it opens a transaction, takes `pg_advisory_xact_lock(hashtextextended('user:' || id, 0))` exclusively, runs `fn` and rolls back.
- **What Delete runs inside it:**
  1. ListDeletionBlockers;
  2. DeleteIdentity;
  3. User.Delete.
- **What the creators do.** Each path that creates a blocker takes the shared form `pg_advisory_xact_lock_shared` of the same key inside its own insert transaction. It then confirms the users row exists, and fails with NotFound if it does not. Those paths are:
  - `Checkout.GetOrCreateHeld`;
  - `LotteryEntry.Create`;
  - `ResaleListing.Create`.
- **Why this closes the race:**
  - A creator that committed before Delete took the lock is visible to step 1.
  - A creator that starts after Delete took the lock waits for it. It then finds no user and stores nothing.
  - Tickets are issued only from an Entered entry or a Committed checkout. Both are blockers, so no issuance can start for a user that passed step 1.

Alternative considered: `SELECT … FROM users FOR UPDATE` against `FOR KEY SHARE` in the creators. `fn` runs its reads and the `DELETE` on other pool connections, so it would wait on its own row lock. The advisory lock has no such problem, and the codebase already uses it.

The identity is removed before the row on purpose, as today. If the row delete fails, a retry finishes the job. If the order were reversed, a failed identity removal would leave a person who can sign in with no account.

### D3. Proof of a fresh sign-in is the ID token of a `max_age=300` request

- **Request.** The fan `DeleteRequest` carries `string id_token`. It is a proto `string` with `min_len: 1`.
- **Checks in the handler.** The handler validates the ID token with the existing JWKS validator, then checks:
  - the issuer is the fan issuer;
  - `aud` contains the fan app's client id;
  - `sub` equals the access token's `sub`;
  - `auth_time` ≥ now − 300 s, with no extra skew allowance.
- **Errors.** Any failed check returns PermissionDenied. An empty token returns InvalidArgument through protovalidate.
- **Where the token comes from.** The frontend gets the token from the same mechanism passkey management uses. `max_age=300` makes Zitadel ask for a passkey unless the last sign-in is under 5 minutes old. The ID token's `auth_time` then shows that sign-in.

Alternatives considered:
- A Zitadel Action that copies `auth_time` into the access token. This needs a new Action in cloud-provisioning and changes every fan token, only to serve one RPC.
- Token introspection. Its response carries no `auth_time` either.
- Trusting the screen. A direct RPC call would skip the check.

**Where the identity is removed.** The fan API's listener on the identity service also serves the existing `DeleteIdentity`, and the fan workload builds the identity remover the admin workload uses. The identity service does not check the ID token again: only the fan API can reach that listener, and the fan API is where an outside request enters, so the check belongs there. A compromised fan API could remove any fan's identity, but it can already change every User row, so the added exposure is small. The fan app's client id comes from a new fan API setting `FAN_OIDC_CLIENT_ID`, set in cloud-provisioning.

Alternative considered: a new identity-service method that takes the ID token and checks it there. It would keep a compromised fan API from removing identities, at the cost of a second copy of the check, JWKS access in the identity service and a new backend RPC.

### D4. One fresh-sign-in service for passkeys and withdrawal

- **The service.** `PasskeyAuthService` becomes a fresh-sign-in service. `start` takes the screen to return to, which is stored in the oidc-client-ts request state.
- **Scopes.** The request keeps both scopes:
  - the Zitadel API audience, which passkey management needs;
  - the org scope.
- **Callback.** `/auth/passkeys-callback` stays the single callback and routes by the stored return screen. Reusing the registered redirect URI avoids a cloud-provisioning change and a deploy-order dependency. The route's name no longer describes everything it does. This is a naming debt; rename it when the redirect URIs are next edited.
- **Abandoned sign-in.** When the fan leaves the hosted sign-in with the browser's Back button, the callback never runs and the withdrawal screen reloads without a token. Before redirecting, the screen writes a sessionStorage marker (the return screen and an expiry 10 minutes later, never a token). On load, a marker with no session tells the screen that the fan abandoned the sign-in, so it says nothing was deleted.
- **What withdrawal uses.** The withdrawal screen uses only the session's ID token and drops it after the call (spec `route/delete-account`).

Alternative considered: a second UserManager with its own callback. It needs a new redirect URI and a second copy of the callback logic.

### D5. Where each value on the new screens is read from

| screen | value | source |
|---|---|---|
| withdrawal | blockers and counts | fan `ListDeletionBlockers` → `blockers[].kind`, `.count` |
| withdrawal | statements, Privacy Policy link | static copy (ja/en) |
| admin Users | name, email, id | admin `GetByEmail` → `user.name`, `user.email`, `user.id` |
| admin Users | blockers and counts | admin `GetByEmail` → `blockers[].kind`, `.count` |

Nothing is passed between screens. The admin screen keeps the typed email only in its own field.

### D6. After deletion the app signs out locally

The Zitadel user no longer exists after deletion, so a hosted end-session redirect has no session to end. The app removes the stored OIDC user (oidc-client-ts `removeUser`), calls `analytics.reset()`, and then routes to a static "account deleted" view. The Welcome screen is reached from that view.

### D7. Privacy Policy retention period

Order and ticket records are kept for 7 years. That is the longest period that 法人税法 (Corporation Tax Act) record retention can require for 帳簿書類 (books and records). The ja and en policy texts say so. A tax accountant should confirm the number before the release. If it changes, only the policy copy changes.

## Risks / Trade-offs

- [A fan who bought tickets cannot withdraw until the event day passes.] → This is intended: their entry ticket shows their 本人確認 (identity check) details. The withdrawal screen and the admin screen both show the reason.
- [Orders and tickets keep a `user_id` that no longer resolves to anyone. An admin order view will show no buyer.] → This is acceptable for records. Card last-4 and amounts on the order are enough for accounting and disputes.
- [The creators of the three blockers each gain one lock and one existence check.] → The shared lock never waits except during a deletion of the same user.
- [The callback route `/auth/passkeys-callback` now also serves withdrawal.] → It routes by state. The naming debt is noted in D4.
- [Re-registration with the same email after deletion creates a new account. After identity verification ships, the same person can verify again because the old IdentityVerification row is gone.] → This is accepted. Banning is out of scope.

## Migration Plan

1. specification: add the proto, release it, and wait for BSR generation.
2. cloud-provisioning: set `FAN_OIDC_CLIENT_ID` on the fan API, and admit `DeleteIdentity` on the fan API's identity listener in the NetworkPolicy comment. The setting is unused until the backend reads it.
3. backend: add the new operations and usecases, the creator locks, the handlers, the fresh-sign-in check, `DeleteIdentity` on the fan API's identity listener and the identity remover on the fan workload. No schema migration. Deploy.
4. frontend: add the fan withdrawal route, the Settings row, the fresh-sign-in generalization, the admin Users route and the Privacy Policy text. Deploy.

Rollback: revert the frontend first. The backend RPCs are additive. The narrowed admin rule only lets more deletions through, so reverting the backend restores the stricter rule.

## Open Questions

- The exact retention period stated in the Privacy Policy (D7). It defaults to 7 years until a tax accountant confirms; only the copy changes.
