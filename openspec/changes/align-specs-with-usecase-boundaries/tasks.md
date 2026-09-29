# Tasks

Every test named below is in liverty-music/backend. Mark each test with `// @spec <capability-path> "<scenario name>"`, spelled exactly as the scenario is written.

## 1. Usecase removal (components/usecase/organizer/get-by-zitadel-org-id)

- [ ] 1.1 Delete `GetByZitadelOrgID` from the `OrganizerUseCase` interface and from `organizerUseCase` in `internal/usecase/organizer_uc.go`. Keep the entity operation `entity.OrganizerRepository.GetByZitadelOrgID` and its rdb implementation, which `ResolveCaller` and the onboarding test stub still use. Regenerate the mocks with mockery. Update the comment in `internal/infrastructure/auth/org_scoped.go` that names `GetByZitadelOrgID` so it names `OrganizerUseCase.ResolveCaller`. Verify that `grep -rn "organizerUC.GetByZitadelOrgID\|OrganizerUseCase.GetByZitadelOrgID" internal` finds nothing and that `make check` passes.

## 2. Usecase (components/usecase/concert/search-new-concerts-on-first-follow)

- [ ] 2.1 Annotate the existing tests and verify they pass:
  - `internal/adapter/event/follow_search_consumer_test.go` `TestFollowSearchConsumer_Handle/"delegates to SearchNewConcertsOnFirstFollow"` → "Follow announced".
  - `internal/usecase/concert_uc_test.go` `TestConcertUseCase_SearchNewConcertsOnFirstFollow`:
    - "first follow - never searched, triggers discovery" → "Artist never searched".
    - "already searched - no-op" → "Artist searched before".
    - "search log lookup fails - returns error" → "Search history unreadable".
- [ ] 2.2 Add a case "search fails - returns error" to `TestConcertUseCase_SearchNewConcertsOnFirstFollow`, where the SearchLog is NotFound and the searcher fails. It must assert that `SearchNewConcertsOnFirstFollow` returns an error. Annotate it "Search fails" and verify it passes.

## 3. Usecase (components/usecase/follow/follow)

- [ ] 3.1 Annotate `internal/usecase/follow_uc_test.go` `TestFollowUseCase_Follow_PublishesAnalyticsEvent/"publishes ARTIST.followed on first follow"` → "New follow announced". Add a case "tolerates publisher failure (non-fatal)" to the same test: publishing ARTIST.followed fails, and `Follow` returns nil. Annotate it "Announcement fails" and verify both pass.

## 4. Usecase (components/usecase/notification/deliver)

- [ ] 4.1 Annotate `internal/adapter/event/deliver_notification_consumer_test.go` `TestDeliverNotificationConsumer_Handle`:
  - "delegates to NotificationUseCase.Deliver" → "Notification requested".
  - "returns error when Deliver fails" → "Recording fails for one request".
  Verify both pass.
- [ ] 4.2 Annotate the existing tests in `internal/usecase/notification_uc_test.go` and verify they pass:
  - `TestDeliver_NilPayloadRejected` → "Missing message".
  - `TestDeliver_RecordFailureDoesNotSend` → "Recording fails".
  - `TestDeliver_Success` → "Message identifies its notification" and "Delivered".
  - `TestDeliver_NoSubscriptionRecordedAsFailed` → "No browser registered".
  - `TestDeliver_SendFailureRecordedAsFailed` → "Every send fails", "Delivery failed" and "Failed". For "Failed", add an assertion that no NOTIFICATION.delivered event is published.
  - `TestDeliver_GoneSubscriptionCleanedUpAndFailed` → "Browser gone".
- [ ] 4.3 Add tests to `internal/usecase/notification_uc_test.go`, annotate them and verify they pass:
  - `TestDeliver_OneOfTwoBrowsersAccepts`: two subscriptions, one send fails and one is accepted; the outcome is Delivered. → "One of two browsers accepts".
  - `TestDeliver_CancelledAfterOneAcceptedSend`: three subscriptions, and the context is cancelled after the first send is accepted; exactly one Send happens and the outcome is Delivered. → "Cancelled after one accepted send".
  - `TestDeliver_UpdateDeliveryFailureIsNonFatal`: UpdateDelivery fails after an accepted send; Deliver returns the Notification as Delivered with no error. → "Outcome cannot be stored".

## 5. Usecase (components/usecase/notification/notify-new-concerts)

