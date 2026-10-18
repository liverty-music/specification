## Why

All three web apps put server and library error text on screen. The admin Organizers screen shows `This organizer cannot be deleted: the organizer has a payout account (failed_precondition).` (seen in prod on 2026-10-18, change admin-organizer-status-and-delete task 4.2). The admin approval queue and published concerts screens show `err.message` for every failure. The admin, organizer and fan sign-in callbacks show the identity library's message. The fan error banner shows the captured error's message. The fan dashboard's inline error shows the error's message under its own copy. The fan checkout and lottery entry show the card payment form's message. That text is written for developers, can carry the server's `(code)` suffix, can change with any backend or library release, and is not in the user's language.

The owner decided on 2026-10-19 that the admin console, the organizer console and the fan app all choose their own copy from the error code. The server's message goes only to the browser console log. Most organizer console and fan screens already work this way.

## What Changes

- **Every screen of the three apps**: a failure shows copy the app owns, chosen from the error code and the operation that failed.
  - A code the screen has no copy for, and a failure that is not a server response (for example, the network is down), shows the screen's own "failed" copy for that operation.
  - The server's message and library text never reach the screen. They stay in the browser console log, where they already go.
  - The organizer console and the fan app take this copy from their ja/en catalogs. The admin console uses English literals, as it does today.
- **Admin Organizers screen, Delete refused (FailedPrecondition)**: the server's reason is replaced by one fixed sentence naming the three possible blockers: "This organizer cannot be deleted while it has an order that is not refunded, a settlement that is not reversed, or a payout account."
- **Admin Organizers screen, Create**:
  - AlreadyExists keeps "That short name is already used by another organizer. Choose a different one."
  - InvalidArgument shows fixed copy saying the sign-in service did not accept the owner email. Once the screen's own field checks pass, that is the only remaining cause.
  - FailedPrecondition no longer says the Organizer is deactivated, which was wrong for a Create.
- **Admin business details and platform fee rate forms**: InvalidArgument shows "The request was invalid. Check the fields." These forms check every field before sending.
- **All three sign-in callbacks** show only fixed failure copy. The fan callback's copy becomes localized.
- **Fan error banner**: shows a fixed, localized title and message (and localized button labels) with the Error ID. The error's message stays in the copied details and the report.
- **Fan inline error** (dashboard): the error-message line is dropped. Its own message stays, and its Retry label becomes localized.
- **Fan checkout and lottery entry**: a card payment failure shows the app's own copy for its kind:
  - the card details are incomplete or invalid;
  - the card was declined or could not be authenticated;
  - anything else.
  The payment form's message is no longer shown, and the existing fixed Japanese fallbacks move to the catalog.
- **Removed**: the unused organizer helper that fell back to the server's message.
- **No proto or backend change**: no ErrorInfo reasons are added, and go-apperr's message format (with its `(code)` suffix) stays as it is.

## Capabilities

### New Capabilities

- `components/infrastructure/admin/web/global/error-messages`: how every admin console screen reports a failed call. Covers copy owned by the console and chosen from the error code and the operation, the session-expired copy, the sign-in failure copy, and keeping the server's message in the console log.
- `components/infrastructure/organizer/web/global/error-messages`: the same rule for the organizer console, in the member's language, for the snackbar, inline messages and the sign-in callback.
- `components/infrastructure/fan/web/global/error-messages`: the same rule for the fan app, in the fan's language, including card payment failures and the sign-in callback.

### Modified Capabilities

- `components/infrastructure/admin/web/route/organizers`: "Delete's outcome is shown" shows one fixed sentence for a refused Delete instead of the server's reason. A new requirement states what a refused Create shows.
- `components/infrastructure/fan/web/global/error-banner`: a new requirement that the banner's text comes from the app's catalog and never shows the captured error's message.

## Impact

- **frontend** only:
  - **Admin**:
    - `admin/organizers/organizer-error-message.ts` stops using `rawMessage`/`err.message`, gets the fixed Delete refusal and takes per-operation overrides.
    - `organizers-route.ts` passes the Create overrides.
    - `organizer-commercial-terms.ts` gets the new InvalidArgument copy.
    - A shared admin mapping replaces `err.message` in `approval-queue-route.ts` and `approved-concerts-route.ts`.
    - `admin/auth-callback/auth-callback-route.ts` shows fixed copy.
  - **Organizer**:
    - `organizer/auth-callback/auth-callback-route.{ts,html}` shows fixed copy.
    - `toOrganizerErrorMessage` (used only by its own test) is removed.
  - **Fan**:
    - `src/routes/auth-callback/auth-callback-route.{ts,html}`, `src/components/error-banner/error-banner.html`, `src/components/inline-error/inline-error.{ts,html}` and `src/services/stripe-service.ts` change, together with its callers in `checkout-route` and `lottery-entry-route`.
    - New keys in `src/locales/{ja,en}/translation.json`.
  - Tests that expect server or library text on screen are rewritten.
- **specification**: no proto change. **backend**, **cloud-provisioning**: none.
- **Reception app**: out of scope. It shows no server or library text outside the dev-only bootstrap detail.
