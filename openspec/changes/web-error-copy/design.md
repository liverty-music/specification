## Context

See proposal.md - Why. State of frontend `origin/main` (`9785b60`, 2026-10-19), the places where server or library text reaches the screen:

| Place | What it shows today |
|---|---|
| `admin/organizers/organizer-error-message.ts` `toUserMessage` | InvalidArgument and every unlisted code: `err.rawMessage`; non-Connect errors: `err.message` |
| same file, `toDeleteMessage` | FailedPrecondition: `This organizer cannot be deleted: <server reason>.` |
| `admin/approval-queue/approval-queue-route.ts` load, approve, conflict resolution, reject | `err.message` (a ConnectError's message is `[code] message`) |
| `admin/approved-concerts/approved-concerts-route.ts` load, delete | `err.message` |
| `admin/auth-callback/auth-callback-route.ts` | `Login failed: <library message>` |
| `organizer/auth-callback/auth-callback-route.{ts,html}` | the library message under サインインできませんでした。 |
| `organizer/services/connect-error-copy.ts` `toOrganizerErrorMessage` | `rawMessage` fallbacks, but no screen calls it (only its test) |
| `src/routes/auth-callback/auth-callback-route.ts:173` (fan) | `Login failed: <library message>`, with English-only "Verifying authentication..." and "Return Home" |
| `src/components/error-banner/error-banner.html:6` (fan) | the captured error's message, under an English-only title and buttons. Fed only by unexpected errors: router navigation errors (`app-shell.ts:288`), `window.onerror` and unhandled rejections (`services/global-error-handler.ts`) |
| `src/components/inline-error/inline-error.{ts,html}` (fan, used twice on the dashboard) | `error.message` (or `String(error)`) as a detail line under the caller's i18n message; English-only Retry |
| `src/services/stripe-service.ts:152,164,200,239` (fan, checkout and lottery entry) | the card payment form's `error.message`, falling back to fixed Japanese literals |

Every other organizer console screen already shows i18n keys chosen from the code (for example `firstComeEditor.rejected` for FailedPrecondition, `event.publishFailed` otherwise) and logs the error. Every other fan screen already shows catalog keys (checkout and lottery entry `message` keys, discovery and My Artists snackbars). The reception app shows only fixed copy. The four bootstrap error pages (`src/main.ts`, `{admin,organizer,reception}/main.ts`) add the error text only when `import.meta.env.DEV` is true, which is false in every deployed build.

What the server can send, from backend `origin/main`:

- Organizer Delete FailedPrecondition: not deactivated, an Order that is not refunded, a Settlement that is not reversed, a payout account (`internal/infrastructure/database/rdb/organizer_repo.go:484-500`). The screen offers Delete only for a deactivated Organizer and no operation reactivates one, so the first cannot reach the screen.
- Organizer Create InvalidArgument: entity validation (`organizer_uc.go:240`), which the screen's `createFormError` mirrors (name length, short name rule and reserved names, email shape), or the sign-in service rejecting the owner email (`zitadel/organization_repository.go:608`). After the screen's checks pass, only the second remains in practice.
- Organizer Create AlreadyExists: the short name is used (spec `usecase/organizer/create`); FailedPrecondition can come from provisioning, which today shows the wrong "deactivated" copy.
- ConcertCandidate Approve and Reject, admin Concert Delete: InvalidArgument only for ids the screen did not type, and a Reject reason the screen already requires.

## Goals / Non-Goals

**Goals:** no server or library text on any admin console, organizer console or fan app screen in a deployed build; each screen keeps saying which operation failed.

**Non-Goals:**

- Proto `ErrorInfo` reasons or any backend change (owner decision 2026-10-19). A refused Delete names all three blockers instead.
- go-apperr's `(code)` suffix.
- The dev-only bootstrap detail: it is not in deployed builds and helps local debugging. The fan app-shell requirement "Bootstrap failures SHALL surface a static error page" already limits the underlying message to non-production environments.
- The fan error banner's copied details and GitHub report: the fan starts them and they are diagnostics, so they keep the error's message (sanitized as today).
- The reception app: nothing to change.

## Decisions

### D1. One copy function per console, from code and operation

Admin: move `toUserMessage` to `admin/services/error-message.ts` as `toUserMessage(err, fallback, overrides?: Partial<Record<Code, string>>)`. It returns `overrides[code]` when given, `Your session expired — signing you back in…` for Unauthenticated, and `fallback` for everything else, including non-Connect errors. It never reads `rawMessage` or `message`. The Organizers screen keeps its own defaults in `admin/organizers/organizer-error-message.ts` as a thin wrapper: NotFound `The organizer or artist no longer exists.`, FailedPrecondition `This organizer is deactivated and can no longer be changed.`, AlreadyExists `That artist is already represented by an organizer.`, InvalidArgument `The request was invalid. Check the fields.`. The approval queue and the published concerts screen call the shared function with their existing fallbacks.

Organizer: no shared function is needed; screens already pick i18n keys from the code. `toOrganizerErrorMessage` is deleted with its test because it is unused and its fallbacks are the anti-pattern; `find-organizer-route.ts` imports `Code` and `ConnectError` from `@connectrpc/connect`.

Alternative: one helper in `shared/` for both consoles. Rejected: admin copy is English literals and organizer copy is i18n keys, so the shared part would be a single `switch` on Unauthenticated.

### D2. Copy per admin screen and code

| Screen, operation | AlreadyExists | NotFound | FailedPrecondition | InvalidArgument | Unauthenticated | anything else, no code |
|---|---|---|---|---|---|---|
| Organizers, load list / roster / search | — | — | — | — | session copy | `Failed to load organizers.` / `Failed to load the roster.` / `Artist search failed.` |
| Organizers, Create | `That short name is already used by another organizer. Choose a different one.` | — | `Failed to create the organizer.` | `The sign-in service did not accept this owner email. Check it or use a different address.` | session copy | `Failed to create the organizer.` |
| Organizers, Deactivate | — | no longer exists | deactivated copy | fixed invalid copy | session copy | `Failed to deactivate the organizer.` |
| Organizers, Delete | — | no longer exists | `This organizer cannot be deleted while it has an order that is not refunded, a settlement that is not reversed, or a payout account.` | fixed invalid copy | session copy | `Failed to delete the organizer.` |
| Organizers, Associate / Remove artist | `That artist is already represented by an organizer.` | no longer exists | deactivated copy | fixed invalid copy | session copy | `Failed to associate the artist.` / `Failed to remove the artist.` |
| Commercial terms, load / business details / fee rate | — | no longer exists | deactivated copy | `The request was invalid. Check the fields.` | session copy | existing `Failed to …` copy |
| Approval queue, load / Approve / conflict resolution / Reject | — | — | — | — | session copy | `Failed to load the approval queue.` / `Approval failed. Try again.` / `Reconciliation failed. Try again.` / `Rejection failed. Try again.` |
| Published concerts, load / Delete | — | — | — | — | session copy | `Failed to load published concerts.` / `Delete failed. Try again.` |
| Sign-in callback | | | | | | `Sign-in failed. Return to the console and sign in again.` |

"—" means the code falls into the last column. The Delete refusal text is the owner's wording. On the commercial-terms forms the screen checks every field first, so a server InvalidArgument means the screen's checks and the server's rules disagree; the fixed copy plus the logged message is enough to find that.

### D2b. Fan app copy

New catalog keys in `src/locales/{ja,en}/translation.json` (English in parentheses):

- Sign-in callback: `authCallback.verifying` 認証を確認しています… (Verifying sign-in…), `authCallback.failed` サインインできませんでした。ホームに戻って、もう一度お試しください。 (Could not sign in. Return home and try again.), `authCallback.home` ホームに戻る (Return home). The route keeps a boolean failure flag instead of a message.
- Error banner: `errorBanner.title` 問題が発生しました (Something went wrong), `errorBanner.message` 予期しないエラーが発生しました。ページを再読み込みしてください。 (An unexpected error occurred. Reload the page.), and labels `errorBanner.copy`, `errorBanner.report`, `errorBanner.dismiss`, `errorBanner.reload`. The banner is fed only by errors no screen handled, so there is no code or operation to choose from: one fixed message is the honest copy.
- Inline error: the detail line and the `errorMessage` getter are removed; the caller's `message` stays (the dashboard passes `dashboard.error.load`); Retry uses `common.retry` 再試行 (Retry).
- Card payment (`stripe-service.ts` returns a catalog key instead of a message): the payment form's error type `validation_error` gives `payment.error.cardDetails` カード情報を確認してください。 (Check the card details.); `card_error` (declines and failed issuer authentication) gives `payment.error.declined` カードを利用できませんでした。 (The card could not be used.); any other type, no error object, or an authorization not left in `requires_capture` gives `payment.error.failed` カードを確認できませんでした。もう一度お試しください。 (The card could not be checked. Try again.). The checkout keeps its `checkout.payment.tryAnother` hint after the copy. The service still logs the error type and code.

Considered and rejected: showing the payment form's own message for `card_error` and `validation_error`. The payment provider's API reference says "For card errors, these messages can be shown to your users" (docs.stripe.com/api/errors, attribute `message`), and the message names the decline reason (insufficient funds, expired card). It is rejected because it follows the browser's language rather than the fan's chosen one (the card form is created without a `locale` in `stripe-service.ts`), it is text the app does not own (the owner's rule), and the card form already shows its own field errors inside its frame. If the owner wants decline reasons, the simple follow-up is copy per `decline_code` in the catalog.

### D3. Where the general rule is specified

A new `components/infrastructure/<audience>/web/global/error-messages` per app (admin, organizer, fan). The project context defines `global/<surface>` as "a surface shared by screens" and already uses it for cross-screen rules such as i18n; the schema writes a contract several audiences rely on under each audience. The organizer snack-bar spec does not fit alone because the rule also covers inline form messages and the sign-in callback page, and the admin console has no shared surface spec yet. The admin approval queue and published concerts route specs need no delta: their requirements do not mention failure copy, and the global rule covers them. For the fan app the existing `global/error-banner` spec owns the banner, so its fixed copy is an ADDED requirement there; the existing "Error Banner UI in Root Component" requirement already asks for "a user-friendly error message" and stays as it is (MODIFYING it would only restate it, and would put its six untested scenarios under the archive coverage check). The fan checkout's "Card declined" scenario ("the screen says the card could not be used") already matches the new copy, so the checkout and lottery entry route specs need no delta; the card payment rule is in the fan global spec because both screens share it.

### D4. Information that fixed copy would lose

- Delete refusal: the screen no longer says which blocker applies. Accepted by the owner; the admin finds the blocker in the console log or by a read-only query.
- Create InvalidArgument: covered by the screen-specific owner-email copy, since the screen's checks leave only that cause.
- Commercial-terms InvalidArgument: no loss in practice (the screen checks every field), see D2.
- Approval queue, published concerts: their InvalidArgument causes are ids the admin did not type, so nothing the admin can act on is lost.
- Fan card payment: the decline reason is no longer shown (D2b, rejected alternative).
- Fan error banner and inline error: the developer text leaves the screen but stays in the copied details, the report and the console log.

## Risks / Trade-offs

- [The screen's Create checks drift from the server's validation, so an InvalidArgument names the owner email when the name was the problem] → the error and its message are in the console log; the Create checks share `isOrganizerShortName` with the rest of the frontend, and drift is fixed in the checks.
- [A new FailedPrecondition cause for Delete appears in the backend] → the fixed copy would not name it; the change adding it updates this copy.

## Migration Plan

Frontend PR only; a release deploys the fan app and both consoles. Rollback is a revert. No proto release, no backend release.

## Verification without a test

The prod check by the owner (task 4.1) is a confirmation, not a substitute: every ADDED and MODIFIED scenario has a unit test.
