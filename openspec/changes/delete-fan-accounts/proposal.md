## Why

A fan cannot leave Liverty Music: there is no withdrawal screen, and the only way to remove an account is the admin `UserService.Delete`, which no admin screen calls (it was last run from browser DevTools). Its rule also blocks every fan who ever bought a ticket, because a ticket stays Issued after its event and a paid Order stays Paid, so the deletion path the identity-verification change relies on does not exist in practice.

## What Changes

- **Deletion rule.** UserUseCase.Delete is blocked only by what is still in progress: an Issued Ticket for an event whose date (in Japan time) is today or later, a Listed resale listing, a lottery entry still Entered (awaiting its draw), or a Checkout still being paid (Committed, or Held before its hold expires). A held event's ticket and a paid Order no longer block. **BREAKING** for the admin RPC's FailedPrecondition cases, which narrow.
- **Deletion stays physical.** The User row, its sign-in identity and everything that belongs only to it (follows, journeys, push subscriptions, notifications, reminders, IdentityVerification records, passkeys, wallet keys) are removed; Orders, Tickets, Checkouts, lottery entries and resale listings stay, keyed by the deleted User's id, as transaction records.
- **Deletion blockers are readable.** A new UserUseCase.ListDeletionBlockers returns what currently blocks a User's deletion, so both screens show it before the fan or admin commits, and Delete uses the same rule.
- **Fan withdrawal.** The fan UserService gains Delete (and ListDeletionBlockers) for the caller's own User. Delete requires proof of a sign-in made within the last 5 minutes by the same identity; the backend checks it, not the screen. A new withdrawal screen, reached from Settings, lists blockers, states what deletion means (history unavailable, irreversible, re-registering with the same email starts fresh), asks the fan to sign in again (the same fresh sign-in passkey management uses) and then deletes. After deletion the app signs out and resets analytics identity; PostHog persons are not deleted.
- **Admin removal screen.** The admin UserService gains GetByEmail (exact match, case-insensitive) returning one User with its deletion blockers. A new admin screen finds a fan by email, shows name, email, id and blockers, and deletes after confirmation.
- **Privacy policy.** The policy states that transaction records (orders, tickets) are kept after withdrawal for accounting and dispute handling, and that analytics data stays in a form that no longer identifies the person.

Out of scope: suspending or banning accounts, and keeping a deleted person's provider user id to stop re-registration.

## Capabilities

### New Capabilities

- `stories/delete-my-account`: a signed-in fan withdraws from Liverty Music from Settings.
- `stories/delete-a-fan-account`: an admin removes a fan's account at the fan's request, found by email.
- `components/usecase/user/list-deletion-blockers`: what currently blocks a User's deletion.
- `components/usecase/user/get-by-email`: an admin reads one User by email address.
- `components/entity/lottery-entry/list-by-user`: a User's lottery entries, needed to find one still awaiting its draw.
- `components/entity/checkout/list-by-user`: a User's checkouts, needed to find one still being paid.
- `components/infrastructure/fan/web/route/delete-account`: the fan withdrawal screen.
- `components/infrastructure/admin/web/route/users`: the admin screen that finds and removes a fan.

### Modified Capabilities

- `components/usecase/user/delete`: the blocking rule narrows to in-progress tickets, resale listings, lottery entries and checkouts, and the usecase is exposed to the fan as well as the admin.
- `components/adapter/fan/api/rpc/user`: adds Delete (fresh sign-in within 5 minutes) and ListDeletionBlockers for the caller's own User.
- `components/adapter/admin/api/rpc/user`: adds GetByEmail returning a User with its deletion blockers.
- `components/infrastructure/fan/web/route/settings`: an account section row that opens the withdrawal screen.
- `components/infrastructure/fan/web/global/legal-document`: the Privacy Policy states what is kept after withdrawal.

Unchanged and relied on: `components/entity/user/delete` (already removes owned data and keeps purchases), `components/entity/user/delete-identity`, `components/entity/user/get-by-email`, `components/entity/ticket/list-by-user`, `components/entity/resale-listing/list-by-user`, `components/entity/event/get`.

## Impact

- **specification**: proto for fan `UserService.Delete` / `ListDeletionBlockers` and admin `UserService.GetByEmail` (with a `DeletionBlocker` message); the specs above.
- **backend**: UserUseCase (Delete rule, ListDeletionBlockers, GetByEmail), LotteryEntry.ListByUser and Checkout.ListByUser, fan and admin user handlers, a fresh-sign-in check on the fan Delete (the access token carries no `auth_time`; design.md decides how it is proved), and a row lock that keeps a purchase from starting while a deletion runs.
- **frontend**: fan withdrawal route and Settings row, reuse of the passkey-management fresh sign-in (`src/services/passkey-auth-service.ts`), admin users route, privacy policy text (ja/en).
- **Data**: no schema migration expected; orders, tickets, checkouts, lottery entries and resale listings already keep `user_id` without a foreign key.
