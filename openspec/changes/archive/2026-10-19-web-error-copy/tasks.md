# Tasks

Frontend only (admin console, organizer console, fan app); no proto or backend work. Every test task cites its scenarios with `@spec <capability-path> "<scenario>"` so `scripts/check-scenario-coverage.py` finds them at archive.

## 1. Admin console (components/infrastructure/admin/web/global/error-messages, components/infrastructure/admin/web/route/organizers)

- [x] 1.1 Add `admin/services/error-message.ts` `toUserMessage(err, fallback, overrides?)` per design D1 (overrides, Unauthenticated session copy, otherwise the fallback; never `rawMessage` or `message`); verify unit tests for `@spec components/infrastructure/admin/web/global/error-messages "Failure without an error code"` (a `TypeError` gives the fallback) and `"Session expired during a call"` pass
  - Done (2026-10-19, liverty-music/frontend#784).
- [x] 1.2 Reduce `admin/organizers/organizer-error-message.ts` to the Organizers defaults of design D2 on top of 1.1; Delete FailedPrecondition shows the fixed three-blocker sentence; Create passes AlreadyExists, InvalidArgument (owner email) and FailedPrecondition (create fallback) overrides; verify `test/admin/organizers/organizers-route.spec.ts` tests for `@spec components/infrastructure/admin/web/route/organizers "Delete succeeds"`, `"Delete blocked by an order"` (server reason absent), `"Delete fails otherwise"`, `"Short name already used"`, `"Owner email not accepted"` and `"Create fails otherwise"` pass
  - Done (2026-10-19, liverty-music/frontend#784): the artist AlreadyExists copy is an override for Associate/Remove only, per the D2 table (D1 listed it among the defaults).
- [x] 1.3 `organizer-commercial-terms.ts` keeps its calls; verify a `test/admin/organizers/organizer-commercial-terms.spec.ts` test for `@spec components/infrastructure/admin/web/global/error-messages "Business details refused by the server"` passes (server text absent)
  - Done (2026-10-19, liverty-music/frontend#784).
- [x] 1.4 Approval queue (load, Approve, conflict resolution, Reject) and published concerts (load, Delete) call 1.1 with their existing fallbacks in place of `err.message`, keeping the logger calls; verify tests in `test/admin/approval-queue/approval-queue-route.spec.ts` for `"Server message stays off the screen"` (row copy, message absent from the DOM, logger called with the error) and in `test/admin/approved-concerts/approved-concerts-route.spec.ts` for `"Failure without an error code"` and `"Code without copy of its own"` pass, and any existing test that expected server text is rewritten
  - Done (2026-10-19, liverty-music/frontend#784).
- [x] 1.5 Admin sign-in callback shows `Sign-in failed. Return to the console and sign in again.` and the existing link; verify a test for `@spec components/infrastructure/admin/web/global/error-messages "Sign-in callback fails"` passes (library text absent)
  - Done (2026-10-19, liverty-music/frontend#784).

## 2. Organizer console (components/infrastructure/organizer/web/global/error-messages)

- [x] 2.1 Organizer sign-in callback: drop the error-detail line from the template and keep only an error flag (the state-miss self-heal keeps reading the error); verify `test/organizer/auth-callback/auth-callback-route.spec.ts` for `@spec components/infrastructure/organizer/web/global/error-messages "Sign-in callback fails"` passes
  - Done (2026-10-19, liverty-music/frontend#784).
- [x] 2.2 Delete `toOrganizerErrorMessage` and `test/organizer/services/connect-error-copy.spec.ts`; `find-organizer-route.ts` imports `Code` and `ConnectError` from `@connectrpc/connect`; update the client doc comments that point at `connect-error-copy`; verify `make check` passes and `git grep -n -E 'rawMessage|err\.message' -- admin organizer` lists only the organizer callback's state-miss check and the dev-only bootstrap detail
  - Done (2026-10-19, liverty-music/frontend#784).
- [x] 2.3 Add tests for the existing behavior: `"Refused first-come sale save"` (ticket sale editor shows `firstComeEditor.rejected`, server text absent) and `"Publish fails without copy of its own"` (event route snackbar `event.publishFailed` with Retry, server text absent); verify they pass
  - Done (2026-10-19, liverty-music/frontend#784): loading the two routes in tests dropped branch coverage to 59.44% (< 60%); fixed with behaviour tests in `event-route.spec.ts` (13) and `ticket-sale-editor-route.spec.ts` (20), not by lowering the threshold; CI 61.84%.

## 3. Fan app (components/infrastructure/fan/web/global/error-messages, components/infrastructure/fan/web/global/error-banner)

- [x] 3.1 Sign-in callback: a failure flag in place of the message, the `authCallback.*` keys of design D2b for the loading text, the failure copy and the home link; verify a `test/routes/auth-callback-route.spec.ts` test for `@spec components/infrastructure/fan/web/global/error-messages "Sign-in callback fails"` passes (library text absent)
  - Done (2026-10-19, liverty-music/frontend#784).
- [x] 3.2 Error banner: title, message and button labels from the `errorBanner.*` keys, Error ID kept, `currentError.message` no longer rendered; verify `test/components/error-banner.spec.ts` tests for `@spec components/infrastructure/fan/web/global/error-banner "Unhandled error shows fixed copy"` and `"English labels"` pass, and the copied report still contains the message
  - Done (2026-10-19, liverty-music/frontend#784).
- [x] 3.3 Inline error: drop the detail line and the `errorMessage` getter, Retry from `common.retry`; verify a dashboard test for `@spec components/infrastructure/fan/web/global/error-messages "Timetable fails to load"` passes (server text absent)
  - Done (2026-10-19, liverty-music/frontend#784): the dashboard test renders the template's error block as a fixture (`test/routes/dashboard-inline-error.fixture.spec.ts`).
- [x] 3.4 Card payment: `stripe-service.ts` returns the `payment.error.*` key by error type (design D2b) and logs type and code; `checkout-route` and `lottery-entry-route` render it through the catalog; verify `src/services/stripe-service.spec.ts` and checkout tests for `"Card declined at checkout"` and `"Card details incomplete"` pass (payment form message absent), and `git grep -n -E 'rawMessage|err\.message|error\.message|String\(err' -- src admin organizer` lists no line that reaches the DOM
  - Done (2026-10-19, liverty-music/frontend#784).

## 4. Release and production check

- [x] 4.1 Open the frontend PR citing this change (`OpenSpec-Change: web-error-copy`), `make check` passes, merge, cut the release and confirm the fan app, admin console and organizer console deploys succeed; then the owner opens Delete for `fan-test` on the prod admin Organizers screen (refused: it has a payout account) and confirms the detail shows the fixed three-blocker sentence with no `(failed_precondition)`; record the result here
  - Partial (2026-10-19): liverty-music/frontend#784 merged (`b3cdb1e7`), CI green; Release v1.102.1, deploy jobs and post-deploy-smoke success. Owner's prod check (2026-10-19, admin console v1.102.1): Delete of `fan-test` showed "This organizer cannot be deleted while it has an order that is not refunded, a settlement that is not reversed, or a payout account." with no `(failed_precondition)`; the server message appeared only in the browser console log.
