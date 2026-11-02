## 1. Prerequisite

- [ ] 1.1 Confirm the backend release of `publish-events-through-outbox` (archived) is in production: verify that the backend image running in prod (`kubectl get deploy -n backend -o wide`) is a release that contains its implementation PRs

## 2. specification: proto and analytics catalogue

- [ ] 2.1 Add `HypeSetBy` and `Follow.hype_set_by = 4` to `entity/v1/follow.proto`, and `TicketJourneyStatusSetBy` and `TicketJourney.status_set_by = 4` to `entity/v1/ticket_journey.proto`, as in design "Proto: the entity messages carry who set the value"; verify `buf lint`, `buf format -d` and `buf breaking` pass
- [ ] 2.2 Add `rpc InferTracking(InferTrackingRequest) returns (InferTrackingResponse)` to `rpc/ticket_journey/v1/ticket_journey_service.proto` (required `event_id`, `bool started`) with doc comments; verify `buf lint` and `buf breaking` pass and `make words` passes
- [ ] 2.3 Update the doc comments of `UserService.Create` and `CreateRequest.home`: a new identity needs a home, and Create without one returns an existing User or fails with FailedPrecondition; verify `buf lint` passes and the field stays optional (`buf breaking` passes)
- [ ] 2.4 Document the `set_by` property on `artist.hype.changed` and `ticket.journey.status.changed` in `docs/analytics/event-catalog.md`; verify the catalogue lists its values (default, fan, inference / fan, platform, inference)
- [ ] 2.5 Open the specification PR, merge it, cut the release and confirm `buf-release.yml` succeeds (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 3. cloud-provisioning: the consumer of new lottery entries (design "Platform writes come from announcements")

- [ ] 3.1 Add `consumer-mark-ticket-journey-applied.yaml` (`filterSubject: ORDER.lottery_entry_entered`, the same settings as `consumer-mark-ticket-journey-paid.yaml`) to the JetStream kustomization; verify `kustomize build` of the prod overlay lists it, merge, and after ArgoCD syncs prod confirm read-only that the consumer exists on the `ORDER` stream

## 4. backend: schema (design "Storage")

- [ ] 4.1 Add `hype_set_by` and `status_set_by` with their CHECK constraints and `COMMENT ON COLUMN` to `schema.sql`, generate the Atlas migration with the backfill (`'fan'` where `hype <> 'nearby'`, else `'default'`; every journey `'fan'`); verify `make lint-schema` passes and `atlas migrate apply --env local` on a copy with sample rows leaves the backfilled values

## 5. backend: entity (components/entity/follow, components/entity/ticket-journey, components/entity/user)

- [ ] 5.1 Add `HypeSetBy` and `TicketJourneySetBy` with their validation, `Follow.HypeSetBy`, `TicketJourney.StatusSetBy`, and the `internal/adapter/pb` conversions for the new proto fields; verify unit tests for each value and the round trip through the proto message
- [ ] 5.2 Implement `Hype.IsAbove`, `LowestHypeMatching` and `(*Follow).RaisableTo` beside `MatchingConcerts`; verify one table-test case per scenario of "A new Follow starts at Nearby", "The lowest hype level that matches a concert" and "The app may raise only a hype level the fan did not set"
- [ ] 5.3 Implement `(*TicketJourney).ReplaceableBy(status, setBy)` (a nil journey is replaceable); verify one table-test case per scenario of "Which journeys the platform and the app may replace", plus Applied by the platform over Tracking and Applied (replaceable) and over Unpaid (not replaceable)

## 6. backend: entity operations

- [ ] 6.1 `Follow.Follow` stores `hype_set_by = 'default'`; verify the contract tests for every scenario of `entity/follow/follow`
- [ ] 6.2 `Follow.SetHype` stores `'fan'`, changes and announces when only who set it changes, and puts `hype_set_by` in the announced Follow; verify the contract tests for every scenario of `entity/follow/set-hype`, including "Fan picks the default level" with one outbox row
- [ ] 6.3 Add `Follow.RaiseHype` (`SELECT ... FOR UPDATE`, `RaisableTo`, `UPDATE`, announcement in one transaction) to the follow repository interface and implementation; verify the contract tests for every scenario of `entity/follow/raise-hype`, with "Fan sets the level at the same time" run as two concurrent transactions
- [ ] 6.4 `Follow.ListByUser` returns `hype_set_by`; verify the contract tests for every scenario of `entity/follow/list-by-user`
- [ ] 6.5 `TicketJourney.Upsert` takes and stores the status set by, and announces when only it changes; verify the contract tests for every scenario of `entity/ticket-journey/upsert`
- [ ] 6.6 Add `TicketJourney.UpsertIfReplaceable` (`INSERT ... ON CONFLICT DO NOTHING`, else `SELECT ... FOR UPDATE`, `ReplaceableBy`, `UPDATE`; announcement only when stored; returns whether it stored) as in design "`TicketJourney.UpsertIfReplaceable`"; verify the contract tests for every scenario of `entity/ticket-journey/upsert-if-replaceable`, with "Fan writes at the same moment" run as two concurrent transactions
- [ ] 6.7 `LotteryEntry.Create` records `ORDER.lottery_entry_entered` with the Pending Order in its transaction, only for a new entry; add the subject to `AllSubjects`; verify the contract tests for every scenario of "A new entry is announced with it" in `entity/lottery-entry/create`, and that the stream-match test of the outbox change finds the `ORDER` stream for the subject

## 7. backend: usecases

- [ ] 7.1 Add the unexported `raiseHypeToMatch` helper of design "Raising the hype level" (log and swallow every failure; skip a User without a home); verify unit tests with the operations mocked for a raise, a fan-set level, an already matched concert, two followed performers, a User without a home, a non-concert event and each failing step
- [ ] 7.2 `FollowUseCase.SetHype` passes set by fan; verify one unit test per scenario of `usecase/follow/set-hype`
- [ ] 7.3 `TicketJourneyUseCase.SetStatus` records set by fan and calls the helper for Applied, Unpaid and Paid; verify one unit test per scenario of `usecase/ticket-journey/set-status`
- [ ] 7.4 `TicketJourneyUseCase.MarkPaid` records set by platform and calls the helper; verify one unit test per scenario of `usecase/ticket-journey/mark-paid`
- [ ] 7.5 Add `TicketJourneyUseCase.InferTracking` over `TicketJourney.UpsertIfReplaceable`; verify one unit test per scenario of `usecase/ticket-journey/infer-tracking`
- [ ] 7.6 Add `TicketJourneyUseCase.MarkApplied` (`LotteryEntry.Get`, nothing unless the entry is Entered; UpsertIfReplaceable with Applied set by platform; the helper only when stored) and its consumer of `ORDER.lottery_entry_entered` in `event-consumer`, reading the event of the Order's TicketStock as the MarkPaid consumer does; verify one unit test per scenario of `usecase/ticket-journey/mark-applied` and a consumer test that a failed UpsertIfReplaceable nacks the message

## 8. backend: RPC, analytics and release

- [ ] 8.1 Upgrade the generated package from BSR, add the `InferTracking` handler (signed-in fan, request validation, `started` in the response) and register it; verify handler tests for every scenario of `adapter/fan/api/rpc/ticket-journey`
- [ ] 8.2 The analytics consumer adds `set_by` to `artist.hype.changed` and `ticket.journey.status.changed` from the payload; verify unit tests for each value
- [ ] 8.3 Run `make check`, open the backend PR (OpenSpec Traceability filled), merge, release; confirm read-only in prod that the AtlasMigration applied, `followed_artists.hype_set_by` and `ticket_journeys.status_set_by` hold the backfilled values, and a hype change made in prod reaches product analytics with `set_by = fan`
- [ ] 8.4 Run `gh workflow run stripe-sandbox-e2e.yml` in backend and confirm the lottery leg shows the entering fan's journey Applied set by the platform after the entry is announced, then Paid set by the platform after the win (covers `stories/win-tickets-in-a-lottery` "An entry marks the fan's journey Applied")

## 9. frontend: home at sign-up (stories/sign-up-or-sign-in, global/user-home-selector)

- [ ] 9.1 The auth callback, on FailedPrecondition from `UserService.Create`, opens the `user-home-selector` with `required`, calls Create again with the chosen home and continues to the return URL; the Dashboard no longer opens the home sheet for a signed-in fan; verify component tests for every scenario of "Every sign-in resolves the account with Create" and "The home sheet at sign-up cannot be closed"
- [ ] 9.2 The Playwright sign-up helpers choose a home when the sheet opens; add an E2E test for "Sign-up from the event page without a home" (the backend returns FailedPrecondition only after group 14, so the test stubs that `UserService.Create` response); verify both pass against a local build

## 10. frontend: guest hype (stories/merge-guest-data-on-signup)

- [ ] 10.1 Guest follow entries carry `hypeSetBy`; a guest hype change sets `'fan'`; legacy entries are read as in design "Guest storage"; the merge calls `FollowService.SetHype` for every entry set by the fan; verify unit tests for every modified scenario of "Guest Data Storage" and "Data Merge on Authentication", including "Guest's chosen Nearby is kept as the fan's choice"

## 11. frontend: event detail sheet (components/infrastructure/fan/web/global/event-detail-sheet)

- [ ] 11.1 Upgrade the generated package; add `InferTracking` to the ticket journey client and store (sets Tracking on `started`); the calendar link calls it for a signed-in fan with no journey, then shows the snack on return as in design "The calendar snack waits for the fan to come back", with 「取り消す」 deleting the journey; verify component tests for every scenario of "Adding to the calendar starts tracking"
- [ ] 11.2 After a saved Applied, Unpaid or Paid on a card that was not matched, the sheet re-reads `FollowService.List` (bypassing the session cache), and on a raised level shows the snack whose 「取り消す」 calls `FollowService.SetHype(previous)`; verify component tests for every scenario of "A hype level raised by a journey change is shown with undo"
- [ ] 11.3 Add the ja and en copy for both snacks to `locales/*/translation.json`; verify the i18n key test passes in both locales
- [ ] 11.4 Run a local build in Playwright: a signed-in fan adds a concert to the calendar, comes back, sees the snack and undoes it; then saves Applied for an away-lane concert of an artist at the default level and sees the raise snack and the highlighted card; verify both flows pass

## 12. frontend: wording (route/dashboard, global/live-highway, stories/set-hype-for-an-artist)

- [ ] 12.1 Update the `@spec` annotations of the existing tests to the renamed requirement "Concerts the fan's hype level matches are highlighted", the replaced live-highway requirements ("Dashboard cards show whether the hype level matches the concert", "Artist name shown on every card", "Artist name larger than the location label"), the set-hype requirements, and "Post-signup dialog opens after the celebration" of `global/post-signup-dialog`; verify `scripts/check-scenario-coverage.py` finds a test for each modified scenario

## 13. Stories and frontend release

- [ ] 13.1 Add the E2E tests for `stories/track-ticket-journey` ("Adding a concert to the calendar starts tracking it", "A journey for a distant concert raises the artist's hype level") and `stories/set-hype-for-an-artist` ("The app never changes a hype level the fan set"); verify they pass against a local build
- [ ] 13.2 Run `make check`, open the frontend PR (OpenSpec Traceability filled), merge, release; confirm in prod (the owner's account) that a calendar add shows Tracking with the snack, and that `ticket_journeys.status_set_by` holds `inference` for it (read-only)

## 14. backend: home required (design "Every User has a home"; after the frontend release of group 13)

- [ ] 14.1 Count read-only in prod the `users` rows with no home; sign in to each such account and set a home in Settings, or delete it; verify the count is 0
- [ ] 14.2 `User.Create` fails with InvalidArgument without a Home; verify the contract tests for every scenario of "Create stores the user and its home together" in `entity/user/create`
- [ ] 14.3 `UserUseCase.Create` without a Home returns the identity's existing User or fails with FailedPrecondition; verify one unit test per scenario of "A new identity is registered" in `usecase/user/create`
- [ ] 14.4 Make `users.home_id` NOT NULL and change `fk_users_home_id` to `ON DELETE RESTRICT` in `schema.sql`, update its `COMMENT ON COLUMN`, and generate the Atlas migration; verify `make lint-schema` passes and `atlas migrate apply --env local` fails on a copy with a row without a home and succeeds without one
- [ ] 14.5 Run `make check`, open the second backend PR (OpenSpec Traceability filled), merge, release; confirm read-only in prod that the AtlasMigration applied and `users.home_id` is NOT NULL, and that the owner's sign-up of a new test identity from an event page asks for the home and creates the account with it

## 15. Follow-ups

- [ ] 15.1 File issues for: a lost lottery entry recording the journey Lost (after `make-lottery-draw-durable`); showing the effect of hype outside the help sheet; asking about the journey when the fan returns from the official site; the journey of a fan who resells their tickets; verify each issue exists and is linked from this change's proposal
