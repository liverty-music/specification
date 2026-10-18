# Tasks

Frontend only; no proto or backend work. Every test task cites its scenarios with `@spec <capability-path> "<scenario>"` so `scripts/check-scenario-coverage.py` finds them at archive.

## 1. Admin console (components/infrastructure/admin/web/global/error-messages, components/infrastructure/admin/web/route/organizers)

- [ ] 1.1 Add `admin/services/error-message.ts` `toUserMessage(err, fallback, overrides?)` per design D1 (overrides, Unauthenticated session copy, otherwise the fallback; never `rawMessage` or `message`); verify unit tests for `@spec components/infrastructure/admin/web/global/error-messages "Failure without an error code"` (a `TypeError` gives the fallback) and `"Session expired during a call"` pass
- [ ] 1.2 Reduce `admin/organizers/organizer-error-message.ts` to the Organizers defaults of design D2 on top of 1.1; Delete FailedPrecondition shows the fixed three-blocker sentence; Create passes AlreadyExists, InvalidArgument (owner email) and FailedPrecondition (create fallback) overrides; verify `test/admin/organizers/organizers-route.spec.ts` tests for `@spec components/infrastructure/admin/web/route/organizers "Delete succeeds"`, `"Delete blocked by an order"` (server reason absent), `"Delete fails otherwise"`, `"Short name already used"`, `"Owner email not accepted"` and `"Create fails otherwise"` pass
- [ ] 1.3 `organizer-commercial-terms.ts` keeps its calls; verify a `test/admin/organizers/organizer-commercial-terms.spec.ts` test for `@spec components/infrastructure/admin/web/global/error-messages "Business details refused by the server"` passes (server text absent)
- [ ] 1.4 Approval queue (load, Approve, conflict resolution, Reject) and published concerts (load, Delete) call 1.1 with their existing fallbacks in place of `err.message`, keeping the logger calls; verify tests in `test/admin/approval-queue/approval-queue-route.spec.ts` for `"Server message stays off the screen"` (row copy, message absent from the DOM, logger called with the error) and in `test/admin/approved-concerts/approved-concerts-route.spec.ts` for `"Failure without an error code"` and `"Code without copy of its own"` pass, and any existing test that expected server text is rewritten
- [ ] 1.5 Admin sign-in callback shows `Sign-in failed. Return to the console and sign in again.` and the existing link; verify a test for `@spec components/infrastructure/admin/web/global/error-messages "Sign-in callback fails"` passes (library text absent)

## 2. Organizer console (components/infrastructure/organizer/web/global/error-messages)

- [ ] 2.1 Organizer sign-in callback: drop the error-detail line from the template and keep only an error flag (the state-miss self-heal keeps reading the error); verify `test/organizer/auth-callback/auth-callback-route.spec.ts` for `@spec components/infrastructure/organizer/web/global/error-messages "Sign-in callback fails"` passes
- [ ] 2.2 Delete `toOrganizerErrorMessage` and `test/organizer/services/connect-error-copy.spec.ts`; `find-organizer-route.ts` imports `Code` and `ConnectError` from `@connectrpc/connect`; update the client doc comments that point at `connect-error-copy`; verify `make check` passes and `git grep -n -E 'rawMessage|err\.message' -- admin organizer` lists only the organizer callback's state-miss check and the dev-only bootstrap detail
- [ ] 2.3 Add tests for the existing behavior: `"Refused first-come sale save"` (ticket sale editor shows `firstComeEditor.rejected`, server text absent) and `"Publish fails without copy of its own"` (event route snackbar `event.publishFailed` with Retry, server text absent); verify they pass

## 3. Release and production check

- [ ] 3.1 Open the frontend PR citing this change (`OpenSpec-Change: console-error-copy`), `make check` passes, merge, cut the release and confirm the admin and organizer console deploys succeed; then the owner opens Delete for `fan-test` on the prod admin Organizers screen (refused: it has a payout account) and confirms the detail shows the fixed three-blocker sentence with no `(failed_precondition)`; record the result here