- [ ] 5.1 In `internal/usecase/push_notification_uc_test.go` `TestPushNotificationUseCase_NotifyNewConcerts`, add a case with three matched AWAY followers that asserts one `PublishEventWithID` to NOTIFICATION.requested per follower, each carrying that follower's user id and the new_concerts type. Annotate it "Every matched follower is requested".
- [ ] 5.2 Extend the case "return error when publishing the notification request fails" to three matched followers, where the second publish fails. Assert that the third publish never happens and that an error is returned. Annotate it "Request fails for one follower".
- [ ] 5.3 Add `TestNotifyNewConcerts_RequestIDIsDeterministic` to `internal/usecase/notification_delivery_test.go`, mirroring `TestAnnounceDiscoveredPhase_RequestIDIsDeterministic`: running twice for the same artist, concerts and follower derives the same id, and a different follower derives a different id. Annotate it "Same concerts notified twice".
- [ ] 5.4 Verify tasks 5.1 to 5.3 pass.

## 6. Usecase (components/usecase/sales-phase/announce-discovered-phase)

- [ ] 6.1 Annotate and verify these tests pass:
  - `internal/usecase/sales_phase_announcement_uc_test.go` `TestAnnounceDiscoveredPhase_LocalizesCopyPerRecipient` → "Two recipients". It publishes one request per tracking fan.
  - `internal/usecase/notification_delivery_test.go` `TestAnnounceDiscoveredPhase_RequestIDIsDeterministic` → "Same phase announced twice".
- [ ] 6.2 Extend `TestAnnounceDiscoveredPhase_PublishError_PropagatesAndAborts` to three recipients, where the second publish fails. Assert that the third publish never happens and that an error is returned. Annotate it "Request fails" and verify it passes.

## 7. Usecase (components/usecase/organizer/resolve-caller)

- [ ] 7.1 Annotate the cases of `internal/usecase/organizer_uc_test.go` `TestOrganizerUseCase_ResolveCaller` and verify they pass:
  - "return the organizer when active" → "Active Organizer".
  - "PermissionDenied (non-revealing) when no organizer is linked" → "Tenant with no Organizer".
  - "PermissionDenied when the organizer is still provisioning" → "Provisioning Organizer".
  - "FailedPrecondition when the organizer is deactivated" → "Deactivated Organizer".
  - "propagates a non-NotFound repository failure unchanged" → "Organizer unreadable".

## 8. Usecase (components/usecase/organizer/list-own-artists)

- [ ] 8.1 Annotate the cases of `internal/usecase/organizer_uc_test.go` `TestOrganizerUseCase_ListOwnArtists` and verify they pass:
  - "return own roster when reqOrganizerID matches the caller" → "Own roster".
  - "PermissionDenied when reqOrganizerID does not match the caller" → "Another Organizer's roster".
  - "NotFound when the caller's own organizer no longer exists" → "Own Organizer gone".

## 9. Usecase (components/usecase/user/resolve-caller)

- [ ] 9.1 Annotate the cases of `internal/usecase/user_uc_test.go` `TestUserUseCase_ResolveCaller` and verify they pass:
  - "success — reqUserID matches the caller's own id" → "Own account".
  - "PermissionDenied — reqUserID does not match the caller's own id" → "Another user's account".
  - "InvalidArgument — reqUserID is empty" → "Missing user id".
  - "NotFound — no user exists for externalID" → "Caller has no account".

## 10. Usecase (components/usecase/user/resend-email-verification)

- [ ] 10.1 Annotate the cases of `internal/usecase/user_uc_test.go` `TestUserUseCase_ResendEmailVerification` and verify they pass:
  - "success — sends the verification email" → "Caller resends their own email".
  - "PermissionDenied — reqUserID does not match the caller's own id" → "Another user's account".
  - "FailedPrecondition — email already verified propagates from the verifier" → "Already verified".
  - "Unavailable — email verifier is not configured (nil)" → "Verification unavailable". Confirm that the case sets no user-repository expectation, so it holds even when the caller has no User.
  - "ResourceExhausted — 4th request within the 10-minute window is rate-limited" → "Too many requests".
  - "rate limit is scoped per user" → "Limit is per user".
- [ ] 10.2 Add a case "failed attempts count toward the limit" to the same test: three requests fail with FailedPrecondition from the verifier, and the fourth fails with ResourceExhausted without calling the verifier. Annotate it "Failed attempts count" and verify it passes.

