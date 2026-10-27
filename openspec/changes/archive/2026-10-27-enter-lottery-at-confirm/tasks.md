## 1. Proto and rules (specification)

- [x] 1.1 Apply design "Proto": delete `Start` and its messages; change `AuthorizeCardRequest`, `AuthorizeCardResponse` and `ConfirmRequest`; reserve `LOTTERY_ENTRY_STATE_DRAFT` (5); make `LotteryEntry.card_authorization_id` required and remove its CEL rule; rewrite the comments that describe the Draft and Start; update the `ReferralCode` comment; verify `make check` (buf lint, format, forbidden words) passes
- [x] 1.2 Rewrite the multi-step purchase line of `.claude/skills/rpc-design/SKILL.md:41` (design "Proto") and verify it no longer lists `LotteryEntryService` under `Start`
- [x] 1.3 Delete `openspec/changes/remove-lottery-entry-withdrawal`, and move `identity-ekyc-jpki`'s `usecase/lottery-entry/start` delta to `authorize-card`, in the plan PR; verify `openspec list` no longer shows the first and `openspec validate identity-ekyc-jpki --strict` passes
- [x] 1.4 Open the specification PR with the `buf skip breaking` label, merge it once `CI Success` passes, cut the Release and confirm `buf-release.yml` succeeds (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 2. Webhook subscription (cloud-provisioning)

- [x] 2.1 Add `payment_intent.amount_capturable_updated` to the Stripe webhook endpoint's `enabledEvents` (`src/index.ts`) and update its description; verify `pulumi preview` for prod shows only the endpoint's event list changing, then merge and confirm the prod `pulumi up`

## 3. Schema (backend)

- [x] 3.1 Add the Atlas migration of design "Schema migration" and update `schema.sql`; verify `atlas migrate validate`, `make lint-schema` and a migration integration test (`migrationtest`) that loads a Draft, a Withdrawn entry with a Referral, an Entered entry with a Referral and a Checkout with a Referral, applies the migration, and finds the Draft and Withdrawn gone, the codes in `lottery_entries.referral_code` and `checkouts.referral_code`, `referrals` dropped, and the new constraints rejecting state 5 and a NULL card authorization

## 4. Entities (components/entity/lottery-entry, card-authorization, checkout, referral)

- [x] 4.1 Remove the Draft and Withdrawn states, `IsConfirmable`, `IsActive` and `IsWithdrawable` from the LotteryEntry entity; add `ReferralCode`; verify the unit test "New entry" and the count-rule tests pass
- [x] 4.2 Add purpose, user, ticket type, ticket count and referral code to CardAuthorization and its purchase type; verify the existing "Accepted card brands" and "A card authorization confirms a purchase…" tests pass
- [x] 4.3 Add the referral code to Checkout, remove the Referral entity and its repository; verify the ReferralCode format tests ("Code from a link", "Empty or too long", "Other characters", "One code whatever the case in links") pass and `make check` has no remaining reference to the Referral

## 5. Entity operations

- [x] 5.1 `LotteryEntry.Create` (components/entity/lottery-entry/create), as in design "Check-then-act and locked rows"; verify one contract test per scenario ("Entry stored", "Second entry", "Double tap", "Same card authorization again", "Entry for another event of the same sale", "After the end time", "Unknown ticket type"), and that `Get` returns entries in any state ("Existing entry", "Unknown id")
- [x] 5.2 Remove `GetOrCreateDraft`, `SetCardAuthorization` and `UpdateState` with their tests and mocks; change `ListUndrawnForTicketType`, `GetStatsByTicketType`, `PersistDrawOutcome` and `ListByTicketTypeAndUser`; verify their contract tests ("Mixed states", "No candidates"; "After the draw", "Before the draw", "No entries"; "Outcome recorded", "Failure leaves nothing recorded", "Empty draw"; "Entry of the user", "Never entered") and `Order.ListLotteryEntryIDsAwaitingIssuance` "Not won" pass
- [x] 5.3 `CardAuthorization.Create` and `Get` carry the purchase as PaymentIntent metadata (design "The PaymentIntent carries the purchase"); verify the contract tests "Card authorization opened", "Retried after a lost response", "Lottery entry authorized again", "Non-positive amount", "Payment provider unavailable", "Waiting for card authentication", "Authorized card authorization", "Unknown id" and Get's "Payment provider unavailable" against the Stripe test API (`make test-stripe-e2e`)
- [x] 5.4 `Checkout.SetReferralCode` (components/entity/checkout/set-referral-code); verify one contract test per scenario ("First code", "Last link wins", "Committed checkout keeps its code", "Unknown checkout")
- [x] 5.5 `Order.ListReferralStatsByEvent` replaces `Referral.ListStatsByEvent`; verify one contract test per scenario ("Two codes and direct purchases", "Lottery win counted once its Order exists", "Refunded order excluded", "Abandoned checkout not counted", "Other events not counted", "No purchases")
- [x] 5.6 `TicketSale.ListDueForDraw` returns a sale 1 minute after its end time; verify "Closed and undrawn", "Just closed", "Still open", "Already drawn", "Discovered lottery has closed"
- [x] 5.7 Remove the Draft clause from the event removal check (`event_removal.go`), shared by Concert and Organizer deletion; verify the contract tests of "Paid records and purchases in progress block the delete" and "Delete refuses while purchases or payouts remain" pass

## 6. Usecases

- [x] 6.1 Delete `LotteryEntryUseCase.Start` and `Withdraw` with their tests and mocks; verify `make check`
- [x] 6.2 Rewrite `LotteryEntryUseCase.AuthorizeCard`; verify one unit test per scenario of "Card authorized for a ticket count while the window is open" and "Verification gate"
- [x] 6.3 Rewrite `LotteryEntryUseCase.Confirm` as in design "Confirm in one place, for two callers"; verify one unit test per scenario of "An entry is made from an authorized card authorization" (including "Amount differs", "TicketType gone", "Release fails") and "Card authentication completed without the fan"
- [x] 6.4 Change `RunDraw` to draw only Entered entries; verify the unit tests of "Draw a sale's entered entries" pass with the rest of the run-draw spec
- [x] 6.5 Update the `IssueFromCapturedWin` unit test "Entry not won" to Entered and Lost; verify it passes
- [x] 6.6 `CheckoutUseCase.Start` sets the code with `Checkout.SetReferralCode`, and `TicketSaleUseCase.ListOwnByEvent` reads `Order.ListReferralStatsByEvent`; verify the unit tests of "Record the referral code the checkout started with" and "Purchases per referral code"

## 7. Adapters (backend)

- [x] 7.1 Upgrade the generated package; change `LotteryEntryHandler` (no Start or Withdraw; AuthorizeCard returns the id; Confirm takes the card authorization); verify the handler tests of "Every lottery entry call is made by the signed-in fan" and "Lottery entry requests are validated at the boundary"
- [x] 7.2 Route `payment_intent.amount_capturable_updated` from the Stripe webhook adapter straight to `LotteryEntryUseCase.Confirm`, keeping the processed-event check and record (design "Confirm in one place, for two callers"); verify the tests "Fan closed the browser", "Entry already made", "Payment provider unreachable" and "Refund confirmation"

## 8. Stories (backend integration)

- [x] 8.1 Rewrite `lottery_story_integration_test.go`; verify against the Stripe test API (`STRIPE_INTEGRATION_TEST=1`): "Demand within quantity" (now reached through AuthorizeCard and Confirm), "Count changed before confirming", "Browser closed after card authentication" (the test runs the notice's `Confirm` instead of the fan's), "Entry made only after the window closed", "Card authentication abandoned", "Oversubscribed sale", "Presale winner at the limit", "Presale winner below the limit"
- [x] 8.2 Add an rdb integration test that runs the fan's `Confirm` and the notice's `Confirm` for one Authorized card authorization at the same time just before the end time, and verify one entry exists and the card authorization is not released ("Fan and notice at the same time")
- [x] 8.3 Update the referral story test so a lottery entry carries the code it was authorized with; verify "Guest from a member's link buys after signing up" and the other scenarios of `stories/attribute-a-purchase-to-a-referral-link`

## 9. Frontend

- [x] 9.1 Upgrade the generated package; the lottery entry screen calls `AuthorizeCard` with the count, details and kept code, calls it again on a count change, and confirms with `card_authorization_id`; remove the Draft from `entities/lottery-entry.ts` and the status route; verify the component tests of "Saved details are prefilled", "The kept referral code goes with the entry", "Starting and submitting an entry are reported" and "A refused entry is explained", and `make check`
- [x] 9.2 Run the entry flow with Playwright on a local build against stubbed `AuthorizeCard` and `Confirm`: choose 2 tickets, go back, choose 3, and confirm; the stub sees two `AuthorizeCard` calls (2, then 3), and the done step shows the 3-ticket entry

## 10. Release and production check

- [x] 10.1 Merge the backend PR, cut the release, and confirm in prod (read-only) that the AtlasMigration is applied, `referrals` is gone and `uq_lottery_entries_ticket_type_user` exists, the fan-api rollout finished, and `gh workflow run stripe-sandbox-e2e.yml` succeeds
- [x] 10.2 Merge the frontend PR, cut the release and confirm the rollout

## 11. Archive

- [x] 11.1 Apply the main-spec Purposes of design "Main-spec Purposes, edited at archive", delete the emptied specs, and verify `openspec validate --specs` and `make check` pass
