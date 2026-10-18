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

Every other organizer console screen already shows i18n keys chosen from the code (for example `firstComeEditor.rejected` for FailedPrecondition, `event.publishFailed` otherwise) and logs the error. The reception app shows only fixed copy. The three bootstrap error pages (`{admin,organizer,reception}/main.ts`) add the error text only when `import.meta.env.DEV` is true, which is false in every deployed build.

What the server can send, from backend `origin/main`:

- Organizer Delete FailedPrecondition: not deactivated, an Order that is not refunded, a Settlement that is not reversed, a payout account (`internal/infrastructure/database/rdb/organizer_repo.go:484-500`). The screen offers Delete only for a deactivated Organizer and no operation reactivates one, so the first cannot reach the screen.
- Organizer Create InvalidArgument: entity validation (`organizer_uc.go:240`), which the screen's `createFormError` mirrors (name length, short name rule and reserved names, email shape), or the sign-in service rejecting the owner email (`zitadel/organization_repository.go:608`). After the screen's checks pass, only the second remains in practice.
- Organizer Create AlreadyExists: the short name is used (spec `usecase/organizer/create`); FailedPrecondition can come from provisioning, which today shows the wrong "deactivated" copy.
- ConcertCandidate Approve and Reject, admin Concert Delete: InvalidArgument only for ids the screen did not type, and a Reject reason the screen already requires.

## Goals / Non-Goals

**Goals:** no server or library text on any admin or organizer console screen in a deployed build; each screen keeps saying which operation failed.

**Non-Goals:**

- Proto `ErrorInfo` reasons or any backend change (owner decision 2026-10-19). A refused Delete names all three blockers instead.
- go-apperr's `(code)` suffix.
- The fan app. Its sign-in callback (`src/routes/auth-callback/auth-callback-route.ts:173`) and its error banner (`src/components/error-banner/error-banner.html:6`) still show library text; this contradicts the premise that the fan app already works this way, and is left for a follow-up.
- The dev-only bootstrap detail: it is not in deployed builds and helps local debugging.
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

### D3. Where the general rule is specified

A new `components/infrastructure/<audience>/web/global/error-messages` per console. The project context defines `global/<surface>` as "a surface shared by screens" and already uses it for cross-screen rules such as i18n; the schema writes a contract several audiences rely on under each audience. The organizer snack-bar spec does not fit alone because the rule also covers inline form messages and the sign-in callback page, and the admin console has no shared surface spec yet. The admin approval queue and published concerts route specs need no delta: their requirements do not mention failure copy, and the global rule covers them.

### D4. Information that fixed copy would lose

- Delete refusal: the screen no longer says which blocker applies. Accepted by the owner; the admin finds the blocker in the console log or by a read-only query.
- Create InvalidArgument: covered by the screen-specific owner-email copy, since the screen's checks leave only that cause.
- Commercial-terms InvalidArgument: no loss in practice (the screen checks every field), see D2.
- Approval queue, published concerts: their InvalidArgument causes are ids the admin did not type, so nothing the admin can act on is lost.

## Risks / Trade-offs

- [The screen's Create checks drift from the server's validation, so an InvalidArgument names the owner email when the name was the problem] → the error and its message are in the console log; the Create checks share `isOrganizerShortName` with the rest of the frontend, and drift is fixed in the checks.
- [A new FailedPrecondition cause for Delete appears in the backend] → the fixed copy would not name it; the change adding it updates this copy.

## Migration Plan

Frontend PR only; merges deploy both consoles. Rollback is a revert. No proto release, no backend release.

## Verification without a test

The prod check by the owner (tasks 3.1) is a confirmation, not a substitute: every ADDED and MODIFIED scenario has a unit test.