## 11. Adapter (components/adapter/organizer/api/rpc/organizer)

- [ ] 11.1 Annotate the cases in `internal/adapter/rpc/organizer_handler_test.go` and verify they pass:
  - `TestOrganizerHandler_Get`:
    - "return PERMISSION_DENIED when no organizer linked to zitadel org" → "Tenant with no Organizer".
    - "return PERMISSION_DENIED when organizer is in provisioning status" → "Provisioning Organizer".
    - "return FAILED_PRECONDITION when own organizer is deactivated" → "Deactivated Organizer".
  - `TestOrganizerHandler_ListArtists`:
    - "return own roster ascending by artist id" and "return empty roster when organizer represents no artists" → "Operator lists their own roster".
    - "return PERMISSION_DENIED when organizer_id does not match caller's organizer" → "Another Organizer's roster".
- [ ] 11.2 Add a test that sends ListArtists through the protovalidate interceptor without an organizer_id and with a malformed one, and asserts InvalidArgument. Put it next to the existing interceptor or handler tests. Annotate it "Missing or malformed OrganizerId" and verify it passes.

## 12. Adapter (components/adapter/organizer/api/rpc/lottery)

- [ ] 12.1 Annotate the cases of `internal/adapter/rpc/organizer_lottery_handler_test.go` `TestOrganizerLotteryHandler_ConfigureLotteryPhase` and verify they pass:
  - "success: returns created phase" → "Active Organizer configures a phase".
  - "error: organizer not found returns PermissionDenied" → "Tenant with no Organizer".
  - "error: deactivated organizer returns FailedPrecondition" → "Deactivated Organizer".

## 13. Adapter (components/adapter/organizer/api/rpc/payout-onboarding)

- [ ] 13.1 Annotate the sign-in cases and verify they pass:
  - `internal/infrastructure/auth/authn_test.go` "return unauthenticated error when Authorization header is missing" → "Not signed in".
  - `internal/infrastructure/auth/org_scoped_test.go` "deny when multiple login-scope orgs are present (ambiguous)" → "Roles in several tenants".
- [ ] 13.2 Create `internal/adapter/rpc/payout_onboarding_handler_test.go`. In it, GetPayoutOnboarding with a mocked `OrganizerUseCase.ResolveCaller` must return PermissionDenied ("Tenant with no Organizer") and FailedPrecondition ("Deactivated Organizer") unchanged, without calling the onboarding usecase. Annotate both cases and verify they pass.

## 14. Adapter (components/adapter/organizer/api/rpc/concert)

- [ ] 14.1 Create `internal/adapter/rpc/organizer_concert_handler_test.go`. Annotate each case and verify they pass:
  - List with an active Organizer from `ResolveCaller` returns that Organizer's concerts → "Operator of an active Organizer lists concerts".
  - PermissionDenied from `ResolveCaller` is returned unchanged and the authoring usecase is not called → "Provisioning Organizer".
  - FailedPrecondition from `ResolveCaller` is returned unchanged and the authoring usecase is not called → "Deactivated Organizer".

## 15. Adapter (components/adapter/fan/api/rpc/user)

- [ ] 15.1 Annotate the cases in `internal/adapter/rpc/user_handler_test.go` and verify they pass:
  - `TestUserHandler_Get`:
    - "returns user when the use case resolves the caller" → "Own account".
    - "propagates PermissionDenied from ResolveCaller on user_id mismatch" → "Another user's account".
    - "propagates InvalidArgument from ResolveCaller when user_id is empty" → "Missing user id".
    - "returns error when user not found" → "Caller has no account".
  - `TestUserHandler_ResendEmailVerification`:
    - "delegates to the use case and returns an empty response on success" → "Caller resends their own email".
    - "propagates the use case's error unchanged" (its ResourceExhausted row) → "Usecase failure returned unchanged".

## 16. Stories (stories/follow-an-artist, stories/get-notified-of-new-concerts)

- [ ] 16.1 Run each `@spec-manual` check listed in design.md on the dev environment, after the backend PR is deployed there. Record the outcome of each in the backend PR description.

## 17. Integration

- [ ] 17.1 With backend main containing tasks 1 to 15, run `python3 scripts/check-scenario-coverage.py align-specs-with-usecase-boundaries` in the specification repository and verify it reports every scenario covered.
