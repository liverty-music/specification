## 1. Prerequisite

- [x] 1.1 Confirm `infer-hype-and-journey` is archived (its specs carry "Adding to the calendar starts tracking" and "A hype level raised by a journey change is shown with undo") and its frontend release is in production; verify with `openspec list --store openspec-store` and the frontend image running in prod (`kubectl get deploy -n frontend -o wide`)

## 2. backend: schema (design "Result date", "Result-day stage")

- [x] 2.1 Add `ticket_sales.result_date DATE` with its CHECK (discovered Lottery only, no earlier than the JST day of `sale_end_at`) and `COMMENT ON COLUMN`, widen `chk_ticket_sale_reminders_stage` to (1, 2, 4) and update the stage comment, and generate the Atlas migration; verify `make lint-schema` passes and `atlas migrate apply --env local` accepts a discovered lottery with a result date and rejects one on a first-come sale

## 3. backend: entity (components/entity/ticket-sale, components/entity/ticket-sale-reminder)

- [x] 3.1 Add `TicketSale.ResultDate` and `DiscoveredTicketSale.ResultDate` and the validation of "Only a discovered lottery has a result date"; verify one table-test case per scenario of that requirement
- [x] 3.2 Add `ReminderStageResultDay = 4` to `IsValid`, `String` and the stage anchor (09:00 on the result date in the fan's time zone, a discovered Lottery with a result date only) and its expiry (22:00 that day); verify one table-test case per scenario of "Stage values are closed" and "Stages by method"

## 4. backend: entity operations

- [x] 4.1 `TicketSale.SearchPublishedSales`: add the optional `result_date` to the Gemini response schema and prompt, parse it, and drop only the field when it is unparsable or before the end date (reported as a discard reason); verify unit tests for every scenario of "A lottery's result date is returned when the pages state it" and add result-date cases to the real-page integration test
- [x] 4.2 `TicketSale.UpsertDiscovered` stores the result date on insert, and on update takes the new one or keeps the stored one while it is no earlier than the JST day of the new end time; verify the contract tests for every scenario of `entity/ticket-sale/upsert-discovered` "Same series, method and start date is one discovered sale"
- [x] 4.3 `TicketSale.ListWithPendingMilestones` also keeps a sale whose result date is no earlier than the day before the JST day of now minus the lookback; verify the contract tests for every scenario of "Sales are selected by start time and end time"
- [x] 4.4 Add `TicketJourney.ListUserIDsAppliedSeries` to the ticket journey repository interface and implementation, beside `ListUserIDsTrackingSeries`; verify the contract tests for every scenario of `entity/ticket-journey/list-user-ids-applied-series`

## 5. backend: usecase (components/usecase/ticket-sale/scan-due-reminders)

- [x] 5.1 `ScanDueReminders` evaluates `RESULT_DAY` for a discovered Lottery with a result date, over `ListUserIDsAppliedSeries`, with the `RESULT_DAY` content rows in Japanese and English and the link to the linked event; verify one unit test per scenario of "The audience is the fans tracking or applied for the series", "Reminder content names the sale and the tour" and "A stage is requested from its due time until it expires", with the operations mocked

## 6. backend: story and release (stories/get-reminded-of-ticket-sale-milestones)

- [x] 6.1 Add a story test (in-memory push, fake clock) for every scenario of "Milestone reminders reach tracking and applied fans" and "The Organizer's own sales are reminded too" (no result-day push for an Organizer's lottery), including "Fan who has applied" receiving one 今日は抽選結果の発表日 push and "Fan still tracking on the result day" receiving none; verify it passes in backend CI
- [x] 6.2 Run `make check`, open the backend PR (OpenSpec Traceability filled), merge and release; confirm read-only in prod that the AtlasMigration applied and `ticket_sales.result_date` exists, and run the real-page eval (`GEMINI_SP_EVAL=1`, case `kinggnu`) to confirm the search returns the result dates the official pages state. (Run on 2026-11-04 at backend `origin/main` 3bd71304, one repetition: `found=2/2 wrong_or_extra=0`, result dates 2026-11-03 and 2026-12-02 as the official pages state.)

## 7. frontend: snack bar (components/infrastructure/fan/web/global/snack-bar)

- [x] 7.1 Add the `limit` bindable (3 in the fan app shell) and the `replaceKey` snack option to `<snack-bar>`, skipping snacks that do not dismiss on their own; verify component tests for every scenario of "At most three snacks are shown at once" and a story for four stacked snacks

## 8. frontend: push offer (components/infrastructure/fan/web/global/notification-prompt)

- [x] 8.1 Replace the session flag and the unanswered counter of `PushOfferService` with `pushState()` (`on`, `offerable`, `settings`) remove the counter's device key on startup, and add the `event_detail_sheet` value to `PermissionRequestSource` for offers from the event detail sheet; verify unit tests for every scenario of "Where the push offer appears", "Push offer eligibility", "Only the post-signup offer is limited", "Outcome of the browser permission prompt" and "The permission answer is reported"

## 9. frontend: hype snack (components/infrastructure/fan/web/route/my-artists, global/page-help)

- [x] 9.1 Add `hypeReachWords(hype, home)` and the `hypeReach.*` keys (JA and EN); verify unit tests for each level, with a home and without one
- [x] 9.2 Add the `onboarding.hypeSnackSeen:<level>` flags to `onboarding-storage.ts` and rename `clearAllHelpSeen()` to `clearOnboardingSeenFlags()`, clearing both prefixes; verify unit tests and the page-help scenarios of "Help seen flags cleared on onboarding reset"
- [x] 9.3 Replace `offerPush()` on My Artists with the hype snack (`replaceKey: hype:<artistId>`, action from `pushState()`, 「登録する」 for a guest) and remove the `pushOffer.hypeChanged` key; verify component tests for every scenario of "A hype change says where new concerts are pushed"
- [x] 9.4 Run My Artists with Playwright against a local build: as a signed-in fan with push undecided, change three artists quickly and check that at most three snacks show and each reads the place words; as a guest, check the 「登録する」 form

## 10. frontend: ticket section (components/infrastructure/fan/web/global/event-detail-sheet, route/dashboard)

- [x] 10.1 Set `JOURNEY_STATUS_CONFIG.tracking.icon` to 🔔; verify the scenarios of "Journey-Status Presentation" in the map's unit test and the card badge and filter chip stories
- [x] 10.2 Rebuild the sheet order and the ticket section: calendar link in the date row, the notification button, the `aria-pressed` status row (pressing the selected one deletes the journey), the push line from `pushState()`, the official site button, no footer; replace the `eventDetail.*` keys as "Localized Concert Detail Sheet Copy" lists; verify component tests for every scenario of "The ticket section follows the venue and holds the official site button", "The ticket section leads with the ticket sale notification button", "The push line says what the current status brings", "Status controls are shown to signed-in fans only", "Ticket Status buttons accessibility", "The ticket section shows the four statuses in one row" and "Concert detail sheet", and update the sheet's stories and visual baselines
- [x] 10.3 Reword the calendar-tracking snack and the hype-raise snack from `infer-hype-and-journey` (the raise snack through `hypeReachWords`); verify component tests for every scenario of "Adding to the calendar starts tracking" and "A hype level raised by a journey change is shown with undo"
- [x] 10.4 Add the out-of-range notice (lane → lowest matching level, `followStore.setHype`, saved form with the push action); verify component tests for every scenario of "The out-of-range notice widens what is pushed"
- [x] 10.5 If the route template markers change, update `ROUTE_MARKERS` and verify `npm run build && npm run verify:build-templates`

## 11. frontend: guest tracking through sign-up (stories/track-ticket-journey, stories/sign-up-or-sign-in)

- [x] 11.1 Add `trackEventId` to `AuthFlowState` and the `ticket_notify` sign-up source; the guest's notification button starts sign-up with `returnTo: /concerts/<id>`, and the auth callback calls `TicketJourneyService.SetStatus(TRACKING)` after the account is resolved and the guest merge ran; verify component tests for every scenario of "A guest's notification button starts sign-up" and of "A sign-in from any screen resolves the account with Create"
- [x] 11.2 Add E2E tests for every scenario of "A guest's request for ticket sale notifications survives sign-up", "Guests and signed-out fans see no statuses" and "Sign-up and sign-in start only where the person chooses"; verify they pass against a local build

## 12. frontend: release

- [x] 12.1 Run `make check`, open the frontend PR (OpenSpec Traceability filled), merge and release; then in prod with the owner's account open a tracked concert and a concert outside the hype level, and confirm the ticket section, the push line and the out-of-range notice read as the specs state
