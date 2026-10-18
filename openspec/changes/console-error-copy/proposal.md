## Why

The admin console and the organizer console put server and library error text on screen: the admin Organizers screen shows `This organizer cannot be deleted: the organizer has a payout account (failed_precondition).` (seen in prod on 2026-10-18, change admin-organizer-status-and-delete task 4.2), the approval queue and the published concerts screens show `err.message` for every failure, and both sign-in callbacks show the identity library's message. That text is written for developers, carries the server's `(code)` suffix, can change with any backend or library release, and is not in the member's language. The owner decided on 2026-10-19 that both consoles choose their own copy from the error code, as most organizer console screens already do, and that the server's message goes only to the console's log.

## What Changes

- Every admin console screen shows copy the console owns for a failed call, chosen from the Connect error code and the operation that failed; a code it has no copy for, and a failure that is not a server response (network down), shows the screen's own "failed" copy for that operation. The server's message and library text never reach the screen; they stay in the browser console log, where they already go.
- Admin Organizers screen, Delete refused (FailedPrecondition): one fixed sentence naming the three possible blockers instead of the server's reason: "This organizer cannot be deleted while it has an order that is not refunded, a settlement that is not reversed, or a payout account."
- Admin Organizers screen, Create: AlreadyExists keeps "That short name is already used by another organizer. Choose a different one."; InvalidArgument (after the screen's own field checks pass, the only remaining cause is the sign-in service rejecting the owner email) says so in fixed copy instead of the server's text; FailedPrecondition no longer says the Organizer is deactivated (a wrong message for a Create).
- Admin business details and platform fee rate forms: InvalidArgument shows "The request was invalid. Check the fields." (the forms check every field before sending).
- Admin and organizer sign-in callbacks show only their fixed failure copy, without the library's message.
- The unused organizer helper that fell back to the server's message is removed.
- No proto or backend change: no ErrorInfo reasons, and go-apperr's message format (with its `(code)` suffix) stays as it is.

## Capabilities

### New Capabilities

- `components/infrastructure/admin/web/global/error-messages`: how every admin console screen reports a failed call: copy owned by the console and chosen from the error code and the operation, the session-expired copy, the sign-in failure copy, and the server's message kept to the console log.
- `components/infrastructure/organizer/web/global/error-messages`: the same rule for the organizer console, in the member's language, for the snackbar, inline messages and the sign-in callback.

### Modified Capabilities

- `components/infrastructure/admin/web/route/organizers`: "Delete's outcome is shown" shows one fixed sentence for a refused Delete instead of the server's reason; a new requirement states what a refused Create shows.

## Impact

- **frontend** only:
  - `admin/organizers/organizer-error-message.ts` (no `rawMessage`/`err.message`; fixed Delete refusal; per-operation overrides), `organizers-route.ts` (Create overrides), `organizer-commercial-terms.ts` (unchanged calls, new InvalidArgument copy).
  - A shared admin mapping used by `admin/approval-queue/approval-queue-route.ts` and `admin/approved-concerts/approved-concerts-route.ts` in place of `err.message`.
  - `admin/auth-callback/auth-callback-route.ts`, `organizer/auth-callback/auth-callback-route.{ts,html}`: fixed copy only.
  - `organizer/services/connect-error-copy.ts`: `toOrganizerErrorMessage` (used only by its own test) removed; `find-organizer-route.ts` imports `Code`/`ConnectError` from `@connectrpc/connect`.
  - Tests in `test/admin/**` and `test/organizer/auth-callback/**` that expect server text on screen are rewritten.
- **specification**: no proto change. **backend**, **cloud-provisioning**: none.
- **Fan app and reception app**: out of scope. The reception app shows no server or library text outside the dev-only bootstrap detail. The fan app still shows library text on its sign-in callback and its error banner (see design.md, Non-Goals).
